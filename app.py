import streamlit as st
import pyperclip
from summarizer import summarize_text
from database import init_db, save_summary, get_all_summaries
from evaluation import evaluate_summary

# ---------- Page Config ----------
st.set_page_config(page_title="Thai Summarizer", page_icon="🧠", layout="wide")
init_db()

# ---------- Session State สำหรับ Theme ----------
if "theme" not in st.session_state:
    st.session_state.theme = "🌞 Light"

# ---------- Sidebar ----------
theme = st.sidebar.radio(
    "ธีม", 
    ["🌞 Light", "🌙 Dark"], 
    index=0 if st.session_state.theme == "🌞 Light" else 1
)
st.session_state.theme = theme

menu = st.sidebar.radio(
    "เมนู",
    ["สรุปข้อความ", "ดูประวัติ", "ประเมินโมเดล", "ข้อมูลโมเดล 🧠"]
)

# ---------- CSS Theme Function ----------
def set_theme(theme):
    if theme == "🌙 Dark":
        bg = "#2C2C2C"
        text_color = "#FFFFFF"
        card_bg = "rgba(50,50,50,0.9)"
        button_bg = "#555555"
        button_hover = "#888888"
        sidebar_bg = "#1B1B1B"
        sidebar_text = "#FFFFFF"
        topbar_bg = "#1B1B1B"   # Dark Topbar
    else:
        bg = "#D8C3A5"
        text_color = "#0d47a1"
        card_bg = "rgba(255,255,255,0.9)"
        button_bg = "#42a5f5"
        button_hover = "#1565c0"
        sidebar_bg = "#8B6D5C"      # Sidebar brown
        sidebar_text = "#000000"
        topbar_bg = "#D98C6D"       # Terracotta Light

    st.markdown(f"""
    <style>
    /* Main App */
    .stApp {{
        background-color: {bg};
        color: {text_color};
    }}
    /* Top bar */
    header {{
        background-color: {topbar_bg} !important;
        color: white !important;
    }}
    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg};
        color: {sidebar_text};
    }}
    section[data-testid="stSidebar"] * {{
        color: {sidebar_text};
    }}
    /* Card */
    .card {{
        background-color: {card_bg};
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        margin: 15px 0;
        color: {text_color};
    }}
    /* Button */
    .stButton>button {{
        border-radius: 10px;
        background-color: {button_bg};
        color: white;
        font-weight: bold;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        background-color: {button_hover};
    }}
    </style>
    """, unsafe_allow_html=True)

# เรียกใช้ Theme
set_theme(st.session_state.theme)

# ---------- หน้าเว็บ ----------
st.title("🧠 Thai Text Summarization System")
st.subheader("✨ ระบบสรุปใจความสำคัญภาษาไทยอัตโนมัติ ✨")

# ---------- เมนูหลัก ----------
if menu == "สรุปข้อความ":
    st.markdown("### 📝 ป้อนข้อความที่ต้องการให้ระบบสรุป")
    text_input = st.text_area("ข้อความ:", height=200)

    if st.button("🚀 สรุปข้อความ"):
        if text_input.strip():
            with st.spinner("⏳ กำลังสรุปข้อความ..."):
                summary = summarize_text(text_input)
                save_summary(text_input, summary)
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.success("✅ สรุปสำเร็จ!")
                st.markdown("### 📄 ผลลัพธ์:")
                st.write(summary)
                if st.button("📋 คัดลอกข้อความสรุป"):
                    pyperclip.copy(summary)
                    st.toast("✅ คัดลอกแล้ว!", icon="📋")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("⚠️ กรุณาป้อนข้อความก่อน")

elif menu == "ดูประวัติ":
    st.subheader("📜 ประวัติการสรุปข้อความที่ผ่านมา")
    data = get_all_summaries()
    if not data:
        st.info("ยังไม่มีข้อมูลในฐานข้อมูล")
    else:
        for row in data:
            st.markdown(f"""
            <div class='card'>
                <b>🕒 วันที่:</b> {row[3]}<br>
                <b>📝 ข้อความต้นฉบับ:</b> {row[1][:200]}...<br>
                <b>📄 สรุป:</b> {row[2]}
            </div>
            """, unsafe_allow_html=True)

elif menu == "ประเมินโมเดล":
    st.subheader("📈 การประเมินผลโมเดล (ROUGE / BLEU)")
    reference = st.text_area("สรุปจริง (Reference):", height=100)
    candidate = st.text_area("สรุปจากโมเดล (Candidate):", height=100)

    if st.button("📊 ประเมิน"):
        if reference.strip() and candidate.strip():
            scores = evaluate_summary(reference, candidate)
            st.success("ผลการประเมิน:")
            st.write(f"🔹 ROUGE-1: {scores['ROUGE-1']}")
            st.write(f"🔹 ROUGE-L: {scores['ROUGE-L']}")
            st.write(f"🔹 BLEU: {scores['BLEU']}")
        else:
            st.warning("⚠️ ป้อนข้อความทั้งสองช่องก่อนประเมิน")

elif menu == "ข้อมูลโมเดล 🧠":
    st.subheader("🧠 Model Information: mT5-base-thaisum-text-summarization")
    st.markdown("""
    <div class='card'>
        <h3>📘 ข้อมูลทั่วไป</h3>
        <ul>
            <li><b>Model Name:</b> StelleX/mt5-base-thaisum-text-summarization</li>
            <li><b>Framework:</b> PyTorch + Hugging Face Transformers</li>
            <li><b>Language:</b> Thai</li>
            <li><b>Architecture:</b> Encoder–Decoder (Text-to-Text)</li>
            <li><b>Task Type:</b> Text Summarization</li>
            <li><b>Base Model:</b> Google mT5 (Multilingual T5)</li>
            <li><b>Parameters:</b> ≈ 580 million</li>
        </ul>
    </div>
    <div class='card'>
        <h3>🧩 จุดเด่นของโมเดล</h3>
        <ul>
            <li>รองรับหลายภาษา (Multilingual) รวมถึงภาษาไทย</li>
            <li>สามารถเข้าใจและสรุปเนื้อหายาวได้</li>
            <li>เหมาะกับงานสรุปข่าว บทความ หรือรายงานภาษาไทย</li>
            <li>สามารถต่อยอดไปยังงานแปลภาษา หรือถาม–ตอบได้</li>
        </ul>
    </div>
    <div class='card'>
        <h3>🔬 อ้างอิง</h3>
        <p>โมเดลนี้ถูกพัฒนาโดย <a href='https://huggingface.co/StelleX' target='_blank'>StelleX</a> 
        และเผยแพร่บน Hugging Face Hub</p>
    </div>
    """, unsafe_allow_html=True)
