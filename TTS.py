import openai  # For interacting with the OpenAI API
import io  # For handling in-memory byte streams
import wave
import numpy as np
import sounddevice as sd  # For playing back the audio


def tts(text):
    if len(text) > 0:
        response = openai.audio.speech.create(
            model="tts-1",
            voice="alloy",
            response_format="wav",
            input=text,
        )

        # Convert MP3 to WAV using wave module
        audio_data = io.BytesIO(response.content)
        with wave.open(audio_data, "rb") as wf:
            sample_rate = wf.getframerate()
            audio_data = wf.readframes(wf.getnframes())

        # Convert audio data to numpy array for playback
        audio_array = np.frombuffer(audio_data, dtype=np.int16)

        # Play the audio without blocking
        sd.play(audio_array, samplerate=sample_rate)
        sd.wait()
