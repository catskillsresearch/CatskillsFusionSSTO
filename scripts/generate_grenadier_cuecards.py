#!/usr/bin/env python3
"""Generate full Grenadier cue-card binders + menu popups."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Cuecards"
W, H = 496, 664
MARGIN = 28


def _font(size: int):
    for p in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _card(title: str, lines: list[str], footer: str = "GRENADIER TA") -> Image.Image:
    im = Image.new("RGB", (W, H), (245, 242, 230))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 52), fill=(28, 32, 40))
    d.text((MARGIN, 14), title[:42], fill=(245, 245, 248), font=_font(20))
    y = 68
    body, bold = _font(15), _font(16)
    for line in lines:
        if not line:
            y += 8
            continue
        font = bold if line.startswith("##") else body
        text = line[2:].strip() if line.startswith("##") else line
        fill = (20, 60, 100) if line.startswith("##") else (20, 20, 22)
        words = text.split()
        cur = ""
        for w in words:
            trial = (cur + " " + w).strip()
            if d.textbbox((0, 0), trial, font=font)[2] > W - 2 * MARGIN and cur:
                d.text((MARGIN, y), cur, fill=fill, font=font)
                y += 20
                cur = w
            else:
                cur = trial
        if cur:
            d.text((MARGIN, y), cur, fill=fill, font=font)
            y += 22 if line.startswith("##") else 20
        if y > H - 56:
            break
    d.rectangle((0, H - 36, W, H), fill=(28, 32, 40))
    d.text((MARGIN, H - 28), footer, fill=(200, 200, 205), font=_font(12))
    d.rectangle((2, 2, W - 3, H - 3), outline=(80, 80, 85), width=2)
    return im


def save_pair(prefix: str, page: int, left: tuple[str, list[str]], right: tuple[str, list[str]]) -> None:
    _card(*left).save(OUT / f"{prefix}-L-{page:02d}.jpg", quality=92)
    _card(*right).save(OUT / f"{prefix}-R-{page:02d}.jpg", quality=92)


def save_png(name: str, title: str, lines: list[str], size=(455, 520)) -> None:
    _card(title, lines).resize(size, Image.Resampling.LANCZOS).save(OUT / name)
    print("wrote", name)


POWERED: list[tuple[tuple[str, list[str]], tuple[str, list[str]]]] = [
    (
        ("GRENADIER — INDEX", ["## Sections", "1 Plant services", "2 Avionics keep", "3 CHARM", "4 Engine σ", "5 RCS green", "6 Safing / landing", "", "KEDW · Plan A · no cargo"]),
        ("VEHICLE ID", ["CATSKILLS-SSTO-TA-GRENADIER", "", "CHARM + 3-cycle electric", "OMS engines deleted", "Full Shuttle RCS nozzles", "LMP-103S green mono"]),
    ),
    (
        ("PLANT SERVICES", ["## APU row = pad/plant", "APU1 ground cart ONLINE", "APU2 flight battery ONLINE", "APU3 cryo ENABLE", "", "APU ctrl1 Magnet ARM", "APU ctrl2 Fuel ENABLE", "APU ctrl3 RF ENABLE"]),
        ("PLANT SERVICES (2)", ["SSME-right A = Vacuum READY", "OMS L/R = σ − / σ +", "Throttle = engine throttle", "Main Eng Limit→Enable = SCRAM", "", "Fuel cells = inert"]),
    ),
    (
        ("AVIONICS KEEP", ["## Flight path", "RHC / THC / DAP / RCS", "HUD / ADI / HSI", "GPC / IDP / MEDS"]),
        ("NAV / IMU", ["√ IMU / star tracker", "COAS as required", "No ET/SRB stack UI"]),
    ),
    (
        ("COMM / GNC", ["Standard Shuttle GNC keep", "DAP modes for RCS jets", "Abort CWS (Grenadier msgs later)"]),
        ("DPS", ["IDP / GPC power as required", "Keyboard / MDU dim"]),
    ),
    (
        ("ECLS", ["Cabin fans / lighting", "O₂/N₂ heritage keep", "Bay doors: plant access"]),
        ("EPS → BUS", ["CHARM plant bus = primary", "Flight battery float/backup", "No fuel-cell reactants"]),
    ),
    (
        ("WATER / FUEL", ["√ water-kg shield+σ3", "√ proton + ¹¹B inventory", "Water ≠ RCS propellant"]),
        ("BATTERY", ["√ battery-kwh ≥ min", "ONLINE before light-off", "Space restart budget"]),
    ),
    (
        ("CHARM PRECOND", ["mode OFF / scram=0", "√ inventories", "Ground cart available", "Bay doors as ops require"]),
        ("CHARM POWER PATH", ["source = CART (Earth)", "cart-tied = 1", "√ aux-bus-v", "battery ONLINE"]),
    ),
    (
        ("CHARM CRYO", ["Cryo ENABLE → √ go-cryo", "Magnet ARM → √ I≥0.95", "Mode → CRYO"]),
        ("CHARM ARM", ["Fuel ENABLE → √ ready", "Vacuum READY", "Mode → ARM"]),
    ),
    (
        ("CHARM LIGHT", ["RF ENABLE", "CHARM LIGHT", "√ plasma-proxy", "Mode → LIGHT"]),
        ("CHARM POWER", ["DEC ONLINE", "√ bus-mw", "Mode → POWER", "Detie cart"]),
    ),
    (
        ("CHARM SCRAM", ["Limit Shutdown → Enable", "mode SCRAM latched", "Inhibit RF/mag/fuel"]),
        ("CHARM SHUTDOWN", ["POWER→ARM→CRYO→OFF", "Bus undervolt: derate eng", "Water empty: σ3 only"]),
    ),
    (
        ("ENGINE GATE", ["Need CHARM POWER", "AND σ + throttle", "√ plant-ok / go-bus"]),
        ("ENGINE σ1", ["EDF / free air", "inlets OPEN", "σ=1 · low altitude"]),
    ),
    (
        ("ENGINE σ2", ["MW air plasma", "inlets OPEN", "precomp + MW farm", "climb / high-Q"]),
        ("ENGINE σ3", ["Water plasma", "inlet SEALED", "√ water-kg > 0", "vacuum Δv"]),
    ),
    (
        ("ENGINE MONITOR", ["bus-frac cable limit", "recommended vs cmd σ", "throttle response"]),
        ("ENGINE INHIBIT", ["SCRAM / not POWER", "σ3 no water", "σ2/1 if sealed wrong"]),
    ),
    (
        ("RCS GREEN", ["## LMP-103S (ADN)", "Bradford/ECAPS-class thrusters", "Shuttle locations/counts", "Municipal / KEDW OK"]),
        ("RCS LAYOUT", ["FWD module 14+2", "AFT L 12+2", "AFT R 12+2", "Attitude only — not σ3"]),
    ),
    (
        ("RCS MONITOR", ["√ tank P / manifold", "√ jet fail CWS", "DAP / RHC"]),
        ("RCS SECURE", ["Secure when ordered", "No MMH/N₂O₄ SCAPE", "No OMS engines"]),
    ),
    (
        ("ABORT ATTITUDE", ["RCS for abort pointing", "Does not replace σ3 Δv", "Keep DAP known"]),
        ("ENTRY NOTE", ["RCS trim available", "σ3 inhibit if needed", "Plant SCRAM if ordered"]),
    ),
    (
        ("LANDING KEDW", ["15,000 ft-class runway", "Gear / brakes / NWS", "Plan A m_land ~190 t"]),
        ("NO STACK", ["No ET / SRB", "No MPS He story", "Single combined nozzle"]),
    ),
    (
        ("CHECKLISTS", ["Help → Checklist:", "Grenadier — CHARM startup", "Grenadier — Engine stage"]),
        ("DOCS", ["Documentation/grenadier/", "reactor_startup.md", "panel_audit.md"]),
    ),
    (
        ("PROFILE ASCENT", ["σ1→σ2→σ3 gates", "Plant POWER continuous", "Scoops seal at σ3"]),
        ("PROFILE ORBIT", ["σ3 / RCS attitude", "Battery restart class", "Bay = plant bay"]),
    ),
    (
        ("PROFILE ENTRY", ["Glide energy primary", "RCS trim", "KEDW approach"]),
        ("PROFILE LAND", ["Gear down", "No chute / SRB", "TA recovery"]),
    ),
    (
        ("CHARM QUICK", ["OFF→CRYO→ARM→LIGHT→POWER", "Panel: APU + vac + OMS σ"]),
        ("ENGINE QUICK", ["σ1 open · σ2 open · σ3 sealed", "Throttle after POWER"]),
    ),
    (
        ("RCS QUICK", ["LMP-103S banks", "FWD + aft pods"]),
        ("SAFING QUICK", ["SCRAM Enable", "Shutdown reverse seq"]),
    ),
    (
        ("BUS / CABLE", ["DEC → plant bus", "Bus hole → coupler", "Engine cable limit"]),
        ("INLETS", ["variable_inlets L/R", "Plenum → EDF | σ2", "σ3 inlet-sealed"]),
    ),
    (
        ("WATER PATH", ["Bay tanks → injector", "~duct to σ3", "Not RCS feed"]),
        ("FUEL PATH", ["Proton + B11 → chambers", "CHARM only"]),
    ),
    (
        ("CREW CALL", ["CDR: CHARM / SCRAM", "PLT: σ / throttle / seal"]),
        ("END POWERED", ["26 spreads", "See glided binder for entry"]),
    ),
    (
        ("RESERVED", ["Powered p26"]),
        ("NOTES", ["Generated cue cards", "scripts/generate_grenadier_cuecards.py"]),
    ),
]

GLIDED: list[tuple[tuple[str, list[str]], tuple[str, list[str]]]] = [
    (
        ("GLIDED — INDEX", ["## Entry / land binder", "CHARM secure", "Engine inhibit", "RCS green", "KEDW landing"]),
        ("GLIDED ID", ["CATSKILLS-SSTO-TA-GRENADIER", "Unpowered approach energy", "RCS = LMP-103S"]),
    ),
    (
        ("CHARM ENTRY", ["Prefer POWER for loads", "or ARM/CRYO if cold", "√ no unintended SCRAM"]),
        ("SPACE RESTART", ["source = BATTERY", "≤ ~300–500 kWh", "Skip cart"]),
    ),
    (
        ("ENGINE INHIBIT", ["Throttle → 0", "σ hold / σ3 inhibit", "√ water / seal state"]),
        ("INLET / WATER", ["√ inlet-sealed as required", "No σ2 ingest on entry", "Water = σ3 only"]),
    ),
    (
        ("RCS ATTITUDE", ["FWD + aft L/R banks", "DAP / RHC trim", "Heritage ports"]),
        ("RCS MONITOR", ["√ TK P green mono", "√ jet availability"]),
    ),
    (
        ("RCS SECURE", ["Secure jets when ordered", "Keep DAP modes known"]),
        ("NO HYPERGOL", ["No MMH/N₂O₄ crossfeed", "Per-module LMP-103S"]),
    ),
    (
        ("PLANT LOADS", ["Bus undervolt → derate", "Cryo if magnets hot"]),
        ("LANDING KEDW", ["15,000 ft class", "Gear / brakes / NWS"]),
    ),
    (
        ("APPROACH", ["Energy management glide", "Body flap / elevons", "No MPS"]),
        ("GEAR", ["Gear down checklist", "Anti-skid / brakes"]),
    ),
    (
        ("σ3 / SCRAM", ["σ3 inhibit if no water", "SCRAM if hard trip"]),
        ("CHECKLISTS", ["Help → Grenadier lists", "Documentation/grenadier/"]),
    ),
]


def _pad(spreads: list, n: int, tag: str) -> list:
    out = list(spreads)
    while len(out) < n:
        i = len(out) + 1
        out.append(
            (
                (f"{tag} p{i}", [f"Reserved spread {i}"]),
                (f"{tag} p{i}R", ["See powered binder / checklists"]),
            )
        )
    return out[:n]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    powered = _pad(POWERED, 26, "POWERED")
    glided = _pad(GLIDED, 34, "GLIDED")
    for i, pair in enumerate(powered, 1):
        save_pair("powered_flight", i, pair[0], pair[1])
    for i, pair in enumerate(glided, 1):
        save_pair("glided_flight", i, pair[0], pair[1])
    print(f"wrote powered×{len(powered)} and glided×{len(glided)} L/R spreads")

    save_png(
        "charm_startup.png",
        "CHARM STARTUP",
        [
            "## OFF → CRYO → ARM → LIGHT → POWER",
            "0 √ inventories / battery / scram=0",
            "1 Cart ONLINE + tied; batt ONLINE",
            "2 Cryo ENABLE; Magnet ARM → CRYO",
            "3 Fuel ENABLE; Vac READY → ARM",
            "4 RF; LIGHT; DEC → POWER; detie",
        ],
    )
    save_png(
        "charm_scram.png",
        "CHARM SCRAM",
        [
            "Main Eng Limit Shutdown → Enable",
            "→ mode SCRAM (latched)",
            "RF / magnets / fuel inhibit",
            "",
            "Shutdown: POWER→ARM→CRYO→OFF",
        ],
        size=(423, 400),
    )
    save_png(
        "engine_sigma.png",
        "ENGINE σ1 / σ2 / σ3",
        [
            "Need CHARM POWER + throttle",
            "OMS L/R = σ − / σ +",
            "",
            "σ1 EDF — inlets open",
            "σ2 MW air — inlets open",
            "σ3 water — inlet SEALED + water",
        ],
        size=(455, 400),
    )
    save_png(
        "rcs_green.png",
        "RCS LMP-103S",
        [
            "## Green monoprop",
            "LMP-103S (ADN) + Bradford/ECAPS-class",
            "Shuttle nozzle locations & counts",
            "FWD + aft L/R pods",
            "Attitude / abort only — not σ3 Δv",
        ],
        size=(455, 400),
    )

    # Heritage menu filenames kept; content rewritten for Plan A.
    save_png(
        "ascent_nominal.png",
        "ASCENT — PLAN A",
        [
            "## KEDW · no cargo · grow wing/gear",
            "0 CHARM POWER + σ1 takeoff roll",
            "1 Rotate; climb σ1 EDF",
            "2 σ2 MW air when schedule calls",
            "3 Seal inlets → σ3 water plasma",
            "4 MECO / circularize on bus",
            "",
            "OMS engines deleted — σ is primary Δv",
        ],
        size=(455, 520),
    )
    save_png(
        "rtls_cdr.png",
        "ABORT — EARLY",
        [
            "## Before commit to σ3",
            "Throttle back / SCRAM if needed",
            "Turn toward KEDW or divert field",
            "σ1/σ2 for energy as available",
            "Configure for heavy glide landing",
            "",
            "No RTLS stack — single vehicle",
        ],
        size=(455, 480),
    )
    save_png(
        "rtls_plt.png",
        "ABORT — LATE",
        [
            "## After σ3 commit / low energy",
            "Protect CHARM / water inventory",
            "Attitude with RCS (LMP-103S)",
            "Aim ditch or emergency field",
            "Gear only if runway assured",
        ],
        size=(455, 480),
    )
    save_png(
        "contingency_abort.png",
        "CONTINGENCY",
        [
            "## Plant / engine trips",
            "SCRAM → RF/magnets/fuel inhibit",
            "Bus undervolt → derate σ",
            "Inlet fail → seal + σ3 if water OK",
            "Water loss → no σ3; glide/RCS only",
            "",
            "Crew: abort attitude with RCS",
        ],
        size=(455, 520),
    )
    save_png(
        "rtls_contingency.png",
        "CHARM SCRAM",
        [
            "Main Eng Limit Shutdown → Enable",
            "→ mode SCRAM (latched)",
            "RF / magnets / fuel inhibit",
            "",
            "Shutdown: POWER→ARM→CRYO→OFF",
        ],
        size=(423, 400),
    )
    save_png(
        "tal_redesignation_zza.png",
        "DIVERT / KEDW",
        [
            "## Home field KEDW 15,000 ft",
            "Energy management glide",
            "Body flap / elevons / speedbrake",
            "No MPS / no OMS Δv",
            "Gear / brakes / NWS on short final",
        ],
        size=(455, 420),
    )
    save_png(
        "entry_nominal.png",
        "ENTRY / GLIDE",
        [
            "## Unpowered Plan A return",
            "Attitude: RCS → aero as denser",
            "Cross-range with Shuttle OML",
            "Energy to KEDW corridor",
            "Gear down checklist",
            "No SSME / no OMS",
        ],
        size=(455, 520),
    )


if __name__ == "__main__":
    main()
