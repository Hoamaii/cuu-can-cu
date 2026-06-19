import streamlit as st
from groq import Groq

# ======================
# GROQ
# ======================

client = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)

# ======================
# PAGE
# ======================

st.set_page_config(
    page_title="🐑 Cừu Cần Cù",
    layout="wide"
)

# ======================
# SIDEBAR
# ======================

with st.sidebar:

    st.image("IMG_7823.jpeg", width=160)

    st.markdown("## 🐑 Cừu Cần Cù")

    st.caption(
        "Người bạn đồng hành tài chính"
    )

    st.divider()

    st.button("💬 Chat cùng Cừu")

    st.button("🔍 Tìm sản phẩm TCBS")

    st.button("🎯 Kế hoạch tiết kiệm")

    st.button("❤️ Nhật ký cảm xúc")

    st.button("🕘 Lịch sử hội thoại")

    st.divider()

    st.success(
        """
🌱 Tích tiểu thành đại

Chỉ cần bắt đầu từ số tiền nhỏ mỗi ngày.
"""
    )

# ======================
# MAIN PAGE
# ======================

st.markdown("# 👋 Xin chào!")

st.markdown(
"""
Mình là **Cừu Cần Cù**

Người bạn đồng hành tài chính của bạn.

### 🌱 Tích tiểu thành đại từ số tiền nhỏ
"""
)

# ======================
# MEMORY
# ======================

if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lịch sử chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ======================
# CHAT INPUT
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
