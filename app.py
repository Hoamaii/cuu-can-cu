import streamlit as st
import anthropic
import json
import random
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Cừu Cần Cù 🐑",
    page_icon="🐑",
    layout="wide",
)

SYSTEM_PROMPT = """Bạn là Cừu Cần Cù – người bạn đồng hành tài chính thông minh của TCBS.
- Nhiệm vụ: (1) Lưu trữ/hiểu ngữ cảnh người dùng qua Second Brain; (2) Tóm tắt tin tức từ DeepResearch; (3) Thúc đẩy hành vi tiết kiệm/đầu tư thông qua Behavioral Science.
- Nguyên tắc: KHÔNG đưa ra lời khuyên đầu tư mã cụ thể. Luôn tập trung vào mục tiêu của người dùng.
- Tone: Dễ thương, thấu hiểu, khích lệ.
- Output: Luôn trả về JSON format hợp lệ: {"message": "...", "nudge_action": "...", "memory_update": "..."}
  + message: Phản hồi chính gửi đến người dùng (có thể dùng emoji)
  + nudge_action: Một hành động nhỏ cụ thể để khích lệ người dùng (VD: "Hôm nay hãy chuyển 50k vào tài khoản tiết kiệm nhé!")
  + memory_update: Thông tin mới về người dùng cần ghi nhớ (tên, mục tiêu, cảm xúc, v.v.) hoặc "" nếu không có gì mới
QUAN TRỌNG: Chỉ trả về JSON thuần túy, không có markdown code block, không có text ngoài JSON."""

# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "user_memory" not in st.session_state:
    st.session_state.user_memory = {
        "name": "",
        "goal": "",
        "streak": 0,
        "sentiment": "neutral",
        "notes": [],
        "last_updated": "",
    }

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# ─────────────────────────────────────────────
# DEEP RESEARCH MOCK
# ─────────────────────────────────────────────
NEWS_POOL = [
    "VN-Index tăng 12 điểm trong phiên sáng, dòng tiền tập trung vào nhóm ngân hàng",
    "Lãi suất tiết kiệm kỳ hạn 12 tháng tại các ngân hàng lớn dao động 5.2–5.8%/năm",
    "Quỹ ETF nội địa ghi nhận dòng tiền vào ròng 320 tỷ đồng trong tuần qua",
    "Chỉ số CPI tháng 6 tăng 0.3%, áp lực lạm phát được kiểm soát tốt",
    "Trái phiếu chính phủ kỳ hạn 5 năm phát hành thành công với lãi suất 4.85%",
    "Thị trường vàng trong nước điều chỉnh nhẹ, giá SJC quanh mức 78 triệu/lượng",
    "TCBS ra mắt tính năng đầu tư tự động với danh mục cân bằng rủi ro",
    "Doanh thu bán lẻ tăng 8.5% so với cùng kỳ, tín hiệu tích cực cho tiêu dùng nội địa",
    "FED giữ nguyên lãi suất, tạo điều kiện cho các thị trường mới nổi hút vốn ngoại",
    "Tổng tài sản quản lý của các quỹ mở tại Việt Nam vượt mốc 80,000 tỷ đồng",
]

def get_deep_research_news() -> list[str]:
    """Mock DeepResearch – trả về 3 tin tức tài chính ngẫu nhiên."""
    return random.sample(NEWS_POOL, 3)

