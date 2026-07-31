import streamlit as st
import pandas as pd
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from pipeline import run_pipeline

st.title("Microbial Diversity Analyzer")

uploaded_file = st.file_uploader("Upload your data table (CSV)", type="csv")

if uploaded_file is not None:
    st.write("File uploaded successfully!")
    st.write(uploaded_file.name)