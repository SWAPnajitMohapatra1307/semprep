import streamlit as st
import re
import html


# ─────────────────────────────────────────────────────────────
# CLEAN + PARSE MARKDOWN
# ─────────────────────────────────────────────────────────────

def parse_question_bank(qb_text):
    topics = []

    topic_blocks = re.split(r'\n(?=### )', qb_text.strip())

    for block in topic_blocks:
        if not block.strip():
            continue

        header_match = re.search(
            r'###\s+(.+?)\s*\(Weight:\s*([\d.]+)\s*\|\s*Band:\s*(\w+)\)',
            block
        )

        if not header_match:
            continue

        topic_name = header_match.group(1).strip()
        weight = header_match.group(2).strip()
        band = header_match.group(3).strip()

        questions = []

        # Split by question marker
        q_sections = re.split(r'\*\*Q', block)[1:]

        for section in q_sections:
            # Re-add Q to beginning
            section = "**Q" + section

            header_match = re.search(
                r'\*\*Q(\d+)\s*\((\d+)\s*marks?\):\*\*\s*(.*)',
                section
            )

            if not header_match:
                continue

            q_number = header_match.group(1)
            q_marks = header_match.group(2)

            # Extract full question text (until Answer)
            q_text_match = re.search(
                r'\*\*Q\d+\s*\(\d+\s*marks?\):\*\*\s*(.*?)\n\*\*Answer',
                section,
                re.DOTALL
            )

            if q_text_match:
                q_text = q_text_match.group(1).strip()
            else:
                q_text = header_match.group(3).strip()
            q_text = re.sub(r'<.*?>', '', q_text)

            # Extract answer bullets
            answer_match = re.search(
                r'\*\*Answer[^:]*:\*\*\s*\n(.*)',
                section,
                re.DOTALL
            )

            answer_points = []

            if answer_match:
                answer_block = answer_match.group(1)
                lines = answer_block.split("\n")

                for line in lines:
                    clean = re.sub(r'^[-•]\s*', '', line).strip()
                    clean = re.sub(r'^Point\s+\d+:\s*', '', clean)
                    if clean and not clean.startswith("**Q"):
                        answer_points.append(clean)

            questions.append({
                "number": q_number,
                "marks": q_marks,
                "question": q_text,
                "answer": answer_points
            })

        if questions:
            topics.append({
                "topic": topic_name,
                "weight": weight,
                "band": band,
                "questions": questions
            })

    return topics


# ─────────────────────────────────────────────────────────────
# COLOR HELPERS
# ─────────────────────────────────────────────────────────────

def get_band_color(band):
    band = band.upper()
    if band == "CRITICAL":
        return "#ef4444"
    elif band == "HIGH":
        return "#f59e0b"
    elif band == "MEDIUM":
        return "#22c55e"
    else:
        return "#888888"


def get_marks_color(marks):
    try:
        m = int(marks)
        if m >= 10:
            return "#ef4444", "rgba(239,68,68,0.08)", "rgba(239,68,68,0.2)"
        elif m >= 5:
            return "#f59e0b", "rgba(245,158,11,0.08)", "rgba(245,158,11,0.2)"
        else:
            return "#3b82f6", "rgba(59,130,246,0.08)", "rgba(59,130,246,0.2)"
    except:
        return "#888", "rgba(136,136,136,0.08)", "rgba(136,136,136,0.2)"


# ─────────────────────────────────────────────────────────────
# MAIN RENDER FUNCTION
# ─────────────────────────────────────────────────────────────

