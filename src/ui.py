from __future__ import annotations
import streamlit as st
from src.i18n import t


def inject_css():
    st.markdown(r"""
    <style>
      .stApp { background: #f7faff; }
      [data-testid="stSidebar"] { background: linear-gradient(180deg,#eef6ff,#f8fbff); border-right:1px solid #dce7f6; }
      .brand { font-size:2.0rem; font-weight:900; letter-spacing:-0.04em; color:#0a1838; margin-top:.2rem; }
      .status-dot { display:inline-block; width:9px; height:9px; background:#22c55e; border-radius:50%; margin-right:7px; }
      .result-card { padding:22px 24px; border-radius:16px; border:1px solid; margin:4px 0 18px; }
      .result-ai { background:#fff1f2; border-color:#fecdd3; }
      .result-real { background:#effcf4; border-color:#bbf7d0; }
      .result-kicker { font-size:.88rem; color:#5f6f8d; font-weight:650; text-transform:uppercase; letter-spacing:.04em; }
      .result-value { font-size:2rem; line-height:1.05; font-weight:900; margin-top:6px; }
      .result-ai .result-value { color:#d51e2b; }
      .result-real .result-value { color:#16803c; }
      .prob-row { margin:10px 0 14px; }
      .prob-label { display:flex; justify-content:space-between; font-weight:700; margin-bottom:6px; }
      .bar-bg { width:100%; height:11px; background:#e7edf5; border-radius:999px; overflow:hidden; }
      .bar-ai { height:100%; background:linear-gradient(90deg,#ff6b6b,#dc2626); border-radius:999px; }
      .bar-real { height:100%; background:linear-gradient(90deg,#4ba3ff,#1565d8); border-radius:999px; }
      .block-container { padding-top:2.1rem; max-width:1320px; }
      h1 { color:#08152f; letter-spacing:-.03em; }
      div[data-testid="stFileUploader"] { background:white; padding:10px 14px; border-radius:16px; border:1px solid #dfe8f5; }
    </style>
    """, unsafe_allow_html=True)


def result_card(is_ai: bool, p_ai: float, lang: str):
    verdict = "AI-GENERATED" if is_ai else "REAL"
    clazz = "result-ai" if is_ai else "result-real"
    subtitle = {
        "Қазақша": "Модель бойынша бұл сурет жасанды интеллект арқылы жасалған болуы ықтимал." if is_ai else "Модель бойынша бұл сурет шынайы болуы ықтимал.",
        "Русский": "По оценке модели изображение, вероятно, сгенерировано ИИ." if is_ai else "По оценке модели изображение, вероятно, реальное.",
        "English": "The model flags this image as likely AI-generated." if is_ai else "The model flags this image as likely real.",
    }.get(lang, "")
    st.markdown(f"""
    <div class="result-card {clazz}">
      <div class="result-kicker">{t(lang, 'result_heading')}</div>
      <div class="result-value">{verdict}</div>
      <div style="margin-top:8px;color:#52617b">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def probability_bar(label: str, value: float, danger: bool):
    pct = max(0.0, min(1.0, value)) * 100
    cls = "bar-ai" if danger else "bar-real"
    st.markdown(f"""
    <div class="prob-row">
      <div class="prob-label"><span>{label}</span><span>{pct:.1f}%</span></div>
      <div class="bar-bg"><div class="{cls}" style="width:{pct:.2f}%"></div></div>
    </div>
    """, unsafe_allow_html=True)
