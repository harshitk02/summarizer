# backend/summarizer/utils.py
import moviepy.editor as mp
import logging
import os
from pydub import AudioSegment

# Set up logging
logging.basicConfig(filename='Summarizer.log', level=logging.INFO)


def extract_audio(video_path, output_path):
    """
    Extract audio from a video using MoviePy.

    Parameters:
    - video_path (str): Path to the input video file.
    - output_path (str): Path to save the extracted audio file.

    Returns:
    - str: Path to the extracted audio file.
    """
    try:
        # Load the video clip
        video_clip = mp.VideoFileClip(video_path)

        # Extract audio
        audio_clip = video_clip.audio

        # Save the audio file
        audio_clip.write_audiofile(output_path)

        # Close the video clip
        video_clip.close()

        # Return the path to the extracted audio file
        return output_path

    except Exception as e:
        # Log the exception
        logging.error(f"Error in extract_audio: {e}")
        raise


def split_audio(audio_path, output_folder,filename):
    """
    Split the audio into 15-minute intervals.

    Parameters:
    - audio_path (str): Path to the input audio file.
    - output_folder (str): Path to save the split audio chunks.
    """

    try:
        # Load the audio file
        sound = AudioSegment.from_file(audio_path)

        # Define the length of each interval in milliseconds (15 minutes)
        interval_length = 15 * 60 * 1000

        # Ensure the output directory exists
        os.makedirs(output_folder, exist_ok=True)

        # Split the audio into 15-minute intervals
        for i, start_time in enumerate(range(0, len(sound), interval_length)):
            end_time = start_time + interval_length
            interval_chunk = sound[start_time:end_time]

            # Save each 15-minute interval to a separate file
            interval_chunk.export(f"{output_folder}{filename}_interval_{i + 1}.mp3", format="mp3")
        return output_folder

    except Exception as e:
        # Log the exception
        logging.error(f"Error in split_audio: {e}")
        raise

# Function to update processing progress
def update_processing_progress(step, progress_percent):
    global processing_progress
    processing_progress["current_step"] = step
    processing_progress["progress_percent"] = progress_percent