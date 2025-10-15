# # import streamlit as st
# # import pyttsx3
# # import PyPDF2
# # import tempfile
# # import os

# # # Initialize TTS engine
# # speaker = pyttsx3.init()
# # speaker.setProperty('rate', 150)

# # def read_pdf(pdf_file, start_page):
# #     pdfReader = PyPDF2.PdfReader(pdf_file)
# #     pages = len(pdfReader.pages)
# #     if start_page < 1 or start_page > pages:
# #         st.error("Invalid page number.")
# #         return
    
# #     for num in range(start_page - 1, pages):
# #         page = pdfReader.pages[num]
# #         text = page.extract_text()
# #         if text:
# #             words = text.split()
# #             page_text = ' '.join(words)
# #             speaker.say(page_text)
# #             speaker.runAndWait()

# # # ------------------- Frontend -------------------
# # st.title("📖 PDF Reader with Text-to-Speech")

# # name = st.text_input("Enter your Name:")
# # if name:
# #     st.success(f"Hello {name}! 👋 I am Pie, your reading assistant.")

# # uploaded_files = st.file_uploader("Upload one or more PDF files", type=["pdf"], accept_multiple_files=True)

# # if uploaded_files:
# #     pdf_names = [file.name for file in uploaded_files]
# #     choice = st.selectbox("Choose a PDF to read", pdf_names)

# #     chosen_file = None
# #     for file in uploaded_files:
# #         if file.name == choice:
# #             chosen_file = file
# #             break

# #     if chosen_file:
# #         # Save file temporarily
# #         with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
# #             tmp_file.write(chosen_file.read())
# #             tmp_path = tmp_file.name

# #         # Count pages
# #         pdfReader = PyPDF2.PdfReader(tmp_path)
# #         total_pages = len(pdfReader.pages)
# #         st.info(f"📑 '{choice}' has {total_pages} pages")

# #         page_no = st.number_input("From which page should I start reading?", min_value=1, max_value=total_pages, value=1)

# #         if st.button("Start Reading"):
# #             st.success(f"Reading '{choice}' from page {page_no}...")
# #             read_pdf(tmp_path, page_no)
# #             os.remove(tmp_path)

# import streamlit as st
# import pyttsx3
# import PyPDF2
# import tempfile
# import os
# import threading
# import time

# # Helper that speaks pages in a background thread
# def speak_pdf_pages(pdf_path: str, start_page: int, rate: int = 150):
#     try:
#         pdfReader = PyPDF2.PdfReader(pdf_path)
#         pages = len(pdfReader.pages)

#         # Initialize engine inside the thread (fresh instance per run)
#         engine = pyttsx3.init()
#         engine.setProperty('rate', rate)

#         for num in range(start_page - 1, pages):
#             page = pdfReader.pages[num]
#             text = page.extract_text()
#             if text:
#                 # Clean up spacing
#                 words = text.split()
#                 page_text = ' '.join(words)

#                 engine.say(page_text)
#                 # runAndWait will process all queued say() calls up to this point
#                 engine.runAndWait()

#                 # Optional small pause between pages to avoid overlapping
#                 time.sleep(0.1)

#         # tidy up
#         try:
#             engine.stop()
#         except Exception:
#             pass

#     except Exception as e:
#         # We cannot call st.error from inside a background thread safely,
#         # so store the error to session_state for main thread to show.
#         st.session_state.tts_error = str(e)
#     finally:
#         # mark finished so UI can react
#         st.session_state.is_reading = False

# # ------------------- Frontend -------------------
# st.title("📖 PDF Reader with Text-to-Speech")

# name = st.text_input("Enter your Name:")
# if name:
#     st.success(f"Hello {name}! 👋 I am Pie, your reading assistant.")

# uploaded_files = st.file_uploader("Upload one or more PDF files", type=["pdf"], accept_multiple_files=True)

# # initialize state flags
# if "is_reading" not in st.session_state:
#     st.session_state.is_reading = False
# if "tts_error" not in st.session_state:
#     st.session_state.tts_error = None

# if uploaded_files:
#     pdf_names = [file.name for file in uploaded_files]
#     choice = st.selectbox("Choose a PDF to read", pdf_names)

#     chosen_file = None
#     for file in uploaded_files:
#         if file.name == choice:
#             chosen_file = file
#             break

