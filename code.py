import os
import openai
# from dotenv import load_dotenv
import json
import streamlit as st

# load_dotenv()

# to summarize
openai.api_type = "azure"
endpoint = "https://launchpad-assistant-api.launchpad.tech.gov.sg/services/openai/"
api_version = "2023-07-01-preview"
# api_key = os.getenv("OPENAI_API_KEY")
api_key = st.secrets["OPEN_API_KEY"]

client = openai.AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version="2023-03-15-preview"
    )

# generate summary
def generate_summary(input):
    message_text = [{"role":"system","content":
"You are a helpful assistant who summarizes transcribed contents",
"role":"user","content":f"analyze the text given in {input} and summarize it"}]

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages = message_text, 
        # stream=True,
        temperature=0.0,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
        )
    # for chunk in response:
    #     if chunk.choices[0].delta.content is not None:
    #         print(chunk.choices[0].delta.content, end="")
    response_message = response.choices[0].message.content
    return response_message
    # return response