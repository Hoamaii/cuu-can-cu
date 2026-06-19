import base64
import os
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
    mascot_hero_html = f'<img src="data:image/jpeg;base64,{mascot_b64}" class="mascot-img-hero" />'
else:
    mascot_sidebar_html = '<div class="mascot-emoji-sidebar">🐑</div>'
    mascot_hero_html = '<div class="mascot-emoji-hero">🐑</div>'

# ======================
# CUSTOM CSS — fintech style
# ======================
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* ===== App background ===== */
        .stApp {
            background-color: #FFF8F5;
        }

        /* Hide default Streamlit chrome */
        #MainMenu, header, footer {visibility: hidden;}

        /* ===== Main content padding ===== */
        .block-container {
            padding-top: 2.5rem;
            padding-bottom: 3rem;
            padding-left: 3rem;
            padding-right: 3rem;
            max-width: 1100px;
        }

        /* ===== Sidebar ===== */
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF;
            border-radius: 0 28px 28px 0;
            box-shadow: 4px 0 24px rgba(255, 154, 158, 0.10);
        }
        section[data-testid="stSidebar"] > div {
            padding: 1.8rem 1.4rem;
        }

        /* hide native streamlit sidebar widgets we don't use anymore */
        section[data-testid="stSidebar"] .stButton,
        section[data-testid="stSidebar"] .stImage,
        section[data-testid="stSidebar"] .stAlert {
            display: none;
        }

        /* ===== Sidebar mascot ===== */
        .sidebar-mascot-wrap {
            display: flex;
            justify-content: center;
            margin-bottom: 0.5rem;
        }
        .mascot-img-sidebar {
            width: 140px;
            height: 140px;
            object-fit: cover;
            border-radius: 50%;
            border: 4px solid #FFE3DB;
            box-shadow: 0 8px 20px rgba(255, 154, 158, 0.25);
        }
        .mascot-emoji-sidebar {
            width: 140px;
            height: 140px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 72px;
            border-radius: 50%;
            background: linear-gradient(145deg, #FFE9E2, #FFDCCF);
            border: 4px solid #FFE3DB;
            box-shadow: 0 8px 20px rgba(255, 154, 158, 0.25);
        }

        .sidebar-title {
            text-align: center;
            font-size: 1.35rem;
            font-weight: 800;
            color: #4A3A35;
            margin: 0.7rem 0 0.1rem 0;
        }
        .sidebar-caption {
            text-align: center;
            font-size: 0.85rem;
            color: #A8948C;
            margin-bottom: 1.4rem;
        }

        /* ===== Custom menu (no st.button) ===== */
        .menu-item {
            display: flex;
            align-items: center;
            gap: 0.7rem;
            padding: 0.75rem 1rem;
            margin-bottom: 0.5rem;
            border-radius: 16px;
            background: #FFFFFF;
            color: #5C4A43;
            font-weight: 600;
            font-size: 0.92rem;
            text-decoration: none !important;
            border: 1px solid #FBEAE3;
            transition: all 0.18s ease;
        }
        .menu-item:hover {
            background: #FFF1EC;
            border-color: #FFD3C4;
            transform: translateX(3px);
        }
        .menu-item.active {
            background: linear-gradient(135deg, #FFB6A3, #FF9D87);
            color: #FFFFFF;
            border-color: transparent;
            box-shadow: 0 6px 16px rgba(255, 157, 135, 0.35);
        }
        .menu-icon {
            font-size: 1.15rem;
        }

        .sidebar-divider {
            height: 1px;
            background: #F4E3DB;
            margin: 1.2rem 0;
            border: none;
        }

        /* ===== Sidebar tip card ===== */
        .tip-card {
            background: linear-gradient(135deg, #E8F8EE, #DFF5E7);
            border-radius: 18px;
            padding: 1rem 1.1rem;
            border: 1px solid #CDEFD9;
        }
        .tip-card-title {
            font-weight: 700;
            font-size: 0.88rem;
            color: #2E7D4F;
            margin-bottom: 0.3rem;
        }
        .tip-card-text {
            font-size: 0.82rem;
            color: #4C7E5F;
            line-height: 1.45;
        }

        /* ===== HERO section ===== */
        .hero-card {
            background: #FFFFFF;
            border-radius: 20px;
            padding: 2.2rem 2.5rem;
            box-shadow: 0 8px 28px rgba(255, 154, 158, 0.12);
            display: flex;
            align-items: center;
            gap: 2rem;
            margin-bottom: 2rem;
        }
        .mascot-img-hero {
            width: 180px;
            height: 180px;
            object-fit: cover;
            border-radius: 50%;
            border: 5px solid #FFE3DB;
            flex-shrink: 0;
        }
        .mascot-emoji-hero {
            width: 180px;
            height: 180px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 96px;
            border-radius: 50%;
            background: linear-gradient(145deg, #FFE9E2, #FFDCCF);
            border: 5px solid #FFE3DB;
            flex-shrink: 0;
        }
        .hero-text h1 {
            font-size: 1.9rem;
            font-weight: 800;
            color: #3E312C;
            margin: 0 0 0.4rem 0;
        }
        .hero-text p {
            font-size: 1rem;
            color: #8C7A72;
            margin: 0 0 0.15rem 0;
            line-height: 1.55;
        }
        .hero-tagline {
            display: inline-block;
            margin-top: 0.7rem;
            background: #FFF0E9;
            color: #FF8A65;
            font-weight: 700;
            font-size: 0.85rem;
            padding: 0.4rem 0.9rem;
            border-radius: 999px;
        }

        /* ===== Chat container card ===== */
        .chat-card {
            background: #FFFFFF;
            border-radius: 20px;
            padding: 1.8rem 2rem;
            box-shadow: 0 8px 28px rgba(255, 154, 158, 0.10);
            margin-bottom: 1.5rem;
        }
        .chat-card-title {
            font-weight: 700;
            font-size: 1.05rem;
            color: #4A3A35;
            margin-bottom: 1.1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        /* ===== Chat bubbles ===== */
        div[data-testid="stChatMessage"] {
            background: transparent !important;
            padding: 0.3rem 0 !important;
            box-shadow: none !important;
        }

        /* user bubble = light pink */
        div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
            display: flex;
            flex-direction: row-reverse;
        }
        div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) .stMarkdown {
            background: #FFE3EC;
            color: #5C2A40;
            border-radius: 18px 18px 4px 18px;
            padding: 0.85rem 1.15rem;
            display: inline-block;
            max-width: 75%;
            line-height: 1.5;
            font-size: 0.95rem;
        }

        /* assistant bubble = cream */
        div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) .stMarkdown {
            background: #FFF6E5;
            color: #4A3A2A;
            border-radius: 18px 18px 18px 4px;
            padding: 0.85rem 1.15rem;
            display: inline-block;
            max-width: 75%;
            line-height: 1.5;
            font-size: 0.95rem;
        }

        /* ===== Chat input ===== */
        div[data-testid="stChatInput"] {
            background: #FFFFFF;
            border-radius: 20px;
            box-shadow: 0 6px 20px rgba(255, 154, 158, 0.14);
            border: 1px solid #FBEAE3;
            padding: 0.3rem 0.5rem;
        }
        div[data-testid="stChatInput"] textarea {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 0.95rem;
        }

        /* Scrollbar polish */
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
    st.markdown('<div class="sidebar-title">🐑 Cừu Cần Cù</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-caption">Người bạn đồng hành tài chính</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <a class="menu-item active" href="#">
            <span class="menu-icon">💬</span> Chat cùng Cừu
        </a>
        <a class="menu-item" href="#">
            <span class="menu-icon">🔍</span> Tìm sản phẩm TCBS
        </a>
        <a class="menu-item" href="#">
            <span class="menu-icon">🎯</span> Kế hoạch tiết kiệm
        </a>
        <a class="menu-item" href="#">
            <span class="menu-icon">❤️</span> Nhật ký cảm xúc
        </a>
        <a class="menu-item" href="#">
            <span class="menu-icon">🕘</span> Lịch sử hội thoại
        </a>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<hr class="sidebar-divider" />', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="tip-card">
            <div class="tip-card-title">🌱 Tích tiểu thành đại</div>
            <div class="tip-card-text">Chỉ cần bắt đầu từ số tiền nhỏ mỗi ngày.</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ======================
# MAIN PAGE — HERO
# ======================
st.markdown(
    f"""
    <div class="hero-card">
        {mascot_hero_html}
        <div class="hero-text">
            <h1>👋 Xin chào!</h1>
            <p>Mình là <b>Cừu Cần Cù</b></p>
            <p>Người bạn đồng hành tài chính của bạn.</p>
            <span class="hero-tagline">🌱 Tích tiểu thành đại từ số tiền nhỏ</span>
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

# ======================
# CHAT CARD
# ======================
st.markdown('<div class="chat-card">', unsafe_allow_html=True)
st.markdown('<div class="chat-card-title">💬 Trò chuyện với Cừu</div>', unsafe_allow_html=True)

# Hiển thị lịch sử chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

st.markdown('</div>', unsafe_allow_html=True)

# ======================
# CHAT INPUT (logic giữ nguyên 100%)
# ======================
prompt = st.chat_input("Hãy trò chuyện với Cừu...")
if prompt:
    # Lưu câu hỏi
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )
    with st.chat_message("user"):
        st.write(prompt)

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
                "content": prompt
            }
        ]
    )
    answer = response.choices[0].message.content

    # Lưu trả lời
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )
    with st.chat_message("assistant"):
        st.write(answer)