#     if chosen_file:
#         # Save file temporarily
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
#             tmp_file.write(chosen_file.read())
#             tmp_path = tmp_file.name

#         # Count pages
#         pdfReader = PyPDF2.PdfReader(tmp_path)
#         total_pages = len(pdfReader.pages)
#         st.info(f"📑 '{choice}' has {total_pages} pages")

#         page_no = st.number_input("From which page should I start reading?",
#                                   min_value=1, max_value=total_pages, value=1)

#         rate = st.slider("Reading speed (words per minute)", min_value=100, max_value=250, value=150)

#         start_button = st.button("Start Reading", disabled=st.session_state.is_reading)

#         if start_button and not st.session_state.is_reading:
#             # mark as running and start thread
#             st.session_state.is_reading = True
#             st.session_state.tts_error = None
#             st.success(f"Reading '{choice}' from page {page_no}...")

#             t = threading.Thread(target=speak_pdf_pages, args=(tmp_path, page_no, rate), daemon=True)
#             t.start()

#         # show status
#         if st.session_state.is_reading:
#             st.info("🔊 Reading in progress... (click again to try later)")
#         else:
#             st.write("Ready to read.")

#         # If a background thread reported an error, show it and clear
#         if st.session_state.tts_error:
#             st.error(f"TTS error: {st.session_state.tts_error}")
#             st.session_state.tts_error = None

#         # Remove temp file only when not reading
#         if not st.session_state.is_reading:
#             try:
#                 os.remove(tmp_path)
#             except Exception:
#                 pass

import streamlit as st
import PyPDF2
import tempfile
import os
import threading
import time
import pyttsx3

# -------------------
# Thread worker that speaks PDF content with pause/resume/stop
# -------------------
def speak_worker(pdf_path: str, start_page: int, rate: int, pause_event: threading.Event, stop_event: threading.Event):
    """Background thread function that reads pdf page-by-page, sentence-by-sentence.
       Uses pause_event (when set -> paused) and stop_event (when set -> stop immediately).
    """
    try:
        reader = PyPDF2.PdfReader(pdf_path)
        pages = len(reader.pages)

        engine = pyttsx3.init()
        engine.setProperty("rate", rate)

        # iterate pages
        for p in range(start_page - 1, pages):
            if stop_event.is_set():
                break

            raw_text = reader.pages[p].extract_text() or ""
            # very simple sentence splitter; you can improve this if needed
            # splitting to smaller chunks lets us pause/resume reasonably quickly
            sentences = [s.strip() for s in raw_text.replace("\n", " ").split(". ") if s.strip()]

            for sent in sentences:
                # check stop
                if stop_event.is_set():
                    break

                # pause: wait until pause_event is cleared
                while pause_event.is_set() and not stop_event.is_set():
                    time.sleep(0.2)

                # speak this sentence
                # call say + runAndWait for single chunk to keep control fine-grained
                engine.say(sent)
                try:
                    engine.runAndWait()
                except RuntimeError:
                    # If engine internals complain, try stopping and re-init once
                    try:
                        engine.stop()
                    except Exception:
                        pass
                    engine = pyttsx3.init()
                    engine.setProperty("rate", rate)
                    engine.say(sent)
                    engine.runAndWait()

            # small pause between pages to allow UI to react
            time.sleep(0.05)

        # graceful stop of engine
        try:
            engine.stop()
        except Exception:
            pass

        # mark finished
        st.session_state.is_reading = False
        st.session_state.just_finished = True

    except Exception as e:
        st.session_state.is_reading = False
        st.session_state.worker_error = str(e)

# -------------------
# Helpers to manage thread and events in session_state
# -------------------
def start_reading(tmp_path, page_no, rate):
    if st.session_state.is_reading:
        return

    # initialize control events and worker thread
    st.session_state.pause_event = threading.Event()  # when set => paused
    st.session_state.stop_event = threading.Event()   # when set => stop
    st.session_state.is_reading = True
    st.session_state.just_finished = False
    st.session_state.worker_error = None

    t = threading.Thread(
        target=speak_worker,
        args=(tmp_path, page_no, rate, st.session_state.pause_event, st.session_state.stop_event),
        daemon=True
    )
    st.session_state.worker_thread = t
    t.start()

def pause_resume():
    if not st.session_state.is_reading:
        return
    # toggle pause
    if not st.session_state.pause_event.is_set():
        st.session_state.pause_event.set()   # pause
    else:
        st.session_state.pause_event.clear() # resume

