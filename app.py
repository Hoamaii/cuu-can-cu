import streamlit as st
import anthropic
import json
import random
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(page_title="Cừu Cần Cù 🐑", page_icon="🐑", layout="wide")

MASCOT_URL = "https://raw.githubusercontent.com/Hoamaii/cuu-can-cu/main/mascot.png"

# ─────────────────────────────────────────────
# PASTEL STYLING
# ─────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stApp"] {
    background: linear-gradient(135deg, #FFF0F5 0%, #F0F8FF 60%, #F5FFF8 100%);
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #FFF5F8 0%, #F0F8FF 100%) !important;
    border-right: 2px solid #FFD6E8 !important;
}
h1 { font-size: 1.6rem !important; font-weight: 700 !important; color: #C75B8A !important; }
h2 { font-size: 1.25rem !important; font-weight: 600 !important; color: #5B8AC7 !important; }
h3 { font-size: 1.05rem !important; font-weight: 600 !important; color: #555 !important; }
p, .stMarkdown p, label { font-size: 0.9rem !important; }
.stButton > button {
    border-radius: 20px !important;
    border: 1.5px solid #FFB7D5 !important;
    background: linear-gradient(135deg, #FFF0F5, #EEF5FF) !important;
    color: #555 !important;
    font-size: 0.85rem !important;
    padding: 0.4rem 0.8rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #FFD6E8, #D6E8FF) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px rgba(255,150,200,0.25) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #FF9EBB, #7EC8E3) !important;
    color: white !important;
    border: none !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
}
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #FFF5FA, #F5F8FF) !important;
    border-radius: 12px !important;
    border: 1px solid #FFD6E8 !important;
    padding: 6px !important;
}
[data-testid="metric-container"] [data-testid="metric-label"] { font-size: 0.75rem !important; }
[data-testid="metric-container"] [data-testid="metric-value"] { font-size: 1.1rem !important; }
.stProgress > div > div > div {
    background: linear-gradient(90deg, #FF9EBB, #7EC8E3) !important;
    border-radius: 10px !important;
}
.stAlert { border-radius: 12px !important; font-size: 0.85rem !important; }
[data-testid="stChatMessage"] { border-radius: 16px !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SYSTEM PROMPTS
# ─────────────────────────────────────────────
SYSTEM_PROMPT_ATTACHMENT = """Bạn là Cừu Cần Cù – người bạn đồng hành cảm xúc, KHÔNG phải chuyên gia tài chính.
Xưng hô: Mình (Cừu Cần Cù) – Bạn (người dùng). KHÔNG xưng "em" hay "Cừu Mai".

TUYỆT ĐỐI KHÔNG đề cập: chứng khoán cụ thể, lợi nhuận, NAV, khuyến nghị mua bán.
Nhiệm vụ: Lắng nghe như người bạn thân, ấm áp, không phán xét.

Phát hiện Life Event và gắn tag:
- học hành, thi cử → Education
- chia tay, buồn, cô đơn → Emotional
- mua xe, mua nhà, mua đồ → Consumption Goal
- hết tiền, thiếu tiền, nợ, khó khăn tài chính → Cashflow Problem
- nghỉ việc, chuyển việc, thất nghiệp, sự nghiệp → Career Change
