import streamlit as st
import pyttsx3
import PyPDF2
import tempfile
import os

# Initialize TTS engine
speaker = pyttsx3.init()
speaker.setProperty('rate', 150)

def read_pdf(pdf_file, start_page):
    pdfReader = PyPDF2.PdfReader(pdf_file)
    pages = len(pdfReader.pages)
    if start_page < 1 or start_page > pages:
        st.error("Invalid page number.")
        return
    
    for num in range(start_page - 1, pages):
        page = pdfReader.pages[num]
        text = page.extract_text()
        if text:
            words = text.split()
            page_text = ' '.join(words)
            speaker.say(page_text)
            speaker.runAndWait()

# ------------------- Frontend -------------------
st.title("📖 PDF Reader with Text-to-Speech")

name = st.text_input("Enter your Name:")
if name:
    st.success(f"Hello {name}! 👋 I am Pie, your reading assistant.")

uploaded_files = st.file_uploader("Upload one or more PDF files", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    pdf_names = [file.name for file in uploaded_files]
    choice = st.selectbox("Choose a PDF to read", pdf_names)

    chosen_file = None
    for file in uploaded_files:
        if file.name == choice:
            chosen_file = file
            break

    if chosen_file:
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(chosen_file.read())
            tmp_path = tmp_file.name

        # Count pages
        pdfReader = PyPDF2.PdfReader(tmp_path)
        total_pages = len(pdfReader.pages)
        st.info(f"📑 '{choice}' has {total_pages} pages")

        page_no = st.number_input("From which page should I start reading?", min_value=1, max_value=total_pages, value=1)

        if st.button("Start Reading"):
            st.success(f"Reading '{choice}' from page {page_no}...")
            read_pdf(tmp_path, page_no)
            os.remove(tmp_path)
