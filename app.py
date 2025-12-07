import streamlit as st
import pyperclip
from summarizer import summarize_text
from database import init_db, save_summary, get_all_summaries, delete_summary
from evaluation import evaluate_summary

# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------
st.set_page_config(page_title="Thai Summarizer", page_icon="🧠", layout="wide")
init_db()

# ------------------------------------------------------------
# THEME SESSION
# ------------------------------------------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "🌞 Light"

# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------
theme = st.sidebar.radio(
    "ธีม", ["🌞 Light", "🌙 Dark"],
    index=0 if st.session_state.theme == "🌞 Light" else 1
)
st.session_state.theme = theme

menu = st.sidebar.radio(
    "เมนู",
    ["สรุปข้อความ", "ดูประวัติ", "ประเมินโมเดล"]
)

# ------------------------------------------------------------
# THEME CSS
# ------------------------------------------------------------
def set_theme(theme):
    if theme == "🌙 Dark":
        bg = "#1A1A1A"
        text_color = "#FFFFFF"
        card_bg = "rgba(30,30,30,0.95)"
        sidebar_bg = "#000000"
        sidebar_text = "#FFFFFF"
        input_bg = "#333333"
    else:
        bg = "#D8C3A5"
        text_color = "#0d47a1"
        card_bg = "rgba(255,255,255,0.95)"
        sidebar_bg = "#8B6D5C"
        sidebar_text = "#000000"
        input_bg = "#FFFFFF"

    st.markdown(f"""
    <style>

    .stApp {{
        background-color: {bg};
        color: {text_color};
    }}

    /* ปรับทุกตัวหนังสือ */
    * {{
        color: {text_color} !important;
    }}

    /* การ์ด */
    .card {{
        background-color: {card_bg};
        padding: 20px;
        border-radius: 12px;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg};
    }}

    section[data-testid="stSidebar"] * {{
        color: {sidebar_text} !important;
    }}

    /* text_area, input ให้เป็นพื้นเข้มใน Dark */
    textarea, input, .stTextInput input {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
        border-radius: 6px;
        padding: 8px;
    }}

    /* ปุ่ม */
    .stButton>button {{
        background-color: #444 !important;
        color: #fff !important;
        border-radius: 8px;
        font-weight: bold;
        transition: 0.2s;
    }}
    .stButton>button:hover {{
        background-color: #777 !important;
        color: white !important;
    }}

    </style>
    """, unsafe_allow_html=True)

set_theme(st.session_state.theme)

# ------------------------------------------------------------
# MAIN TITLE
# ------------------------------------------------------------
st.title("🧠 Thai Text Summarization System")
st.subheader("✨ ระบบสรุปข้อความภาษาไทยอัตโนมัติ ✨")

# ------------------------------------------------------------
# 1) สรุปข้อความ
# ------------------------------------------------------------
if menu == "สรุปข้อความ":
    st.markdown("### 📝 ป้อนข้อความที่ต้องการสรุป")

    if "temp_text" not in st.session_state:
        st.session_state.temp_text = ""

    text_input = st.text_area("ข้อความ:", height=200, value=st.session_state.temp_text)

    if st.button("🧹 ล้างข้อความ"):
        st.session_state.temp_text = ""
        st.rerun()

    if st.button("🚀 สรุปข้อความ"):
        if text_input.strip():
            st.session_state.temp_text = text_input

            with st.spinner("⏳ กำลังสรุป..."):
                summary = summarize_text(text_input)
                save_summary(text_input, summary)

            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.success("✨ สรุปสำเร็จ!")

            st.markdown("### 📄 ผลลัพธ์:")
            st.write(summary)

            if st.button("📋 คัดลอกผลสรุป"):
                pyperclip.copy(summary)
                st.toast("คัดลอกแล้ว ✔")

            st.markdown("</div>", unsafe_allow_html=True)

        else:
            st.warning("⚠️ กรุณาป้อนข้อความก่อน")

# ------------------------------------------------------------
# 2) ดูประวัติ
# ------------------------------------------------------------
elif menu == "ดูประวัติ":

    st.subheader("📜 ประวัติการสรุปข้อความ")

    data = get_all_summaries()

    if not data:
        st.info("ยังไม่มีข้อมูล")
    else:
        data = data[::-1]

        for i, (record_id, original, summary, created_at) in enumerate(data):

            ori_lines = original.split("\n")
            sum_lines = summary.split("\n")

            if f"ori_expand_{i}" not in st.session_state:
                st.session_state[f"ori_expand_{i}"] = False
            if f"sum_expand_{i}" not in st.session_state:
                st.session_state[f"sum_expand_{i}"] = False

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown(f"### 🕒 วันที่: {created_at}")

            # -------- ORIGINAL TEXT ----------
            st.markdown("#### 📝 ข้อความต้นฉบับ:")
            if len(ori_lines) > 5:
                if st.session_state[f"ori_expand_{i}"]:
                    st.write(original)
                else:
                    st.write("\n".join(ori_lines[:5]) + " ...")

                if st.session_state[f"ori_expand_{i}"]:
                    if st.button("🔼 ซ่อน", key=f"hide_ori_{i}"):
                        st.session_state[f"ori_expand_{i}"] = False
                else:
                    if st.button("🔽 ดูเพิ่มเติม", key=f"show_ori_{i}"):
                        st.session_state[f"ori_expand_{i}"] = True
            else:
                st.write(original)

            # -------- SUMMARY TEXT ----------
            st.markdown("#### 📄 ผลสรุป:")
            if len(sum_lines) > 5:
                if st.session_state[f"sum_expand_{i}"]:
                    st.write(summary)
                else:
                    st.write("\n".join(sum_lines[:5]) + " ...")

                if st.session_state[f"sum_expand_{i}"]:
                    if st.button("🔼 ซ่อนสรุป", key=f"hide_sum_{i}"):
                        st.session_state[f"sum_expand_{i}"] = False
                else:
                    if st.button("🔽 ดูเพิ่มเติมสรุป", key=f"show_sum_{i}"):
                        st.session_state[f"sum_expand_{i}"] = True
            else:
                st.write(summary)

            # -------- ACTION BUTTONS ----------
            col1, col2 = st.columns(2)

            with col1:
                if st.button("📋 คัดลอก", key=f"copy_{i}"):
                    pyperclip.copy(summary)
                    st.toast("คัดลอกแล้ว ✔")

            with col2:
                if st.button("🗑 ลบ", key=f"delete_{i}"):
                    delete_summary(record_id)
                    st.success("ลบแล้ว")
                    st.rerun()

            st.markdown("</div><br>", unsafe_allow_html=True)

# ------------------------------------------------------------
# 3) ประเมินโมเดล
# ------------------------------------------------------------
elif menu == "ประเมินโมเดล":
    st.subheader("📈 ประเมินคุณภาพโมเดล")

    ref = st.text_area("สรุปจริง (Reference)")
    cand = st.text_area("ผลลัพธ์โมเดล (Candidate)")

    if st.button("📊 ประเมิน"):
        if ref.strip() and cand.strip():
            scores = evaluate_summary(ref, cand)
            st.write(scores)
        else:
            st.warning("⚠️ กรุณากรอกให้ครบ")
