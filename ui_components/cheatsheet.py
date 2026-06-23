import streamlit as st
import re
def parse_cheatsheet(cheatsheet_text):
    """
    Parses AI cheatsheet markdown into:
    {
        "Topic Name": {
            "weight": "6.9",
            "points": [
                {"label": "Key Definition", "text": "..."},
                {"label": "Memory Hook",   "text": "..."}
            ]
        }
    }
    """
    topics = {}

    if not cheatsheet_text:
        return topics

    # Clean code fences
    cheatsheet_text = re.sub(r"```.*?\n", "", cheatsheet_text)
    cheatsheet_text = cheatsheet_text.replace("```", "").strip()

    # Split by ### headings
    blocks = re.split(r'\n(?=### )', cheatsheet_text)

    for block in blocks:
        block = block.strip()
        if not block.startswith("###"):
            continue

        # Match: ### Topic Name (Weight: 6.9)
        header_match = re.match(
            r'###\s+(.+?)\s*\(Weight:\s*([\d.]+)\)',
            block
        )

        if header_match:
            topic_name = header_match.group(1).strip()
            weight = header_match.group(2).strip()
        else:
            simple = re.match(r'###\s+(.+)', block)
            if not simple:
                continue
            topic_name = simple.group(1).strip()
            weight = None

        # Remove "* PYQ TOPIC *" markers
        topic_name = re.sub(r'\*\s*PYQ TOPIC\s*\*', '', topic_name).strip()

        # Extract bullet points
        points = []
        for line in block.split("\n"):
            line = line.strip()
            if not line.startswith("-"):
                continue

            clean = re.sub(r'^-\s*', '', line).strip()

            # Try to extract label: "**Key Definition**: text"
            label_match = re.match(r'\*\*(.+?)\*\*[:\-\s]*(.*)', clean)
            if label_match:
                label = label_match.group(1).strip()
                text = label_match.group(2).strip()
            else:
                label = ""
                text = clean

            if text:
                points.append({"label": label, "text": text})

        if points:
            topics[topic_name] = {
                "weight": weight,
                "points": points
            }

    return topics


# ─────────────────────────────────────────────────────────────
# COLOR HELPERS
# ─────────────────────────────────────────────────────────────

def get_band_color(weight):
    try:
        w = float(weight)
        if w >= 9:
            return "#ef4444"
        elif w >= 7:
            return "#f59e0b"
        elif w >= 5:
            return "#22c55e"
        else:
            return "#666666"
    except:
        return "#666666"


def get_band_label(weight):
    try:
        w = float(weight)
        if w >= 9:
            return "CRITICAL"
        elif w >= 7:
            return "HIGH"
        elif w >= 5:
            return "MEDIUM"
        else:
            return "LOW"
    except:
        return "—"


# ─────────────────────────────────────────────────────────────
# MAIN RENDER
# ─────────────────────────────────────────────────────────────

