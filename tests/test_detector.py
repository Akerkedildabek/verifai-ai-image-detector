import math
import numpy as np
from PIL import Image
from src.detector import SPEC, calibrated_ai_probability, preprocess_image


def test_preprocess_shape_dtype_and_finite():
    img = Image.new("RGB", (800, 500), (128, 100, 90))
    x = preprocess_image(img)
    assert x.shape == (1, 3, 384, 384)
    assert x.dtype == np.float32
    assert np.isfinite(x).all()


def test_calibration_boundary_matches_published_threshold():
    p = calibrated_ai_probability(SPEC.raw_logit_boundary)
    assert math.isclose(p, SPEC.probability_threshold, abs_tol=1e-6)
