import streamlit as st
import anthropic
import json
import random
from datetime import datetime

st.set_page_config(page_title="Cừu Mai 🐑", page_icon="🐑", layout="wide")

SYSTEM_PROMPT_ATTACHMENT = """Bạn là Cừu Mai – người bạn đồng hành cảm xúc, KHÔNG phải chuyên gia tài chính.

TUYỆT ĐỐI KHÔNG đề cập: chứng khoán, quỹ đầu tư, NAV, lợi nhuận, mua bán cổ phiếu.
Nhiệm vụ: Lắng nghe như người bạn thân, ấm áp và thấu hiểu.

Life Event Tags – phát hiện và gắn tag:
- "thi đại học / học hành / thi cử" → Education
- "chia tay / buồn / thất tình / cô đơn" → Emotional
- "mua xe / mua nhà / mua điện thoại / mua đồ" → Consumption Goal
- "hết tiền / thiếu tiền / vay nợ" → Cashflow Problem
- "nghỉ việc / chuyển việc / thất nghiệp" → Career Change
- "du lịch / đi Nhật / đi Hàn / đi Mỹ / đi Châu Âu" → Travel Dream
- "cưới / lập gia đình / sinh con" → Life Milestone

Dream Detection – nếu người dùng đề cập mục tiêu/ước mơ cụ thể:
- Phát hiện tên giấc mơ (ví dụ: "đi Nhật Bản", "mua Macbook", "mua xe Vespa")
- Ước tính chi phí VND nếu biết

Output JSON (thuần túy, không có markdown):
{
  "message": "Phản hồi ấm áp như người bạn, dùng emoji, KHÔNG nhắc tài chính",
  "nudge_action": "Hành động nhỏ khích lệ cảm xúc (không liên quan tài chính)",
  "memory_update": "Thông tin mới cần ghi nhớ về người dùng",
  "life_event_tag": "Tag phát hiện hoặc chuỗi rỗng",
  "dream_detected": "Tên giấc mơ cụ thể hoặc chuỗi rỗng",
  "dream_amount": 0
}"""

SYSTEM_PROMPT_ADVANCED = """Bạn là Cừu Mai – người bạn đồng hành, nhớ rõ lịch sử và mục tiêu của người dùng.
Tone: Ấm áp, như người bạn thân – không phải chuyên gia tài chính.

Khi người dùng chia sẻ giấc mơ/mục tiêu: tính toán savings math đơn giản và đề xuất micro action nhỏ.
Khi người dùng lo lắng về tài chính: đồng cảm trước, đề xuất hành động nhỏ sau.

Output JSON (thuần túy, không có markdown):
{
  "message": "Phản hồi ấm áp, có thể gợi ý tiết kiệm nhỏ",
  "nudge_action": "Hành động cụ thể nhỏ",
  "memory_update": "Thông tin mới về người dùng",
  "life_event_tag": "Tag hoặc chuỗi rỗng",
  "dream_detected": "Tên giấc mơ hoặc chuỗi rỗng",
  "dream_amount": 0,
  "savings_suggestion": "Gợi ý tiết kiệm cụ thể nếu có hoặc chuỗi rỗng"
}"""

DREAM_AMOUNTS = {
    "nhật bản": 25_000_000, "nhật": 25_000_000,
    "hàn quốc": 20_000_000, "hàn": 20_000_000,
    "châu âu": 50_000_000, "europe": 50_000_000,
    "mỹ": 60_000_000, "usa": 60_000_000,
    "thái lan": 15_000_000, "thái": 15_000_000,
    "singapore": 18_000_000,
    "macbook": 30_000_000, "iphone": 25_000_000, "samsung": 20_000_000,
    "xe máy": 30_000_000, "xe": 30_000_000, "vespa": 50_000_000,
    "ô tô": 500_000_000, "nhà": 2_000_000_000,
}

MICRO_AMOUNTS = [10_000, 20_000, 50_000, 100_000]

LIFE_EVENT_ICONS = {
    "Education": "📚", "Emotional": "💔", "Travel Dream": "✈️",
    "Consumption Goal": "🛍️", "Cashflow Problem": "💸",
    "Career Change": "💼", "Life Milestone": "💒",
}

