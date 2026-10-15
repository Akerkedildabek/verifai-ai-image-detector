from __future__ import annotations

import re
from PIL import Image

_PATTERNS = [
    (re.compile(r"stable[ _-]?diffusion", re.I), "Stable Diffusion marker"),
    (re.compile(r"comfyui", re.I), "ComfyUI marker"),
    (re.compile(r"automatic1111", re.I), "AUTOMATIC1111 marker"),
    (re.compile(r"midjourney", re.I), "Midjourney marker"),
    (re.compile(r"dall[·\- ]?e", re.I), "DALL-E marker"),
    (re.compile(r"gpt[-_ ]?image", re.I), "GPT Image marker"),
    (re.compile(r"adobe[ _-]?firefly", re.I), "Adobe Firefly marker"),
    (re.compile(r"\bflux(?:[ ._-]?[12])?\b", re.I), "FLUX marker"),
    (re.compile(r"novelai", re.I), "NovelAI marker"),
    (re.compile(r"invokeai", re.I), "InvokeAI marker"),
    (re.compile(r"fooocus", re.I), "Fooocus marker"),
    (re.compile(r"trainedalgorithmicmedia", re.I), "C2PA trainedAlgorithmicMedia marker (unverified)"),
]


def _flatten_metadata(image: Image.Image) -> str:
    parts: list[str] = []
    try:
        for k, v in image.info.items():
            parts.append(f"{k}={v}")
    except Exception:
        pass
    try:
        exif = image.getexif()
        for k, v in exif.items():
            parts.append(f"{k}={v}")
    except Exception:
        pass
    return "\n".join(parts)


def extract_metadata_signals(raw: bytes, image: Image.Image) -> list[str]:
    # Metadata is supporting evidence only. It is not fused into the model score.
    text = _flatten_metadata(image)
    # Byte scan catches PNG text/XMP markers that Pillow may not expose.
    sample = raw[:8_000_000].decode("latin-1", errors="ignore")
    haystack = text + "\n" + sample
    found: list[str] = []
    for pattern, label in _PATTERNS:
        if pattern.search(haystack):
            found.append(label)
    return found
