# ── THÊM VÀO ĐẦU FILE: User Knowledge Vault ──────────
import json
import hashlib
from collections import defaultdict

# Trong production: thay bằng Supabase / Redis / SQLite
# Demo: dùng st.session_state với key persistent (hoặc file JSON)

def get_user_vault(user_id: str = "default") -> dict:
    """
    Obsidian Vault của user — lưu trữ liên session.
    Cấu trúc giống Obsidian: mỗi entry là một 'note' có backlinks.
    """
    vault_key = f"vault_{user_id}"
    if vault_key not in st.session_state:
        st.session_state[vault_key] = {
            "user_id": user_id,
            # ── JOURNAL NODES (Obsidian Daily Notes) ──
            "journal_entries": [],          # [{date, content, emotion, tags, linked_goals}]
            
            # ── EMOTION TIMELINE (Deep Research input) ──
            "emotion_timeline": [],         # [{date, label, intensity, trigger_keywords}]
            
            # ── GOAL GRAPH (Obsidian backlinks) ──
            "goal_graph": {},               # {"mua_nha": {"mentions":3, "first_mention":"2024-01-01"}}
            
            # ── PRODUCT INTEREST GRAPH ──
            "product_affinity": defaultdict(int),  # {"ipower": 5, "ifund": 3}
            
            # ── BEHAVIORAL SIGNALS (Deep Research) ──
            "visit_streak": 0,
            "last_visit": None,
            "total_sessions": 0,
            "avg_session_messages": 0,
            
            # ── DERIVED INSIGHTS (auto-computed) ──
            "risk_profile": None,           # conservative / moderate / aggressive
            "segment": None,               # A / B / C (xem bên dưới)
            "dominant_emotion_pattern": None,
            "financial_wellness_score": 50,
        }
    return st.session_state[vault_key]


def save_to_vault(text: str, emotion: dict, knowledge: dict):
    """
    Mỗi lần user chat = ghi vào Vault như Obsidian ghi note.
    Tự động tag, link với goals và products.
    """
    vault = get_user_vault()
    today = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now().isoformat()
    
    # 1. Ghi emotion timeline
    vault["emotion_timeline"].append({
        "timestamp": now,
        "label": emotion["label"],
        "intensity": emotion["intensity"],
        "trigger": norm(text)[:100]  # keyword snapshot
    })
    
    # 2. Cập nhật goal graph (Obsidian backlinks)
    if knowledge.get("goal"):
        goal_name = knowledge["goal"][0]
        if goal_name not in vault["goal_graph"]:
            vault["goal_graph"][goal_name] = {
                "mentions": 0, 
                "first_mention": today,
                "linked_emotions": []
            }
        vault["goal_graph"][goal_name]["mentions"] += 1
        vault["goal_graph"][goal_name]["linked_emotions"].append(emotion["label"])
    
    # 3. Cập nhật product affinity
    for product in knowledge.get("products", []):
        vault["product_affinity"][product] += 1
    
    # 4. Cập nhật visit streak
    if vault["last_visit"] != today:
        if vault["last_visit"] == (datetime.now() - __import__('timedelta', fromtimestamp=1)(days=1)).strftime("%Y-%m-%d"):
            vault["visit_streak"] += 1
        else:
            vault["visit_streak"] = 1
        vault["last_visit"] = today
    
    # 5. Auto-compute segment (Deep Research engine)
    vault["segment"] = compute_segment(vault)
    vault["risk_profile"] = compute_risk_profile(vault)
