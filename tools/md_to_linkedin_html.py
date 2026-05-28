#!/usr/bin/env python3
"""
Convert Markdown (LaTeX math + tables) to HTML that pastes cleanly into LinkedIn Articles.

LinkedIn's article editor does NOT preserve HTML <table> layout (cells get concatenated) and
does NOT handle KaTeX/MathJax paste well (equations duplicate, e.g. "1H+11B1H+11B").

This converter uses a LinkedIn-safe strategy:
  • Tables → bullet lists with em-dash separators between columns
  • Math → single Unicode / HTML <sup>/<sub> text (no KaTeX, no $ delimiters)

Workflow:
  1. python3 tools/md_to_linkedin_html.py proton_boron_rand.md
  2. Open the .html file in Chrome or Firefox
  3. Click "Select article for copy" → Ctrl+C → paste into LinkedIn

Usage:
  python3 tools/md_to_linkedin_html.py INPUT.md [-o OUTPUT.html]
  python3 tools/md_to_linkedin_html.py INPUT.md --clipboard
"""

from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

import markdown
from bs4 import BeautifulSoup, NavigableString, Tag
from pylatexenc.latex2text import LatexNodes2Text

_LATEX2TEXT = LatexNodes2Text()

_SUPERSCRIPT = str.maketrans(
    "0123456789+-=()",
    "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾",
)
_SUBSCRIPT = str.maketrans(
    "0123456789+-=()",
    "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎",
)

_LATEX_REPLACEMENTS = (
    (r"\\rightarrow", "→"),
    (r"\\leftarrow", "←"),
    (r"\\approx", "≈"),
    (r"\\times", "×"),
    (r"\\cdot", "·"),
    (r"\\pm", "±"),
    (r"\\leq", "≤"),
    (r"\\geq", "≥"),
    (r"\\neq", "≠"),
    (r"\\infty", "∞"),
    (r"\\varepsilon", "ε"),
    (r"\\circ", "°"),
    (r"\\pi", "π"),
    (r"\\sigma", "σ"),
    (r"\\alpha", "α"),
    (r"\\beta", "β"),
    (r"\\gamma", "γ"),
    (r"\\text\{([^}]*)\}", r"\1"),
    (r"\\mathbf\{([^}]*)\}", r"\1"),
    (r"\\mathrm\{([^}]*)\}", r"\1"),
    (r"\\,", " "),
    (r"\\;", " "),
    (r"\\!", ""),
    (r"\\quad", " "),
    (r"\\qquad", "  "),
    (r"\\left", ""),
    (r"\\right", ""),
    (r"\\xrightarrow\{[^}]*\}", "→"),
)

PAGE_STYLE = """
body {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 17px;
  line-height: 1.55;
  color: #1a1a1a;
  max-width: 740px;
  margin: 2rem auto;
  padding: 0 1.25rem;
}
h1 { font-size: 1.75rem; margin: 1.5rem 0 0.75rem; }
h2 { font-size: 1.35rem; margin: 1.75rem 0 0.6rem; border-bottom: 1px solid #ddd; padding-bottom: 0.25rem; }
h3 { font-size: 1.15rem; margin: 1.25rem 0 0.5rem; }
h4 { font-size: 1.05rem; margin: 1rem 0 0.4rem; }
p { margin: 0.65rem 0; }
ul, ol { margin: 0.5rem 0 0.75rem; padding-left: 1.5rem; }
li { margin: 0.35rem 0; }
hr { border: none; border-top: 1px solid #ccc; margin: 1.5rem 0; }
strong { font-weight: 700; }
.math-block {
  text-align: center;
  margin: 1rem 0;
  font-style: italic;
}
.instructions {
  font-family: system-ui, sans-serif;
  font-size: 14px;
  background: #f7f9fc;
  border: 1px solid #c5d4e8;
  border-radius: 6px;
  padding: 12px 14px;
  margin-bottom: 2rem;
}
.instructions strong { display: block; margin-bottom: 6px; }
@media print { .instructions { display: none; } }
"""


