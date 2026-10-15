from __future__ import annotations

import hashlib
import math
import os
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageOps


class DetectorError(RuntimeError):
    pass


@dataclass(frozen=True)
class ModelSpec:
    repo_id: str = "Thermostatic/community-forensics-frontier-detector-2026-08"
    revision: str = "16db135220b318d811b207db576d90368980b595"
    filename: str = "community_forensics_frontier_fp16.onnx"
    sha256: str = "d75791ba2fa59146025d342cfaafa9ddeab24af117642a94f752ee4c1619375d"
    input_size: int = 384
    resize_short_edge: int = 440
    mean: tuple[float, float, float] = (0.485, 0.456, 0.406)
    std: tuple[float, float, float] = (0.229, 0.224, 0.225)
    calibration_intercept: float = -0.7403357915937764
    raw_logit_boundary: float = 1.359375
    probability_threshold: float = 0.65
    license: str = "MIT"


SPEC = ModelSpec()


@dataclass
class Prediction:
    is_ai: bool
    ai_probability: float
    real_probability: float
    raw_logit: float
    latency_ms: float
    threshold: float
    calibration_intercept: float
    model_sha256: str


def sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def calibrated_ai_probability(raw_logit: float, intercept: float = SPEC.calibration_intercept) -> float:
    return sigmoid(float(raw_logit) + float(intercept))


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_model_file(path: str | Path) -> Path:
    path = Path(path)
    if not path.exists():
        raise DetectorError(f"Model file not found: {path}")
    digest = sha256_file(path)
    if digest.lower() != SPEC.sha256.lower():
        raise DetectorError(
            "Model integrity check failed. "
            f"Expected SHA-256 {SPEC.sha256}, got {digest}."
        )
    return path


def download_model() -> Path:
    local_override = os.getenv("VERIFAI_MODEL_PATH")
    if local_override:
        return verify_model_file(local_override)

    try:
        from huggingface_hub import hf_hub_download
    except Exception as exc:
        raise DetectorError("huggingface_hub is not installed.") from exc

    try:
        path = hf_hub_download(
            repo_id=SPEC.repo_id,
            filename=SPEC.filename,
            revision=SPEC.revision,
        )
    except Exception as exc:
        raise DetectorError(
            "Could not download the pretrained detector from Hugging Face. "
            "Check the server internet connection and retry."
        ) from exc
    return verify_model_file(path)


def preprocess_image(image: Image.Image) -> np.ndarray:
    image = ImageOps.exif_transpose(image).convert("RGB")
    w, h = image.size
    short = min(w, h)
    if short <= 0:
        raise ValueError("Invalid image dimensions")

    scale = SPEC.resize_short_edge / short
    new_w = max(SPEC.input_size, int(round(w * scale)))
    new_h = max(SPEC.input_size, int(round(h * scale)))
    image = image.resize((new_w, new_h), Image.Resampling.BILINEAR)

    left = (new_w - SPEC.input_size) // 2
    top = (new_h - SPEC.input_size) // 2
    image = image.crop((left, top, left + SPEC.input_size, top + SPEC.input_size))

    arr = np.asarray(image, dtype=np.float32) / 255.0
    mean = np.asarray(SPEC.mean, dtype=np.float32)
    std = np.asarray(SPEC.std, dtype=np.float32)
    arr = (arr - mean) / std
    arr = np.transpose(arr, (2, 0, 1))[None, ...]
    return np.ascontiguousarray(arr, dtype=np.float32)


class Detector:
    def __init__(self, session: Any, model_sha256: str = SPEC.sha256):
        self.session = session
        self.model_sha256 = model_sha256
        self.input_name = session.get_inputs()[0].name
        self.output_name = session.get_outputs()[0].name

    def predict(self, image: Image.Image) -> Prediction:
        tensor = preprocess_image(image)
        started = time.perf_counter()
        output = self.session.run([self.output_name], {self.input_name: tensor})[0]
        latency_ms = (time.perf_counter() - started) * 1000.0
        raw_logit = float(np.asarray(output).reshape(-1)[0])
        p_ai = calibrated_ai_probability(raw_logit)
        p_ai = min(1.0, max(0.0, p_ai))
        return Prediction(
            is_ai=p_ai >= SPEC.probability_threshold,
            ai_probability=p_ai,
            real_probability=1.0 - p_ai,
            raw_logit=raw_logit,
            latency_ms=latency_ms,
            threshold=SPEC.probability_threshold,
            calibration_intercept=SPEC.calibration_intercept,
            model_sha256=self.model_sha256,
        )


def load_detector() -> Detector:
    path = download_model()
    try:
        import onnxruntime as ort
    except Exception as exc:
        raise DetectorError("onnxruntime is not installed.") from exc

    try:
        opts = ort.SessionOptions()
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        opts.intra_op_num_threads = max(1, min(2, os.cpu_count() or 1))
        session = ort.InferenceSession(
            str(path),
            sess_options=opts,
            providers=["CPUExecutionProvider"],
        )
    except Exception as exc:
        raise DetectorError(f"Could not initialize ONNX Runtime: {exc}") from exc
    return Detector(session, model_sha256=SPEC.sha256)


def get_model_info() -> dict[str, Any]:
    d = asdict(SPEC)
    d.update({
        "task": "whole-image AI-generated vs real screening",
        "labels": {"0": "real", "1": "ai_generated"},
        "model_card": f"https://huggingface.co/{SPEC.repo_id}",
        "note": "Pretrained upstream checkpoint; no training is run by this application.",
    })
    return d
