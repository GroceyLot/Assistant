import sounddevice as sd
import soundfile as sf


def playSound(filePath):
    # Load the sound file
    data, samplerate = sf.read(filePath)

    # Play the sound and wait for it to finish
    sd.play(data, samplerate)