def render_cheatsheet(data, weak_topics):
    weighted_topics = data.get("weighted_topics", {})
    cheatsheet_text = data.get("cheatsheet", "")

    topics_list = []
    if isinstance(weighted_topics, dict):
        if "weighted_topics" in weighted_topics:
            topics_list = weighted_topics["weighted_topics"]
        elif "topics" in weighted_topics:
            topics_list = weighted_topics["topics"]
    elif isinstance(weighted_topics, list):
        topics_list = weighted_topics

    # ── HEADER ───────────────────────────────────────────
    st.markdown(
        "<p style='font-family:Inter,sans-serif;font-size:11px;font-weight:600;"
        "letter-spacing:1.5px;text-transform:uppercase;color:#faff69;"
        "margin:0 0 4px 0;'>CHEAT SHEET</p>"
        "<p style='font-family:Inter,sans-serif;font-size:13px;color:#666;"
        "margin:0 0 24px 0;'>"
        "Ultra-compact. Keywords and memory hooks only. Read 30 mins before exam."
        "</p>",
        unsafe_allow_html=True
    )

    # ── PARSE CHEATSHEET ─────────────────────────────────
    parsed = parse_cheatsheet(cheatsheet_text)

    # ── SEARCH BAR ───────────────────────────────────────
    search_query = st.text_input(
        "Search topics",
        placeholder="🔍  Search topic name or keyword...",
        label_visibility="collapsed",
        key="cheat_search"
    )

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # ── STATS ROW ────────────────────────────────────────
    critical_count = sum(1 for t in topics_list if t.get("weight", 0) >= 9)
    high_count = sum(1 for t in topics_list if 7 <= t.get("weight", 0) < 9)
    medium_count = sum(1 for t in topics_list if 5 <= t.get("weight", 0) < 7)
    weak_count = len(weak_topics) if weak_topics else 0

    stats_html = (
        "<div style='display:flex;gap:8px;margin-bottom:24px;flex-wrap:wrap;'>"
        f"<div style='flex:1;min-width:120px;background:#0f0f0f;border:1px solid #222;"
        f"border-top:2px solid #ef4444;border-radius:6px;padding:10px 14px;'>"
        f"<p style='font-family:JetBrains Mono,monospace;font-size:10px;color:#666;"
        f"margin:0;letter-spacing:1px;'>CRITICAL</p>"
        f"<p style='font-family:Inter,sans-serif;font-size:20px;font-weight:700;"
        f"color:#ef4444;margin:2px 0 0 0;'>{critical_count}</p>"
        f"</div>"
        f"<div style='flex:1;min-width:120px;background:#0f0f0f;border:1px solid #222;"
        f"border-top:2px solid #f59e0b;border-radius:6px;padding:10px 14px;'>"
        f"<p style='font-family:JetBrains Mono,monospace;font-size:10px;color:#666;"
        f"margin:0;letter-spacing:1px;'>HIGH</p>"
        f"<p style='font-family:Inter,sans-serif;font-size:20px;font-weight:700;"
        f"color:#f59e0b;margin:2px 0 0 0;'>{high_count}</p>"
        f"</div>"
        f"<div style='flex:1;min-width:120px;background:#0f0f0f;border:1px solid #222;"
        f"border-top:2px solid #22c55e;border-radius:6px;padding:10px 14px;'>"
        f"<p style='font-family:JetBrains Mono,monospace;font-size:10px;color:#666;"
        f"margin:0;letter-spacing:1px;'>MEDIUM</p>"
        f"<p style='font-family:Inter,sans-serif;font-size:20px;font-weight:700;"
        f"color:#22c55e;margin:2px 0 0 0;'>{medium_count}</p>"
        f"</div>"
        f"<div style='flex:1;min-width:120px;background:#0f0f0f;border:1px solid #222;"
        f"border-top:2px solid #faff69;border-radius:6px;padding:10px 14px;'>"
        f"<p style='font-family:JetBrains Mono,monospace;font-size:10px;color:#666;"
        f"margin:0;letter-spacing:1px;'>WEAK</p>"
        f"<p style='font-family:Inter,sans-serif;font-size:20px;font-weight:700;"
        f"color:#faff69;margin:2px 0 0 0;'>{weak_count}</p>"
        f"</div>"
        f"</div>"
    )
    st.markdown(stats_html, unsafe_allow_html=True)

    # ── WEAK TOPICS PINNED AT TOP ────────────────────────
    if weak_topics:
        weak_objs = [
            t for t in topics_list
            if t.get("topic_name") in weak_topics or t.get("name") in weak_topics
        ]

        if weak_objs:
            st.markdown(
                "<p style='font-family:Inter,sans-serif;font-size:10px;font-weight:600;"
                "letter-spacing:2px;text-transform:uppercase;color:#faff69;"
                "margin:0 0 12px 0;'>⚠ WEAK TOPICS — EXTRA FOCUS</p>",
                unsafe_allow_html=True
            )

            for idx, topic in enumerate(weak_objs):
                name = topic.get("topic_name", topic.get("name", "Unknown"))
                weight = topic.get("weight", 0)
                render_topic_accordion(
                    name, weight, parsed.get(name), accent="#faff69",
                    is_weak=True, search_query=search_query, idx=f"w{idx}"
                )

            st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

    # ── GROUP TOPICS BY BAND ────────────────────────────
    critical = [t for t in topics_list if t.get("weight", 0) >= 9]
    high = [t for t in topics_list if 7 <= t.get("weight", 0) < 9]
    medium = [t for t in topics_list if 5 <= t.get("weight", 0) < 7]

    # ── RENDER SECTIONS ─────────────────────────────────
    if critical:
        render_section_header("CRITICAL — STUDY FIRST", "#ef4444")
        for idx, topic in enumerate(critical):
            name = topic.get("topic_name", topic.get("name", "Unknown"))
            weight = topic.get("weight", 0)
            render_topic_accordion(
                name, weight, parsed.get(name),
                accent="#ef4444", search_query=search_query, idx=f"c{idx}"
            )
        st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

    if high:
        render_section_header("HIGH PRIORITY", "#f59e0b")
        for topic in high:
            name = topic.get("topic_name", topic.get("name", "Unknown"))
            weight = topic.get("weight", 0)
            render_topic_accordion(
                name, weight, parsed.get(name),
                accent="#f59e0b", search_query=search_query
            )
        st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

    if medium:
        render_section_header("MEDIUM — IF TIME PERMITS", "#22c55e")
        for idx, topic in enumerate(medium):
            name = topic.get("topic_name", topic.get("name", "Unknown"))
            weight = topic.get("weight", 0)
            render_topic_accordion(
                name, weight, parsed.get(name),
                accent="#22c55e", search_query=search_query, idx=f"m{idx}"
            )

