from io import BytesIO
from PIL import Image, PngImagePlugin
from src.metadata import extract_metadata_signals


def test_generator_metadata_is_detected():
    img = Image.new("RGB", (32, 32), "white")
    meta = PngImagePlugin.PngInfo()
    meta.add_text("parameters", "Stable Diffusion XL; steps=30")
    buf = BytesIO()
    img.save(buf, format="PNG", pnginfo=meta)
    raw = buf.getvalue()
    opened = Image.open(BytesIO(raw))
    found = extract_metadata_signals(raw, opened)
    assert any("Stable Diffusion" in x for x in found)
