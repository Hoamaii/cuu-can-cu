

# ═══════════════════════════════════════════════════════════════════════════════
# CEO DEMO ENGINE — 6 engines, storytelling-first, no dashboard
# ═══════════════════════════════════════════════════════════════════════════════

def _generate_demo_data():
    """
    Inject 30 days of synthetic data into mem + st.session_state.messages.
    Called when CEO clicks the demo button. Idempotent.
    """
    from copy import deepcopy
    base = datetime(2026, 5, 25)

    # ── Chat messages ──────────────────────────────────────────────────────────
    chat_script = [
        ("user",      "Cừu ơi em muốn đi concert Big Bang năm sau"),
        ("assistant", "🐑 Big Bang!! Bê bê~ Mình cũng nghe tin rồi! Em đang ở đội 'đang có kế hoạch' hay đội 'tay trắng nhưng vẫn mơ'? 😄"),
        ("user",      "Đội hai 😂 vé chắc mấy triệu mà em chưa biết bắt đầu từ đâu"),
        ("assistant", "🐑 Mình hiểu! Vé concert kiểu này thường từ 2-4 triệu. Còn tầm bao lâu nữa thì concert nhỉ?"),
        ("user",      "Tháng 5 năm sau, tức là còn khoảng 12 tháng"),
        ("assistant", "🐑 12 tháng! Nếu mỗi ngày để dành 10k tiền trà sữa thôi thì 12 tháng là 3.6 triệu rồi. Mình tạo 'Lọ Concert Big Bang' cho em nhé?"),
        ("user",      "Oke Cừu ơi! Em cũng muốn mua MacBook để học thiết kế"),
        ("assistant", "🐑 Ồ thiết kế nghe hay ghê! Em học UI/UX hay đồ họa vậy? Mình hỏi để tính specs cần thiết nha."),
        ("user",      "UI/UX ạ, đang học Figma nên cần máy mạnh hơn điện thoại"),
        ("assistant", "🐑 MacBook Air M4 là đủ rồi, khoảng 28-30 triệu. Em cần máy khi nào — đang gấp hay có thể chờ được?"),
        ("user",      "Tầm 6 tháng nữa là lý tưởng ạ"),
        ("assistant", "🐑 6 tháng — vậy cần để dành khoảng 5 triệu/tháng. Mình đặt mục tiêu 'MacBook Air M4' luôn nhé! 💻"),
        ("user",      "Cừu ơi hôm nay em mệt quá, deadline 3 cái dồn cùng lúc"),
        ("assistant", "🐑 Bê bê~ Ba deadline một lúc là quá tải thật 😔 Hôm nay không cần làm gì thêm — cứ nghỉ ngơi. Mình ở đây nè."),
        ("user",      "Cảm ơn Cừu 🥹 Em stress về tiền nữa, cuối tháng hay hết trước"),
        ("assistant", "🐑 Mình hiểu. Nhiều bạn cùng tuổi em cũng vậy. Em có biết mình hay tiêu nhiều nhất vào khoản nào không?"),
        ("user",      "Shopee và đồ ăn ạ, nhiều khi lên app xem đồng đội tag deal là mua luôn"),
        ("assistant", "🐑 Ah 'deal của bạn bè'! Đây là bẫy FOMO rất phổ biến đó. Mình có một mẹo nhỏ: wishlist 24h — muốn mua gì thì đợi 24 tiếng xem còn muốn không? 90% là không mua nữa 😄"),
        ("user",      "Hay thật! Em thấy bạn bè đi Nhật nhiều quá, xem story mà thèm lắm"),
        ("assistant", "🐑 Nhật Bản nhỉ! Em hay xem video về Nhật không — Kyoto, Tokyo, hay Osaka?"),
        ("user",      "Kyoto ạ, em xem mấy video mùa anh đào mà mê luôn"),
        ("assistant", "🐑 Mình nghe đây 🌸 Có vẻ Nhật Bản không phải chỉ là 'muốn đi' — mà là mơ thật rồi đó. Biết đâu đây là mục tiêu tiếp theo sau concert?"),
        ("user",      "Haha đúng rồi Cừu ơi, em không biết bao giờ mới đủ tiền đi Nhật"),
        ("assistant", "🐑 Trip Nhật 7 ngày khoảng 20-25 triệu. Nghe có vẻ lớn — nhưng nếu bắt đầu từ ngày mai, mỗi ngày 50k thôi thì 18 tháng là đến Kyoto rồi! 🌸"),
        ("user",      "Cừu ơi hôm nay sếp khen em trước team! Vui lắm"),
        ("assistant", "🐑 Bê bê~ Tin vui!!! 🎉 Em xứng đáng được khen lắm. Mình tự hào về em đó! Hôm nay phải cho Cừu ăn để ăn mừng nhé?"),
        ("user",      "Hehe em đang nghĩ cuối năm xin tăng lương"),
        ("assistant", "🐑 Kế hoạch hay lắm! Khi thu nhập tăng, tự động tăng phần để dành lên một chút là công thức hay nhất. Mình sẽ nhớ điều này nhé 💙"),
        ("user",      "Em tiết kiệm được 50k hôm nay, không mua cà phê ngoài"),
        ("assistant", "🐑 50k × 30 ngày = 1.5 triệu/tháng = 18 triệu/năm! Nghe nhỏ nhưng to lắm đó bạn ơi 🐑✨"),
        ("user",      "Cho Cừu ăn 50k nha Cừu"),
        ("assistant", "🐑 Yay! Cừu vừa được ăn rồi~ Bê bê~ Concert Big Bang: thêm 50k vào lọ rồi đó! 🎵"),
        ("user",      "Cừu nhớ không em muốn đi concert Big Bang"),
        ("assistant", "🐑 Mình nhớ chứ! Em kể từ ngày 25/05 đó. Hôm nay là ngày thứ 30 em nói chuyện với mình — em đã tích lũy được 2.3 triệu rồi! Còn 1.7 triệu nữa là đủ vé hạng B 🎵"),
    ]
    st.session_state.messages = [{"role": r, "content": c} for r, c in chat_script]

    # ── Diary entries ──────────────────────────────────────────────────────────
    diary_raw = [
        (0,  "😔", "rất lo",       ["cashflow","stress"],
         "Hôm nay lương vừa về nhưng em lại đặt Shopee mất 700k. Không biết mình mua gì nữa.",
         "Bê bê~ Không sao cả — quan trọng là em nhận ra điều này 💙",
         ""),
        (2,  "😔", "áp lực",       ["stress","dream_travel"],
         "Em thấy bạn bè ai cũng đi Đà Lạt mà em không có tiền. Hơi tủi.",
         "Mình hiểu cảm giác nhìn story mà thấy tủi 💙 Mỗi người có timeline riêng.",
         "Du lịch Đà Lạt"),
        (5,  "💪", "quyết tâm",    ["milestone"],
         "Hôm nay tiết kiệm được 50k, không mua cà phê ngoài. Nhỏ thôi nhưng em vui.",
         "50k × 30 ngày = 1.5 triệu! Nghe nhỏ nhưng to lắm 🐑✨",
         ""),
        (8,  "😊", "rất vui",      ["career","milestone"],
         "Sếp khen em trước team. Em đang nghĩ cuối năm có thể xin tăng lương.",
         "Tin vui!! Em xứng đáng lắm! Mình tự hào 🎉",
         "Career growth"),
        (10, "😴", "mệt",          ["stress","career"],
         "Mệt quá, deadline 3 cái dồn lúc. Cảm giác làm mãi không đủ tiền.",
         "Bê bê~ Ba deadline một lúc là quá tải. Hôm nay nghỉ ngơi đi 💙",
         ""),
        (13, "😊", "hơi mơ mộng", ["dream_travel"],
         "Em xem video Kyoto mùa anh đào. Đẹp quá. Không biết bao giờ mình đi được.",
         "Mình thấy em đang mơ về Nhật Bản rồi đó 🌸 Cừu nhớ điều này nhé!",
         "Du lịch Nhật Bản"),
        (16, "💪", "quyết tâm",    ["milestone"],
         "Hôm nay em để dành 100k. Streak 16 ngày rồi!",
         "16 ngày liên tiếp! Em đang hình thành thói quen tài chính thật sự rồi đó 💪",
         ""),
        (18, "😔", "áp lực",       ["cashflow","stress"],
         "Cuối tháng lại hết tiền sớm. Em nghĩ mình không giỏi quản lý tiền.",
         "Đừng nghĩ vậy! Em đang streak 18 ngày — điều đó không phải ai cũng làm được đâu 🐑",
         ""),
        (20, "😊", "rất vui",      ["career"],
         "Hôm nay em được giao project mới, team lead tin tưởng!",
         "Wow!! Trách nhiệm lớn hơn nghĩa là người ta thấy tiềm năng của em 🌟",
         ""),
        (22, "😊", "hơi mơ mộng", ["dream_travel"],
         "Em lại xem video về Nhật. Lần này về Osaka. Thức ăn nhìn ngon quá 🍜",
         "Lần thứ ba em nhắc Nhật Bản rồi đó 🌸 Mình đoán em đang mơ về Nhật thật sự!",
         "Du lịch Nhật Bản"),
        (24, "💪", "quyết tâm",    ["milestone"],
         "Hôm nay tiết kiệm 200k. Concert Big Bang đang đến gần dần rồi!",
         "2.3 triệu rồi! Chỉ còn 1.7 triệu nữa là đủ vé hạng B 🎵",
         "Concert Big Bang"),
        (26, "😴", "mệt",          ["stress"],
         "Mệt mỏi quá. Không muốn làm gì. Chỉ muốn nằm.",
         "Ổn thôi — ai cũng có ngày như vậy. Mình vẫn ở đây nè 💙",
         ""),
        (28, "😊", "rất vui",      ["milestone","cashflow"],
         "Hôm nay em nhận được tiền freelance extra 2 triệu. Vui lắm!",
         "Extra income! Bê bê~ 🎉 Nếu cho một phần vào Concert Jar thì gần lắm rồi!",
         ""),
        (29, "💪", "quyết tâm",    ["milestone"],
         "30 ngày streak rồi! Em không nghĩ mình làm được.",
         "30 NGÀY!! Bê bê~ Đây là cột mốc quan trọng lắm. Mình tự hào về em vô cùng 🏆",
         ""),
        (30, "😊", "mơ mộng",      ["dream_travel","milestone"],
         "Hôm nay nghĩ lại từ ngày đầu đến giờ. Em thấy mình thay đổi nhiều.",
         "Em đã thay đổi thật — không phải vì số tiền, mà vì em đã học cách tin tưởng bản thân 🌱",
         "Du lịch Nhật Bản"),
    ]

    entries = []
    for offset_days, mood_ico, mood_txt, tags, content, reply, dream in diary_raw:
        dt = base + timedelta(days=offset_days)
        entries.append({
            "date":     dt.strftime("%d/%m/%Y"),
            "date_raw": dt.isoformat(),
            "mood":     f"{mood_ico} {mood_txt}",
            "content":  content,
            "reply":    reply,
            "tags":     tags,
            "dream":    dream,
        })

    # ── Feed history ───────────────────────────────────────────────────────────
    feed_log = []
    feed_amounts = [
        (1, 50_000), (3, 20_000), (5, 50_000), (7, 100_000), (9, 20_000),
        (10, 50_000), (12, 50_000), (14, 100_000), (16, 50_000), (18, 20_000),
        (19, 50_000), (20, 100_000), (22, 50_000), (24, 200_000), (25, 50_000),
        (26, 20_000), (27, 50_000), (28, 500_000), (29, 100_000), (30, 100_000),
    ]
    total = 0
    for day_off, amt in feed_amounts:
        dt = base + timedelta(days=day_off)
        total += amt
        feed_log.append({
            "date": dt.strftime("%Y-%m-%d"),
            "amount": amt,
            "cumulative": total,
        })

    # ── Patch mem ──────────────────────────────────────────────────────────────
    today_str = datetime.now().strftime("%Y-%m-%d")
    mem.update({
        "name":           "Linh",
        "notes":          [
            "Muốn đi concert Big Bang, còn 12 tháng, vé 2-4 triệu",
            "Đang học Figma, muốn mua MacBook Air M4 trong 6 tháng",
            "Hay bị FOMO với Shopee deal từ bạn bè",
            "Hay xem video Nhật Bản, mơ đi Kyoto mùa anh đào",
            "Cuối năm muốn xin tăng lương",
        ],
        "life_events":    ["dream_travel", "cashflow", "career", "stress", "milestone", "emotional"],
        "dreams":         [
            {"name": "Concert Big Bang",   "amount": 4_000_000,  "saved": 2_300_000, "tags": ["entertainment"]},
            {"name": "MacBook Air M4",     "amount": 30_000_000, "saved": 1_500_000, "tags": ["education"]},
            {"name": "Du lịch Nhật Bản",  "amount": 25_000_000, "saved": 500_000,   "tags": ["travel"]},
        ],
        "total_saved":    total,
        "streak":         30,
        "last_fed_date":  today_str,
        "last_visit_date": today_str,
        "sentiment":      "positive",
        "diary_entries":  entries,
        "feed_log":       feed_log,
        "user_exp":       3_400,
        "current_level":  4,
        "ilucky_tickets": 6,
        "achievements":   ["first_chat", "streak_7", "streak_30", "level_4"],
        "daily_quests":   {today_str: {"visit": True, "chat": True, "diary": True, "feed": True, "bonus_claimed": True}},
        "wealth_genome":  {"risk_type": "medium", "personality": "dream_chaser", "stage": "accumulation"},
    })
    _save()
    st.session_state.demo_mode = True


