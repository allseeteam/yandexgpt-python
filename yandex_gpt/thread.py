from typing import List, Dict, Union, Any, TypedDict, Optional

from .yandex_gpt import YandexGPT, YandexGPTMessage
from .config_manager import YandexGPTConfigManagerBase


class YandexGPTThreadStatus(TypedDict):
    status: str
    last_error_message: Optional[str]


class YandexGPTThread(YandexGPT):
    def __init__(
            self,
            config_manager: Union[YandexGPTConfigManagerBase, Dict[str, Any]],
            messages: Optional[List[YandexGPTMessage]] = None,
    ) -> None:
        """
        A thread-based interface for interacting with the Yandex GPT model, managing asynchronous messaging and
        maintaining the state of conversation threads.
        :param config_manager: Yandex GPT config manager
        :param messages: optional list of messages with roles and texts
        """
        super().__init__(config_manager=config_manager)

        if messages:
            self.messages = messages
        else:
            self.messages = []

        self.status = YandexGPTThreadStatus(
            status="created",
            last_error_message=None
        )

    def add_message(
            self,
            role: str,
            text: str
    ) -> None:
        """
        Appends a new message to the conversation thread.
        :param role: message role
        :param text: message text
        """
        self.messages.append(YandexGPTMessage(role=role, text=text))

    def __getitem__(self, index):
        """
        Allows to get a message from the conversation thread in array-like style.
        :param index: index of the message
        :return: message from the Thread by index
        """
        return self.messages[index]

    def __len__(self):
        """
        Allows to get the number of messages in the conversation thread.
        :return: number of messages in the Thread
        """
        return len(self.messages)

    async def run_async(
            self,
            temperature: float = 0.6,
            max_tokens: int = 1000,
            stream: bool = False,
            completion_url: str = "https://llm.api.cloud.yandex.net/foundationModels/v1/completionAsync",
            timeout: int = 15
    ):
        """
        Starts the thread.
        :param temperature: from 0 to 1
        :param max_tokens: maximum number of tokens
        :param stream: IDK whould it work in current realization (keep it False)
        :param completion_url: URL of the completion API
        :param timeout: time after which the operation is considered timed out
        """
        if self.status["status"] == "running":
            raise Exception("Thread is already running")
        else:
            self.status["status"] = "running"

            try:
                completion_text = await self.get_async_completion(
                    messages=self.messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=stream,
                    completion_url=completion_url,
                    timeout=timeout
                )
                self.add_message(role="assistant", text=completion_text)
            except Exception as e:
                self.status["status"] = "error"
                self.status["last_error_message"] = str(e)
            finally:
                self.status["status"] = "idle"
