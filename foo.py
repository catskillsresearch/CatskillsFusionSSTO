import ChatTTS
import scipy.io.wavfile

chat = ChatTTS.Chat()
# ChatTTS 0.2.x: use load(), not load_models(). Downloads from Hugging Face on first run.
if not chat.load(source="huggingface"):
    raise RuntimeError("ChatTTS model load failed")

texts = [
    "Hello there! [uv_break] I can speak with natural human pauses, laugh, and sound totally un-robotic."
]
wavs = chat.infer(texts)

scipy.io.wavfile.write("chat_output.wav", 24000, wavs[0])
print("Wrote chat_output.wav")
