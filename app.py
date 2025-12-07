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
    ["สรุปข้อความ", "ดูประวัติ", "ประเมินโมเดล", "ข้อมูลโมเดล 🧠"]
)

# ------------------------------------------------------------
# THEME CSS
# ------------------------------------------------------------
def set_theme(theme):
    if theme == "🌙 Dark":
        bg = "#2C2C2C"
        text_color = "#FFFFFF"
        card_bg = "rgba(50,50,50,0.9)"
        sidebar_bg = "#1B1B1B"
        sidebar_text = "#FFFFFF"
    else:
        bg = "#D8C3A5"
        text_color = "#0d47a1"
        card_bg = "rgba(255,255,255,0.9)"
        sidebar_bg = "#8B6D5C"
        sidebar_text = "#000000"

    st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg}; color: {text_color}; }}

    /* การ์ด UI */
    .card {{
        background-color: {card_bg};
        padding: 20px; border-radius: 12px;
        margin: 15px 0; color: {text_color};
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg};
        color: {sidebar_text};
    }}
    section[data-testid="stSidebar"] * {{
        color: {sidebar_text};
    }}

    /* Label ของ text_area, text_input */
    label, .stTextArea label, .stTextInput label {{
        color: {text_color} !important;
    }}

    </style>
    """, unsafe_allow_html=True)

set_theme(st.session_state.theme)

# ------------------------------------------------------------
# MAIN TITLE
# ------------------------------------------------------------
st.title("🧠 Thai Text Summarization System")
st.subheader("✨ ระบบสรุปใจความสำคัญภาษาไทยอัตโนมัติ ✨")

# ------------------------------------------------------------
# 1) SUMMARIZATION PAGE
# ------------------------------------------------------------
if menu == "สรุปข้อความ":
    st.markdown("### 📝 ป้อนข้อความที่ต้องการให้ระบบสรุป")

    if "temp_text" not in st.session_state:
        st.session_state.temp_text = ""

    text_input = st.text_area("ข้อความ:", height=200, value=st.session_state.temp_text)

    # ปุ่มล้างข้อความ
    if st.button("🧹 ล้างข้อความ"):
        st.session_state.temp_text = ""
        st.rerun()

    if st.button("🚀 สรุปข้อความ"):
        if text_input.strip():
            st.session_state.temp_text = text_input

            with st.spinner("⏳ กำลังสรุปข้อความ..."):
                summary = summarize_text(text_input)
                save_summary(text_input, summary)

            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.success("✅ สรุปสำเร็จ!")
            st.markdown("### 📄 ผลลัพธ์:")
            st.write(summary)

            if st.button("📋 คัดลอกข้อความสรุป"):
                pyperclip.copy(summary)
                st.toast("คัดลอกแล้ว ✔", icon="📋")

            st.markdown("</div>", unsafe_allow_html=True)

        else:
            st.warning("⚠️ กรุณาป้อนข้อความก่อน")


# ------------------------------------------------------------
# 2) HISTORY PAGE
# ------------------------------------------------------------
elif menu == "ดูประวัติ":
    st.subheader("📜 ประวัติการสรุปข้อความทั้งหมด")

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

            # ORIGINAL
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

            # SUMMARY
            st.markdown("#### 📄 ข้อความสรุป:")
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

            col1, col2 = st.columns(2)

            with col1:
                if st.button("📋 คัดลอกสรุป", key=f"copy_{i}"):
                    pyperclip.copy(summary)
                    st.toast("คัดลอกแล้ว ✔")

            with col2:
                if st.button("🗑 ลบบันทึกนี้", key=f"delete_{i}"):
                    delete_summary(record_id)
                    st.success("ลบเรียบร้อย")
                    st.rerun()

            st.markdown("</div><br>", unsafe_allow_html=True)


# ------------------------------------------------------------
# 3) EVALUATION PAGE
# ------------------------------------------------------------
elif menu == "ประเมินโมเดล":
    st.subheader("📈 การประเมินโมเดล")
    ref = st.text_area("สรุปจริง (Reference)")
    cand = st.text_area("ผลลัพธ์โมเดล (Candidate)")

    if st.button("📊 ประเมิน"):
        if ref.strip() and cand.strip():
            scores = evaluate_summary(ref, cand)
            st.write(scores)
        else:
            st.warning("⚠️ กรุณากรอกให้ครบ")


# ------------------------------------------------------------
# 4) MODEL INFO
# ------------------------------------------------------------
elif menu == "ข้อมูลโมเดล 🧠":
    st.markdown("## 🧠 รายละเอียดโมเดล")
    st.write("โมเดล mT5 สำหรับสรุปข้อความภาษาไทย…")
