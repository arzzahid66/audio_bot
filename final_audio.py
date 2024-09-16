import os
import asyncio
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st
from st_audiorec import st_audiorec

load_dotenv()


st.markdown("""
    <style>
    .title {
        font-family: 'Helvetica Neue', sans-serif;
        color: #4B4B4B;
        font-size: 2.5em;
        font-weight: bold;
        text-align: center;
        padding: 20px 0;
        background: -webkit-linear-gradient(#f8cdda, #1e90ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .subtitle {
        font-family: 'Helvetica Neue', sans-serif;
        color: #4B4B4B;
        font-size: 1.5em;
        text-align: center;
        margin-top: -10px;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# Display the styled title
st.markdown('<div class="title">VoiceQuery AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Audio to audio</div>', unsafe_allow_html=True)


# model = whisper.load_model("base")

def transcribe_voice_to_text(audio_location, language='ur'):
    client = OpenAI()
    with open(audio_location, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(model="whisper-1", language=language, file=audio_file)
    return transcript.text

def chat_completion_call(text):
    client = OpenAI()
    messages = [{"role": "user", "content": text}]
    response = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
    return response.choices[0].message.content



def text_to_speech_ai(response):
    if not response.strip():  # Check if the response is empty or contains only whitespace
        raise ValueError("The response text is empty, cannot generate speech.")
    
    client = OpenAI()
    tts_response = client.audio.speech.create(model="tts-1-hd", voice="onyx", input=response)
    return tts_response.content  # Get audio content as bytes

async def process_audio(audio_data):
    audio_location = "audio_file.wav"
    with open(audio_location, "wb") as f:
        f.write(audio_data)
    
    human_question = transcribe_voice_to_text(audio_location, language='ur')
    ai_msg = chat_completion_call(human_question)
    text_to_speech = text_to_speech_ai(ai_msg)
    return text_to_speech
    # if human_question.strip():  # Ensure the transcription is not empty
    #     audio_content = text_to_speech_ai(human_question)
    #     return audio_content
    # else:
    #     return None

# Audio recording
wav_audio_data = st_audiorec()
audio_file_path = "ai_response_audio.mp3"

if wav_audio_data is not None:
    with st.spinner("Generating AI response..."):
        audio_content = asyncio.run(process_audio(wav_audio_data))
        if audio_content:
            with open(audio_file_path, "wb") as audio_file:
                audio_file.write(audio_content)
            st.audio(audio_file_path, format='audio/mp3', start_time=0)
        else:
            st.error("No valid transcription available for TTS.")