def render_section_header(label, color):
    st.markdown(
        f"<p style='font-family:Inter,sans-serif;font-size:10px;font-weight:600;"
        f"letter-spacing:2px;text-transform:uppercase;color:{color};"
        f"margin:0 0 12px 0;'>{label}</p>",
        unsafe_allow_html=True
    )

def render_topic_accordion(name, weight, parsed_topic, accent, is_weak=False, search_query="", idx=0):
    # Filter by search
    if search_query:
        q = search_query.lower().strip()
        match = q in name.lower()
        if parsed_topic:
            for p in parsed_topic["points"]:
                if q in p["text"].lower() or q in p["label"].lower():
                    match = True
                    break
        if not match:
            return

    # Expander label
    weak_marker = "⚠ " if is_weak else ""
    expander_label = f"{weak_marker}{name}  ·  weight {weight:.1f}"

    with st.expander(expander_label, expanded=is_weak):
        # Color accent bar
        st.markdown(
            f"<div style='height:2px;background:{accent};border-radius:1px;"
            f"margin-bottom:12px;'></div>",
            unsafe_allow_html=True
        )

        if not parsed_topic or not parsed_topic["points"]:
            st.markdown(
                "<p style='font-family:Inter,sans-serif;font-size:13px;color:#555;"
                "margin:0;font-style:italic;'>"
                "No detailed cheat content available. "
                "Review your notes for this topic."
                "</p>",
                unsafe_allow_html=True
            )
            return

        # Render each point
        for point in parsed_topic["points"]:
            label = point["label"]
            text = point["text"]

            label_html = ""
            if label:
                label_color = "#faff69"
                if "memory" in label.lower() or "hook" in label.lower():
                    label_color = "#22c55e"
                elif "trick" in label.lower() or "exam" in label.lower():
                    label_color = "#f59e0b"
                elif "definition" in label.lower() or "key" in label.lower():
                    label_color = "#3b82f6"

                label_html = (
                    f"<span style='font-family:JetBrains Mono,monospace;"
                    f"font-size:10px;color:{label_color};font-weight:600;"
                    f"letter-spacing:1px;text-transform:uppercase;"
                    f"margin-right:8px;'>{label}</span>"
                )

            point_html = (
                f"<div style='background:#0f0f0f;border:1px solid #1e1e1e;"
                f"border-radius:6px;padding:10px 14px;margin-bottom:6px;'>"
                f"{label_html}"
                f"<span style='font-family:Inter,sans-serif;font-size:13px;"
                f"color:#cccccc;line-height:1.6;'>{text}</span>"
                f"</div>"
            )

            st.markdown(point_html, unsafe_allow_html=True)

        # Copy-friendly view toggle
        if st.checkbox(f"Show as plain text", key=f"plain_{idx}_{name}"):
            plain_text = f"=== {name} (weight {weight:.1f}) ===\n\n"
            for point in parsed_topic["points"]:
                if point["label"]:
                    plain_text += f"[{point['label']}] {point['text']}\n"
                else:
                    plain_text += f"- {point['text']}\n"

            st.code(plain_text, language=None)