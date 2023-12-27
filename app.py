from tempfile import NamedTemporaryFile

import requests
import streamlit as st
import whisper 
import openai
import code as cd

st.title("Audio Transcription Feature")
st.caption("MSF Social Report Companion with Transcribe Fine-tuned model and Whisper Base Model. Summarized by gpt-4-turbo")

# Generate API Key for Transcribe JWT - for v2, to programmatically obtain API Key
# transcribe_api_url = "https://core.transcribe.gov.sg/auth/apikey"
# transcribe_api_payload = {"email": "chan_li_shing@tech.gov.sg"}

# response = requests.post(transcribe_api_url, json=transcribe_api_payload)

# if response.status_code == 200:
#     transcribe_api_key = response.json()['apikey']
#     st.success("Transcribe API key is successfully generated")
# else:
#     st.error(f'Fail to generate Transcribe API key:{response.text}')

# upload audio file with streamlit
audio_file = st.file_uploader("Upload Audio", type=["wav", "mp3", "m4a"])

st.header("Play original audio file:")
st.audio(audio_file)

col1, col2, col3 = st.columns([1,1,1])

with col1:
    button1 = st.button('Transcribe with Whisper (Base)')
with col2:
    button2 = st.button('Transcribe with Whisper Fine-tuned model')
with col3:
    button3 = st.button('Transcribe with Whisper and summarize with gpt-4')

# using Whisper as a model
if button1:
    # Using Whisper (base, 74m parameters)
    model = whisper.load_model("base")
    st.info("Whisper Base Model Loaded, ready to use")
    with NamedTemporaryFile() as temp:
        temp.write(audio_file.getvalue())
        temp.seek(0)
        transcription = model.transcribe(temp.name)
        st.success("Transcribing Audio")
        st.markdown(transcription["text"])

# logic of Transcribe :
# 1. Create a workspace. for MVP, it will be hardcoded into step 2
# 2. Create a project associated to the workspace. A project can only contain 1 audio file only
# 3. Create the transcriptions within the project. Multiple transcriptions can be in the same project
# 4. Download successful transcripts

if button2:
    # Get JWT with Transcribe API Key
    jwt_url = "https://core.transcribe.gov.sg/auth/tokens?service=https://core.transcribe.gov.sg&expiry=43200"
    jwt_payload = {
        "email": "chan_li_shing@tech.gov.sg",
        "apikey": st.secrets["TRANSCRIBE_API_KEY"]
    }

    response = requests.post(jwt_url, json=jwt_payload)

    if response.status_code == 200:
        transcribe_jwt = response.json()['token']
        st.success("Transcribe JWT Token is successfully generated, ready to use")
    else:
        st.error(f'Fail to generate JWT token:{response.text}')

    create_project = "https://core.transcribe.gov.sg/projects"
    create_transcription = "https://core.transcribe.gov.sg/transcriptions"
    api_headers = {"Authorization": f"Bearer {transcribe_jwt}"}

    with NamedTemporaryFile() as temp:
        temp.write(audio_file.getvalue())
        temp.seek(0)
        
        # stuck at create project; workspace_id missing
        create_project_payload = {
            "name": "launchpad-msf-transcribe",
            "workspace_id": "6583c2f4aa25897ff91ad382",
            "audio": temp.name,
            "sensitivity": "Sensitive Normal",
            "classification": "Restricted"
        }

        response = requests.post(create_project, headers=api_headers, json=create_project_payload)
        if response.status_code == 200:
            project_id = response.json()["id"]
            st.success("Project created successfully!")
        else:
            st.error(f"Failed to create project: {response.text}")
        
        # have not tried this. Fail at postman step
        create_transcription_payload = {
            "project_id": project_id,
            "engine": "whisper",
            "options":{
                "engine": "whisper",
                "language": "english",
                "model": "imda",
                "name": "Whisper SG by Transcribe"
            }
        }

        response = requests.post(create_transcription, headers=api_headers, json=create_transcription_payload)
        if response.status_code == 200:
            transcript_id = response.json()["id"]
            st.success("Transcription is successful!")
        else:
            st.error(f"Transcription has failed: {response.text}")

        transcription_url = f'https://core.transcribe.gov.sg/transcriptions{transcript_id}'
        while True:
            response = requests.get(transcription_status_url, headers=project_headers)

            if response.status_code == 200:
                status = response.json()["status"]

                if status == "Success":
                    st.success("Transcription is successful!")
                    st.markdown(f"Download Link: [Download Transcription](https://your-api-domain.com/transcriptions/{transcript_id}/latest_transcript/download)")
                    break
                elif status == "Fail":
                    st.error("Transcription failed.")
                    break
                else:
                    st.info(f"Transcription status: {status}")
                    st.text("Waiting for transcription to complete...")
                    time.sleep(5)  # Adjust the polling interval as needed
            else:
                st.error(f"Failed to check transcription status: {response.text}")
                break


# using Whisper and gpt-4 to summarize the audio file
if button3:
    # Using Whisper (base, 74m parameters)
    model = whisper.load_model("base")
    st.info("Whisper Base Model Loaded, ready to use")
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