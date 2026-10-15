from __future__ import annotations

import io
import json
from datetime import datetime, timezone

import pandas as pd
import streamlit as st
from PIL import Image, ImageOps

from src.detector import DetectorError, get_model_info, load_detector
from src.i18n import LANGUAGES, t
from src.metadata import extract_metadata_signals
from src.ui import inject_css, probability_bar, result_card

st.set_page_config(
    page_title="VERIFAI — AI Image Authenticity Analyzer",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

if "lang" not in st.session_state:
    st.session_state.lang = "Қазақша"
if "page" not in st.session_state:
    st.session_state.page = "analyze"


@st.cache_resource(show_spinner=False)
def detector_resource():
    return load_detector()


def safe_open_image(raw: bytes) -> Image.Image:
    try:
        image = Image.open(io.BytesIO(raw))
        image.load()
        image = ImageOps.exif_transpose(image).convert("RGB")
        return image
    except Exception as exc:
        raise ValueError(f"Unsupported or damaged image: {exc}") from exc


def analyze_bytes(raw: bytes, name: str):
    image = safe_open_image(raw)
    detector = detector_resource()
    pred = detector.predict(image)
    signals = extract_metadata_signals(raw, image)
    return image, pred, signals


def sidebar():
    with st.sidebar:
        st.markdown("<div class='brand'>VERIFAI</div>", unsafe_allow_html=True)
        st.caption("AI Image Authenticity Analyzer")
        st.markdown("---")

        lang = st.selectbox("Тіл / Язык / Language", LANGUAGES, index=LANGUAGES.index(st.session_state.lang))
        st.session_state.lang = lang

        labels = {
            "analyze": t(lang, "nav_analyze"),
            "batch": t(lang, "nav_batch"),
            "model": t(lang, "nav_model"),
            "deploy": t(lang, "nav_deploy"),
        }
        choice = st.radio("", options=list(labels), format_func=lambda x: labels[x], label_visibility="collapsed")
        st.session_state.page = choice

        st.markdown("---")
        st.markdown("**Model**")
        st.caption("Community Forensics Frontier Detector · ONNX")
        st.markdown("<span class='status-dot'></span> pretrained / no training required", unsafe_allow_html=True)
        st.caption("The model is downloaded once and cached on the server.")


def page_analyze(lang: str):
    st.title(t(lang, "title"))
    st.write(t(lang, "subtitle"))

    uploaded = st.file_uploader(
        t(lang, "upload"),
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=False,
        help=t(lang, "upload_help"),
    )

    if not uploaded:
        st.info(t(lang, "upload_hint"))
        return

    raw = uploaded.getvalue()
    if len(raw) > 20 * 1024 * 1024:
        st.error(t(lang, "too_large"))
        return

    try:
        preview = safe_open_image(raw)
    except ValueError as exc:
        st.error(str(exc))
        return

    left, right = st.columns([0.92, 1.18], gap="large")
    with left:
        st.image(preview, caption=uploaded.name, use_container_width=True)
        st.caption(f"{preview.width} × {preview.height} px · {len(raw)/1024:.1f} KB")

    with right:
        st.markdown("### " + t(lang, "result_heading"))
        run = st.button(t(lang, "analyze_button"), type="primary", use_container_width=True)
        if not run:
            st.caption(t(lang, "press_analyze"))
            return

        with st.spinner(t(lang, "model_loading")):
            try:
                image, pred, signals = analyze_bytes(raw, uploaded.name)
            except DetectorError as exc:
                st.error(t(lang, "model_error") + f"\n\n{exc}")
                return
            except Exception as exc:
                st.error(f"{t(lang, 'analysis_error')}: {exc}")
                return

        result_card(pred.is_ai, pred.ai_probability, lang)
        probability_bar(t(lang, "ai_probability"), pred.ai_probability, danger=True)
        probability_bar(t(lang, "real_probability"), pred.real_probability, danger=False)

        c1, c2 = st.columns(2)
        c1.metric(t(lang, "inference_time"), f"{pred.latency_ms:.0f} ms")
        c2.metric(t(lang, "decision_threshold"), "65% AI")

        st.warning(t(lang, "probability_warning"), icon="⚠️")

    st.markdown("---")
    st.subheader(t(lang, "evidence_heading"))
    e1, e2 = st.columns([1.1, 0.9], gap="large")
    with e1:
        if signals:
            st.success(t(lang, "metadata_found"))
            for s in signals:
                st.code(s, language=None)
        else:
            st.info(t(lang, "metadata_none"))
    with e2:
        st.markdown(t(lang, "what_model_checks"))
        st.caption(t(lang, "whole_image_note"))

    report = {
        "file": uploaded.name,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "verdict": "AI-GENERATED" if pred.is_ai else "REAL",
        "ai_probability": round(pred.ai_probability, 6),
        "real_probability": round(pred.real_probability, 6),
        "raw_logit": round(pred.raw_logit, 6),
        "threshold": pred.threshold,
        "latency_ms": round(pred.latency_ms, 2),
        "metadata_signals": signals,
        "model": get_model_info(),
        "warning": "Screening signal only; not proof of provenance or authorship.",
    }
    st.download_button(
        t(lang, "download_report"),
        json.dumps(report, ensure_ascii=False, indent=2),
        file_name="verifai_report.json",
        mime="application/json",
    )

    with st.expander(t(lang, "technical_details")):
        st.json({
            "raw_logit": pred.raw_logit,
            "calibration_intercept": pred.calibration_intercept,
            "ai_probability": pred.ai_probability,
            "official_threshold": pred.threshold,
            "model_sha256": pred.model_sha256,
        })


def page_batch(lang: str):
    st.title(t(lang, "batch_title"))
    st.write(t(lang, "batch_subtitle"))
    files = st.file_uploader(
        t(lang, "batch_upload"),
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True,
    )
    if not files:
        return
    if len(files) > 12:
        st.warning(t(lang, "batch_limit"))
        files = files[:12]

    if not st.button(t(lang, "analyze_all"), type="primary"):
        return

    try:
        detector = detector_resource()
    except DetectorError as exc:
        st.error(t(lang, "model_error") + f"\n\n{exc}")
        return

    rows = []
    progress = st.progress(0)
    for idx, f in enumerate(files, start=1):
        try:
            raw = f.getvalue()
            image = safe_open_image(raw)
            pred = detector.predict(image)
            rows.append({
                "file": f.name,
                "verdict": "AI-GENERATED" if pred.is_ai else "REAL",
                "AI_probability": round(pred.ai_probability, 4),
                "REAL_probability": round(pred.real_probability, 4),
                "latency_ms": round(pred.latency_ms, 1),
                "metadata_signals": "; ".join(extract_metadata_signals(raw, image)),
            })
        except Exception as exc:
            rows.append({"file": f.name, "verdict": "ERROR", "AI_probability": None, "REAL_probability": None, "latency_ms": None, "metadata_signals": str(exc)})
        progress.progress(idx / len(files))

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button(
        t(lang, "download_csv"),
        df.to_csv(index=False).encode("utf-8-sig"),
        file_name="verifai_batch_results.csv",
        mime="text/csv",
    )


def page_model(lang: str):
    info = get_model_info()
    st.title(t(lang, "model_title"))
    st.write(t(lang, "model_intro"))

    c1, c2, c3 = st.columns(3)
    c1.metric("Backbone", "ViT-S/16")
    c2.metric("Input", "384 × 384")
    c3.metric("Decision", "P(AI) ≥ 0.65")

    st.markdown("#### " + t(lang, "published_validation"))
    st.caption(t(lang, "published_not_ours"))
    vals = pd.DataFrame([
        {"Condition": "Clean", "Balanced accuracy": 0.9568, "AI recall": 0.9585, "Real specificity": 0.9551, "ROC AUC": 0.9890},
        {"Condition": "Web", "Balanced accuracy": 0.9385, "AI recall": 0.9114, "Real specificity": 0.9657, "ROC AUC": 0.9813},
        {"Condition": "Hard", "Balanced accuracy": 0.9047, "AI recall": 0.8538, "Real specificity": 0.9556, "ROC AUC": 0.9650},
    ])
    st.dataframe(vals, use_container_width=True, hide_index=True)

    st.markdown("#### " + t(lang, "training_data"))
    st.write(t(lang, "training_data_text"))

    st.markdown("#### " + t(lang, "limits"))
    st.markdown(t(lang, "limits_text"))

    with st.expander(t(lang, "model_contract")):
        st.json(info)


def page_deploy(lang: str):
    st.title(t(lang, "deploy_title"))
    st.write(t(lang, "deploy_intro"))
    st.markdown(t(lang, "deploy_steps"))
    st.code("streamlit run app.py", language="bash")
    st.info(t(lang, "first_start"))


sidebar()
lang = st.session_state.lang
if st.session_state.page == "analyze":
    page_analyze(lang)
elif st.session_state.page == "batch":
    page_batch(lang)
elif st.session_state.page == "model":
    page_model(lang)
else:
    page_deploy(lang)