def stop_reading():
    if not st.session_state.is_reading:
        return
    st.session_state.stop_event.set()
    # Wait a short time for thread to finish
    # Can't block UI for long; we'll poll a little
    for _ in range(30):
        if not st.session_state.is_reading:
            break
        time.sleep(0.1)
    # Ensure flags updated
    st.session_state.is_reading = False

def exit_app(tmp_path=None):
    # set stop and cleanup, then optionally exit the app via a message
    if st.session_state.is_reading:
        stop_reading()
    if tmp_path and os.path.exists(tmp_path):
        try:
            os.remove(tmp_path)
        except Exception:
            pass
    st.session_state.clear()
    st.experimental_rerun()

# -------------------
# Streamlit UI
# -------------------
st.set_page_config(page_title="PDF Reader — Play/Pause/Stop", layout="centered")
st.title("📖 PDF Reader with Play / Pause / Stop")

if "is_reading" not in st.session_state:
    st.session_state.is_reading = False
if "just_finished" not in st.session_state:
    st.session_state.just_finished = False
if "worker_error" not in st.session_state:
    st.session_state.worker_error = None

name = st.text_input("Enter Your Name")
if name:
    st.success(f"Hello {name}! I'll read your PDFs aloud.")

uploaded_files = st.file_uploader("Upload PDFs (multiple allowed)", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    pdf_names = [f.name for f in uploaded_files]
    choice = st.selectbox("Choose a PDF to read", pdf_names)

    # select the chosen file object
    chosen_file = next((f for f in uploaded_files if f.name == choice), None)

    if chosen_file:
        # save to temp file (one temp per chosen PDF)
        if "tmp_path" not in st.session_state or st.session_state.tmp_name != chosen_file.name:
            # cleanup any old tmp
            if "tmp_path" in st.session_state:
                try:
                    if os.path.exists(st.session_state.tmp_path):
                        os.remove(st.session_state.tmp_path)
                except Exception:
                    pass
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(chosen_file.read())
                st.session_state.tmp_path = tmp.name
                st.session_state.tmp_name = chosen_file.name

        tmp_path = st.session_state.tmp_path

        # get page count
        reader = PyPDF2.PdfReader(tmp_path)
        total_pages = len(reader.pages)
        st.info(f"'{choice}' — {total_pages} pages")

        page_no = st.number_input("Start from page", min_value=1, max_value=total_pages, value=1)
        rate = st.slider("Reading speed (words per minute)", min_value=100, max_value=250, value=150)

        cols = st.columns([1,1,1,1])
        with cols[0]:
            if st.button("Start") and not st.session_state.is_reading:
                st.success(f"Starting reading from page {page_no}...")
                start_reading(tmp_path, page_no, rate)

        with cols[1]:
            # Pause/Resume button (disabled when not reading)
            if st.session_state.is_reading:
                lbl = "Pause" if not (st.session_state.pause_event.is_set()) else "Resume"
                if st.button(lbl):
                    pause_resume()
            else:
                st.button("Pause/Resume", disabled=True)

        with cols[2]:
            if st.button("Stop"):
                stop_reading()
                st.info("Stopped reading.")

        with cols[3]:
            if st.button("Exit"):
                # clean up and restart app
                exit_app(tmp_path if 'tmp_path' in st.session_state else None)

        # show status
        if st.session_state.is_reading:
            if st.session_state.pause_event.is_set():
                st.warning("⏸️ Paused")
            else:
                st.info("🔊 Reading...")

        elif st.session_state.just_finished:
            st.success("✅ Finished reading. You may choose another PDF or press 'Exit'.")
            # clear just_finished after showing
            st.session_state.just_finished = False

        else:
            st.write("Ready. Press Start to begin reading.")

        # show worker errors if any
        if st.session_state.worker_error:
            st.error("TTS worker error: " + st.session_state.worker_error)
            st.session_state.worker_error = None

        # cleanup temp when not reading (so user can pick another PDF later)
        if not st.session_state.is_reading:
            try:
                if os.path.exists(st.session_state.tmp_path):
                    os.remove(st.session_state.tmp_path)
                    # remove keys so choosing another file re-creates tmp
                    del st.session_state.tmp_path
                    del st.session_state.tmp_name
            except Exception:
                pass

else:
    st.info("Upload one or more PDFs to begin.")
