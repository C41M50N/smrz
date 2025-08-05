import whisper
import os
import tempfile
import subprocess
import requests
import shutil


class YoutubeVideoTranscriber:
    def __init__(
        self,
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

    def transcribe_video(self, youtube_video_url: str) -> str:
        try:
            audio_path = self._download_youtube_audio(youtube_video_url)
            return self._transcribe_audio(audio_path)
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

    def _cleanup_temp_files(self):
        try:
            shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Warning: Failed to clean up temporary files: {str(e)}")