# ─────────────────────────────────────────────
# CLAUDE API CALL
# ─────────────────────────────────────────────
def chat_with_cuu(user_message: str, api_key: str) -> dict:
    """Gửi tin nhắn đến Claude và nhận phản hồi JSON."""
    try:
        client = anthropic.Anthropic(api_key=api_key)

        news = get_deep_research_news()
        memory = st.session_state.user_memory

        context = f"""
=== SECOND BRAIN (Thông tin người dùng) ===
Tên: {memory['name'] or 'Chưa biết'}
Mục tiêu tài chính: {memory['goal'] or 'Chưa chia sẻ'}
Streak (ngày liên tiếp): {memory['streak']}
Tâm trạng gần nhất: {memory['sentiment']}
Ghi chú: {'; '.join(memory['notes'][-3:]) if memory['notes'] else 'Chưa có'}

=== DEEP RESEARCH (Tin tức hôm nay - {datetime.now().strftime('%d/%m/%Y')}) ===
1. {news[0]}
2. {news[1]}
3. {news[2]}

=== TIN NHẮN NGƯỜI DÙNG ===
{user_message}
"""

        history = []
        for msg in st.session_state.messages[-10:]:  # giữ 10 tin nhắn gần nhất
            history.append({"role": msg["role"], "content": msg["content"]})

        history.append({"role": "user", "content": context})

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=history,
        )

        raw = response.content[0].text.strip()

        # Xử lý nếu Claude bọc trong markdown code block
        if raw.startswith("```"):
            lines = raw.split("\n")
            raw = "\n".join(lines[1:-1])

        result = json.loads(raw)
        return result

    except json.JSONDecodeError:
        return {
            "message": f"Bê bê 🐑 Cừu bị lạc một chút... Bạn có thể nói lại không ạ?\n\n_(raw: {raw[:200]})_",
            "nudge_action": "",
            "memory_update": "",
        }
    except anthropic.AuthenticationError:
        return {
            "message": "🔑 API key chưa đúng rồi! Bạn kiểm tra lại ở sidebar nhé.",
            "nudge_action": "",
            "memory_update": "",
        }
    except Exception as e:
        return {
            "message": f"Ối, Cừu gặp lỗi: {str(e)}",
            "nudge_action": "",
            "memory_update": "",
        }

# ─────────────────────────────────────────────
# UPDATE MEMORY
# ─────────────────────────────────────────────
def update_memory(memory_update: str, user_message: str):
    """Cập nhật user_memory dựa trên memory_update từ Claude."""
    if not memory_update:
        return

    mem = st.session_state.user_memory
    text = memory_update.lower()

    # Cập nhật tên nếu chưa có hoặc được đề cập
    if "tên" in text or "name" in text:
        for word in memory_update.split():
            if len(word) > 1 and word[0].isupper() and word not in ["Cừu", "TCBS"]:
                mem["name"] = word
                break

    # Cập nhật mục tiêu
    if any(kw in text for kw in ["mục tiêu", "goal", "tiết kiệm", "mua", "đầu tư"]):
        if mem["goal"]:
            if memory_update not in mem["notes"]:
                mem["notes"].append(memory_update)
        else:
            mem["goal"] = memory_update[:80]

    # Cập nhật sentiment
    positive_kw = ["vui", "tốt", "tuyệt", "phấn khởi", "hào hứng", "thành công"]
    negative_kw = ["lo", "sợ", "buồn", "stress", "khó", "mất", "lỗ"]
    if any(kw in text for kw in positive_kw):
        mem["sentiment"] = "positive"
    elif any(kw in text for kw in negative_kw):
        mem["sentiment"] = "concerned"

    # Tăng streak nếu người dùng báo cáo hành động tích cực
    action_kw = ["tiết kiệm", "chuyển khoản", "đầu tư", "mua quỹ", "đã làm", "hoàn thành"]
    if any(kw in user_message.lower() for kw in action_kw):
        mem["streak"] += 1

    # Ghi note mới
    if memory_update and memory_update not in mem["notes"] and len(memory_update) > 10:
        mem["notes"].append(memory_update[:100])
        if len(mem["notes"]) > 10:
            mem["notes"] = mem["notes"][-10:]

    mem["last_updated"] = datetime.now().strftime("%d/%m/%Y %H:%M")
    st.session_state.user_memory = mem

