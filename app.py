import streamlit as st
import pandas as pd
from groq import Groq
import os

st.title("📊 AI Survey Analysis")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

uploaded_file = st.file_uploader("Upload file Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.write(df.head())

    df["Content"] = df["Content"].astype(str)
    df = df[df["Content"].str.strip() != ""]

    clusters = df.groupby("Cluster")["Content"].apply(list)

    if st.button("🚀 Phân tích"):
        for c, texts in clusters.items():
            st.subheader(f"Cluster {c}")

            text = "\n".join(texts[:3])

            prompt = f"""
1. Chủ đề chính
2. Ý nghĩa (insight)

{text}
"""

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}]
            )

            st.write(response.choices[0].message.content)