def render_question_bank(data):
    has_pyqs = data.get("has_pyqs", False)
    qb_text = data.get("question_bank", "")

    # ✅ REMOVE accidental markdown code fences
    if qb_text:
        qb_text = re.sub(r"```.*?\n", "", qb_text)
        qb_text = qb_text.replace("```", "")
        qb_text = qb_text.strip()

    # ── No PYQ warning ──────────────────────────────────────
    if not has_pyqs:
        st.markdown("""
        <div style='background:rgba(245,158,11,0.08);
        border:1px solid rgba(245,158,11,0.2);
        border-radius:8px;padding:10px 16px;margin-bottom:24px;'>
        <span style='color:#f59e0b;font-size:12px;font-weight:500;
        font-family:Inter,sans-serif;'>
        ⚠ No PYQ files detected — questions generated from notes only.
        Year badges will not appear.
        </span></div>
        """, unsafe_allow_html=True)

    if not qb_text:
        st.markdown("""
        <div style='text-align:center;padding:60px 20px;color:#444;
        font-family:Inter,sans-serif;font-size:14px;'>
        No question bank available.
        </div>
        """, unsafe_allow_html=True)
        return

    parsed_topics = parse_question_bank(qb_text)

    if not parsed_topics:
        st.markdown("""
        <div style='text-align:center;padding:60px 20px;color:#444;
        font-family:Inter,sans-serif;font-size:14px;'>
        Question format could not be parsed.<br>
        Please re-run analysis.
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Topic Selector ──────────────────────────────────────
    topic_names = [t["topic"] for t in parsed_topics]

    st.markdown("""
    <p style='font-family:Inter,sans-serif;font-size:11px;
    font-weight:600;letter-spacing:1.5px;text-transform:uppercase;
    color:#888;margin:0 0 8px 0;'>
    SELECT TOPIC
    </p>
    """, unsafe_allow_html=True)

    selected_name = st.selectbox(
        label="topic_select",
        options=topic_names,
        label_visibility="collapsed"
    )

    selected = next(t for t in parsed_topics if t["topic"] == selected_name)

    band_color = get_band_color(selected["band"])

    # ── Topic Header ────────────────────────────────────────
    st.markdown(f"""
    <div style='border-bottom:1px solid #2a2a2a;padding-bottom:16px;
    margin:20px 0 28px 0;'>
        <h3 style='font-family:Inter,sans-serif;font-size:22px;
        font-weight:700;color:#fff;margin:0 0 10px 0;'>
        {selected["topic"]}
        </h3>
        <span style='color:{band_color};font-size:12px;
        font-weight:600;text-transform:uppercase;'>
        {selected["band"]}
        </span>
        <span style='color:#555;margin-left:10px;
        font-family:JetBrains Mono,monospace;'>
        weight = {selected["weight"]}
        </span>
    </div>
    """, unsafe_allow_html=True)

        # ── Questions ─────────────────────────────────────────────────────────────
    for q in selected["questions"]:
        marks_text_color, marks_bg, marks_border = get_marks_color(q["marks"])

        # 1. QUESTION CARD
        card_html = (
            f"<div style='border:1px solid #2a2a2a;border-radius:10px;margin-bottom:8px;overflow:hidden;'>"
            f"<div style='background:#141414;padding:10px 18px;border-bottom:1px solid #2a2a2a;display:flex;align-items:center;gap:10px;'>"
            f"<span style='font-family:JetBrains Mono,monospace;font-size:11px;color:#555;'>Q{q['number']}</span>"
            f"<span style='background:{marks_bg};color:{marks_text_color};border:1px solid {marks_border};font-size:11px;font-weight:600;padding:2px 8px;border-radius:4px;font-family:Inter,sans-serif;'>{q['marks']} marks</span>"
            f"</div>"
            f"<div style='padding:16px 18px;'>"
            f"<p style='font-family:Inter,sans-serif;font-size:15px;font-weight:500;color:#e6e6e6;margin:0;line-height:1.6;'>{q['question']}</p>"
            f"</div>"
            f"</div>"
        )
        st.markdown(card_html, unsafe_allow_html=True)

        # 2. CHECKBOX (this defines show_answer)
        show_answer = st.checkbox(
            "Show answer",
            key=f"ans_{selected_name}_{q['number']}"
        )

        # 3. ANSWER BLOCK
        if show_answer:
            if q["answer"]:
                bullets_html = "".join(
                    f"<li style='margin-bottom:6px;'>{point}</li>"
                    for point in q["answer"]
                )

                answer_html = (
                    f"<div style='background:#0a140a;border-left:2px solid #22c55e;padding:14px 18px;margin-bottom:20px;border-radius:0 0 10px 10px;margin-top:-2px;'>"
                    f"<p style='font-family:JetBrains Mono,monospace;font-size:11px;color:#22c55e;letter-spacing:1px;margin:0 0 12px 0;'>// ANSWER KEYWORDS</p>"
                    f"<ul style='font-family:Inter,sans-serif;color:#cccccc;font-size:14px;margin:0;padding-left:18px;line-height:1.9;'>"
                    f"{bullets_html}"
                    f"</ul>"
                    f"</div>"
                )

                st.markdown(answer_html, unsafe_allow_html=True)

            else:
                st.markdown(
                    "<div style='background:#0a140a;border-left:2px solid #444;padding:14px 18px;margin-bottom:20px;border-radius:0 0 10px 10px;margin-top:-2px;'>"
                    "<p style='font-family:JetBrains Mono,monospace;font-size:11px;color:#555;margin:0;'>// No answer data available</p>"
                    "</div>",
                    unsafe_allow_html=True
                )

        else:
            st.markdown(
                "<div style='margin-bottom:12px;'></div>",
                unsafe_allow_html=True
            )