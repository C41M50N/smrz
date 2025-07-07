import whisper
import os
import tempfile
import subprocess
import requests
import shutil

from app.lib.llm_client import LLMClient
from app.utils import (
    clean_markdown,
    is_direct_audio_url,
    is_direct_video_url,
    is_youtube_url,
)


class VideoTranscriber:
    def __init__(
        self,
        transcript_readability_llm_client: LLMClient,
    ):
        # Ensure yt-dlp is installed
        if not shutil.which("yt-dlp"):
            raise RuntimeError(
                "yt-dlp is not installed. Please install it using 'pip install yt-dlp'."
            )

        # Ensure ffmpeg is installed
        if not shutil.which("ffmpeg"):
            raise RuntimeError(
                "ffmpeg is not installed. Please install it using your package manager or 'brew install ffmpeg' on macOS."
            )

        self.whisper_model = whisper.load_model("base")
        self.temp_dir = tempfile.mkdtemp()
        self.transcript_readability_llm_client = transcript_readability_llm_client

    def transcribe_video(self, source_url: str) -> str:
        try:
            audio_path = None

            if is_direct_audio_url(source_url):
                audio_path = self._download_file(source_url)
            elif is_direct_video_url(source_url):
                video_path = self._download_file(source_url)
                audio_path = self._extract_audio_from_video(video_path)
            elif is_youtube_url(source_url):
                audio_path = self._download_youtube_audio(source_url)
            else:
                raise ValueError(
                    "Invalid input source. Provide a valid YouTube URL, direct video URL, direct audio URL."
                )

            return self._improve_transcript_readability(
                self._transcribe_audio(audio_path)
            )
        except Exception as e:
            raise RuntimeError(f"Failed to transcribe video: {str(e)}")
        finally:
            self._cleanup_temp_files()

    def _download_file(self, url: str) -> str:
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            raise RuntimeError(f"Failed to download file from {url}")

        file_path = os.path.join(self.temp_dir, os.path.basename(url))
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return file_path

    def _download_youtube_audio(self, url: str) -> str:
        audio_path = os.path.join(self.temp_dir, "youtube_extracted_audio.wav")

        # fmt: off
        cmd = [
            'yt-dlp',
            '--extract-audio',
            '--audio-format', 'wav',
            '--audio-quality', '0',
            '--output', audio_path,
            url
        ]
        # fmt: on

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            return audio_path
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to download YouTube audio: {e}")

    def _extract_audio_from_video(self, video_path: str) -> str:
        audio_path = os.path.join(self.temp_dir, "extracted_audio.wav")

        # fmt: off
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vn',  # No video
            '-acodec', 'pcm_s16le',  # WAV format
            '-ar', '16000',  # 16kHz sample rate
            '-ac', '1',  # Mono audio
            '-y',  # Overwrite output file
            audio_path
        ]
        # fmt: on

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            return audio_path
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to extract audio: {e}")

    def _transcribe_audio(self, audio_path: str) -> str:
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        result = self.whisper_model.transcribe(audio_path, language="en")
        if "text" not in result:
            raise RuntimeError("Transcription failed.")

        return str(result["text"]).strip()

    def _improve_transcript_readability(self, transcript: str) -> str:
        try:
            response = self.transcript_readability_llm_client.generate_response(
                user_prompt=f"Improve the readability of the following video transcript: {transcript}",
                temp=825 / 1000,
            )
            return clean_markdown(response.content)
        except Exception as e:
            raise RuntimeError(f"Failed to improve transcript readability: {e}") from e

    def _cleanup_temp_files(self):
        try:
            shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Warning: Failed to clean up temporary files: {str(e)}")


IMPROVE_TRANSCRIPT_PROMPT_1 = """
# IDENTITY and PURPOSE
You are an expert at structuring video transcripts for improved readability. Your task is to add clear, descriptive headers and subheaders to video transcripts WITHOUT modifying, summarizing, or removing any of the original content.

## Instructions:

1. **Preserve ALL original text**: Keep every word, sentence, and paragraph exactly as written in the transcript. Do not summarize, paraphrase, or omit any content.

2. **Add strategic headers**: Insert headers and subheaders that break up the content into logical sections based on topic shifts, narrative flow, or structural elements.

3. **Use descriptive header formats**:
   - **Intro** - Opening remarks, introductions, setup
   - **Background** - Context, history, or foundational information  
   - **Main Point #1: [Specific Topic]** - First major point or argument
   - **Main Point #2: [Specific Topic]** - Second major point or argument
   - **Reason #1: [Specific Reason]** - Supporting reasons or evidence
   - **Example: [Brief Description]** - Case studies, stories, or illustrations
   - **Discussion** - Analysis, debate, or exploration of ideas
   - **Q&A** - Question and answer segments
   - **Key Takeaways** - Important conclusions or insights
   - **Conclusion** - Final thoughts, wrap-up
   - **Outro** - Closing remarks, calls to action, sign-offs

4. **Header placement guidelines**:
   - Insert headers at natural topic transitions
   - Place headers before the relevant content begins
   - Use subheaders (with ##) for subsections within main topics
   - Ensure headers reflect the actual content that follows

5. **Formatting**:
   - Use markdown header formatting (## for main headers, ### for subheaders)
   - Make headers specific and descriptive rather than generic
   - Remove any unneccessary paragraph breaks that do not separate distinct ideas

6. **What NOT to do**:
   - Do not change any original wording (but you can remove newlines in the middle of sentences)
   - Do not add your own commentary or explanations
   - Do not create summaries or bullet points
   - Do not rearrange the content order
   - Do not remove filler words, repetitions, or speech patterns

## Example Output Format:

```
## Intro
[Original transcript text for introduction...]

## Main Point #1: The Importance of Time Management
[Original transcript text about time management...]

### Example: The Pomodoro Technique
[Original transcript text about the example...]

## Main Point #2: Building Better Habits
[Original transcript text about habits...]

## Conclusion
[Original transcript text for conclusion...]

## Outro
[Original transcript text for closing...]
```

Only output Markdown with the added headers and subheaders. Do not include any additional explanations, notes, or formatting outside of the headers. Do not wrap the markdown in a code block or any other formatting.

Your goal is to make the transcript easier to navigate and read while maintaining 100% fidelity to the original content.
"""
