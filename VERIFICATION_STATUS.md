# Verification status

## Completed in this build environment

- Python syntax/compile check: PASS
- Project structure check: PASS
- Unit tests: 3/3 PASS
- Preprocessing output: `[1, 3, 384, 384]` float32, finite: PASS
- Calibration equation: published raw boundary `1.359375` maps to calibrated `P(AI)=0.65`: PASS
- Mock ONNX-session inference path: PASS
- Metadata marker test: PASS

## Real pretrained model verification

The repository includes a GitHub Actions CI step that downloads the pinned 43.8 MB ONNX model, verifies SHA-256, creates an ONNX Runtime session and executes a smoke inference. The current ChatGPT container has outbound package/model downloads blocked by DNS, so that network-dependent step could not be executed locally here. The application never substitutes a fake score if model download or verification fails.

Pinned model SHA-256: `d75791ba2fa59146025d342cfaafa9ddeab24af117642a94f752ee4c1619375d`.