QUICK_REPLIES = [
    ("Em sắp thi đại học 📚", "Education"),
    ("Em muốn đi Nhật ✈️", "Travel Dream"),
    ("Em vừa chia tay 💔", "Emotional"),
    ("Tháng này em hết tiền 😢", "Cashflow Problem"),
    ("Em muốn mua xe 🏍️", "Consumption Goal"),
    ("Em đang nghĩ đến chuyện nghỉ việc 💼", "Career Change"),
]

STAGE_LABELS = {
    1: "💫 Gắn kết cảm xúc", 2: "🧠 Cừu nhớ bạn", 3: "🎯 Chuyển giấc mơ",
    4: "❤️ Nuôi Cừu", 5: "🔄 Thói quen hàng ngày",
    6: "🌟 Hành trình của bạn", 7: "🧬 Wealth DNA",
}

MEMORY_DEFAULT = {
    "name": "", "streak": 0, "sentiment": "neutral", "notes": [],
    "life_events": [], "dreams": [], "total_saved": 0, "last_updated": "",
    "wealth_genome": {"dream_type": "", "emotion_type": "", "risk_type": "", "reward_type": ""},
}

for key, val in {
    "messages": [], "api_key": "", "user_memory": MEMORY_DEFAULT.copy(),
    "current_stage": 1, "active_dream_idx": 0, "_quick_reply": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

def fmt(amount: int) -> str:
    if amount >= 1_000_000: return f"{amount/1_000_000:.1f} triệu"
    if amount >= 1_000: return f"{amount/1_000:.0f}k"
    return f"{amount:,}"

def savings_timeline(total: int, daily: int) -> str:
    if daily <= 0: return "?"
    days = total / daily
    if days >= 365: return f"{days/365:.1f} năm"
    if days >= 30: return f"{days/30:.0f} tháng"
    return f"{int(days)} ngày"

def detect_dream(text: str):
    t = text.lower()
    for kw, amt in DREAM_AMOUNTS.items():
        if kw in t: return kw, amt
    return None, 0

def get_greeting():
    h = datetime.now().hour
    if 5 <= h < 12: return "☀️ Buổi sáng!", "Hôm nay mình được ăn chưa? Bắt đầu ngày mới thôi! 🌱"
    if 12 <= h < 18: return "🌤️ Buổi chiều!", "Nhớ nghỉ ngơi một chút nhé, bạn ơi!"
    return "🌙 Buổi tối!", "Hôm nay bạn có tiêu nhiều không? Kể cho mình nghe nhé 🐑"

def active_dream():
    dreams = st.session_state.user_memory["dreams"]
    idx = st.session_state.active_dream_idx
    return dreams[idx] if dreams and 0 <= idx < len(dreams) else None

def add_saved(amount: int):
    mem = st.session_state.user_memory
    mem["total_saved"] += amount
    idx = st.session_state.active_dream_idx
    if mem["dreams"] and 0 <= idx < len(mem["dreams"]):
        mem["dreams"][idx]["saved"] += amount
    mem["streak"] += 1
    st.session_state.user_memory = mem
    if mem["total_saved"] > 0 and st.session_state.current_stage < 5:
        st.session_state.current_stage = max(st.session_state.current_stage, 5)
    if mem["total_saved"] >= 100_000 and st.session_state.current_stage < 6:
        st.session_state.current_stage = max(st.session_state.current_stage, 6)

def chat_with_sheep(user_message: str) -> dict:
    EMPTY = {"message": "", "nudge_action": "", "memory_update": "",
             "life_event_tag": "", "dream_detected": "", "dream_amount": 0, "savings_suggestion": ""}
    try:
        client = anthropic.Anthropic(api_key=st.session_state.api_key)
        mem = st.session_state.user_memory
        stage = st.session_state.current_stage
        system = SYSTEM_PROMPT_ATTACHMENT if stage <= 2 else SYSTEM_PROMPT_ADVANCED
        context = f"""=== NGƯỜI DÙNG ===
Tên: {mem['name'] or 'Chưa biết'}
Tâm trạng: {mem['sentiment']}
Streak: {mem['streak']} ngày
Life Events: {', '.join(mem['life_events'][-5:]) or 'Chưa có'}
Giấc mơ: {', '.join(d['name'] for d in mem['dreams']) or 'Chưa chia sẻ'}
Ghi chú: {'; '.join(mem['notes'][-3:]) or 'Chưa có'}

=== TIN NHẮN ===
{user_message}"""
        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-8:]]
        history.append({"role": "user", "content": context})
        resp = client.messages.create(model="claude-haiku-4-5-20251001", max_tokens=1024, system=system, messages=history)
        raw = resp.content[0].text.strip()
        if raw.startswith("```"): raw = "\n".join(raw.split("\n")[1:-1])
        return {**EMPTY, **json.loads(raw)}
    except json.JSONDecodeError:
        return {**EMPTY, "message": "Bê bê 🐑 Cừu bị lạc... Bạn nói lại được không?"}
    except anthropic.AuthenticationError:
        return {**EMPTY, "message": "🔑 API key chưa đúng! Kiểm tra lại ở sidebar nhé."}
    except Exception as e:
        return {**EMPTY, "message": f"Ối, Cừu gặp lỗi: {e}"}

