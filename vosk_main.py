import streamlit as st
import pyaudio
import json
from vosk import Model, KaldiRecognizer
import os

# Initialize variables
if 'recording' not in st.session_state:
    st.session_state.recording = False
if 'recognized_text' not in st.session_state:
    st.session_state.recognized_text = ""

# Title and Instructions
st.title("Real-Time Speech Recognition with Vosk")
st.write("Click 'Start' to begin recording and 'Stop' to end the recording.")

# Initialize Vosk Model
if not os.path.exists("ar_model"):
    st.error("Please download the model from https://alphacephei.com/vosk/models and unpack it as 'ar_model' in the current folder.")
    st.stop()

model = Model("ar_model")
recognizer = KaldiRecognizer(model, 16000)

# Initialize PyAudio
p = pyaudio.PyAudio()
if 'stream' not in st.session_state:
    st.session_state.stream = None

# Function to process the audio stream
def process_stream():
    while st.session_state.recording:
        data = st.session_state.stream.read(4000)
        if len(data) == 0:
            break

        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            if 'text' in result:
                st.session_state.recognized_text += result['text'] + " "
                text_display.text(st.session_state.recognized_text)
        else:
            partial_result = json.loads(recognizer.PartialResult())
            if 'partial' in partial_result:
                text_display.text(st.session_state.recognized_text + partial_result['partial'])

# Start and Stop buttons
if st.button("Start Recording"):
    if not st.session_state.recording:
        st.session_state.recording = True
        st.session_state.stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
        st.session_state.stream.start_stream()
        st.write("Recording started...")

if st.button("Stop Recording"):
    if st.session_state.recording:
        st.session_state.recording = False
        if st.session_state.stream:
            st.session_state.stream.stop_stream()
            st.session_state.stream.close()
            st.session_state.stream = None
        st.write("Recording stopped.")
        st.write("Final recognized text:")
        st.write(st.session_state.recognized_text)

# Display the recognized text live
text_display = st.empty()

# Process the audio stream if recording
if st.session_state.recording:
    process_stream()

# Stop the PyAudio stream properly
if not st.session_state.recording and st.session_state.stream:
    st.session_state.stream.stop_stream()
    st.session_state.stream.close()
    p.terminate()
