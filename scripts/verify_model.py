from __future__ import annotations
import math
import sys
import numpy as np
from PIL import Image

from src.detector import SPEC, download_model, load_detector


def main() -> int:
    print("Downloading/verifying pretrained model...")
    path = download_model()
    print("MODEL_OK", path)
    detector = load_detector()
    # Engineering smoke test only: checks graph execution and finite output.
    img = Image.fromarray(np.full((512, 640, 3), 127, dtype=np.uint8), "RGB")
    pred = detector.predict(img)
    if not (math.isfinite(pred.raw_logit) and 0 <= pred.ai_probability <= 1):
        raise SystemExit("Invalid model output")
    print("INFERENCE_OK", {"raw_logit": pred.raw_logit, "p_ai": pred.ai_probability, "threshold": SPEC.probability_threshold})
    return 0

if __name__ == "__main__":
    sys.exit(main())
