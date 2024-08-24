import speech_recognition as sr
from sound import playSound
import threading


class AudioHandler:
    def __init__(
        self,
        audioCallbacks,
        wake="alexa",
        expectationTime=30.0,
        debug=False,
    ):
        self.debug = debug
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 0.5  # Adjusted for faster response
        self.recognizer.energy_threshold = 3000  # Fine-tuned for ambient noise
        self.recognizer.dynamic_energy_threshold = (
            True  # Enable dynamic energy threshold
        )
        self.mic = sr.Microphone()
        self.listening = 0
        self.wake = wake
        self.expectingInput = False
        self.timer = None
        self.expectationTime = expectationTime
        self.callbacks = audioCallbacks(self)

        self.stopListening = None  # Initialize stopListening as None

        self.debugPrint(f"Initialized AudioHandler with wake word '{self.wake}'")

        # Start listening in the background upon instantiation
        self._start_listening()

    def debugPrint(self, *args, **kwargs):
        if self.debug:
            print(*args, **kwargs)

    def startTimer(self, time=30.0):
        if self.timer:
            self.timer.cancel()  # Cancel any existing timer
            self.debugPrint("Existing timer canceled")
        self.expectingInput = True
        self.debugPrint(f"Starting expectation timer for {time} seconds")
        self.timer = threading.Timer(time, self.resetExpectation)
        self.timer.start()

    def resetExpectation(self):
        self.expectingInput = False
        self.debugPrint("Expectation reset. Triggering sleep handler.")
        self.callbacks.sleep()
        if self.timer and self.timer.is_alive():
            self.timer.cancel()
            self.debugPrint("Timer canceled")
        playSound("sounds\\sleep.wav")  # Play the sleep sound

        # Restart the listening process after expectation reset
        self._restart_listening()

    def _start_listening(self):
        def callback(recognizer, audio):
            try:
                phrase = recognizer.recognize_google(audio).lower()
                self.debugPrint(f"Recognized phrase: {phrase}")
                self.callbacks.rawText(phrase)
                if self.expectingInput:
                    self.debugPrint("Expecting input, processing command.")
                    self.startTimer(
                        time=1000.0
                    )  # Reset the timer if new input is received
                    self.callbacks.command(phrase)
                    if self.expectingInput:
                        self.startTimer(
                            time=self.expectationTime
                        )  # Start the expectation timer
                elif self.wake in phrase:
                    self.debugPrint("Wake word detected")
                    playSound("sounds\\wake.wav")  # Play the wake sound
                    self.callbacks.wake()
                    self.startTimer(
                        time=1000.0
                    )  # Reset the timer if new input is received
                    self.callbacks.command(phrase)
                    if self.expectingInput:
                        self.startTimer(
                            time=self.expectationTime
                        )  # Start the expectation timer

            except sr.UnknownValueError:
                self.debugPrint("Speech recognition could not understand the audio")
            except sr.RequestError as e:
                self.debugPrint(f"Error with the recognition service: {e}")

        # Reinitialize the microphone to avoid re-entering context
        self.mic = sr.Microphone()
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source)
        self.stopListening = self.recognizer.listen_in_background(self.mic, callback)
        self.debugPrint("Started background listening")

    def _restart_listening(self):
        self.debugPrint("Restarting background listening")
        if self.stopListening:
            self.stopListening(wait_for_stop=False)  # Stop previous listener
        self._start_listening()  # Start a new listener