def _build_future_memory_timeline(m: dict) -> list[dict]:
    """
    Returns a list of timeline events sorted by date.
    Each: {date, type, content, amount, cumulative}
    """
    events = []

    # First dream mention
    for d in m.get("dreams", []):
        events.append({
            "date": (datetime.now() - timedelta(days=30)).strftime("%d/%m"),
            "type": "dream",
            "icon": "💭",
            "content": f'Bạn lần đầu kể về ước mơ: <strong>"{d["name"]}"</strong>',
            "amount": 0,
            "cumulative": 0,
        })
        break

    # Diary moments
    for e in m.get("diary_entries", [])[:15]:
        try:
            dt = datetime.fromisoformat(e["date_raw"])
            display_date = dt.strftime("%d/%m")
        except Exception:
            display_date = e.get("date", "?")

        snippet = e.get("content", "")[:60] + "..."
        events.append({
            "date": display_date,
            "type": "diary",
            "icon": "📔",
            "content": f'<em>"{snippet}"</em>',
            "amount": 0,
            "cumulative": 0,
        })

    # Feed events
    for f in m.get("feed_log", [])[:5]:
        try:
            dt = datetime.strptime(f["date"], "%Y-%m-%d")
            display_date = dt.strftime("%d/%m")
        except Exception:
            display_date = f.get("date", "?")
        events.append({
            "date": display_date,
            "type": "feed",
            "icon": "🐑",
            "content": f'Cho Cừu ăn <strong>{fmt(f["amount"])}</strong>',
            "amount": f["amount"],
            "cumulative": f.get("cumulative", 0),
        })

    return events[:20]


def _detect_latent_dream(m: dict) -> tuple | None:
    """
    Scan notes + diary tags for repeated travel/dream signals.
    Returns (dream_name, confidence_pct, evidence_list) or None.
    """
    signals = {
        "Nhật Bản":    ["nhật", "nhật bản", "kyoto", "tokyo", "osaka", "anh đào", "sakura"],
        "Hàn Quốc":   ["hàn", "hàn quốc", "seoul", "kpop", "bts", "blackpink"],
        "Châu Âu":    ["châu âu", "paris", "rome", "london", "europe", "backpack"],
        "MacBook":     ["macbook", "mac", "m4", "m3", "apple laptop"],
        "iPhone":      ["iphone", "16 pro", "15 pro", "đổi máy"],
        "Nhà riêng":   ["mua nhà", "có nhà", "chung cư", "nhà riêng"],
    }

    # Existing named dreams — skip those
    existing = {d["name"].lower() for d in m.get("dreams", [])}

    all_text = " ".join(m.get("notes", [])).lower()
    all_text += " " + " ".join(
        e.get("content", "") for e in m.get("diary_entries", [])
    ).lower()

    best_dream, best_score, best_evidence = None, 0, []
    for dream_name, kws in signals.items():
        if any(dream_name.lower() in ex for ex in existing):
            continue
        hits = [kw for kw in kws if kw in all_text]
        count = sum(all_text.count(kw) for kw in kws)
        if count >= 2 and len(hits) >= 1:
            score = min(99, 70 + count * 3 + len(hits) * 5)
            if score > best_score:
                best_dream, best_score, best_evidence = dream_name, score, hits

    if best_dream and best_score >= 75:
        return best_dream, best_score, best_evidence
    return None


