import streamlit as st
import pandas as pd
from groq import Groq
import os

st.title("📊 AI Survey Analysis")

# 🔐 lấy API key từ Secrets (Streamlit Cloud)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

uploaded_file = st.file_uploader("Upload file Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.subheader("📂 Dữ liệu mẫu")
    st.write(df.head())

    # 🧹 làm sạch dữ liệu
    df["Content"] = df["Content"].astype(str)
    df = df[df["Content"].str.strip() != ""]

    # 🔥 FIX: đảm bảo Cluster là số + sắp xếp đúng thứ tự
    df["Cluster"] = df["Cluster"].astype(int)

    clusters = (
        df.groupby("Cluster")["Content"]
        .apply(list)
        .sort_index()
    )

    st.subheader("📊 Kết quả phân tích")

    # 🔥 nút bấm tránh lag
    if st.button("🚀 Phân tích"):
        for c, texts in clusters.items():
            st.markdown(f"### 🔹 Cluster {c}")

            # giảm dữ liệu cho nhanh
            text = "\n".join(texts[:3])

            prompt = f"""
Phân tích các câu trả lời sau:

1. Chủ đề chính (1 câu ngắn)
2. Ý nghĩa (insight):
- Người dùng quan tâm gì?
- Vấn đề nổi bật là gì?

{text}
"""

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}]
            )

            st.write(response.choices[0].message.content)
