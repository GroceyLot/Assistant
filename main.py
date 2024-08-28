import os
import argparse
import pystray
from PIL import Image
import keyboard
from audio import AudioHandler
from handler import Assistant
from tool import Tools
from TTS import tts
from sound import playSound
import threading

# Command-line argument parsing
parser = argparse.ArgumentParser(
    description="Run the assistant with optional debug mode."
)
parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode.")
args = parser.parse_args()
debug = args.debug


def debugPrint(*args, **kwargs):
    if debug:
        print(*args, **kwargs)


class AudioCallbacks:
    def __init__(self, audioHandler):
        self.handler = audioHandler

    def command(self, command):
        return commandHandler(command)

    def sleep(self):
        pass

    def wake(self):
        pass

    def rawText(self, text):
        pass


class AssistantCallbacks:
    def __init__(self, assistant):
        self.assistant = assistant

    def delta(self, chunk, choice, content):
        pass

    def toolDelta(self, args, name, id):
        print(args)
        pass

    def chunkFinish(self, content):
        tts(content)

    def toolFinish(self, name, args, id, content, assistant):
        global tools
        return tools.tool(
            name=name, args=args, id=id, content=content, assistant=assistant
        )

    def fullFinish(self, content):
        pass

def commandHandler(command):
    global working
    working = True
    debugPrint(f"Command received: {command}")
    assistant.appendMessage("user", command)
    playSound("sounds\\messageStart.wav")
    output = assistant.stream(AssistantCallbacks=AssistantCallbacks)
    debugPrint(f"Output from assistant: {output}")
    working = False
    return True


def quitApp(icon, item):
    debugPrint("Quitting application.")
    # Stop listening before quitting
    audioHandler.stopListening()
    icon.stop()  # This stops the pystray icon loop
    os._exit(0)  # This forcefully exits the application


def createTrayIcon():
    debugPrint("Creating tray icon.")
    # Load the icon from an ico file
    icon_path = "images\\icon.ico"  # Replace with the path to your .ico file
    image = Image.open(icon_path)

    # Correctly create a menu
    menu = pystray.Menu(pystray.MenuItem("Quit", quitApp))

    icon = pystray.Icon("Assistant", image, "Assistant", menu)
    debugPrint("Tray icon created.")
    thread = threading.Thread(target=icon.run)
    thread.start()


if __name__ == "__main__":
    debugPrint("Starting application.")
    global audioHandler
    global tools
    global assistant
    try:
        working = False
        audioHandler = AudioHandler(audioCallbacks=AudioCallbacks, debug=debug, wake="alloy")
        tools = Tools(audioHandler, debug=debug)
        assistant = Assistant(
            tools=tools.tools,
            extraInstruct="""You are an AI called Alloy. You are chatting with a friend through voice.
                    You also help them with the tools provided to you.
                    Please note that you are put through text-to-speech, so no markdown is allowed, and keep your responses short. Do not include bulleted lists, abbrviations or file extensions, or anything that could go wrong with the text-to-speech.
                    If the user asks you to go away, use the 'exitChat' function. As well as that, if the query is short like 'what's 9 + 10' use 'exitChat', then respond with the answer.
                    Be punctual and inferring. If the user asks for something that you don't know about, try taking a peek at their screen to see what's up. Or if they ask something out of your scope, use command prompt to do it with commands.
                    Say they ask for an image of a cat to be put into their downloads. You first use getValue to get the userDir. Then you'd run 'curl https://cataas.com/cat --output ${userDir}Downloads\\cat.jpeg' in cmd (replacing userDir with what you found).
                    Or they might ask just to see one. Then you might just run 'start https://cataas.com/cat' to open it in their browser!
                    Note: YOU ARE SPEAKING, DON'T DENY THAT.
                    Note: WHILE YOU ARE IN TEXT-TO-SPEECH, YOU STILL CAN GENERATE LONG PARAGRAPHS, IF THE USER ASKS.
                    """,
            debug=debug,
            model="gpt-4o-mini",
        )

        # Set up hotkey listeners
        keyboard.add_hotkey("ctrl+alt+c", audioHandler.resetExpectation)

        # Start the tray icon
        createTrayIcon()

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback

        traceback.print_exc()