def _detect_churn_risk(m: dict) -> tuple:
    """
    Returns (risk_level, days_since_activity, message)
    risk_level: 'low' | 'medium' | 'high'
    """
    today = datetime.now().date()
    last_fed = m.get("last_fed_date", "")
    last_visit = m.get("last_visit_date", "")

    days_no_feed = 999
    if last_fed:
        try:
            days_no_feed = (today - datetime.strptime(last_fed, "%Y-%m-%d").date()).days
        except Exception:
            pass

    days_no_visit = 999
    if last_visit:
        try:
            days_no_visit = (today - datetime.strptime(last_visit, "%Y-%m-%d").date()).days
        except Exception:
            pass

    streak = m.get("streak", 0)
    total = m.get("total_saved", 0)
    n_diary = len(m.get("diary_entries", []))
    n_chat  = len(st.session_state.get("messages", []))

    # High risk
    if days_no_feed >= 7 or (days_no_visit >= 5 and streak < 3):
        return "high", max(days_no_feed, days_no_visit), (
            f"Mình hơi lo. {max(days_no_feed, days_no_visit)} ngày rồi bạn chưa ghé thăm mình. "
            "Có chuyện gì làm bạn mất động lực không?"
        )
    # Medium risk
    if days_no_feed >= 3 or (streak > 0 and days_no_feed >= 2):
        return "medium", days_no_feed, (
            f"Mình nhớ bạn! Đã {days_no_feed} ngày Cừu chưa được ăn rồi. "
            "Hôm nay cho mình ăn một chút nhé — dù nhỏ cũng được 🐑"
        )
    # Low risk
    return "low", 0, ""


def _build_ai_story(m: dict) -> dict:
    """
    Returns a dict of 5 storytelling sections — no dashboards, no scores.
    {noticed, remember, changed, worried, proud}
    """
    name      = m.get("name") or "bạn"
    dreams    = m.get("dreams", [])
    tags      = m.get("life_events", [])
    notes     = m.get("notes", [])
    streak    = m.get("streak", 0)
    total     = m.get("total_saved", 0)
    diary_cnt = len(m.get("diary_entries", []))
    n_diary   = diary_cnt
    chats     = len(st.session_state.get("messages", [])) // 2

    # ── NOTICED ──
    dream_names = [d["name"] for d in dreams[:3]]
    if dream_names:
        dream_str = " · ".join(f"<strong>{d}</strong>" for d in dream_names)
        noticed = (
            f"{name} ơi, mình để ý thấy bạn có những giấc mơ rất cụ thể: {dream_str}. "
            "Không phải ai cũng biết mình muốn gì — bạn biết, và điều đó quan trọng lắm."
        )
    elif "dream_travel" in tags:
        noticed = f"Mình để ý thấy {name} hay nhắc đến du lịch. Có vẻ đó là điều bạn thực sự muốn."
    elif "career" in tags:
        noticed = f"Mình thấy {name} đang nghĩ rất nhiều về sự nghiệp và tương lai."
    else:
        noticed = f"Mình đang lắng nghe và tìm hiểu thêm về bạn, {name} ơi."

    # ── REMEMBER ──
    memory_items = []
    for note in notes[:3]:
        memory_items.append(f"<li>{note}</li>")
    if streak > 0:
        memory_items.append(f"<li>Bạn đã duy trì streak <strong>{streak} ngày</strong> liên tiếp</li>")
    if total > 0:
        memory_items.append(f"<li>Bạn đã tích lũy được <strong>{fmt(total)}</strong> từ đầu</li>")
    remember = "".join(memory_items) if memory_items else "<li>Mình vẫn đang lắng nghe để hiểu bạn hơn...</li>"

    # ── CHANGED ──
    if streak >= 30:
        changed = (
            f"30 ngày trước, bạn chưa có thói quen tích lũy. "
            f"Hôm nay bạn đang ở ngày thứ <strong>{streak}</strong> streak và có <strong>{fmt(total)}</strong> trong lọ. "
            "Đây không phải may mắn — đây là thứ bạn tự xây dựng."
        )
    elif streak >= 7:
        changed = (
            f"7 ngày trước, bạn bắt đầu một thói quen mới. "
            f"Hôm nay streak đã là <strong>{streak} ngày</strong>. Mình thấy bạn đang thay đổi thật sự."
        )
    elif total > 0:
        changed = (
            f"Từ con số 0, bạn đã có <strong>{fmt(total)}</strong>. "
            "Khoảng cách từ 'chưa bắt đầu' đến 'đang tiến hành' là khoảng cách lớn nhất — và bạn đã vượt qua."
        )
    elif n_diary >= 3:
        changed = (
            f"Bạn đã viết <strong>{n_diary} trang nhật ký</strong>. "
            "Người biết lắng nghe bản thân thường đưa ra quyết định tốt hơn — bạn đang làm điều đó."
        )
    else:
        changed = "Bạn vừa bắt đầu — mình đang theo dõi hành trình của bạn."

    # ── WORRIED ──
    churn_level, days_away, churn_msg = _detect_churn_risk(m)
    if churn_level == "high":
        worried = churn_msg
    elif "stress" in tags or "cashflow" in tags:
        worried = (
            "Mình thấy bạn hay nhắc đến áp lực và tiền bạc. "
            "Stress tài chính là bình thường — nhưng mình lo nếu nó làm bạn mất động lực. "
            "Nhớ là mình ở đây để đồng hành, không phải phán xét nhé."
        )
    else:
        worried = "Mình không lo gì đặc biệt về bạn lúc này. Hãy cứ giữ đà này! 🐑"

    # ── PROUD ──
    prides = []
    if streak >= 30:
        prides.append(f"Streak <strong>{streak} ngày</strong> — top 5% người dùng kiên trì nhất")
    elif streak >= 7:
        prides.append(f"Streak <strong>{streak} ngày</strong> — điều không phải ai cũng làm được")
    if total >= 2_000_000:
        prides.append(f"Đã tích lũy <strong>{fmt(total)}</strong> — đủ để thấy tiến độ thực sự")
    elif total > 0:
        prides.append(f"Đã bắt đầu — <strong>{fmt(total)}</strong> là con số có thật, không phải ước mơ")
    if n_diary >= 10:
        prides.append(f"<strong>{n_diary} trang nhật ký</strong> — bạn đang lắng nghe bản thân tốt hơn hầu hết")
    if dreams:
        prides.append(f"Có <strong>{len(dreams)} mục tiêu cụ thể</strong> — bạn biết mình muốn gì")
    if not prides:
        prides.append("Bạn đang ở đây và đang thử — đó đã là điều mình tự hào rồi.")

    return {
        "noticed":  noticed,
        "remember": remember,
        "changed":  changed,
        "worried":  worried,
        "proud":    prides,
    }


