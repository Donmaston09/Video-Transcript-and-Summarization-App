import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import speech_recognition as sr
from io import BytesIO

# Streamlit UI for API Key Input
st.sidebar.header("🔑 Enter Your Google API Key")
GOOGLE_API_KEY = st.sidebar.text_input("Paste your API key here", type="password")

if GOOGLE_API_KEY:
    # Store the API key in Streamlit session state
    st.session_state["google_api_key"] = GOOGLE_API_KEY
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    st.warning("⚠️ Please enter your Google API key to continue.")
    st.stop()  # Stops execution until the key is provided

# Function to fetch transcript from YouTube video
def get_transcript(video_id):
    """Fetches the transcript of a YouTube video."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([t['text'] for t in transcript])
        return transcript_text
    except Exception as e:
        st.error(f"Error retrieving transcript: {e}")
        return None

# Function to summarize text using Gemini AI
def summarize_text(text):
    """Uses Gemini AI to summarize the transcript."""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")  # Use the correct model here
        response = model.generate_content(f"Summarize the following text:\n\n{text}")
        return response.text
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return "Summary generation failed."

# Function to transcribe uploaded video file
def transcribe_audio_from_file(uploaded_file):
    """Transcribes audio from an uploaded video file."""
    recognizer = sr.Recognizer()
    audio_file = BytesIO(uploaded_file.read())
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
    try:
        transcript = recognizer.recognize_google(audio)
        return transcript
    except sr.UnknownValueError:
        st.error("Sorry, could not understand the audio.")
        return None
    except sr.RequestError:
        st.error("Could not request results from Google Speech Recognition.")
        return None

# Streamlit UI
def main():
    st.title("🎥 Video Transcript and Summarization App")
    
    # Brief about the app
    st.markdown("""
        ### 📜 About the App:
        This app extracts and summarizes transcripts from YouTube videos or uploaded video files.
        It uses **Google Gemini AI** for summarization and **YouTube Transcript API** or **speech recognition** for transcription.
        
        **How it works:**
        1. **Enter a YouTube URL** to extract subtitles.
        2. **Upload a video file** to transcribe speech.
        3. **Summarization** is handled by Google Gemini AI.

        **Note:** An API key is required to use this app.
    """)
    st.markdown("""
        **Created by:** Anthony Onoja  
        **School of Health Science, University of Surrey**
    """)

    # Instructions on how to get an API key
    st.sidebar.header("🔍 How to Get Your API Key")
    st.sidebar.write("""
        1. Go to [Google Cloud Console](https://console.cloud.google.com/)
        2. Create a project and enable **Generative AI API**.
        3. Generate an API key under **API & Services**.
        4. Copy and paste it into the input field above.
    """)

    option = st.radio("Choose an option:", ("Enter YouTube URL", "Upload a Video File"))

    if option == "Enter YouTube URL":
        video_url = st.text_input("📺 Enter the YouTube video URL:")

        if video_url:
            video_id = video_url.split("v=")[-1].split("&")[0]  # Extracts only the video ID
            st.write("⏳ Extracting transcript...")
            transcript = get_transcript(video_id)

            if transcript:
                st.success("✅ Transcript extracted successfully.")
                st.write("**Transcript:**", transcript)
                st.write("⏳ Summarizing transcript...")
                summary = summarize_text(transcript)
                st.subheader("📌 Summary:")
                st.write(summary)
            else:
                st.error("❌ Failed to extract transcript.")
    
    elif option == "Upload a Video File":
        uploaded_file = st.file_uploader("📂 Choose a video file", type=["mp4", "mkv", "avi", "mov"])
        
        if uploaded_file:
            st.write("⏳ Transcribing audio from the video...")
            transcript = transcribe_audio_from_file(uploaded_file)
            
            if transcript:
                st.success("✅ Transcript extracted from video.")
                st.write("**Transcript:**", transcript)
                st.write("⏳ Summarizing transcript...")
                summary = summarize_text(transcript)
                st.subheader("📌 Summary:")
                st.write(summary)
            else:
                st.error("❌ Failed to transcribe the video.")

if __name__ == "__main__":
    main()
