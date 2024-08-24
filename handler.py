import openai


class Assistant:
    def __init__(
        self,
        model="gpt-4o-mini",
        temperature=1.25,
        seed=None,
        tools=None,
        extraInstruct=None,
        debug=False,
    ):
        self.messages = []
        if extraInstruct is not None:
            self.messages.append({"role": "system", "content": extraInstruct})
        self.model = model
        self.debug = debug
        self.toAppend = []
        self.temperature = temperature
        self.seed = seed
        self.tools = tools

    def debugPrint(self, *args, **kwargs):
        if self.debug:
            print(*args, **kwargs)

    def appendMessage(self, role, content):
        self.messages.append({"role": role, "content": content})

    def appendMessageAfterTool(self, role, content):
        self.toAppend.append({"role": role, "content": content})

    def stream(self, AssistantCallbacks, continueOnTool=True, contentSoFar=""):
        assistantCallbacks = AssistantCallbacks(self)
        content = ""

        while True:
            with openai.chat.completions.create(
                model=self.model,
                messages=self.messages,
                temperature=self.temperature,
                tools=self.tools,
                seed=self.seed,
                stream=True,
            ) as completion:
                toolCall = {"args": "", "name": "", "id": ""}
                for chunk in completion:
                    choice = chunk.choices[0]

                    # Handle content delta
                    if choice.delta.content is not None:
                        content += choice.delta.content
                        assistantCallbacks.delta(
                            chunk=chunk, choice=choice, content=content
                        )

                    # Handle tool calls
                    if choice.delta.tool_calls is not None:
                        for call in choice.delta.tool_calls:
                            toolArguments = call.function.arguments
                            toolName = call.function.name
                            toolId = call.id

                            if toolArguments is not None:
                                toolCall["args"] += toolArguments
                            if toolId is not None:
                                toolCall["id"] += toolId
                            if toolName is not None:
                                toolCall["name"] += toolName

                            assistantCallbacks.toolDelta(**toolCall)

                    # Handle finish reasons
                    if choice.finish_reason is not None:
                        reason = choice.finish_reason
                        if reason == "content_filter":
                            break
                        elif reason == "tool_calls":
                            if content is None:
                                content = " "
                            if (
                                toolCall["name"]
                                and toolCall["args"]
                                and toolCall["id"] is not None
                            ):
                                self.messages.append(
                                    {
                                        "role": "assistant",
                                        "content": content,
                                        "tool_calls": [
                                            {
                                                "id": toolCall["id"],
                                                "type": "function",
                                                "function": {
                                                    "name": toolCall["name"],
                                                    "arguments": toolCall["args"],
                                                },
                                            }
                                        ],
                                    }
                                )

                            assistantCallbacks.chunkFinish(content)
                            self.messages.append(
                                assistantCallbacks.toolFinish(
                                    name=toolCall["name"],
                                    args=toolCall["args"],
                                    id=toolCall["id"],
                                    content=content,
                                    assistant=self,
                                )
                            )
                            if len(self.toAppend) > 0:
                                self.debugPrint(f"Appending after tool")
                                self.messages.append(self.toAppend[0])
                                self.toAppend.pop(0)

                            if not continueOnTool:
                                return contentSoFar + content

                        elif reason == "stop":
                            assistantCallbacks.chunkFinish(content)
                            assistantCallbacks.fullFinish(content + contentSoFar)
                            if content is None:
                                content = " "
                            self.messages.append(
                                {"role": "assistant", "content": content}
                            )
                            return contentSoFar + content