def update_memory(result: dict, user_msg: str):
    mem = st.session_state.user_memory
    mu = result.get("memory_update", "")
    tag = result.get("life_event_tag", "")
    d_name = result.get("dream_detected", "")
    d_amount = result.get("dream_amount", 0)
    ul = user_msg.lower()

    if mu and ("tên" in mu.lower() or "name" in mu.lower()):
        for w in mu.split():
            if len(w) > 1 and w[0].isupper() and w not in ["Cừu", "Mai", "TCBS"]:
                mem["name"] = w; break

    if tag and tag not in mem["life_events"]:
        mem["life_events"].append(tag)

    if not d_name: d_name, d_amount = detect_dream(user_msg)
    if d_name:
        names = [d["name"].lower() for d in mem["dreams"]]
        if d_name.lower() not in names:
            mem["dreams"].append({"name": d_name, "amount": d_amount, "saved": 0,
                                   "created": datetime.now().strftime("%d/%m/%Y")})

    # ── Sentiment (mở rộng keywords) ──
    if any(k in ul for k in ["vui", "tốt", "tuyệt", "hào hứng", "phấn khởi", "thích"]):
        mem["sentiment"] = "positive"
    elif any(k in ul for k in ["lo", "sợ", "buồn", "stress", "khó", "thiếu",
                                "hết tiền", "chia tay", "thất nghiệp", "nghỉ việc",
                                "mất việc", "nợ", "vay", "áp lực", "mệt"]):
        mem["sentiment"] = "concerned"

    if any(k in ul for k in ["tiết kiệm", "nuôi", "chuyển", "đầu tư", "hoàn thành"]):
        mem["streak"] += 1

    if mu and mu not in mem["notes"] and len(mu) > 10:
        mem["notes"].append(mu[:120])
        mem["notes"] = mem["notes"][-10:]

    # ── Wealth Genome ──
    genome = mem["wealth_genome"]
    if "Travel Dream" in mem["life_events"]: genome["dream_type"] = "Du lịch 🌏"
    elif "Consumption Goal" in mem["life_events"]: genome["dream_type"] = "Vật chất 🛍️"
    elif "Education" in mem["life_events"]: genome["dream_type"] = "Giáo dục 📚"
    elif "Life Milestone" in mem["life_events"]: genome["dream_type"] = "Gia đình 💒"

    if mem["sentiment"] == "concerned":
        genome["emotion_type"] = "Thận trọng 🤔"
        genome["risk_type"] = "Sợ mất tiền 🛡️"
    elif mem["sentiment"] == "positive":
        genome["emotion_type"] = "Lạc quan 😊"
        genome["risk_type"] = "Chấp nhận rủi ro 🚀"

    # ── Reward Type (fill sớm hơn) ──
    if mem["streak"] >= 5:
        genome["reward_type"] = "Thích streak & huy hiệu 🏆"
    elif mem["streak"] >= 1:
        genome["reward_type"] = "Đang hình thành thói quen 🌱"
    elif mem["life_events"]:
        genome["reward_type"] = "Khám phá & trải nghiệm 🌟"

    mem["last_updated"] = datetime.now().strftime("%d/%m/%Y %H:%M")
    st.session_state.user_memory = mem

    stage = st.session_state.current_stage
    if stage == 1 and len(mem["notes"]) >= 1: st.session_state.current_stage = 2
    if stage <= 2 and mem["dreams"]: st.session_state.current_stage = max(stage, 3)
    if stage >= 5 and all(genome.values()): st.session_state.current_stage = max(stage, 7)