def _build_genome_narrative(m: dict) -> dict:
    """
    Returns a personality narrative — NOT dashboard layers.
    {archetype, archetype_desc, traits, confidence, segment_name, message}
    """
    tags   = m.get("life_events", [])
    dreams = m.get("dreams", [])
    notes  = " ".join(m.get("notes", [])).lower()

    # Determine archetype
    travel_score   = tags.count("dream_travel") + (3 if "du lịch" in notes or "nhật" in notes else 0)
    career_score   = tags.count("career") + tags.count("education")
    fomo_score     = tags.count("stress") + tags.count("cashflow") + (2 if "shopee" in notes or "deal" in notes else 0)
    dream_score    = len(dreams) + (2 if any("concert" in d["name"].lower() or "iphone" in d["name"].lower() or "macbook" in d["name"].lower() for d in dreams) else 0)

    if travel_score >= 3:
        archetype = "✈️ Travel Explorer"
        archetype_desc = "Bạn thuộc nhóm người luôn nhìn xa hơn — không gian sống của bạn không chỉ là thành phố đang ở. Bạn thu thập trải nghiệm, không phải đồ vật."
        traits = [
            "Hay bị cuốn hút bởi hình ảnh du lịch và câu chuyện của người khác",
            "Có khả năng tiết kiệm đều đặn khi mục tiêu đủ cụ thể và hữu hình",
            "Động lực tăng mạnh khi thấy tiến độ — kể cả 1%",
            "Nhạy cảm với community — thích biết có người cùng mục tiêu",
        ]
        segment = "Travel Explorer"
        message = "Trip đầu tiên không bắt đầu bằng visa. Nó bắt đầu bằng 10.000đ."
    elif dream_score >= 4:
        archetype = "🌟 Dream Chaser"
        archetype_desc = "Bạn thuộc nhóm người biết mình muốn gì. Ước mơ của bạn rõ ràng và cụ thể — concert, gadget, trải nghiệm mới. Bạn không mơ chung chung, bạn mơ có địa chỉ."
        traits = [
            "Thường bị hấp dẫn bởi những thứ có tính trải nghiệm cao: concert, công nghệ, sự kiện",
            "Dễ có động lực khi nhìn thấy tiến độ — goal bar là công cụ mạnh nhất với bạn",
            "Tiết kiệm tốt hơn khi mục tiêu có deadline rõ ràng",
            "Hay bị FOMO khi bạn bè check-in — nhưng biết cách chuyển nó thành năng lượng tích lũy",
        ]
        segment = "Dream Chaser"
        message = "Mỗi ngày 10.000đ cũng đưa bạn gần hơn tới chiếc MacBook — hay bất kỳ điều gì bạn đang mơ."
    elif career_score >= 2:
        archetype = "📚 Life Builder"
        archetype_desc = "Bạn thuộc nhóm người đầu tư vào chính mình trước. Bạn hiểu rằng kỹ năng và kiến thức là tài sản dài hạn nhất."
        traits = [
            "Tư duy dài hạn hơn phần lớn bạn bè cùng tuổi",
            "Nhạy với ROI — thích biết tiền mình bỏ ra sẽ sinh ra gì",
            "Có khả năng tích lũy đều đặn khi hiểu lý do đằng sau",
            "Career milestone thường là trigger để tăng saving",
        ]
        segment = "Life Builder"
        message = "Đầu tư cho tương lai cũng là một loại đầu tư — và đó là loại dài hạn nhất."
    else:
        archetype = "🌱 Early Saver"
        archetype_desc = "Bạn đang ở giai đoạn bắt đầu — và đây là giai đoạn quan trọng nhất. Thói quen hình thành ở giai đoạn này sẽ theo bạn cả đời."
        traits = [
            "Đang xây dựng nhận thức tài chính — mỗi ngày học được điều gì đó mới",
            "Cần môi trường hỗ trợ và động lực bên ngoài để duy trì",
            "Streak và milestone nhỏ là công cụ động lực hiệu quả nhất",
            "Tiềm năng cao khi có mục tiêu cụ thể",
        ]
        segment = "Early Saver"
        message = "Bắt đầu nhỏ, bắt đầu ngay — đó là bí quyết duy nhất."

    # Confidence based on data richness
    data_pts = (
        len(dreams) * 15
        + len(tags) * 5
        + min(len(m.get("notes", [])) * 8, 40)
        + min(len(m.get("diary_entries", [])) * 3, 30)
    )
    confidence = min(97, 60 + data_pts // 3)

    return {
        "archetype": archetype,
        "archetype_desc": archetype_desc,
        "traits": traits,
        "confidence": confidence,
        "segment": segment,
        "message": message,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — 🎯 AI INTELLIGENCE  (Storytelling · Not Dashboard)
# "Một người bạn đang hiểu khách hàng" — not a BI dashboard
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:

    # ── Shared CSS ─────────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    /* ── Base card ── */
    .ai-card{background:#fff;border:1.5px solid #ede8ff;border-radius:22px;
             padding:24px 26px;margin-bottom:18px;}
    .ai-card-dark{background:linear-gradient(135deg,#0F0C29,#1a1650);
                  border:none;border-radius:22px;padding:24px 26px;margin-bottom:18px;}

    /* ── Section header — sheep speaks ── */
    .sheep-speaks{display:flex;align-items:flex-start;gap:14px;margin-bottom:18px;}
    .sheep-avatar{width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,#FFB5C8,#FFD6E8);
                  display:flex;align-items:center;justify-content:center;
                  font-size:1.5rem;flex-shrink:0;
                  box-shadow:0 4px 14px rgba(255,140,190,.35);}
    .sheep-text-wrap{flex:1;}
    .sheep-label{font-size:.72rem;font-weight:800;color:#C4607F;text-transform:uppercase;
                 letter-spacing:.08em;margin-bottom:5px;}
    .sheep-text{font-size:.97rem;color:#333;line-height:1.75;}

    /* ── Timeline ── */
    .tl-row{display:flex;gap:14px;align-items:flex-start;padding:10px 0;
            border-bottom:1px solid #f0e8ff;}
    .tl-row:last-child{border-bottom:none;}
    .tl-date{font-size:.75rem;font-weight:700;color:#aaa;width:36px;flex-shrink:0;
             padding-top:2px;text-align:right;}
    .tl-dot-col{display:flex;flex-direction:column;align-items:center;width:20px;flex-shrink:0;}
    .tl-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0;margin-top:3px;}
    .tl-dot-dream{background:#C4607F;}
    .tl-dot-diary{background:#7B5EA7;}
    .tl-dot-feed{background:#4ECDC4;}
    .tl-line{width:2px;background:linear-gradient(180deg,#e8e0ff,transparent);
             flex:1;min-height:16px;}
    .tl-content{font-size:.85rem;color:#444;line-height:1.6;flex:1;}

    /* ── Genome narrative ── */
    .archetype-hero{border-radius:20px;padding:22px 24px;margin-bottom:16px;
                    background:linear-gradient(135deg,#FFF5F9,#F5F0FF,#F0F5FF);}
    .archetype-name{font-size:1.4rem;font-weight:900;color:#302B63;margin-bottom:6px;}
    .archetype-desc{font-size:.92rem;color:#555;line-height:1.7;}
    .trait-item{display:flex;align-items:flex-start;gap:10px;padding:9px 0;
                border-bottom:1px solid #f4f0ff;}
    .trait-item:last-child{border-bottom:none;}
    .trait-dot{width:8px;height:8px;border-radius:50%;background:#C4607F;
               flex-shrink:0;margin-top:5px;}

    /* ── WOW moment — Dream detection ── */
    .wow-card{background:linear-gradient(135deg,#1A1A2E,#302B63);border-radius:22px;
              padding:28px 26px;margin-bottom:18px;text-align:center;}
    .wow-sheep-big{font-size:3.5rem;margin-bottom:10px;}
    .wow-text{font-size:1.1rem;color:rgba(255,255,255,.9);line-height:1.75;margin-bottom:18px;}
    .wow-dream-name{font-size:1.6rem;font-weight:900;color:#FFD700;margin:12px 0;}

    /* ── Churn alert ── */
    .churn-medium{background:linear-gradient(135deg,#FFF8E8,#FFF5E0);border:1.5px solid #FFD060;
                  border-radius:18px;padding:20px 22px;margin-bottom:14px;}
    .churn-high{background:linear-gradient(135deg,#FFF0F0,#FFE8E8);border:1.5px solid #FF9090;
                border-radius:18px;padding:20px 22px;margin-bottom:14px;}
    .churn-low{background:linear-gradient(135deg,#F0FFF8,#E8FFEE);border:1.5px solid #70D4A0;
               border-radius:18px;padding:20px 22px;margin-bottom:14px;}

    /* ── Demo button ── */
    .demo-cta{background:linear-gradient(135deg,#302B63,#7B5EA7);border-radius:18px;
              padding:22px 24px;text-align:center;margin-bottom:24px;}
    .demo-cta h3{color:#FFD700;font-size:1.2rem;font-weight:900;margin:0 0 6px;}
    .demo-cta p{color:rgba(255,255,255,.8);font-size:.88rem;margin:0;}

    /* ── CEO Wow Flow steps ── */
    .wow-flow{display:flex;gap:0;overflow-x:auto;padding:4px 0 12px;
              scrollbar-width:thin;scrollbar-color:#e8e0ff transparent;}
    .flow-step{display:flex;flex-direction:column;align-items:center;
               min-width:90px;text-align:center;}
    .flow-step-circle{width:38px;height:38px;border-radius:50%;
                      display:flex;align-items:center;justify-content:center;
                      font-size:.9rem;font-weight:900;flex-shrink:0;}
    .flow-active{background:linear-gradient(135deg,#C4607F,#7B5EA7);color:#fff;}
    .flow-done{background:#f0ffe8;color:#3A7A10;border:2px solid #70D4A0;}
    .flow-idle{background:#f4f4f4;color:#bbb;border:2px solid #e8e8e8;}
    .flow-connector{width:28px;height:2px;background:linear-gradient(90deg,#C4607F,#7B5EA7);
                    margin-top:19px;flex-shrink:0;}
    .flow-connector-idle{width:28px;height:2px;background:#e8e8e8;
                         margin-top:19px;flex-shrink:0;}
    .flow-label{font-size:.65rem;color:#888;margin-top:5px;line-height:1.3;max-width:80px;}

    /* ── Proud items ── */
    .proud-row{display:flex;align-items:center;gap:14px;padding:12px 0;
               border-bottom:1px solid #f4f0ff;}
    .proud-row:last-child{border-bottom:none;}
    .proud-icon{font-size:1.6rem;flex-shrink:0;}

    /* ── Segment story card ── */
    .seg-story{border-radius:18px;padding:20px 22px;margin-bottom:10px;border:2px solid;}
    .seg-story-a{background:linear-gradient(135deg,#FFF8F0,#FFFFE0);border-color:#FFB347;}
    .seg-story-b{background:linear-gradient(135deg,#E8FFFF,#E0F8FF);border-color:#4ECDC4;}
    .seg-story-c{background:linear-gradient(135deg,#F0FFE8,#EEFFF0);border-color:#7ED321;}
    </style>
    """, unsafe_allow_html=True)

    # ── 0. DEMO DATA BUTTON ────────────────────────────────────────────────────
    _has_data = bool(
        st.session_state.get("messages")
        or mem.get("total_saved", 0) > 0
        or mem.get("diary_entries")
    )

    if not st.session_state.get("demo_mode") and not _has_data:
        st.markdown("""
        <div class="demo-cta">
          <h3>🎬 Chào CEO — Chưa có dữ liệu thực tế</h3>
          <p>Click bên dưới để xem AI hoạt động với 30 ngày dữ liệu mẫu của người dùng Linh, 21 tuổi.<br/>
             Hoặc bắt đầu chat thật với Cừu ở Tab 💬 rồi quay lại đây!</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🎬 Xem Demo CEO — Load 30 ngày dữ liệu", type="primary",
                     use_container_width=True, key="btn_load_demo"):
            _generate_demo_data()
            st.rerun()
        st.stop()
    elif not _has_data and st.session_state.get("demo_mode"):
        _generate_demo_data()

    # Option to reset/reload demo
    _demo_col1, _demo_col2 = st.columns([5, 1])
    with _demo_col2:
        if st.button("🔄 Reload Demo", key="btn_reload_demo", help="Load lại dữ liệu demo"):
            _generate_demo_data()
            st.rerun()

    # ── CEO WOW FLOW ─────────────────────────────────────────────────────────
    _flow_steps = [
        ("💬", "Chat với Cừu"),
        ("📔", "Nhật ký"),
        ("🧠", "AI nhận ra"),
        ("💭", "Phát hiện giấc mơ"),
        ("❤️", "Quan tâm KH"),
        ("👥", "Phân cụm"),
        ("💰", "Micro Saving"),
        ("📈", "Đầu tư quỹ"),
    ]
    _flow_html = '<div class="wow-flow">'
    for _i, (_ico, _lbl) in enumerate(_flow_steps):
        _cls = "flow-active" if _i == 2 else "flow-done" if _i < 2 else "flow-idle"
        _conn_cls = "flow-connector" if _i < 2 else "flow-connector-idle"
        _flow_html += (
            f'<div class="flow-step">'
            f'<div class="flow-step-circle {_cls}">{_ico}</div>'
            f'<div class="flow-label">{_lbl}</div>'
            f'</div>'
        )
        if _i < len(_flow_steps) - 1:
            _flow_html += f'<div class="{_conn_cls}"></div>'
    _flow_html += '</div>'

    st.markdown(
        f'<div style="background:#fff;border:1.5px solid #ede8ff;border-radius:18px;'
        f'padding:16px 20px;margin-bottom:20px;">'
        f'<div style="font-size:.78rem;font-weight:800;color:#7B5EA7;'
        f'text-transform:uppercase;letter-spacing:.08em;margin-bottom:10px;">'
        f'🎯 CEO Wow Flow — Hành trình 8 bước</div>'
        f'{_flow_html}</div>',
        unsafe_allow_html=True,
    )

    # ── BUILD DATA ─────────────────────────────────────────────────────────────
    _story     = _build_ai_story(mem)
    _genome    = _build_genome_narrative(mem)
    _timeline  = _build_future_memory_timeline(mem)
    _latent    = _detect_latent_dream(mem)
    _churn_lv, _churn_days, _churn_msg = _detect_churn_risk(mem)

    _name = mem.get("name") or "bạn"

    # ═══════════════════════════════════════════════════════
    # SECTION 1 — 🐑 Điều mình nhận ra về bạn
    # ═══════════════════════════════════════════════════════
    st.markdown("""
    <div style="font-size:1.15rem;font-weight:900;color:#302B63;margin:6px 0 14px;
         display:flex;align-items:center;gap:10px;">
      🐑 Điều mình nhận ra về bạn
    </div>
    """, unsafe_allow_html=True)

    _gc1, _gc2 = st.columns([3, 2])

    with _gc1:
        # Archetype card
        st.markdown(f"""
        <div class="archetype-hero">
          <div class="archetype-name">{_genome['archetype']}</div>
          <div class="archetype-desc">{_genome['archetype_desc']}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="font-size:.78rem;font-weight:800;color:#7B5EA7;
             text-transform:uppercase;letter-spacing:.07em;margin-bottom:10px;">
          Cừu thấy bạn thường...
        </div>
        """, unsafe_allow_html=True)

        _trait_html = "".join(
            f'<div class="trait-item">'
            f'<div class="trait-dot"></div>'
            f'<div style="font-size:.9rem;color:#444;line-height:1.6;">{t}</div>'
            f'</div>'
            for t in _genome["traits"]
        )
        st.markdown(
            f'<div style="background:#faf8ff;border-radius:14px;padding:14px 16px;">'
            f'{_trait_html}</div>',
            unsafe_allow_html=True,
        )

    with _gc2:
        # Sheep speaks — noticed
        st.markdown(f"""
        <div class="ai-card">
          <div class="sheep-speaks">
            <div class="sheep-avatar">🐑</div>
            <div class="sheep-text-wrap">
              <div class="sheep-label">Cừu nhận ra</div>
              <div class="sheep-text">{_story['noticed']}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Confidence
        _conf = _genome["confidence"]
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#f8f4ff,#fff4f8);border-radius:14px;
             padding:14px 16px;border:1.5px solid #e8d8ff;">
          <div style="font-size:.78rem;font-weight:800;color:#7B5EA7;margin-bottom:8px;">
            AI tin tưởng điều này
          </div>
          <div style="font-size:2.2rem;font-weight:900;color:#C4607F;">{_conf}%</div>
          <div style="background:#f0f0f7;border-radius:8px;height:10px;overflow:hidden;margin:8px 0;">
            <div style="width:{_conf}%;height:100%;border-radius:8px;
                 background:linear-gradient(90deg,#7B5EA7,#C4607F);"></div>
          </div>
          <div style="font-size:.78rem;color:#888;line-height:1.5;">
            Dựa trên {len(mem.get("notes",[]))} ghi chú · {len(mem.get("diary_entries",[]))} nhật ký ·
            {len(st.session_state.get("messages",[]))//2} cuộc trò chuyện
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Segment message
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1A1A2E,#302B63);border-radius:14px;
             padding:14px 16px;margin-top:12px;">
          <div style="font-size:.72rem;font-weight:800;color:#FFD700;margin-bottom:6px;">
            💬 THÔNG ĐIỆP CHO SEGMENT NÀY
          </div>
          <div style="font-size:.9rem;color:rgba(255,255,255,.9);font-style:italic;
               line-height:1.6;">"{_genome['message']}"</div>
        </div>
        """, unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════
    # SECTION 2 — 🐑 Điều mình đang nhớ (Future Memory Timeline)
    # ═══════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("""
    <div style="font-size:1.15rem;font-weight:900;color:#302B63;margin:6px 0 14px;
         display:flex;align-items:center;gap:10px;">
      🐑 Điều mình đang nhớ
    </div>
    """, unsafe_allow_html=True)

    _tc1, _tc2 = st.columns([2, 3])

    with _tc1:
        # Memory card
        st.markdown(f"""
        <div class="ai-card">
          <div class="sheep-speaks">
            <div class="sheep-avatar">🐑</div>
            <div class="sheep-text-wrap">
              <div class="sheep-label">Cừu đang nhớ</div>
              <div class="sheep-text">
                {_name} ơi, đây là những điều mình đang giữ cho bạn:
              </div>
            </div>
          </div>
          <ul style="margin:0;padding:0 0 0 18px;font-size:.88rem;color:#444;line-height:2;">
            {_story['remember']}
          </ul>
        </div>
        """, unsafe_allow_html=True)

        # Today vs Day 1 delta
        _dreams = mem.get("dreams", [])
        if _dreams and _dreams[0].get("saved", 0) > 0:
            _d = _dreams[0]
            _pct = min(100, int(_d["saved"] / _d["amount"] * 100))
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#0F0C29,#302B63);border-radius:18px;
                 padding:20px 22px;color:#fff;text-align:center;">
              <div style="font-size:.78rem;color:rgba(255,255,255,.6);margin-bottom:4px;">
                43 ngày trước bạn từng nghĩ:
              </div>
              <div style="font-size:.88rem;font-style:italic;
                   color:rgba(255,255,255,.75);margin-bottom:14px;">
                "Không biết có đủ tiền không..."
              </div>
              <div style="font-size:.78rem;color:rgba(255,255,255,.6);margin-bottom:4px;">
                Hôm nay bạn đã có:
              </div>
              <div style="font-size:1.8rem;font-weight:900;color:#FFD700;margin-bottom:2px;">
                {fmt(_d["saved"])}
              </div>
              <div style="font-size:.82rem;color:rgba(255,255,255,.7);margin-bottom:12px;">
                {_pct}% mục tiêu <strong style="color:#fff;">{_d['name']}</strong>
              </div>
              <div style="background:rgba(255,255,255,.15);border-radius:8px;height:8px;overflow:hidden;">
                <div style="width:{_pct}%;height:100%;background:linear-gradient(90deg,#FFD700,#FF8C00);
                     border-radius:8px;"></div>
              </div>
              <div style="font-size:.78rem;color:#FFD700;margin-top:8px;">
                Bạn đang gần hơn rất nhiều so với ngày đầu tiên. 🐑
              </div>
            </div>
            """, unsafe_allow_html=True)

    with _tc2:
        # Timeline
        st.markdown("""
        <div style="font-size:.78rem;font-weight:800;color:#7B5EA7;text-transform:uppercase;
             letter-spacing:.07em;margin-bottom:12px;">
          📅 Hành trình của bạn với Cừu
        </div>
        """, unsafe_allow_html=True)

        if _timeline:
            _tl_html = ""
            for _ev in _timeline[:12]:
                _dot_cls = {
                    "dream": "tl-dot-dream",
                    "diary": "tl-dot-diary",
                    "feed":  "tl-dot-feed",
                }.get(_ev["type"], "tl-dot-diary")
                _tl_html += (
                    f'<div class="tl-row">'
                    f'<div class="tl-date">{_ev["date"]}</div>'
                    f'<div class="tl-dot-col">'
                    f'<div class="tl-dot {_dot_cls}"></div>'
                    f'<div class="tl-line"></div>'
                    f'</div>'
                    f'<div class="tl-content">'
                    f'<span style="font-size:1rem;margin-right:6px;">{_ev["icon"]}</span>'
                    f'{_ev["content"]}'
                    f'{"<br/><span style=\'font-size:.75rem;color:#4ECDC4;font-weight:700;\'>+" + fmt(_ev["amount"]) + " → tổng " + fmt(_ev["cumulative"]) + "</span>" if _ev.get("amount") else ""}'
                    f'</div>'
                    f'</div>'
                )
            st.markdown(
                f'<div style="background:#fff;border:1.5px solid #ede8ff;border-radius:16px;'
                f'padding:16px 18px;max-height:380px;overflow-y:auto;">{_tl_html}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="color:#bbb;font-size:.88rem;padding:20px;text-align:center;">'
                'Chưa có dữ liệu timeline. Hãy chat và viết nhật ký để Cừu nhớ!</div>',
                unsafe_allow_html=True,
            )

    # ═══════════════════════════════════════════════════════
    # SECTION 3 — 🐑 Điều đã thay đổi
    # ═══════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("""
    <div style="font-size:1.15rem;font-weight:900;color:#302B63;margin:6px 0 14px;">
      🐑 Điều đã thay đổi
    </div>
    """, unsafe_allow_html=True)

    _ch1, _ch2, _ch3 = st.columns(3)
    _streak  = mem.get("streak", 0)
    _total   = mem.get("total_saved", 0)
    _n_diary = len(mem.get("diary_entries", []))
    _n_chat  = len(st.session_state.get("messages", [])) // 2

    for _col, _val, _label, _sub, _color in [
        (_ch1, f"{_streak} ngày",  "🔥 Streak",         "Ngày liên tiếp", "#C4607F"),
        (_ch2, fmt(_total),        "💰 Đã tích lũy",    "Tổng cộng",      "#7B5EA7"),
        (_ch3, f"{_n_diary} trang", "📔 Nhật ký",       "Đã viết",        "#4ECDC4"),
    ]:
        _col.markdown(f"""
        <div style="background:#fff;border:1.5px solid #ede8ff;border-radius:18px;
             padding:18px;text-align:center;">
          <div style="font-size:.88rem;font-weight:800;color:{_color};margin-bottom:2px;">{_label}</div>
          <div style="font-size:1.6rem;font-weight:900;color:#1a1a2e;margin:4px 0;">{_val}</div>
          <div style="font-size:.75rem;color:#aaa;">{_sub}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="ai-card" style="margin-top:14px;">
      <div class="sheep-speaks">
        <div class="sheep-avatar">🐑</div>
        <div class="sheep-text-wrap">
          <div class="sheep-label">Cừu muốn kể cho bạn nghe</div>
          <div class="sheep-text">{_story['changed']}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════
    # SECTION 4 — 🐑 Điều mình đang lo (Churn Prediction)
    # ═══════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("""
    <div style="font-size:1.15rem;font-weight:900;color:#302B63;margin:6px 0 14px;">
      🐑 Điều mình đang lo
    </div>
    """, unsafe_allow_html=True)

    if _churn_lv == "high":
        st.markdown(f"""
        <div class="churn-high">
          <div class="sheep-speaks" style="margin-bottom:0;">
            <div class="sheep-avatar" style="background:linear-gradient(135deg,#FFD0D0,#FFE0E0);">🐑</div>
            <div class="sheep-text-wrap">
              <div class="sheep-label" style="color:#C05050;">Cừu hơi lo</div>
              <div class="sheep-text">{_churn_msg}</div>
            </div>
          </div>
        </div>
        <div style="font-size:.82rem;color:#888;font-style:italic;margin-top:-10px;margin-bottom:14px;
             padding-left:6px;">
          ⚠️ Hệ thống phát hiện: {_churn_days} ngày không có hoạt động — cần re-engage ngay.
          Không hiển thị "Retention Score" cho khách hàng — chỉ Cừu quan tâm.
        </div>
        """, unsafe_allow_html=True)
    elif _churn_lv == "medium":
        st.markdown(f"""
        <div class="churn-medium">
          <div class="sheep-speaks" style="margin-bottom:0;">
            <div class="sheep-avatar" style="background:linear-gradient(135deg,#FFF0C0,#FFE8A0);">🐑</div>
            <div class="sheep-text-wrap">
              <div class="sheep-label" style="color:#806020;">Cừu nhắc nhở</div>
              <div class="sheep-text">{_churn_msg}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="churn-low">
          <div class="sheep-speaks" style="margin-bottom:0;">
            <div class="sheep-avatar" style="background:linear-gradient(135deg,#D0FFE8,#C0FFD8);">🐑</div>
            <div class="sheep-text-wrap">
              <div class="sheep-label" style="color:#2A7A50;">Cừu không lo</div>
              <div class="sheep-text">{_story['worried']}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════
    # WOW MOMENT — Dream Detection Engine
    # ═══════════════════════════════════════════════════════
    if _latent:
        _dream_name, _dream_conf, _dream_evidence = _latent
        _known_dream_names = [d["name"].lower() for d in mem.get("dreams", [])]
        _already_confirmed = st.session_state.get("demo_dream_confirm") == _dream_name

        if not _already_confirmed:
            st.markdown("---")
            st.markdown(f"""
            <div class="wow-card">
              <div class="wow-sheep-big">🐑</div>
              <div class="wow-text">
                Mình nghĩ mình vừa phát hiện ra điều gì đó...<br/><br/>
                Qua những gì bạn kể với mình, mình thấy bạn nhắc đến
                <strong style="color:#FFD700;">{', '.join(_dream_evidence[:3])}</strong>
                nhiều lần.<br/>
                Có vẻ bạn đang mơ về:
              </div>
              <div class="wow-dream-name">✨ {_dream_name} ✨</div>
              <div style="font-size:.9rem;color:rgba(255,255,255,.7);margin-bottom:4px;">
                Mình có đoán đúng không?
              </div>
              <div style="font-size:.78rem;color:rgba(255,215,0,.7);">
                AI confidence: {_dream_conf}%
              </div>
            </div>
            """, unsafe_allow_html=True)

            _wd1, _wd2, _wd3 = st.columns([2, 1, 1])
            with _wd2:
                if st.button("✅ Đúng rồi Cừu!", type="primary",
                             use_container_width=True, key="btn_dream_yes"):
                    if _dream_name not in [d["name"] for d in mem.get("dreams", [])]:
                        mem.setdefault("dreams", []).append({
                            "name": _dream_name, "amount": 25_000_000,
                            "saved": 0, "tags": ["travel"],
                        })
                        _save()
                    st.session_state.demo_dream_confirm = _dream_name
                    st.rerun()
            with _wd3:
                if st.button("❌ Chưa đúng", use_container_width=True, key="btn_dream_no"):
                    st.session_state.demo_dream_confirm = f"no_{_dream_name}"
                    st.rerun()
        else:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#F0FFF8,#E8FFEE);border-radius:18px;
                 padding:20px 22px;margin-bottom:18px;border:1.5px solid #70D4A0;">
              <div class="sheep-speaks" style="margin-bottom:0;">
                <div class="sheep-avatar" style="background:linear-gradient(135deg,#C0FFD8,#A0FFE0);">🐑</div>
                <div class="sheep-text-wrap">
                  <div class="sheep-label" style="color:#2A7A50;">Bê bê~ Cừu đoán đúng rồi!</div>
                  <div class="sheep-text">
                    Mình đã thêm <strong>{_dream_name}</strong> vào mục tiêu của bạn 💙
                    Khi nào bạn muốn, mình sẽ giúp bạn lên kế hoạch tích lũy nhé.
                  </div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════
    # SECTION 5 — 🐑 Điều mình tự hào
    # ═══════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("""
    <div style="font-size:1.15rem;font-weight:900;color:#302B63;margin:6px 0 14px;">
      🐑 Điều mình tự hào về bạn
    </div>
    """, unsafe_allow_html=True)

    _p1, _p2 = st.columns([3, 2])
    with _p1:
        _proud_html = "".join(
            f'<div class="proud-row">'
            f'<div class="proud-icon">🏆</div>'
            f'<div style="font-size:.9rem;color:#333;line-height:1.6;">{p}</div>'
            f'</div>'
            for p in _story["proud"]
        )
        st.markdown(
            f'<div class="ai-card">'
            f'<div class="sheep-speaks" style="margin-bottom:14px;">'
            f'<div class="sheep-avatar">🐑</div>'
            f'<div class="sheep-text-wrap">'
            f'<div class="sheep-label">Cừu tự hào</div>'
            f'<div class="sheep-text">Nhìn lại từ đầu đến giờ, mình muốn nói với bạn:</div>'
            f'</div></div>'
            f'{_proud_html}</div>',
            unsafe_allow_html=True,
        )

    with _p2:
        # AI Story — the 4-line narrative
        _final_story = ""
        if _streak >= 14:
            _final_story = (
                f"Mình thấy {_name} là kiểu người luôn có những giấc mơ rất cụ thể. "
                f"Nhưng điều làm mình tự hào không phải giấc mơ — mà là {_streak} ngày "
                f"bạn đã kiên trì, dù có ngày mệt, có ngày stress.<br/><br/>"
                f"<strong>Tin vui là:</strong> {_streak} ngày gần đây bạn đang kiên trì hơn trước rất nhiều."
            )
        elif _total > 0:
            _final_story = (
                f"Mình thấy {_name} đã đi được một chặng đường từ 0 đến {fmt(_total)}. "
                f"Không phải con số lớn — nhưng đó là bằng chứng rằng bạn làm được.<br/><br/>"
                f"<strong>Tin vui là:</strong> người bắt đầu nhỏ thường đi xa hơn người chờ 'đúng thời điểm'."
            )
        else:
            _final_story = (
                f"Mình thấy {_name} đang trong giai đoạn bắt đầu — và giai đoạn này quan trọng nhất. "
                f"Mình sẽ ở đây đồng hành mỗi ngày."
            )

        st.markdown(f"""
        <div class="ai-card-dark" style="height:100%;">
          <div style="font-size:.78rem;font-weight:800;color:#FFD700;margin-bottom:12px;
               text-transform:uppercase;letter-spacing:.07em;">
            🐑 AI kể chuyện về bạn
          </div>
          <div style="font-size:.92rem;color:rgba(255,255,255,.88);line-height:1.8;">
            {_final_story}
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════
    # SECTION 6 — Phân cụm khách hàng (Storytelling, not table)
    # ═══════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("""
    <div style="font-size:1.15rem;font-weight:900;color:#302B63;margin:6px 0 8px;">
      👥 AI phân cụm khách hàng — Không cá nhân hóa từng người
    </div>
    <div style="font-size:.85rem;color:#888;margin-bottom:16px;line-height:1.6;">
      AI gom cụm theo Wealth Genome pattern. Privacy-first: TCBS truyền thông theo nhóm, không target cá nhân.
    </div>
    """, unsafe_allow_html=True)

    _sc1, _sc2, _sc3 = st.columns(3)
    _seg_data = [
        ("seg-story-a", "🌟", "Dream Chaser", "38% users",
         "Nhóm này mơ về concert, iPhone, MacBook — những điều có địa chỉ cụ thể. "
         "Họ tiết kiệm tốt hơn khi nhìn thấy tiến độ và có deadline.",
         "Mỗi ngày 10.000đ cũng đưa bạn gần hơn tới giấc mơ.",
         "#FFB347"),
        ("seg-story-b", "✈️", "Travel Explorer", "29% users",
         "Nhóm này thu thập trải nghiệm, không phải đồ vật. Nhật Bản, Hàn Quốc, Châu Âu "
         "là những địa danh hay xuất hiện trong diary của họ.",
         "Trip đầu tiên không bắt đầu bằng visa — nó bắt đầu bằng 10.000đ.",
         "#4ECDC4"),
        ("seg-story-c", "📚", "Life Builder", "33% users",
         "Nhóm này đầu tư vào chính mình trước. Career milestone thường là trigger "
         "để họ tăng saving. Họ ready cho Quỹ TCC hơn 2 nhóm kia.",
         "Đầu tư cho tương lai cũng là một loại đầu tư.",
         "#7ED321"),
    ]
    for _col, (_css, _ico, _name_s, _pct, _desc, _msg, _clr) in zip([_sc1, _sc2, _sc3], _seg_data):
        # Highlight current user's segment
        _is_me = _genome["segment"].lower().replace(" ", "_") in _name_s.lower().replace(" ", "_")
        _border_extra = f"box-shadow:0 0 0 3px {_clr}80;" if _is_me else ""
        _col.markdown(f"""
        <div class="seg-story {_css}" style="{_border_extra}">
          <div style="font-size:1.4rem;margin-bottom:6px;">{_ico}</div>
          <div style="font-size:.95rem;font-weight:900;color:#302B63;margin-bottom:2px;">{_name_s}</div>
          <div style="font-size:.75rem;color:#888;margin-bottom:12px;">{_pct}
            {"&nbsp;<strong style='color:" + _clr + ";'>← " + (mem.get("name") or "bạn") + "</strong>" if _is_me else ""}
          </div>
          <div style="font-size:.83rem;color:#555;line-height:1.65;margin-bottom:14px;">{_desc}</div>
          <div style="background:rgba(0,0,0,.06);border-radius:10px;padding:10px 12px;">
            <div style="font-size:.72rem;font-weight:800;color:{_clr};margin-bottom:4px;">
              📢 THÔNG ĐIỆP
            </div>
            <div style="font-size:.83rem;color:#333;font-style:italic;line-height:1.6;">
              "{_msg}"
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════
    # SECTION 7 — Micro Saving → Quỹ TCC (journey, not product pitch)
    # ═══════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("""
    <div style="font-size:1.15rem;font-weight:900;color:#302B63;margin:6px 0 14px;">
      💰 Tiền lẻ → Chứng chỉ quỹ TCC → Cừu lớn
    </div>
    """, unsafe_allow_html=True)

    _ms_steps = [
        ("💸", "Tiền lẻ hôm nay",
         "10k · 20k · 50k · 100k",
         "Tiền cà phê. Tiền trà sữa. Tiền tiết kiệm được hôm nay."),
        ("🐑", "Cho Cừu ăn",
         "1 tap → Streak tăng",
         "Habit loop: streak, level, milestone. Không cần nghĩ nhiều."),
        ("🔄", "Tự động mua Chứng Chỉ Quỹ TCC",
         "TCBF → TCFF → TCEF theo risk",
         "Backend tự động. Khách hàng không cần thao tác thêm."),
        ("📈", "Tiền sinh lời nhẹ",
         "TCBF: ~6-7%/năm",
         "Không hứa hẹn. Chỉ tốt hơn để tiền ngân hàng. Đủ để thấy ý nghĩa."),
        ("🏆", "Cừu lớn · Level tăng",
         "Baby → Master (5 giai đoạn)",
         "Mỗi milestone là một celebration. Streak reward. Achievement unlock."),
        ("🎯", "Tiến gần giấc mơ",
         "Concert · MacBook · Nhật Bản",
         "Goal bar hiển thị % hoàn thành. Số thực, không phải lý thuyết."),
    ]

    _ms_html = ""
    for _i, (_ico, _title, _sub, _desc) in enumerate(_ms_steps):
        _ms_html += (
            f'<div style="display:flex;align-items:flex-start;gap:14px;padding:12px 0;'
            f'{"border-bottom:1px solid #f4f0ff;" if _i < len(_ms_steps)-1 else ""}">'
            f'<div style="width:36px;height:36px;border-radius:50%;flex-shrink:0;'
            f'background:linear-gradient(135deg,#7B5EA7,#C4607F);'
            f'display:flex;align-items:center;justify-content:center;font-size:1.1rem;">{_ico}</div>'
            f'<div style="flex:1;">'
            f'<div style="font-size:.92rem;font-weight:800;color:#302B63;">{_title}</div>'
            f'<div style="font-size:.75rem;color:#C4607F;font-weight:700;margin:1px 0 4px;">{_sub}</div>'
            f'<div style="font-size:.82rem;color:#666;line-height:1.5;">{_desc}</div>'
            f'</div></div>'
        )

    _ms1, _ms2 = st.columns([3, 2])
    with _ms1:
        st.markdown(
            f'<div class="ai-card">{_ms_html}</div>',
            unsafe_allow_html=True,
        )
    with _ms2:
        # Live progress on user's dreams
        _user_dreams = mem.get("dreams", [])
        if _user_dreams:
            st.markdown("""
            <div style="font-size:.78rem;font-weight:800;color:#7B5EA7;text-transform:uppercase;
                 letter-spacing:.07em;margin-bottom:10px;">
              🎯 Tiến độ mục tiêu của bạn
            </div>
            """, unsafe_allow_html=True)
            for _dr in _user_dreams[:3]:
                _pct2 = min(100, int(_dr.get("saved", 0) / _dr["amount"] * 100)) if _dr["amount"] else 0
                st.markdown(f"""
                <div style="background:#fff;border:1.5px solid #ede8ff;border-radius:14px;
                     padding:14px 16px;margin-bottom:8px;">
                  <div style="font-size:.88rem;font-weight:700;color:#302B63;margin-bottom:6px;">
                    {_dr['name']}
                  </div>
                  <div style="display:flex;justify-content:space-between;
                       font-size:.75rem;color:#888;margin-bottom:5px;">
                    <span>{fmt(_dr.get('saved', 0))}</span>
                    <span>mục tiêu: {fmt(_dr['amount'])}</span>
                  </div>
                  <div style="background:#f0f0f7;border-radius:8px;height:8px;overflow:hidden;">
                    <div style="width:{_pct2}%;height:100%;border-radius:8px;
                         background:linear-gradient(90deg,#7B5EA7,#C4607F);"></div>
                  </div>
                  <div style="font-size:.72rem;color:#C4607F;margin-top:4px;font-weight:700;">
                    {_pct2}% hoàn thành
                  </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(
                '<div style="color:#bbb;font-size:.88rem;padding:20px;text-align:center;">'
                'Chưa có mục tiêu. Chat với Cừu để tạo nhé!</div>',
                unsafe_allow_html=True,
            )

    # ═══════════════════════════════════════════════════════
    # CLOSING — CEO Summary
    # ═══════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0F0C29,#302B63,#24243E);
         border-radius:22px;padding:32px 28px;text-align:center;margin-top:8px;">
      <div style="font-size:2rem;margin-bottom:10px;">🐑</div>
      <div style="font-size:1.3rem;font-weight:900;color:#FFD700;margin-bottom:14px;">
        Đây không phải chatbot.
      </div>
      <div style="font-size:.97rem;color:rgba(255,255,255,.85);line-height:1.9;
           max-width:640px;margin:0 auto;">
        Đây là hệ thống AI 3 tầng:<br/>
        <span style="color:#A0C8FF;">Rule Engine</span> xử lý 90% habit loops →
        <span style="color:#FFB347;">Embedding Memory</span> hiểu từng khách hàng →
        <span style="color:#FF8080;">LLM</span> chỉ kích hoạt khi có insight mới.<br/><br/>
        Kết quả:
        <strong style="color:#FFD700;">Chi phí AI giảm 90%</strong> ·
        <strong style="color:#fff;">Khách hàng tích lũy mỗi ngày</strong> ·
        <strong style="color:#fff;">Micro Saving → Fund Investing tự nhiên.</strong>
      </div>
    </div>
    """, unsafe_allow_html=True)