def _escape_excited_state_asterisks(text: str) -> str:
    """Prevent markdown from treating nuclear C* / Be* markers as italics."""
    return re.sub(
        r"([A-Za-z0-9⁰¹²³⁴⁵⁶⁷⁸⁹]+)\*(\s*→)",
        r"\1∗\2",
        text,
    )


def _normalize_math_delimiters(text: str) -> str:
    text = re.sub(
        r"(?<!\$)\$\$(?!\$)([^\n]+?)(?<!\$)\$\$(?!\$)",
        r"\n$$\1$$\n",
        text,
        flags=re.DOTALL,
    )
    return text


def _unwrap_arithmatex_latex(raw: str) -> str:
    text = raw.strip()
    for open_d, close_d in (("\\[", "\\]"), ("\\(", "\\)"), ("$$", "$$"), ("$", "$")):
        if text.startswith(open_d) and text.endswith(close_d):
            return text[len(open_d) : -len(close_d)].strip()
    return text


def _carets_to_unicode(text: str) -> str:
    def repl_braced(match: re.Match[str]) -> str:
        inner = match.group(1)
        if re.fullmatch(r"[0-9+\-=()]+", inner):
            return inner.translate(_SUPERSCRIPT)
        return f"^{inner}"

    def repl_simple(match: re.Match[str]) -> str:
        inner = match.group(1)
        return inner.translate(_SUPERSCRIPT)

    text = re.sub(r"\^\{([^}]+)\}", repl_braced, text)
    text = re.sub(r"\^([0-9+\-=()]+)", repl_simple, text)
    return text


_IDENT_WITH_UNDERSCORES = re.compile(
    r"(?<![A-Za-z0-9])([A-Za-z][A-Za-z0-9]*(?:_[A-Za-z0-9]+)+)(?![A-Za-z0-9_])"
)


def _apply_identifier_subscripts(text: str, *, as_html: bool) -> str:
    """``P_fusion``, ``fuel_coupling_norm`` → subscript the part after the first ``_``."""

    def repl(match: re.Match[str]) -> str:
        token = match.group(1)
        head, _, tail = token.partition("_")
        if not tail:
            return token
        if as_html:
            return f"{head}<sub>{html.escape(tail)}</sub>"
        if re.fullmatch(r"[0-9+\-=(),.]+", tail):
            return head + tail.translate(_SUBSCRIPT)
        return token

    return _IDENT_WITH_UNDERSCORES.sub(repl, text)


def _underscores_to_unicode(text: str) -> str:
    def repl_braced(match: re.Match[str]) -> str:
        inner = match.group(1)
        if re.fullmatch(r"[A-Za-z0-9+\-=()]+", inner):
            return inner.translate(_SUBSCRIPT)
        return f"_{inner}"

    text = re.sub(r"_\{([^}]+)\}", repl_braced, text)
    text = _apply_identifier_subscripts(text, as_html=False)
    return text


def _append_html_fragment(parent: Tag, fragment_html: str) -> None:
    if not fragment_html or not fragment_html.strip():
        return
    parsed = BeautifulSoup(fragment_html, "html.parser")
    for node in list(parsed.contents):
        parent.append(node)


