#!/usr/bin/env python3
"""Minimal local WebUI for ChatTTS using Gradio."""

from __future__ import annotations

import ChatTTS
import gradio as gr
import numpy as np
import torch


chat = ChatTTS.Chat()
if not chat.load(source="huggingface"):
    raise RuntimeError("ChatTTS model load failed")


def synthesize(
    text: str,
    seed: int,
    speed: float,
    temperature: float,
    top_p: float,
    top_k: int,
    refine_prompt: str,
) -> tuple[tuple[int, np.ndarray], str]:
    """Return audio and speaker token used for this synthesis."""
    if not text.strip():
        text = "Hello from ChatTTS."
    torch.manual_seed(int(seed))
    rand_spk = chat.sample_random_speaker()
    speed_level = max(1, min(9, int(round(speed))))
    params_infer_code = chat.InferCodeParams(
        spk_emb=rand_spk,
        temperature=float(temperature),
        top_P=float(top_p),
        top_K=int(top_k),
        prompt=f"[speed_{speed_level}]",
    )
    params_refine_text = chat.RefineTextParams(prompt=refine_prompt)
    wavs = chat.infer(
        [text],
        params_refine_text=params_refine_text,
        params_infer_code=params_infer_code,
    )
    wav = np.asarray(wavs[0], dtype=np.float32)
    return (24000, wav), rand_spk


def random_seed() -> int:
    """Generate a random 32-bit seed for voice sampling."""
    return int(torch.randint(0, 2**31 - 1, (1,)).item())


with gr.Blocks(title="ChatTTS WebUI") as demo:
    gr.Markdown("## ChatTTS WebUI")
    gr.Markdown("Type text, choose a voice seed, tune prosody, and click Generate.")
    text = gr.Textbox(
        label="Input text",
        lines=5,
        value=(
            "Okay... [uv_break] let's get through this list. [lbreak] "
            "First up... deuterium injector assembly. [lbreak] "
            "Next... [uv_break] cryogenic couplers and vacuum jacket seals."
        ),
    )
    with gr.Row():
        seed = gr.Number(label="Voice seed", value=3798, precision=0)
        random_btn = gr.Button("Random Seed")
    with gr.Row():
        speed = gr.Slider(minimum=1.0, maximum=9.0, value=3.0, step=0.5, label="Speed (mapped to [speed_n])")
        temperature = gr.Slider(minimum=0.05, maximum=1.2, value=0.35, step=0.01, label="Temperature")
    with gr.Row():
        top_p = gr.Slider(minimum=0.1, maximum=1.0, value=0.7, step=0.01, label="Top-P")
        top_k = gr.Slider(minimum=1, maximum=100, value=20, step=1, label="Top-K")
    refine_prompt = gr.Textbox(
        label="Refine prompt tags",
        lines=1,
        value="[oral_1][laugh_0][break_6]",
    )
    audio = gr.Audio(label="Output audio", type="numpy")
    spk_token = gr.Textbox(label="Speaker token used", lines=2)
    btn = gr.Button("Generate")
    random_btn.click(fn=random_seed, outputs=[seed])
    btn.click(
        fn=synthesize,
        inputs=[text, seed, speed, temperature, top_p, top_k, refine_prompt],
        outputs=[audio, spk_token],
    )


if __name__ == "__main__":
    demo.queue().launch(server_name="127.0.0.1", server_port=7860, share=False)
