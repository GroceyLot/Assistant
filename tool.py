import json
import os
import subprocess
import datetime
import time
import win32api
import win32con
import win32gui
from PIL import ImageGrab
import pyautogui
import tempfile
import base64
from io import BytesIO
from sound import playSound

class Tools:
    def __init__(self, audioHandler, debug=False):
        true = True
        false = False
        self.debug = debug
        self.toolsTemp = [
            {
                "name": "getScreenShot",
                "description": "Get a screenshot of one of my monitors for context, use this when the user asks you to look at their screen.",
                "strict": true,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "monitor": {
                            "type": "string",
                            "description": "Which monitor, 1 or 2?",
                            "enum": ["1", "2"],
                        }
                    },
                    "additionalProperties": false,
                    "required": ["monitor"],
                },
            },
            {
                "name": "getFileStructure",
                "description": "See what files are underneath a specific folder",
                "strict": true,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The location under which to find them, e.g. C:\\Users\\walte\\Documents\\Projects\\Love2D\\Example",
                        }
                    },
                    "additionalProperties": false,
                    "required": ["location"],
                },
            },
            {
                "name": "runCmd",
                "description": "Run a command in cmd or powershell. This may not return anything, also be careful, as if you run 'notepad' it will not continue your tts until the user closes it, so instead run 'start notepad'",
                "strict": true,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The command to run.",
                        },
                        "shell": {
                            "type": "string",
                            "description": "The shell to use",
                            "enum": ["cmd", "powershell"],
                        },
                        "location": {
                            "type": "string",
                            "description": "The location to run the command, e.g. C:\\Users\\walte.",
                        },
                        "admin": {
                            "type": "boolean",
                            "description": "Whether or not to request administrator permissions before running the commands",
                        },
                    },
                    "additionalProperties": false,
                    "required": ["command", "shell", "location", "admin"],
                },
            },
            {
                "name": "createFileOrFolder",
                "description": "Create a file/folder at a directory",
                "strict": true,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The directory e.g. C:\\Users\\walte",
                        },
                        "name": {
                            "type": "string",
                            "description": "The name of the file/folder, if file then you need an extension like .bat or .lua",
                        },
                        "type": {
                            "type": "string",
                            "description": "File or folder?",
                            "enum": ["file", "folder"],
                        },
                    },
                    "additionalProperties": false,
                    "required": ["location", "name", "type"],
                },
            },
            {
                "name": "writeFile",
                "description": "Write content to a file",
                "strict": true,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The file location, e.g. C:\\Users\\walte\\Documents\\Projects\\Love2D\\Example\\main.lua",
                        },
                        "content": {
                            "type": "string",
                            "description": "The file content, in the format specified by contentFormat",
                        },
                        "contentFormat": {
                            "type": "string",
                            "description": "The format for the content, binary is 0s and 1s, ascii is your characters interpreted as ascii, plainText is just text",
                            "enum": ["binary", "ascii", "plainText"],
                        },
                    },
                    "additionalProperties": false,
                    "required": ["location", "content", "contentFormat"],
                },
            },
            {
                "name": "readFile",
                "description": "Read content from a file",
                "strict": true,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The file location, e.g. C:\\Users\\walte\\Documents\\Projects\\Love2D\\Example\\main.lua",
                        },
                        "contentFormat": {
                            "type": "string",
                            "description": "The format for the content to be sent as",
                            "enum": ["binary", "ascii", "plainText"],
                        },
                    },
                    "additionalProperties": false,
                    "required": ["location", "contentFormat"],
                },
            },
            {
                "name": "getValue",
                "description": "Get lots of useful info",
                "strict": true,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "value": {
                            "type": "string",
                            "description": "The value to get",
                            "enum": ["time", "userDir", "date"],
                        }
                    },
                    "additionalProperties": false,
                    "required": ["value"],
                },
            },
            {
                "name": "afterTimeRemindMe",
                "description": "Remind me something after time",
                "strict": true,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "time": {
                            "type": "integer",
                            "description": "The time to wait in unit units",
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["minutes", "hours", "days", "seconds"],
                        },
                        "title": {
                            "type": "string",
                            "description": "The title of the notification",
                        },
                        "text": {"type": "string", "description": "What to say"},
                    },
                    "additionalProperties": false,
                    "required": ["time", "unit", "title", "text"],
                },
            },
            {
                "name": "requestConsent",
                "description": "Request consent to do a specific action",
                "strict": true,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "consent": {
                            "type": "string",
                            "description": "What do you want consent to do?",
                        }
                    },
                    "additionalProperties": false,
                    "required": ["consent"],
                },
            },
            {
                "name": "typeText",
                "description": "Type some text on the keyboard",
                "strict": true,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "The text to type"}
                    },
                    "additionalProperties": false,
                    "required": ["text"],
                },
            },
            {
                "name": "runAhkMacro",
                "description": "Run a keyboard macro in autohotkey script",
                "strict": true,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "macro": {"type": "string", "description": "The macro code"}
                    },
                    "additionalProperties": false,
                    "required": ["macro"],
                },
            },
            {
                "name": "getFocusedWindow",
                "description": "Get the currently focused window",
                "strict": false,
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
            {
                "name": "exitChat",
                "description": "Pause the chat until the user starts it again",
                "strict": false,
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        ]
        self.tools = []
        for tool in self.toolsTemp:
            self.tools.append({"type": "function", "function": tool})

        self.toolFuncs = {
            "getScreenShot": self.getScreenShot,
            "getFileStructure": self.getFileStructure,
            "runCmd": self.runCmd,
            "createFileOrFolder": self.createFileOrFolder,
            "writeFile": self.writeFile,
            "readFile": self.readFile,
            "getValue": self.getValue,
            "afterTimeRemindMe": self.afterTimeRemindMe,
            "requestConsent": self.requestConsent,
            "typeText": self.typeText,
            "runAhkMacro": self.runAhkMacro,
            "getFocusedWindow": self.getFocusedWindow,
            "exitChat": self.exitChat,
            "remember": self.remember,
            "forget": self.forget,
        }
        self.audioHandler = audioHandler

    def debugPrint(self, *args, **kwargs):
        if self.debug:
            print(*args, **kwargs)

    def tool(self, name, args, id, content, assistant):
        self.debugPrint(f"Tool called: {name} with args: {args}")
        arguments = json.loads(args)
        toolResponse = self.toolFuncs[name](arguments, content, assistant)
        self.debugPrint(f"Tool response: {toolResponse}")
        output = {"role": "tool", "tool_call_id": id, "content": toolResponse}
        return output

    # Example modification of a function to include debug prints
    def getScreenShot(self, params, content, assistant):
        playSound("sounds\\screenshot.wav")
        self.debugPrint(f"getScreenShot called with params: {params}")
        monitor = int(params["monitor"]) - 1
        screens = ImageGrab.grab()

        # Validate the monitor number
        if monitor > 1:
            return "Only up to 2 monitors are supported."

        # If multiple monitors are available, adjust the screenshot accordingly
        monitors = screens.split()  # Assuming this splits the image based on monitors
        if monitor >= len(monitors):
            return f"Monitor {monitor + 1} does not exist."

        screenshot = monitors[monitor]
        self.debugPrint("Screenshot captured.")

        # Save screenshot to a BytesIO object instead of a file
        img_buffer = BytesIO()
        screenshot.save(img_buffer, format="PNG")
        img_buffer.seek(0)

        # Encode the image to base64
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode("utf-8")
        self.debugPrint("Screenshot encoded to base64.")

        # Create the image URL
        image_url = f"data:image/png;base64,{img_base64}"
        assistant.appendMessageAfterTool(
            "user", [{"type": "image_url", "image_url": {"url": image_url}}]
        )
        return f"The image will be placed in a message by the user"

    def getFileStructure(self, params, content, assistant):
        self.debugPrint(f"getFileStructure called with params: {params}")
        location = params["location"]
        if os.path.exists(location):
            file_structure = os.listdir(location)
            self.debugPrint(f"File structure at {location}: {file_structure}")
            return f"File structure at {location}: {file_structure}"
        else:
            self.debugPrint(f"Location {location} does not exist.")
            return f"Location {location} does not exist."

    def exitChat(self, params, content, assistant):
        self.debugPrint("exitChat called.")
        self.audioHandler.resetExpectation()
        return f"Conversation paused, any further text sent will be said."

    def runCmd(self, params, content, assistant):
        self.debugPrint(f"runCmd called with params: {params}")
        command = params["command"]
        shell = params["shell"]
        location = params["location"]
        admin = params["admin"]

        try:
            if shell == "cmd":
                full_command = f'cmd /c "{command}"'
            else:
                full_command = f'powershell -Command "{command}"'

            if admin:
                full_command = f"runas /user:Administrator {full_command}"

            self.debugPrint(f"Running command: {full_command} in location: {location}")
            result = subprocess.run(
                full_command, shell=True, cwd=location, capture_output=True, text=True
            )
            self.debugPrint(
                f"Command output: {result.stdout if result.returncode == 0 else result.stderr}"
            )
            return result.stdout if result.returncode == 0 else result.stderr
        except Exception as e:
            self.debugPrint(f"Error running command: {e}")
            return str(e)

    def createFileOrFolder(self, params, content, assistant):
        self.debugPrint(f"createFileOrFolder called with params: {params}")
        location = params["location"]
        name = params["name"]
        type_ = params["type"]

        full_path = os.path.join(location, name)
        if type_ == "file":
            try:
                self.debugPrint(f"Creating file at: {full_path}")
                with open(full_path, "w") as f:
                    f.write("")  # Create an empty file
                self.debugPrint(f"File {full_path} created.")
                return f"File {full_path} created."
            except Exception as e:
                self.debugPrint(f"Error creating file: {e}")
                return str(e)
        elif type_ == "folder":
            try:
                self.debugPrint(f"Creating folder at: {full_path}")
                os.makedirs(full_path, exist_ok=True)
                self.debugPrint(f"Folder {full_path} created.")
                return f"Folder {full_path} created."
            except Exception as e:
                self.debugPrint(f"Error creating folder: {e}")
                return str(e)
        else:
            self.debugPrint("Invalid type specified.")
            return "Invalid type specified."

    def writeFile(self, params, content, assistant):
        self.debugPrint(f"writeFile called with params: {params}")
        location = params["location"]
        file_content = params["content"]
        content_format = params["contentFormat"]

        try:
            self.debugPrint(f"Writing to file at: {location}")
            with open(location, "w") as f:
                if content_format == "plainText":
                    f.write(file_content)
                elif content_format == "ascii":
                    f.write(file_content.encode("ascii").decode("ascii"))
                elif content_format == "binary":
                    f.write(file_content.encode("ascii").decode("ascii"))
            self.debugPrint(f"Written content to {location}.")
            return f"Written content to {location}."
        except Exception as e:
            self.debugPrint(f"Error writing file: {e}")
            return str(e)

    def readFile(self, params, content, assistant):
        self.debugPrint(f"readFile called with params: {params}")
        location = params["location"]
        content_format = params["contentFormat"]

        try:
            self.debugPrint(f"Reading file at: {location}")
            with open(location, "r") as f:
                if content_format == "plainText":
                    content = f.read()
                elif content_format == "ascii":
                    content = f.read().encode("ascii").decode("ascii")
                elif content_format == "binary":
                    content = f.read().encode("ascii").decode("ascii")
            self.debugPrint(f"File content: {content}")
            return content
        except Exception as e:
            self.debugPrint(f"Error reading file: {e}")
            return str(e)

    def getValue(self, params, content, assistant):
        self.debugPrint(f"getValue called with params: {params}")
        value = params["value"]

        if value == "time":
            current_time = time.strftime("%I:%M %p")
            self.debugPrint(f"Current time is {current_time}.")
            return f"Current time is {current_time}."
        elif value == "userDir":
            user_dir = os.environ["USERPROFILE"]
            self.debugPrint(f"User directory is {user_dir}.")
            return user_dir
        elif value == "date":
            current_date = datetime.date.today().strftime("%Y-%m-%d")
            self.debugPrint(f"Today's date is {current_date}.")
            return f"Today's date is {current_date}."
        else:
            self.debugPrint("Unknown value requested.")
            return "Unknown value requested."

    def afterTimeRemindMe(self, params, content, assistant):
        self.debugPrint(f"afterTimeRemindMe called with params: {params}")
        time_delay = params["time"]
        unit = params["unit"]
        title = params["title"]
        text = params["text"]

        now = datetime.datetime.now()
        if unit == "seconds":
            trigger_time = now + datetime.timedelta(seconds=time_delay)
        elif unit == "minutes":
            trigger_time = now + datetime.timedelta(minutes=time_delay)
        elif unit == "hours":
            trigger_time = now + datetime.timedelta(hours=time_delay)
        elif unit == "days":
            trigger_time = now + datetime.timedelta(days=time_delay)

        formatted_time = trigger_time.strftime("%H:%M")
        task_name = f"Reminder_{title}"

        schtasks_command = f'schtasks /create /tn "{task_name}" /tr "msg * {text}" /sc once /st {formatted_time} /f'
        self.debugPrint(f"Scheduling reminder with command: {schtasks_command}")
        subprocess.run(schtasks_command, shell=True)

        return f"Reminder scheduled: {title} - {text} at {formatted_time}."

    def requestConsent(self, params, content, assistant):
        self.debugPrint(f"requestConsent called with params: {params}")
        consent = params["consent"]
        response = win32api.MessageBox(
            0, f"{consent}", "Consent Request", win32con.MB_YESNO
        )
        self.debugPrint(
            f"Consent response: {'granted' if response == win32con.IDYES else 'denied'}"
        )
        if response == win32con.IDYES:
            return "Consent granted."
        else:
            return "Consent denied."

    def typeText(self, params, content, assistant):
        self.debugPrint(f"typeText called with params: {params}")
        text = params["text"]
        pyautogui.write(text)
        self.debugPrint(f"Typed text: {text}")
        return f"Typed text: {text}"

    def runAhkMacro(self, params, content, assistant):
        self.debugPrint(f"runAhkMacro called with params: {params}")
        macro = params["macro"]
        with tempfile.NamedTemporaryFile(suffix=".ahk", delete=False) as tmp_file:
            tmp_file.write(macro.encode("utf-8"))
            ahk_script_path = tmp_file.name
        self.debugPrint(f"Running AHK macro from file: {ahk_script_path}")
        subprocess.run(["autohotkey", ahk_script_path])
        return f"Executed AHK macro."

    def getFocusedWindow(self, params, content, assistant):
        self.debugPrint("getFocusedWindow called.")
        hwnd = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(hwnd)
        self.debugPrint(f"Currently focused window: {window_title}")
        return f"Currently focused window: {window_title}."
