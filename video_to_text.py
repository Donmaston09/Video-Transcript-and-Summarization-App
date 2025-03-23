import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import speech_recognition as sr
from io import BytesIO

# Fetch the Google API key from Streamlit secrets
GOOGLE_API_KEY = st.secrets["google"]["api_key"]

# Configure Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

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
    st.title("Video Transcript and Summarization App")
    
    # Brief about the app
    st.markdown("""
        ### About the App:
        This app allows you to extract and summarize transcripts from YouTube videos or uploaded video files. 
        Whether you want to summarize educational videos, research talks, or interviews, this tool helps 
        in quickly extracting meaningful content from long videos. The app uses **Google Gemini AI** for 
        summarizing text and **YouTube Transcript API** or **speech recognition** for transcribing video/audio files.

        Simply input the **YouTube video URL** or **upload a video file**, and let the app do the rest!
    """)

    # Your name and institution info
    st.markdown("""
        **Created by:** Anthony Onoja  
        **School of Health Science, University of Surrey**
    """)

    # Instructions on how to get an API key
    st.sidebar.header("How to Get Your API Key")
    st.sidebar.write("""
        To use this app, you need a Google API key for the Gemini AI service. 
        Follow these steps to obtain your own API key:
        
        1. Go to the Google Cloud Console: [https://console.cloud.google.com/](https://console.cloud.google.com/)
        2. Create a new project or select an existing one.
        3. Enable the **Generative AI API**.
        4. Generate an API key from the **API & Services** section.
        5. Once you have the API key, store it in a `.streamlit/secrets.toml` file as follows:
        
        ```toml
        [google]
        api_key = "YOUR_GOOGLE_API_KEY_HERE"
        ```
        
        Replace `"YOUR_GOOGLE_API_KEY_HERE"` with the actual API key you obtained.
    """)

    option = st.radio("Choose an option", ("Enter YouTube URL", "Upload a Video File"))

    if option == "Enter YouTube URL":
        video_url = st.text_input("Enter the YouTube video URL:")

        if video_url:
            video_id = video_url.split("v=")[-1].split("&")[0]  # Extracts only the video ID
            st.write("Extracting transcript...")
            transcript = get_transcript(video_id)

            if transcript:
                st.success("Transcript extracted successfully.")
                st.write("Transcript:", transcript)
                st.write("Summarizing transcript...")
                summary = summarize_text(transcript)
                st.subheader("Summary:")
                st.write(summary)
            else:
                st.error("Failed to extract transcript.")
    
    elif option == "Upload a Video File":
        uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "mkv", "avi", "mov"])
        
        if uploaded_file:
            st.write("Transcribing audio from the video...")
            transcript = transcribe_audio_from_file(uploaded_file)
            
            if transcript:
                st.success("Transcript extracted from video.")
                st.write("Transcript:", transcript)
                st.write("Summarizing transcript...")
                summary = summarize_text(transcript)
                st.subheader("Summary:")
                st.write(summary)
            else:
                st.error("Failed to transcribe the video.")
            
if __name__ == "__main__":
    main()