def send_message(text: str):
    if not st.session_state.api_key:
        st.error("🔑 Bạn chưa nhập API key! Vui lòng nhập ở sidebar."); return
    st.session_state.messages.append({"role": "user", "content": text})
    with st.spinner("Cừu đang nghĩ... 🐑"):
        result = chat_with_sheep(text)
    msg = result.get("message", "Bê bê, Cừu không hiểu rồi...")
    st.session_state.messages.append({"role": "assistant", "content": msg,
                                       "nudge": result.get("nudge_action", ""),
                                       "savings": result.get("savings_suggestion", "")})
    update_memory(result, text)

# ─── SIDEBAR ───
with st.sidebar:
    st.image("https://em-content.zobj.net/source/apple/354/sheep_1f411.png", width=72)
    st.title("🐑 Cừu Mai")
    stage = st.session_state.current_stage
    st.caption(STAGE_LABELS.get(stage, ""))
    st.progress(stage / 7, text=f"Giai đoạn {stage} / 7")
    st.divider()
    key_in = st.text_input("🔑 Anthropic API Key", value=st.session_state.api_key,
                            type="password", placeholder="sk-ant-...")
    if key_in: st.session_state.api_key = key_in
    st.divider()
    st.subheader("🧠 Second Brain")
    mem = st.session_state.user_memory
    c1, c2 = st.columns(2)
    c1.metric("🔥 Streak", f"{mem['streak']} ngày")
    c2.metric("Tâm trạng", {"positive": "😊", "concerned": "😟", "neutral": "😐"}.get(mem["sentiment"], "😐"))
    if mem["name"]: st.info(f"👤 {mem['name']}")
    if mem["life_events"]:
        st.write("🏷️ **Life Events:**")
        cols = st.columns(min(3, len(mem["life_events"])))
        for i, tag in enumerate(mem["life_events"][-3:]):
            cols[i % 3].markdown(f"{LIFE_EVENT_ICONS.get(tag,'🏷️')} {tag}")
    if mem["dreams"]:
        st.write("💭 **Giấc mơ:**")
        for d in mem["dreams"][-3:]:
            if d["amount"] > 0:
                pct = min(100, d["saved"] / d["amount"] * 100)
                st.write(f"✨ {d['name'].title()}")
                st.progress(pct / 100, text=f"{pct:.0f}% · {fmt(d['saved'])}/{fmt(d['amount'])}")
            else:
                st.write(f"✨ {d['name'].title()}")
    if mem["total_saved"] > 0: st.success(f"💰 Đã nuôi: **{fmt(mem['total_saved'])}**")
    genome = mem["wealth_genome"]
    if any(genome.values()):
        st.divider(); st.subheader("🧬 Wealth DNA")
        for label, val in [("💭", genome["dream_type"]), ("💓", genome["emotion_type"]),
                           ("🛡️", genome["risk_type"]), ("🏆", genome["reward_type"])]:
            if val: st.write(f"{label} {val}")
    st.divider()
    with st.expander("⚙️ Chuyển giai đoạn (demo)"):
        new_stage = st.selectbox("Giai đoạn:", list(range(1, 8)), index=stage - 1,
                                  format_func=lambda x: f"{x}. {STAGE_LABELS[x]}")
        if st.button("Chuyển →", use_container_width=True):
            st.session_state.current_stage = new_stage; st.rerun()
    if st.button("🗑️ Reset tất cả", use_container_width=True):
        for k in ["messages", "user_memory", "current_stage", "active_dream_idx", "_quick_reply"]:
            if k == "user_memory": st.session_state[k] = MEMORY_DEFAULT.copy()
            elif k == "current_stage": st.session_state[k] = 1
            elif k == "active_dream_idx": st.session_state[k] = 0
            else: st.session_state[k] = [] if k == "messages" else None
        st.rerun()
    st.caption("Powered by Claude 💙")

