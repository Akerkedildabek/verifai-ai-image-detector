# Model cache note

No model weight is committed here. The application downloads the pinned pretrained ONNX artifact on first inference and verifies its SHA-256. Set `VERIFAI_MODEL_PATH=/path/to/community_forensics_frontier_fp16.onnx` to use a pre-downloaded local copy.
