from typing import List, Dict, Union, Any, TypedDict, Optional

from .yandex_gpt import YandexGPT, YandexGPTMessage
from .config_manager import YandexGPTConfigManagerBase


class YandexGPTThreadStatus(TypedDict):
    status: str
    last_error_message: Optional[str]


class YandexGPTThread(YandexGPT):
    """
    A thread-based interface for interacting with the Yandex GPT model.

    This class manages asynchronous messaging and maintains the state of conversation threads.

    :ivar messages: List of messages maintained in the conversation thread.
    :ivar status: Tracks the current status and last error message of the thread.

    Attributes
    ----------
    messages : List[YandexGPTMessage]
        Maintained list of messages in the conversation thread.
    status : YandexGPTThreadStatus
        Current status and last error information of the thread.
    """
    def __init__(
            self,
            config_manager: Union[YandexGPTConfigManagerBase, Dict[str, Any]],
            messages: Optional[List[YandexGPTMessage]] = None,
    ) -> None:
        """
        Initializes a new instance of the YandexGPTThread.

        Parameters
        ----------
        config_manager : Union[YandexGPTConfigManagerBase, Dict[str, Any]]
            Configuration manager for the Yandex GPT model.
        messages : Optional[List[YandexGPTMessage]], optional
            Initial list of messages within the thread, by default None.
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

        Parameters
        ----------
        role : str
            The role of the message, typically 'user' or 'assistant'.
        text : str
            The content of the message.
        """
        self.messages.append(YandexGPTMessage(role=role, text=text))

    def __getitem__(self, index):
        """
        Allows retrieval of a message by index from the conversation thread.

        Parameters
        ----------
        index : int
            Index of the message to retrieve.

        Returns
        -------
        YandexGPTMessage
            The message at the specified index.
        """
        return self.messages[index]

    def __len__(self):
        """
        Returns the number of messages in the conversation thread.

        Returns
        -------
        int
            The number of messages.
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
        Runs the thread asynchronously, requesting and appending completion from the Yandex GPT model.

        Parameters
        ----------
        temperature : float
            Sampling temperature, scales the likelihood of less probable tokens. Value from 0 to 1.
        max_tokens : int
            Maximum number of tokens to generate.
        stream : bool
            Stream responses from the API (not currently supported).
        completion_url : str
            URL of the asynchronous completion API.
        timeout : int
            Timeout in seconds for the asynchronous call.

        Raises
        ------
        Exception
            If the thread is already running.
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

    def run_sync(
            self,
            temperature: float = 0.6,
            max_tokens: int = 1000,
            stream: bool = False,
            completion_url: str = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    ):
        """
        Runs the thread synchronously, requesting and appending completion from the Yandex GPT model.

        Parameters
        ----------
        temperature : float
            Sampling temperature, scales the likelihood of less probable tokens. Value from 0 to 1.
        max_tokens : int
            Maximum number of tokens to generate.
        stream : bool
            Stream responses from the API (not currently supported).
        completion_url : str
            URL of the synchronous completion API.

        Raises
        ------
        Exception
            If the thread is already running.
        """
        if self.status["status"] == "running":
            raise Exception("Thread is already running")
        else:
            self.status["status"] = "running"

            try:
                completion_text = self.get_sync_completion(
                    messages=self.messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=stream,
                    completion_url=completion_url
                )
                self.add_message(role="assistant", text=completion_text)
            except Exception as e:
                self.status["status"] = "error"
                self.status["last_error_message"] = str(e)
            finally:
                self.status["status"] = "idle"
