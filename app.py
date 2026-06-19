import base64
import os
from datetime import datetime

import streamlit as st
from groq import Groq

# ======================
# GROQ (logic giữ nguyên 100%)
# ======================
client = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)

# ======================
# PAGE
# ======================
st.set_page_config(
    page_title="🐑 Cừu Cần Cù",
    page_icon="🐑",
    layout="wide"
)

# ======================
# HELPERS — mascot image as base64 (fallback to emoji if file missing)
# ======================
def get_image_base64(path: str):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

MASCOT_PATH = "IMG_7823.jpeg"
mascot_b64 = get_image_base64(MASCOT_PATH)

if mascot_b64:
    mascot_sidebar_html = f'<img src="data:image/jpeg;base64,{mascot_b64}" class="mascot-img-sidebar" />'
    mascot_avatar_html = f'<img src="data:image/jpeg;base64,{mascot_b64}" class="mascot-img-avatar" />'
else:
    mascot_sidebar_html = '<div class="mascot-emoji-sidebar">🐑</div>'
    mascot_avatar_html = '<div class="mascot-emoji-avatar">🐑</div>'

# ======================
# CUSTOM CSS — fintech style (bám sát ảnh mẫu)
# ======================
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        .stApp {
            background-color: #FFF8F5;
        }

        #MainMenu, header, footer {visibility: hidden;}

        .block-container {
            padding-top: 1.6rem;
            padding-bottom: 2rem;
            padding-left: 2.2rem;
            padding-right: 2.2rem;
            max-width: 1500px;
        }

        /* ===== Sidebar ===== */
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF;
            border-radius: 0 24px 24px 0;
            box-shadow: 4px 0 24px rgba(255, 154, 158, 0.10);
        }
        section[data-testid="stSidebar"] > div {
            padding: 1.6rem 1.3rem;
        }
        section[data-testid="stSidebar"] .stButton,
        section[data-testid="stSidebar"] .stImage,
        section[data-testid="stSidebar"] .stAlert {
            display: none;
        }

        /* ===== Sidebar mascot ===== */
        .sidebar-mascot-wrap {
            display: flex;
            justify-content: center;
            margin-bottom: 0.6rem;
            position: relative;
        }
        .mascot-img-sidebar {
            width: 180px;
            height: 180px;
            object-fit: cover;
            border-radius: 24px;
        }
        .mascot-emoji-sidebar {
            width: 180px;
            height: 180px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 96px;
            border-radius: 24px;
            background: linear-gradient(145deg, #FFE9E2, #FFDCCF);
        }

        .sidebar-title {
            text-align: center;
            font-size: 1.55rem;
            font-weight: 800;
            color: #2B2320;
            margin: 0.4rem 0 0.15rem 0;
        }
        .sidebar-caption {
            text-align: center;
            font-size: 0.88rem;
            color: #A8948C;
            margin-bottom: 1.3rem;
        }

        /* ===== Custom menu (no st.button) ===== */
        .menu-item {
            display: flex;
            align-items: center;
            gap: 0.7rem;
            padding: 0.7rem 0.9rem;
            margin-bottom: 0.35rem;
            border-radius: 14px;
            color: #5C4A43;
            font-weight: 600;
            font-size: 0.92rem;
            text-decoration: none !important;
            transition: all 0.18s ease;
        }
        .menu-item:hover {
            background: #FFF4EF;
        }
        .menu-item.active {
            background: #FFE3E0;
            color: #E8584C;
        }
        .menu-icon {
            font-size: 1.05rem;
            width: 22px;
            text-align: center;
        }

        .sidebar-divider {
            height: 1px;
            background: #F4E3DB;
            margin: 1rem 0;
            border: none;
        }

        /* ===== Sidebar tip card (bottom) ===== */
        .sidebar-tip-card {
            background: #EAF8EE;
            border-radius: 18px;
            padding: 1rem 1.1rem;
            margin-top: 0.5rem;
        }
        .sidebar-tip-title {
            display: flex;
            align-items: center;
            gap: 0.4rem;
            font-weight: 700;
            font-size: 0.9rem;
            color: #2E7D4F;
            margin-bottom: 0.35rem;
        }
        .sidebar-tip-text {
            font-size: 0.82rem;
            color: #4C7E5F;
            line-height: 1.5;
        }

        /* ===== Main panel wrapper ===== */
        .main-panel {
            background: #FFFFFF;
            border-radius: 24px;
            box-shadow: 0 8px 28px rgba(255, 154, 158, 0.10);
            padding: 1.8rem 2.2rem 1.4rem 2.2rem;
        }

        /* ===== Header row: hello + tip ===== */
        .header-row {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 1.5rem;
            padding-bottom: 1.3rem;
            border-bottom: 1px solid #F2E8E3;
            margin-bottom: 0;
        }
        .hello-block h1 {
            font-size: 1.9rem;
            font-weight: 800;
            color: #2B2320;
            margin: 0 0 0.5rem 0;
        }
        .hello-block p {
            font-size: 0.98rem;
            color: #5C4A43;
            margin: 0 0 0.2rem 0;
            line-height: 1.5;
        }
        .hello-highlight {
            color: #F0594A;
            font-weight: 600;
        }
        .tip-box {
            background: #FFF7E0;
            border-radius: 18px;
            padding: 1rem 1.2rem;
            min-width: 280px;
            max-width: 320px;
            flex-shrink: 0;
        }
        .tip-box-title {
            display: flex;
            align-items: center;
            gap: 0.4rem;
            font-weight: 700;
            font-size: 0.92rem;
            color: #3E312C;
            margin-bottom: 0.3rem;
        }
        .tip-box-text {
            font-size: 0.84rem;
            color: #8C7A5F;
            line-height: 1.5;
        }

        /* ===== Chat area ===== */
        .chat-scroll {
            padding-top: 1.4rem;
            padding-bottom: 0.5rem;
            min-height: 320px;
        }

        .msg-time {
            font-size: 0.74rem;
            color: #B8A89F;
            margin: 0.25rem 0.4rem;
            align-self: center;
        }

        .avatar-circle-user {
            width: 38px;
            height: 38px;
            border-radius: 50%;
            background: #FFE3E2;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.15rem;
            color: #F0594A;
            flex-shrink: 0;
            margin-left: 0.5rem;
        }
        .avatar-circle-ai {
            width: 42px;
            height: 42px;
            border-radius: 50%;
            overflow: hidden;
            flex-shrink: 0;
            margin-right: 0.5rem;
            border: 2px solid #FFE9E2;
        }
        .mascot-img-avatar {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        .mascot-emoji-avatar {
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.3rem;
            background: #FFE9E2;
        }

        .msg-row {
            display: flex;
            align-items: flex-end;
            margin-bottom: 0.7rem;
        }
        .msg-row.user-row {
            justify-content: flex-end;
        }
        .msg-row.ai-row {
            justify-content: flex-start;
        }
        .bubble-user {
            max-width: 65%;
            background: #FFE3E2;
            color: #3E312C;
            border-radius: 18px 18px 4px 18px;
            padding: 0.9rem 1.3rem;
            line-height: 1.55;
            font-size: 0.96rem;
        }
        .bubble-ai {
            max-width: 70%;
            background: #FFF7E0;
            color: #3E312C;
            border-radius: 18px 18px 18px 4px;
            padding: 1rem 1.3rem;
            line-height: 1.65;
            font-size: 0.96rem;
        }

        /* ===== Suggestion chips row ===== */
        div[data-testid="column"] .stButton button {
            background: #FFFFFF !important;
            color: #5C4A43 !important;
            border: 1.5px solid #F2E0D8 !important;
            border-radius: 999px !important;
            padding: 0.55rem 1.1rem !important;
            font-size: 0.86rem !important;
            font-weight: 600 !important;
            box-shadow: none !important;
            transition: all 0.15s ease !important;
            width: 100%;
        }
        div[data-testid="column"] .stButton button:hover {
            border-color: #FF9D87 !important;
            color: #E8584C !important;
            background: #FFF6F3 !important;
        }
        .refresh-btn button {
            border-radius: 50% !important;
            width: 42px !important;
            height: 42px !important;
            padding: 0 !important;
            font-size: 1.1rem !important;
        }
        .chip-divider {
            border-top: 1px solid #F2E8E3;
            margin: 0.8rem 0 1rem 0;
        }

        /* ===== Chat input ===== */
        div[data-testid="stChatInput"] {
            background: #FFFFFF;
            border-radius: 18px;
            border: 1.5px solid #F2E0D8;
            padding: 0.3rem 0.6rem;
            margin-top: 0.4rem;
        }
        div[data-testid="stChatInput"] textarea {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 0.95rem;
        }

        .disclaimer-row {
            display: flex;
            align-items: center;
            gap: 0.4rem;
            font-size: 0.78rem;
            color: #B8A89F;
            margin-top: 0.8rem;
            padding-left: 0.3rem;
        }

        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-thumb { background: #FFD3C4; border-radius: 8px; }
    </style>
    """,
    unsafe_allow_html=True
)

# ======================
# SIDEBAR
# ======================
with st.sidebar:
    st.markdown(f'<div class="sidebar-mascot-wrap">{mascot_sidebar_html}</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">Cừu Cần Cù</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-caption">Người bạn đồng hành tài chính ❤️</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <a class="menu-item active" href="#">
            <span class="menu-icon">💬</span> Chat cùng Cừu
        </a>
        <a class="menu-item" href="#">
            <span class="menu-icon">🔍</span> Tìm sản phẩm
        </a>
        <a class="menu-item" href="#">
            <span class="menu-icon">📖</span> Kho kiến thức
        </a>
        <a class="menu-item" href="#">
            <span class="menu-icon">🎯</span> Kế hoạch tiết kiệm
        </a>
        <a class="menu-item" href="#">
            <span class="menu-icon">🤍</span> Nhật ký cảm xúc
        </a>
        <a class="menu-item" href="#">
            <span class="menu-icon">🕘</span> Lịch sử hội thoại
        </a>
        <a class="menu-item" href="#">
            <span class="menu-icon">⚙️</span> Cài đặt
        </a>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="sidebar-tip-card">
            <div class="sidebar-tip-title">🌱 Tích tiểu thành đại</div>
            <div class="sidebar-tip-text">
                Bắt đầu từ những khoản nhỏ mỗi ngày, Cừu sẽ giúp bạn đầu tư thông minh để đạt được mục tiêu lớn! 🌱
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ======================
# MEMORY (logic giữ nguyên)
# ======================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "suggestion_set_idx" not in st.session_state:
    st.session_state.suggestion_set_idx = 0

# Bộ câu gợi ý xoay vòng (chỉ là UI, không đổi logic chatbot)
SUGGESTION_SETS = [
    [
        "So sánh iPower và iFund",
        "Đầu tư với 200k/tháng",
        "Mục tiêu dài hạn",
        "Tôi là người mới bắt đầu",
    ],
    [
        "Tích lũy cho con đi học",
        "Quỹ dự phòng khẩn cấp là gì?",
        "Nên để tiền tiết kiệm hay đầu tư?",
        "Rủi ro khi đầu tư là gì?",
    ],
    [
        "Lãi suất kép hoạt động thế nào?",
        "Tiết kiệm 50k/ngày được bao nhiêu?",
        "Kế hoạch nghỉ hưu sớm",
        "Cừu ơi, bắt đầu từ đâu?",
    ],
]

def call_groq(user_prompt: str):
    """Logic Groq giữ nguyên 100% — chỉ tách thành hàm để tái sử dụng cho chip gợi ý."""
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_prompt
        }
    )

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": """
Bạn là Cừu Cần Cù.
Vai trò:
- Người bạn đồng hành tài chính.
- Luôn lắng nghe trước.
- Trả lời thân thiện, dễ hiểu.
- Không ép khách hàng đầu tư.
- Có thể gợi ý tích lũy từ số tiền nhỏ.
"""
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )
    answer = response.choices[0].message.content

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

# ======================
# MAIN PANEL
# ======================
st.markdown('<div class="main-panel">', unsafe_allow_html=True)

st.markdown(
    """
    <div class="header-row">
        <div class="hello-block">
            <h1>👋 Xin chào!</h1>
            <p>Mình là <b>Cừu Cần Cù</b>, người bạn đồng hành tài chính của bạn.</p>
            <p class="hello-highlight">Cùng Cừu bắt đầu hành trình tích tiểu thành đại nhé!</p>
        </div>
        <div class="tip-box">
            <div class="tip-box-title">💡 Tip của Cừu</div>
            <div class="tip-box-text">
                Đầu tư thông minh từ số tiền nhỏ hôm nay, tương lai sẽ lớn hơn bạn nghĩ! ✨
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ======================
# CHAT HISTORY (custom bubble rendering, dữ liệu vẫn từ session_state gốc)
# ======================
st.markdown('<div class="chat-scroll">', unsafe_allow_html=True)

now_str = datetime.now().strftime("%H:%M")

for msg in st.session_state.messages:
    safe_content = msg["content"]
    if msg["role"] == "user":
        st.markdown(
            f"""
            <div class="msg-row user-row">
                <div class="bubble-user">{safe_content}</div>
                <span class="msg-time">{now_str}</span>
                <div class="avatar-circle-user">👤</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div class="msg-row ai-row">
                <div class="avatar-circle-ai">{mascot_avatar_html}</div>
                <div class="bubble-ai">
                    {safe_content}
                    <div class="msg-time" style="margin-left:0;">{now_str}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="chip-divider"></div>', unsafe_allow_html=True)

# ======================
# SUGGESTION CHIPS (gửi prompt thật + nút refresh đổi bộ gợi ý)
# ======================
current_suggestions = SUGGESTION_SETS[st.session_state.suggestion_set_idx % len(SUGGESTION_SETS)]

chip_cols = st.columns([1, 1, 1, 1, 0.4])
clicked_suggestion = None

for i, suggestion in enumerate(current_suggestions):
    with chip_cols[i]:
        if st.button(suggestion, key=f"chip_{st.session_state.suggestion_set_idx}_{i}"):
            clicked_suggestion = suggestion

with chip_cols[4]:
    st.markdown('<div class="refresh-btn">', unsafe_allow_html=True)
    if st.button("🔄", key="refresh_suggestions"):
        st.session_state.suggestion_set_idx += 1
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ======================
# CHAT INPUT (logic giữ nguyên 100%)
# ======================
prompt = st.chat_input("Nhắn tin cho Cừu...")

final_prompt = clicked_suggestion or prompt

if final_prompt:
    call_groq(final_prompt)
    st.rerun()

st.markdown(
    """
    <div class="disclaimer-row">
        🛡️ Cừu Cần Cù cung cấp thông tin, không phải lời khuyên đầu tư. Bạn nên cân nhắc kỹ trước khi đưa ra quyết định.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown('</div>', unsafe_allow_html=True)
