import streamlit as st


def render_study_plan(data, days_remaining):
    weighted_topics = data.get("weighted_topics", {})

    topics_list = []
    if isinstance(weighted_topics, dict):
        if "weighted_topics" in weighted_topics:
            topics_list = weighted_topics["weighted_topics"]
        elif "topics" in weighted_topics:
            topics_list = weighted_topics["topics"]
    elif isinstance(weighted_topics, list):
        topics_list = weighted_topics

    subject = data.get("subject", "default")

    # ── HEADER ─────────────────────────────────────────────
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            "<p style='font-family:Inter,sans-serif;font-size:11px;font-weight:600;"
            "letter-spacing:1.5px;text-transform:uppercase;color:#888;margin:0 0 4px 0;'>"
            "STUDY PLAN</p>"
            "<p style='font-family:Inter,sans-serif;font-size:13px;color:#666;margin:0;'>"
            "Day-by-day breakdown based on topic weights</p>",
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"<div style='text-align:right;'>"
            f"<span style='font-family:JetBrains Mono,monospace;font-size:40px;"
            f"font-weight:700;color:#faff69;letter-spacing:-1px;'>{days_remaining}</span>"
            f"<p style='font-family:Inter,sans-serif;font-size:11px;color:#666;"
            f"margin:0;letter-spacing:1px;text-transform:uppercase;'>days left</p>"
            f"</div>",
            unsafe_allow_html=True
        )

    st.markdown("<hr style='border-color:#2a2a2a;margin:20px 0 28px 0;'>",
                unsafe_allow_html=True)

    if not topics_list:
        st.markdown(
            "<div style='text-align:center;padding:60px 20px;color:#444;"
            "font-family:Inter,sans-serif;font-size:14px;'>"
            "No topics available. Re-run analysis to generate plan."
            "</div>",
            unsafe_allow_html=True
        )
        return

    # ── BUILD DAY PLAN ─────────────────────────────────────
    critical = [t for t in topics_list if t.get("weight", 0) >= 9]
    high = [t for t in topics_list if 7 <= t.get("weight", 0) < 9]
    medium = [t for t in topics_list if 5 <= t.get("weight", 0) < 7]

    day_plan = []
    if critical:
        day_plan.append({
            "day": 1, "label": "CRITICAL FOCUS",
            "topics": critical[:2],
            "color": "#ef4444", "hours": "4-6h", "revision": False
        })
    if high:
        day_plan.append({
            "day": 2, "label": "HIGH PRIORITY",
            "topics": high[:2],
            "color": "#f59e0b", "hours": "3-4h", "revision": False
        })
    if len(high) > 2:
        day_plan.append({
            "day": 3, "label": "HIGH PRIORITY",
            "topics": high[2:],
            "color": "#f59e0b", "hours": "3-4h", "revision": False
        })
    if medium and days_remaining > 3:
        day_plan.append({
            "day": 4, "label": "MEDIUM PRIORITY",
            "topics": medium[:3],
            "color": "#22c55e", "hours": "2-3h", "revision": False
        })
    if days_remaining >= 2:
        day_plan.append({
            "day": days_remaining, "label": "REVISION DAY",
            "topics": [],
            "color": "#faff69", "hours": "2-3h", "revision": True
        })

    # ── OVERALL PROGRESS ──────────────────────────────────
    if "study_progress" not in st.session_state:
        st.session_state.study_progress = {}

    if subject not in st.session_state.study_progress:
        st.session_state.study_progress[subject] = {}

    progress_data = st.session_state.study_progress[subject]

    total_topics = sum(len(d["topics"]) for d in day_plan if not d["revision"])
    completed_topics = sum(
        1 for k, v in progress_data.items()
        if v and k.startswith(subject)
    )

    if total_topics > 0:
        overall_pct = int((completed_topics / total_topics) * 100)
    else:
        overall_pct = 0

    st.markdown(
        f"<div style='background:#0f0f0f;border:1px solid #222;border-radius:10px;"
        f"padding:14px 18px;margin-bottom:24px;'>"
        f"<div style='display:flex;justify-content:space-between;align-items:center;"
        f"margin-bottom:8px;'>"
        f"<span style='font-family:JetBrains Mono,monospace;font-size:11px;"
        f"color:#888;letter-spacing:1px;'>OVERALL PROGRESS</span>"
        f"<span style='font-family:JetBrains Mono,monospace;font-size:13px;"
        f"color:#faff69;font-weight:600;'>{completed_topics}/{total_topics} · {overall_pct}%</span>"
        f"</div>"
        f"<div style='background:#1a1a1a;height:6px;border-radius:3px;overflow:hidden;'>"
        f"<div style='background:#faff69;height:100%;width:{overall_pct}%;"
        f"transition:width 0.3s;'></div>"
        f"</div>"
        f"</div>",
        unsafe_allow_html=True
    )

    # ── RENDER EACH DAY ───────────────────────────────────
    for entry in day_plan:
        day_num = entry["day"]
        label = entry["label"]
        color = entry["color"]
        hours = entry["hours"]
        topics = entry["topics"]
        is_revision = entry["revision"]

        # Day topics completed count
        day_completed = 0
        day_total = len(topics)
        for topic in topics:
            key = f"{subject}_day{day_num}_{topic.get('topic_name', topic.get('name', ''))}"
            if progress_data.get(key, False):
                day_completed += 1

        if day_total > 0:
            day_pct = int((day_completed / day_total) * 100)
        else:
            day_pct = 100 if is_revision else 0

        # Day header with expander
        text_color = "#0a0a0a" if color == "#faff69" else "#ffffff"

        expander_label = f"Day {day_num}  ·  {label}  ·  {hours}"
        if not is_revision:
            expander_label += f"  ·  {day_completed}/{day_total} done"

        with st.expander(expander_label, expanded=(day_num <= 2)):

            # Color bar on top
            st.markdown(
                f"<div style='height:3px;background:{color};border-radius:2px;"
                f"margin:0 0 16px 0;'></div>",
                unsafe_allow_html=True
            )

            if is_revision:
                st.markdown(
                    "<div style='background:#161616;border:1px solid #222;"
                    "border-radius:8px;padding:16px 20px;'>"
                    "<p style='font-family:Inter,sans-serif;font-size:13px;"
                    "color:#999;margin:0;line-height:1.7;'>"
                    "📚 No new topics today.<br>"
                    "Review all CRITICAL and HIGH priority topics.<br>"
                    "Go through flashcards and cheat sheet."
                    "</p>"
                    "</div>",
                    unsafe_allow_html=True
                )
            else:
                # Day progress bar
                st.markdown(
                    f"<div style='display:flex;justify-content:space-between;"
                    f"align-items:center;margin-bottom:10px;'>"
                    f"<span style='font-family:JetBrains Mono,monospace;font-size:10px;"
                    f"color:#666;letter-spacing:1px;'>DAY PROGRESS</span>"
                    f"<span style='font-family:JetBrains Mono,monospace;font-size:11px;"
                    f"color:{color};font-weight:600;'>{day_pct}%</span>"
                    f"</div>"
                    f"<div style='background:#1a1a1a;height:4px;border-radius:2px;"
                    f"overflow:hidden;margin-bottom:18px;'>"
                    f"<div style='background:{color};height:100%;width:{day_pct}%;'></div>"
                    f"</div>",
                    unsafe_allow_html=True
                )

                # Topic checklist
                for idx, topic in enumerate(topics):
                    name = topic.get("topic_name", topic.get("name", "Unknown"))
                    weight = topic.get("weight", 0)
                    years = topic.get("years_appeared", [])
                    typical_marks = topic.get("typical_marks", "")
                    unit = topic.get("unit", "")

                    key = f"{subject}_day{day_num}_{name}"
                    is_done = progress_data.get(key, False)

                    # Render topic card
                    year_str = " · ".join(map(str, years)) if years else ""
                    pyq_badge = (
                        f"<span style='font-family:JetBrains Mono,monospace;"
                        f"font-size:10px;color:#faff69;margin-left:10px;'>"
                        f"PYQ {year_str}</span>"
                        if year_str else ""
                    )

                    marks_badge = (
                        f"<span style='font-family:JetBrains Mono,monospace;"
                        f"font-size:10px;color:#666;margin-left:10px;'>"
                        f"{typical_marks}M</span>"
                        if typical_marks else ""
                    )

                    unit_badge = (
                        f"<span style='font-family:JetBrains Mono,monospace;"
                        f"font-size:10px;color:#666;margin-left:10px;'>"
                        f"{unit}</span>"
                        if unit else ""
                    )

                    opacity = "0.5" if is_done else "1"
                    line_through = "text-decoration:line-through;" if is_done else ""

                    topic_html = (
                        f"<div style='background:#111;border:1px solid #222;"
                        f"border-left:3px solid {color};border-radius:6px;"
                        f"padding:12px 16px;margin-bottom:8px;opacity:{opacity};'>"
                        f"<div style='display:flex;justify-content:space-between;"
                        f"align-items:center;'>"
                        f"<div style='{line_through}'>"
                        f"<span style='font-family:Inter,sans-serif;font-size:14px;"
                        f"font-weight:500;color:#e6e6e6;'>{name}</span>"
                        f"{marks_badge}"
                        f"{unit_badge}"
                        f"{pyq_badge}"
                        f"</div>"
                        f"<span style='font-family:JetBrains Mono,monospace;"
                        f"font-size:12px;color:{color};font-weight:600;'>"
                        f"{weight:.1f}</span>"
                        f"</div>"
                        f"</div>"
                    )

                    st.markdown(topic_html, unsafe_allow_html=True)

                    # Checkbox
                    checked = st.checkbox(
                        f"Mark complete",
                        value=is_done,
                        key=f"check_{key}"
                    )

                    if checked != is_done:
                        progress_data[key] = checked
                        st.rerun()

                # Mark day complete button
                if day_completed < day_total:
                    if st.button(
                        f"✓ Mark Day {day_num} Complete",
                        key=f"day_complete_{day_num}",
                        use_container_width=True
                    ):
                        for topic in topics:
                            name = topic.get("topic_name", topic.get("name", "Unknown"))
                            key = f"{subject}_day{day_num}_{name}"
                            progress_data[key] = True
                        st.rerun()
                else:
                    st.markdown(
                        f"<div style='background:rgba(34,197,94,0.08);"
                        f"border:1px solid rgba(34,197,94,0.2);border-radius:6px;"
                        f"padding:10px 16px;text-align:center;margin-top:8px;'>"
                        f"<span style='font-family:Inter,sans-serif;font-size:12px;"
                        f"color:#22c55e;font-weight:600;'>"
                        f"✓ DAY {day_num} COMPLETED"
                        f"</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )