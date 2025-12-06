from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# 🔹 โหลดโมเดล mT5 ที่ถูก fine-tune สำหรับภาษาไทย
# (มาจาก Hugging Face)
model_name = "StelleX/mt5-base-thaisum-text-summarization"

# 🔹 โหลด Tokenizer และ Model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def summarize_text(text, max_input_length=1024, max_output_length=300):
    """
    ฟังก์ชันหลักสำหรับสรุปข้อความภาษาไทย
    - ใช้โมเดล mT5 (Text-to-Text) 
    - สามารถสรุปข้อความยาวได้ และคงสาระสำคัญ
    """

    # ✅ ตรวจว่ามีข้อความหรือไม่
    if not text.strip():
        return "⚠️ กรุณาป้อนข้อความก่อนสรุป"

    # ✅ เตรียมข้อความนำเข้าให้โมเดล
    inputs = tokenizer.encode(
        "summarize: " + text,
        return_tensors="pt",
        max_length=max_input_length,
        truncation=True
    )

    # ✅ สร้างผลลัพธ์ด้วยโมเดล
    summary_ids = model.generate(
        inputs,
        max_length=max_output_length,   # ความยาวสรุปสูงสุด
        min_length=80,                  # ความยาวต่ำสุด (ยาวกว่าเดิม)
        num_beams=5,                    # ใช้ beam search เพื่อให้ผลลัพธ์มีคุณภาพ
        temperature=0.8,                # เพิ่มความหลากหลายของผลลัพธ์
        top_p=0.95,                     # ควบคุมความน่าจะเป็นรวม
        no_repeat_ngram_size=3,         # ไม่ให้คำซ้ำเกิน 3
        early_stopping=True
    )

    # ✅ แปลง token กลับเป็นข้อความภาษาไทย
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary
