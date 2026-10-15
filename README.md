# VERIFAI — AI Image Authenticity Analyzer

GitHub + Streamlit Community Cloud үшін дайын web application. Суретті **REAL** немесе **AI-GENERATED** ретінде probabilistic screening арқылы бағалайды.

## Ready model

The app uses the pretrained **Thermostatic/community-forensics-frontier-detector-2026-08** checkpoint (MIT license), distributed as a compact ONNX model. No training is run by this repository.

Pinned model contract:

- Architecture: Community Forensics ViT-S/16, 384×384
- Labels: `0=real`, `1=ai_generated`
- Resize: short edge → 440, center crop → 384×384
- Normalization: ImageNet mean/std
- Calibrated AI threshold: `0.65`
- ONNX SHA-256: `d75791ba2fa59146025d342cfaafa9ddeab24af117642a94f752ee4c1619375d`
- Pinned HF revision: `16db135220b318d811b207db576d90368980b595`

At first inference, the app downloads the 43.8 MB ONNX artifact with `huggingface_hub`, verifies its SHA-256, and caches it. This keeps the GitHub repository small and avoids Git LFS while still using a fixed, pretrained model.

## Features

- Single-image REAL / AI-GENERATED analysis
- Calibrated AI probability and complementary REAL score
- Batch analysis for up to 12 images + CSV export
- Separate metadata marker scan for Stable Diffusion, ComfyUI, Midjourney, DALL-E, FLUX, Firefly, etc.
- JSON report export
- Kazakh / Russian / English interface
- Model integrity verification before inference
- GitHub Actions CI with real model download + ONNX smoke-test
- Streamlit Community Cloud configuration included

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Or on Windows, run `run_windows.bat`.

## Deploy

See [`DEPLOYMENT_KZ.md`](DEPLOYMENT_KZ.md).

## Model evidence and limitations

The upstream model card reports development/calibration balanced accuracy of 0.9568 on clean, 0.9385 on web-laundered, and 0.9047 on hard views. The authors explicitly state that these are development results, not an untouched competition-test estimate. They also report weakness on severe low resolution, tiny/diluted synthetic regions, and hard laundering. The upstream red-team report marks its overall robustness gate as not fully valid because several declared stress-test gates failed.

VERIFAI therefore displays the detector as a **screening signal, not proof**. It must not be the sole basis for accusations, disciplinary action, admissions/employment decisions, or legal conclusions.

## Student work

You can upload a screenshot/photo of a student poster, infographic, illustration, or other image-based submission. The detector estimates whether the **image itself** looks AI-generated. It does **not** determine whether the student wrote a text themselves, detect plagiarism, or prove academic misconduct.

## Sources / attribution

- Model: https://huggingface.co/Thermostatic/community-forensics-frontier-detector-2026-08
- Base work: Park & Owens, *Community Forensics: Using Thousands of Generators to Train Fake Image Detectors*, CVPR 2025.
- Streamlit: https://streamlit.io/

See `THIRD_PARTY_NOTICES.md`.
