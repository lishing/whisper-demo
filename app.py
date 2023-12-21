from tempfile import NamedTemporaryFile

import streamlit as st
import whisper 
import openai
import code as cd

st.title("Audio Transcription Feature")
st.caption("For MSF Social Report Companion with Whisper Base Model. Summarized by gpt-4-turbo")

# import model (base, 74m parameters)
model = whisper.load_model("base")
st.info("Whisper Base Model Loaded")

# upload audio file with streamlit
audio_file = st.file_uploader("Upload Audio", type=["wav", "mp3", "m4a"])

st.header("Play original audio file:")
st.audio(audio_file)

col1, col2 = st.columns([1,1])

with col1:
    button1 = st.button('Transcribe Audio')
with col2:
    button2 = st.button('Summarize Audio Clip')

if button1:
    with NamedTemporaryFile() as temp:
        temp.write(audio_file.getvalue())
        temp.seek(0)
        transcription = model.transcribe(temp.name)
        st.success("Transcribing Audio")
        st.markdown(transcription["text"])
if button2:
    with NamedTemporaryFile() as temp:
        temp.write(audio_file.getvalue())
        temp.seek(0)
        transcription = model.transcribe(temp.name)
        summary = cd.generate_summary(transcription["text"])
        st.success("Summary generated by OpenAI:")
        st.markdown(summary)

    # if audio_file is not None:
    #     st.success("Transcribing Audio")
    #     transcription = model.transcribe(audio_file.name)
    #     st.success("Transcribing Audio")
    #     st.markdown(transcription["text"])
    # else:
    #     st.error("Please upload an audio file")