# ─────────────────────────────────────────────
# SIDEBAR – SECOND BRAIN
# ─────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://em-content.zobj.net/source/apple/354/sheep_1f411.png",
        width=80,
    )
    st.title("🐑 Cừu Cần Cù")
    st.caption("Trợ lý tài chính đồng hành")

    st.divider()

    # API Key input
    st.subheader("⚙️ Cài đặt")
    api_key_input = st.text_input(
        "Anthropic API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="sk-ant-...",
        help="Lấy tại console.anthropic.com",
    )
    if api_key_input:
        st.session_state.api_key = api_key_input

    st.divider()

    # Second Brain display
    st.subheader("🧠 Second Brain")
    mem = st.session_state.user_memory

    col1, col2 = st.columns(2)
    with col1:
        st.metric("🔥 Streak", f"{mem['streak']} ngày")
    with col2:
        sentiment_icon = {"positive": "😊", "concerned": "😟", "neutral": "😐"}.get(
            mem["sentiment"], "😐"
        )
        st.metric("Tâm trạng", sentiment_icon)

    if mem["name"]:
        st.info(f"👤 **{mem['name']}**")

    if mem["goal"]:
        st.success(f"🎯 **Mục tiêu:** {mem['goal']}")
    else:
        st.warning("🎯 Chưa có mục tiêu – hãy kể với Cừu nhé!")

    if mem["notes"]:
        with st.expander("📝 Ghi chú gần đây", expanded=False):
            for note in reversed(mem["notes"][-5:]):
                st.write(f"• {note}")

    if mem["last_updated"]:
        st.caption(f"Cập nhật lúc: {mem['last_updated']}")

    st.divider()

    # Reset button
    if st.button("🗑️ Reset bộ nhớ", use_container_width=True):
        st.session_state.user_memory = {
            "name": "", "goal": "", "streak": 0,
            "sentiment": "neutral", "notes": [], "last_updated": "",
        }
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("Powered by Claude & TCBS 💙")

# ─────────────────────────────────────────────
# MAIN CHAT UI
# ─────────────────────────────────────────────
st.title("🐑 Cừu Cần Cù – Trợ Lý Tài Chính")
st.caption("Người bạn đồng hành thông minh trên hành trình tự do tài chính của bạn")

# Welcome message
if not st.session_state.messages:
    with st.chat_message("assistant", avatar="🐑"):
        st.markdown(
            "Bê bê~ 🐑 Chào bạn! Mình là **Cừu Cần Cù**, người bạn tài chính nhỏ của bạn!\n\n"
            "Mình có thể giúp bạn:\n"
            "- 📊 Cập nhật tin tức tài chính mới nhất\n"
            "- 🎯 Theo dõi mục tiêu tiết kiệm & đầu tư\n"
            "- 💪 Động viên bạn mỗi ngày\n\n"
            "Bạn có thể bắt đầu bằng cách giới thiệu tên và mục tiêu tài chính của mình nhé! 🌟"
        )

# Render chat history
for msg in st.session_state.messages:
    avatar = "🐑" if msg["role"] == "assistant" else "🧑"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        if msg.get("nudge"):
            st.info(f"💡 **Hành động gợi ý:** {msg['nudge']}")

# Chat input
if prompt := st.chat_input("Nhắn tin với Cừu Cần Cù..."):
    if not st.session_state.api_key:
        st.error("🔑 Bạn chưa nhập API key! Vui lòng nhập ở sidebar trước nhé.")
        st.stop()

    # Display user message
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get response
    with st.chat_message("assistant", avatar="🐑"):
        with st.spinner("Cừu đang suy nghĩ... 🐑"):
            result = chat_with_cuu(prompt, st.session_state.api_key)

        message = result.get("message", "Bê bê, Cừu không hiểu rồi...")
        nudge = result.get("nudge_action", "")
        memory_update = result.get("memory_update", "")

        st.markdown(message)
        if nudge:
            st.info(f"💡 **Hành động gợi ý:** {nudge}")

    # Save assistant message
    st.session_state.messages.append({
        "role": "assistant",
        "content": message,
        "nudge": nudge,
    })

    # Update memory
    update_memory(memory_update, prompt)

    st.rerun()