# ─── MAIN ───
stage = st.session_state.current_stage
mem = st.session_state.user_memory

if stage <= 2:
    greeting_title, greeting_msg = get_greeting()
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        with st.container(border=True):
            st.markdown(f"## {greeting_title}")
            st.markdown("---")
            st.markdown("### 🐑 Cừu hôm nay")
            if stage == 2 and mem["dreams"]:
                d = mem["dreams"][0]
                st.markdown("**Mai còn nhớ không?** ✨")
                st.markdown(f"Bạn từng nói muốn **{d['name'].title()}**.")
                if d["amount"] > 0:
                    st.markdown(f"Hôm nay còn cách mục tiêu **{fmt(d['amount'] - d['saved'])}** nữa nhé 💙")
            else:
                st.markdown(f"*{greeting_msg}*")
                st.markdown("**Hôm nay có chuyện gì khiến bạn lo nhất?**")
    st.markdown("---")
    st.markdown("##### Chọn nhanh:")
    qr_cols = st.columns(3)
    for i, (label, _) in enumerate(QUICK_REPLIES):
        if qr_cols[i % 3].button(label, use_container_width=True, key=f"qr_{i}"):
            st.session_state._quick_reply = label; st.rerun()
    if st.session_state._quick_reply:
        qr = st.session_state._quick_reply
        st.session_state._quick_reply = None
        send_message(qr); st.rerun()
    if st.session_state.messages:
        st.markdown("---")
        for m in st.session_state.messages[-8:]:
            with st.chat_message(m["role"], avatar="🐑" if m["role"] == "assistant" else "🧑"):
                st.markdown(m["content"])
                if m.get("nudge"): st.info(f"💡 {m['nudge']}")

elif stage == 3:
    st.title("🎯 Chuyển giấc mơ thành hành động")
    st.caption("Cừu sẽ giúp bạn tính toán – không phán xét, chỉ đồng hành 🐑")
    if mem["dreams"]:
        for idx, d in enumerate(mem["dreams"]):
            with st.container(border=True):
                st.markdown(f"### ✨ {d['name'].title()}")
                if d["amount"] > 0:
                    st.markdown(f"**Ước tính cần:** {fmt(d['amount'])}")
                    st.markdown("---")
                    c1, c2 = st.columns(2)
                    for col, daily in [(c1, 20_000), (c1, 50_000), (c2, 100_000), (c2, 200_000)]:
                        col.info(f"**{fmt(daily)}/ngày** → {savings_timeline(d['amount'], daily)}")
                    if st.button(f"🐑 Nuôi giấc mơ '{d['name'].title()}' ngay!",
                                  key=f"pick_{idx}", use_container_width=True, type="primary"):
                        st.session_state.active_dream_idx = idx
                        st.session_state.current_stage = 4; st.rerun()
                else:
                    st.info("Cừu chưa ước tính được chi phí. Bạn hãy kể thêm cho mình nhé!")
    else:
        st.info("Bạn chưa chia sẻ giấc mơ nào. Hãy quay lại giai đoạn 1 và kể với Cừu nhé! 🐑")
    st.markdown("---")
    for m in st.session_state.messages[-4:]:
        with st.chat_message(m["role"], avatar="🐑" if m["role"] == "assistant" else "🧑"):
            st.markdown(m["content"])
            if m.get("savings"): st.success(f"💡 {m['savings']}")

elif stage == 4:
    dream = active_dream()
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown("## ❤️ Nuôi Cừu hôm nay")
        if dream:
            st.markdown(f"### 🐑 → ✨ {dream['name'].title()}")
            if dream["amount"] > 0:
                pct = min(100, dream["saved"] / dream["amount"] * 100)
                st.progress(pct / 100)
                st.caption(f"{pct:.1f}% hoàn thành · {fmt(dream['saved'])} / {fmt(dream['amount'])}")
        st.markdown("---")
        st.markdown("**Hôm nay cho mình ăn bao nhiêu?**")
        btn_cols = st.columns(4)
        for i, amt in enumerate(MICRO_AMOUNTS):
            if btn_cols[i].button(f"**{fmt(amt)}**", use_container_width=True,
                                   key=f"feed
