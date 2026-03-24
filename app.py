import streamlit as st
import pandas as pd
from groq import Groq
import os

st.set_page_config(page_title="AI Survey Analysis", layout="wide")

st.title("📊 AI Survey Analysis")

# 🔐 Lấy API key
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("❌ Không tìm thấy API KEY. Vào Settings → Secrets để thêm.")
else:
    client = Groq(api_key=api_key)

    uploaded_file = st.file_uploader("📂 Upload file Excel", type=["xlsx"])

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)

            st.subheader("📋 Dữ liệu mẫu")
            st.dataframe(df.head())

            # 🔍 Kiểm tra cột
            if "Cluster" not in df.columns or "Content" not in df.columns:
                st.error("❌ File phải có cột 'Cluster' và 'Content'")
            else:
                # 🧹 Làm sạch Content
                df["Content"] = df["Content"].astype(str)
                df = df[df["Content"].str.strip() != ""]

                # 🔥 Fix Cluster lỗi
                df["Cluster"] = pd.to_numeric(df["Cluster"], errors="coerce")
                df = df.dropna(subset=["Cluster"])
                df["Cluster"] = df["Cluster"].astype(int)

                # 📊 Group + sort
                clusters = (
                    df.groupby("Cluster")["Content"]
                    .apply(list)
                    .sort_index()
                )

                st.subheader("📊 Kết quả phân tích")

                # 🔥 Nút chạy
                if st.button("🚀 Phân tích"):
                    for c, texts in clusters.items():
                        st.markdown(f"### 🔹 Cluster {c}")

                        # giảm dữ liệu cho nhanh
                        text = "\n".join(texts[:3])

                        prompt = f"""
Phân tích các câu trả lời sau:

1. Chủ đề chính (1 câu ngắn)
2. Ý nghĩa (insight):
- Người dùng quan tâm điều gì?
- Vấn đề nổi bật là gì?

{text}
"""

                        try:
                            response = client.chat.completions.create(
                                model="llama-3.1-8b-instant",
                                messages=[{"role": "user", "content": prompt}]
                            )

                            st.write(response.choices[0].message.content)

                        except Exception as e:
                            st.error(f"❌ Lỗi gọi AI: {e}")

        except Exception as e:
            st.error(f"❌ Lỗi đọc file: {e}")