def latex_to_plain(latex: str) -> str:
    """Convert LaTeX to plain Unicode text (no duplicate sources for paste)."""
    text = latex.strip()
    for pattern, repl in _LATEX_REPLACEMENTS:
        text = re.sub(pattern, repl, text)
    text = re.sub(r"\\frac\{([^}]*)\}\{([^}]*)\}", r"\1/\2", text)
    text = re.sub(r"\{\}", "", text)

    try:
        text = _LATEX2TEXT.latex_to_text(text)
    except Exception:
        pass

    text = _carets_to_unicode(text)
    text = _underscores_to_unicode(text)
    text = text.replace("^", "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def latex_to_html(latex: str) -> str:
    """LaTeX → HTML with <sup>/<sub> where Unicode is insufficient."""
    text = latex.strip()
    for pattern, repl in _LATEX_REPLACEMENTS:
        text = re.sub(pattern, repl, text)
    text = re.sub(r"\\frac\{([^}]*)\}\{([^}]*)\}", r"(\1)/(\2)", text)
    text = re.sub(r"\{\}", "", text)

    try:
        text = _LATEX2TEXT.latex_to_text(text)
    except Exception:
        pass

    def sup_repl(m: re.Match[str]) -> str:
        inner = m.group(1)
        if re.fullmatch(r"[0-9+\-=()]+", inner):
            return f"<sup>{inner.translate(_SUPERSCRIPT)}</sup>"
        return f"<sup>{html.escape(inner)}</sup>"

    def sub_repl(m: re.Match[str]) -> str:
        inner = m.group(1)
        if re.fullmatch(r"[A-Za-z0-9+\-=()]+", inner):
            converted = inner.translate(_SUBSCRIPT)
            if converted != inner:
                return f"<sub>{converted}</sub>"
        return f"<sub>{html.escape(inner)}</sub>"

    text = re.sub(r"\^\{([^}]+)\}", sup_repl, text)
    text = re.sub(r"\^([0-9+\-=()]+)", sup_repl, text)
    text = re.sub(r"_\{([^}]+)\}", sub_repl, text)
    text = re.sub(
        r"_\[([^\]]+)\]",
        lambda m: f"<sub>{html.escape(m.group(1))}</sub>",
        text,
    )
    text = _apply_identifier_subscripts(text, as_html=True)
    text = text.replace("^", "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _latex_to_soup_tag(latex: str, display: bool) -> Tag:
    soup = BeautifulSoup("", "html.parser")
    rendered = latex_to_html(latex)
    if display:
        tag = soup.new_tag("p", attrs={"class": "math-block"})
        _append_html_fragment(tag, rendered)
    else:
        tag = soup.new_tag("span")
        _append_html_fragment(tag, rendered)
    return tag


def _cell_inner_html(cell: Tag) -> str:
    parts: list[str] = []
    for child in cell.children:
        if isinstance(child, NavigableString):
            parts.append(str(child))
        elif isinstance(child, Tag):
            parts.append(str(child))
    return "".join(parts).strip()


def _table_to_list(table: Tag) -> Tag:
    soup = BeautifulSoup("", "html.parser")
    ul = soup.new_tag("ul")

    headers: list[str] = []
    thead = table.find("thead")
    if thead:
        row = thead.find("tr")
        if row:
            headers = [th.get_text(" ", strip=True) for th in row.find_all("th")]

    body_rows = table.find("tbody")
    rows = body_rows.find_all("tr") if body_rows else table.find_all("tr")

    for tr in rows:
        if thead and tr in thead.find_all("tr"):
            continue
        cells = tr.find_all(["td", "th"])
        if not cells:
            continue
        if all(c.name == "th" for c in cells) and not headers:
            headers = [c.get_text(" ", strip=True) for c in cells]
            continue

        values = [_cell_inner_html(c) for c in cells]
        if values and all(re.fullmatch(r"[\s\-:|]+", re.sub(r"<[^>]+>", "", v)) for v in values):
            continue
        li = soup.new_tag("li")

        if len(values) == 1:
            _append_html_fragment(li, values[0])
        elif len(values) == 2:
            _append_html_fragment(li, values[0])
            li.append(" — ")
            _append_html_fragment(li, values[1])
        elif headers and len(headers) == len(values):
            _append_html_fragment(li, values[0])
            for val in values[1:]:
                li.append(" — ")
                _append_html_fragment(li, val)
        else:
            for i, val in enumerate(values):
                if i:
                    li.append(" — ")
                _append_html_fragment(li, val)

        ul.append(li)

    return ul


def _replace_math(soup: BeautifulSoup) -> None:
    for tag in list(
        soup.find_all(["span", "div"], class_=lambda c: c and "arithmatex" in c)
    ):
        latex = _unwrap_arithmatex_latex(tag.get_text())
        if not latex:
            tag.decompose()
            continue
        replacement = _latex_to_soup_tag(latex, display=tag.name == "div")
        tag.replace_with(replacement)

    # Any leftover $...$ in text nodes (shouldn't happen, but guard)
    for text_node in list(soup.find_all(string=re.compile(r"\$"))):
        parent = text_node.parent
        if not parent or parent.name in ("script", "style"):
            continue
        new_text = text_node
        for match in re.finditer(r"\$\$([^$]+)\$\$|\$([^$]+)\$", str(text_node)):
            latex = match.group(1) or match.group(2)
            plain = latex_to_plain(latex)
            new_text = new_text.replace(match.group(0), plain)
        text_node.replace_with(new_text)


def _replace_tables(soup: BeautifulSoup) -> None:
    for table in list(soup.find_all("table")):
        table.replace_with(_table_to_list(table))


_IMAGE_MD = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")


def _resolve_image_path(src: str, base_dir: Path) -> Path:
    raw = src.strip().split()[0] if src.strip() else ""
    p = Path(raw)
    if p.is_absolute():
        return p.resolve()
    return (base_dir / p).resolve()


def _substitute_images_in_markdown(md: str, base_dir: Path) -> str:
    def repl(match: re.Match[str]) -> str:
        path = match.group(2).strip()
        if not path or path.startswith("<") or "://" in path:
            return match.group(0)
        full = _resolve_image_path(path, base_dir)
        return f"\n\nINSERT HERE: {full}\n\n"

    return _IMAGE_MD.sub(repl, md)


def _replace_images(soup: BeautifulSoup, base_dir: Path) -> None:
    for img in list(soup.find_all("img")):
        src = (img.get("src") or "").strip()
        full = _resolve_image_path(src, base_dir) if src else Path(src or "unknown")
        p = soup.new_tag("p")
        p.string = f"INSERT HERE: {full}"
        img.replace_with(p)


def _strip_code_blocks(soup: BeautifulSoup) -> None:
    for pre in list(soup.find_all("pre")):
        pre.decompose()
    for code in list(soup.find_all("code")):
        parent = code.parent
        if parent and parent.name == "p" and parent.get_text(strip=True) == code.get_text(strip=True):
            parent.decompose()
        else:
            code.unwrap()


def _flatten_nested_lists(soup: BeautifulSoup) -> None:
    """LinkedIn mangles nested bullets — promote nested items to a single list level."""
    while True:
        nested_ul = None
        for ul in soup.find_all("ul"):
            if ul.find_parent("ul") is not None:
                nested_ul = ul
                break
        if nested_ul is None:
            return
        parent_ul = nested_ul.find_parent("ul")
        parent_li = nested_ul.find_parent("li")
        if parent_ul is None or parent_li is None:
            nested_ul.unwrap()
            continue
        prefix_parts: list[str] = []
        for child in parent_li.children:
            if getattr(child, "name", None) == "ul":
                break
            if isinstance(child, NavigableString):
                prefix_parts.append(str(child))
            elif getattr(child, "name", None) != "ul":
                prefix_parts.append(child.get_text())
        prefix = " ".join("".join(prefix_parts).split())
        insert_at = parent_li
        for sub_li in list(nested_ul.find_all("li", recursive=False)):
            text = sub_li.get_text(" ", strip=True)
            line = f"{prefix} — {text}" if prefix else text
            new_li = soup.new_tag("li")
            new_li.string = line
            insert_at.insert_after(new_li)
            insert_at = new_li
        parent_li.decompose()


def _cap_heading_depth(soup: BeautifulSoup) -> None:
    for tag in soup.find_all(["h4", "h5", "h6"]):
        tag.name = "h3"


_PIPE_ROW = re.compile(r"^\|.+\|\s*$")
_PIPE_SEP = re.compile(r"^\|[\s\-:|]+\|\s*$")
_PIPE_TWO_COL = re.compile(r"^\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*$")


def _drop_orphan_table_separator_lines(md: str) -> str:
    """Remove ``|------|`` rows that are not between two pipe-table data/header rows."""
    lines = md.splitlines()
    out: list[str] = []

    def is_pipe_row(line: str) -> bool:
        s = line.strip()
        return bool(_PIPE_ROW.match(s)) and not _PIPE_SEP.match(s)

    for i, line in enumerate(lines):
        if not _PIPE_SEP.match(line.strip()):
            out.append(line)
            continue
        prev_ok = i > 0 and is_pipe_row(lines[i - 1])
        next_ok = i + 1 < len(lines) and is_pipe_row(lines[i + 1])
        if prev_ok and next_ok:
            out.append(line)
    return "\n".join(out)


def _repair_pipe_tables_in_markdown(md: str) -> str:
    """
    Fix tables that lost GFM separator rows (render as ``<p>| col | …</p>``) and convert
    two-column spec sheets to bullets before the Markdown parser runs.
    """
    md = _drop_orphan_table_separator_lines(md)
    lines = md.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        hm = _PIPE_TWO_COL.match(line.strip())
        if hm and hm.group(1).strip().lower() == "spec":
            if i + 1 < len(lines) and _PIPE_SEP.match(lines[i + 1].strip()):
                i += 2
            while i < len(lines):
                dm = _PIPE_TWO_COL.match(lines[i].strip())
                if not dm:
                    break
                out.append(f"- **{dm.group(1).strip()}:** {dm.group(2).strip()}")
                i += 1
            out.append("")
            continue
        if _PIPE_ROW.match(line.strip()) and i + 1 < len(lines):
            nxt = lines[i + 1].strip()
            if _PIPE_ROW.match(nxt) and not _PIPE_SEP.match(nxt):
                cells = [c for c in line.split("|")[1:-1]]
                out.append(line)
                out.append("|" + "|".join("---" for _ in cells) + "|")
                i += 1
                continue
        out.append(line)
        i += 1
    return "\n".join(out)


def _pipe_row_cells(row: str) -> list[str]:
    return [c.strip() for c in row.strip().strip("|").split("|")]


def _pipe_rows_to_ul(soup: BeautifulSoup, rows: list[str]) -> Tag | None:
    ul = soup.new_tag("ul")
    for row in rows:
        if _PIPE_SEP.match(row.strip()):
            continue
        cells = _pipe_row_cells(row)
        if not cells or all(re.fullmatch(r"[\s\-:|]+", c) for c in cells):
            continue
        li = soup.new_tag("li")
        if len(cells) == 1:
            li.string = cells[0]
        elif len(cells) == 2:
            strong = soup.new_tag("strong")
            strong.string = f"{cells[0]}:"
            li.append(strong)
            li.append(f" {cells[1]}")
        else:
            strong = soup.new_tag("strong")
            strong.string = f"{cells[0]}:"
            li.append(strong)
            li.append(" " + " — ".join(cells[1:]))
        ul.append(li)
    return ul if ul.find("li") else None


def _repair_pipe_tables_in_html(soup: BeautifulSoup) -> None:
    """Convert ``<p>`` blocks that contain pipe-table text into bullet lists."""
    for p in list(soup.find_all("p")):
        text = p.get_text().strip()
        if _PIPE_SEP.match(text):
            p.decompose()
            continue
        if "|" not in text or text.count("|") < 4:
            continue
        rows = [ln.strip() for ln in text.splitlines() if ln.strip().startswith("|")]
        if len(rows) < 2:
            continue
        ul = _pipe_rows_to_ul(soup, rows)
        if ul is not None:
            p.replace_with(ul)


def markdown_to_body_html(md: str, *, base_dir: Path | None = None) -> str:
    md = _escape_excited_state_asterisks(md)
    md = _normalize_math_delimiters(md)
    md = _repair_pipe_tables_in_markdown(md)
    if base_dir is not None:
        md = _substitute_images_in_markdown(md, base_dir)
    html_fragment = markdown.markdown(
        md,
        extensions=[
            "markdown.extensions.tables",
            "markdown.extensions.fenced_code",
            "markdown.extensions.nl2br",
            "markdown.extensions.sane_lists",
            "pymdownx.arithmatex",
        ],
        extension_configs={
            "pymdownx.arithmatex": {
                "generic": True,
                "block_tag": "div",
                "inline_tag": "span",
            }
        },
    )
    soup = BeautifulSoup(html_fragment, "html.parser")
    _replace_math(soup)
    _repair_pipe_tables_in_html(soup)
    _replace_tables(soup)
    if base_dir is not None:
        _replace_images(soup, base_dir)
    _strip_code_blocks(soup)
    _flatten_nested_lists(soup)
    _cap_heading_depth(soup)
    return str(soup)


def wrap_document(body_html: str, title: str) -> str:
    safe_title = html.escape(title)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_title}</title>
  <style>{PAGE_STYLE}</style>
</head>
<body>
  <div class="instructions">
    <strong>LinkedIn-safe paste</strong>
    Tables are bullet lists; math is plain Unicode (no KaTeX). Open in Chrome/Firefox,
    click <em>Select article for copy</em>, then Ctrl+C and paste into LinkedIn.
    <p style="margin: 0.75rem 0 0;">
      <button type="button" id="select-article"
        style="font-size: 14px; padding: 6px 12px; cursor: pointer;">
        Select article for copy
      </button>
    </p>
  </div>
  <article id="content">
{body_html}
  </article>
  <script>
    document.getElementById("select-article").addEventListener("click", function () {{
      var article = document.getElementById("content");
      var range = document.createRange();
      range.selectNodeContents(article);
      var sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
      article.scrollIntoView({{block: "start"}});
    }});
  </script>
</body>
</html>
"""


def copy_html_to_clipboard(html_path: Path) -> bool:
    data = html_path.read_text(encoding="utf-8").encode("utf-8")
    if shutil.which("wl-copy"):
        return subprocess.run(
            ["wl-copy", "--type", "text/html"], input=data, check=False
        ).returncode == 0
    if shutil.which("xclip"):
        return subprocess.run(
            ["xclip", "-selection", "clipboard", "-t", "text/html"],
            input=data,
            check=False,
        ).returncode == 0
    return False


def write_linkedin_html(
    md_path: Path,
    *,
    output: Path | None = None,
    title: str | None = None,
) -> Path:
    """Convert Markdown to LinkedIn-safe HTML; returns output path."""
    md = md_path.read_text(encoding="utf-8")
    body = markdown_to_body_html(md, base_dir=md_path.parent)
    doc_title = title or md_path.stem.replace("_", " ").title()
    document = wrap_document(body, doc_title)
    out = output or md_path.with_suffix(".html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(document, encoding="utf-8")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Markdown → LinkedIn-safe HTML (Unicode math, list tables)."
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--clipboard", action="store_true")
    args = parser.parse_args()

    if not args.input.is_file():
        print(f"error: not found: {args.input}", file=sys.stderr)
        return 1

    out = write_linkedin_html(args.input, output=args.output)
    document = out.read_text(encoding="utf-8")
    print(f"Wrote {out} ({len(document):,} bytes)")
    print("Open in browser → Select article for copy → paste into LinkedIn.")

    if args.clipboard:
        if copy_html_to_clipboard(out):
            print("HTML copied to clipboard.")
        else:
            print("Install wl-copy or xclip for --clipboard.", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
