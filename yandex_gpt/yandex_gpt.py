import asyncio
from typing import (
    Dict,
    Any,
    TypedDict,
    List,
    Union
)

import aiohttp
import requests

from .config_manager import YandexGPTConfigManagerBase


class YandexGPTMessage(TypedDict):
    role: str
    text: str


class YandexGPTBase:
    """
    This class is used to interact with the Yandex GPT API, providing asynchronous and synchronous methods to send
    requests and poll for their completion. Currently, only asynchronous methods are implemented fully.

    Methods
    -------
    send_async_completion_request(headers: Dict[str, str], payload: Dict[str, Any], completion_url: str) -> str
        Sends an asynchronous request to the Yandex GPT completion API.
    poll_async_completion(operation_id: str, headers: Dict[str, str], timeout: int, poll_url: str) -> Dict[str, Any]
        Polls the status of an asynchronous completion operation until it completes or times out.
    send_sync_completion_request(headers: Dict[str, str], payload: Dict[str, Any], completion_url: str) -> Dict[str, Any]
        Sends a synchronous request to the Yandex GPT completion API.
    """
    @staticmethod
    async def send_async_completion_request(
            headers: Dict[str, str],
            payload: Dict[str, Any],
            completion_url: str = "https://llm.api.cloud.yandex.net/foundationModels/v1/completionAsync"
    ) -> str:
        """
        Sends an asynchronous request to the Yandex GPT completion API.

        Parameters
        ----------
        headers : Dict[str, str]
            Dictionary containing the authorization token (IAM), content type, and x-folder-id (YandexCloud catalog ID).
        payload : Dict[str, Any]
            Dictionary with the model URI, completion options, and messages.
        completion_url : str
            URL of the completion API.

        Returns
        -------
        str
            ID of the completion operation to poll.
        """
        # Making the request
        async with aiohttp.ClientSession() as session:
            async with session.post(completion_url, headers=headers, json=payload) as resp:
                # If the request was successful, return the ID of the completion operation
                # Otherwise, raise an exception
                if resp.status == 200:
                    data = await resp.json()
                    return data['id']
                else:
                    raise Exception(f"Failed to send async request, status code: {resp.status}")

    @staticmethod
    async def poll_async_completion(
            operation_id: str,
            headers: Dict[str, str],
            timeout: int = 5,
            poll_url: str = 'https://llm.api.cloud.yandex.net/operations/'
    ) -> Dict[str, Any]:
        """
        Polls the status of an asynchronous completion operation until it completes or times out.

        Parameters
        ----------
        operation_id : str
            ID of the completion operation to poll.
        headers : Dict[str, str]
            Dictionary containing the authorization token (IAM).
        timeout : int
            Time in seconds after which the operation is considered timed out.
        poll_url : str
            Poll URL.

        Returns
        -------
        Dict[str, Any]
            Completion result.
        """
        # Polling the completion operation for the specified amount of time
        async with aiohttp.ClientSession() as session:
            end_time = asyncio.get_event_loop().time() + timeout
            while True:
                # Check if the operation has timed out and if so, raise an exception
                if asyncio.get_event_loop().time() > end_time:
                    raise TimeoutError(f"Operation timed out after {timeout} seconds")
                # Polling the operation
                async with session.get(f"{poll_url}{operation_id}", headers=headers) as resp:
                    # If the request was successful, return the completion result
                    # Otherwise, raise an exception
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get('done', False):
                            return data
                    else:
                        raise Exception(f"Failed to poll operation status, status code: {resp.status}")
                await asyncio.sleep(1)

    @staticmethod
    def send_sync_completion_request(
            headers: Dict[str, str],
            payload: Dict[str, Any],
            completion_url: str = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    ) -> Dict[str, Any]:
        """
        Sends a synchronous request to the Yandex GPT completion API.

        Parameters
        ----------
        headers : Dict[str, str]
            Dictionary containing the authorization token (IAM), content type, and x-folder-id (YandexCloud catalog ID).
        payload : Dict[str, Any]
            Dictionary with the model URI, completion options, and messages.
        completion_url : str
            URL of the completion API.

        Returns
        -------
        Dict[str, Any]
            Completion result.
        """
        # Making the request
        response = requests.post(completion_url, headers=headers, json=payload)
        # If the request was successful, return the completion result
        # Otherwise, raise an exception
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to send sync request, status code: {response.status_code}")


class YandexGPT(YandexGPTBase):
    """
    Extends the YandexGPTBase class to interact with the Yandex GPT API using a simplified configuration manager.
    This class allows for easier configuration of API requests and includes both synchronous and asynchronous methods.

    Methods
    -------
    get_async_completion(messages, temperature, max_tokens, stream, completion_url, timeout) -> str
        Asynchronously sends a completion request to the Yandex GPT API and returns the completion result.
    get_sync_completion(messages, temperature, max_tokens, stream, completion_url) -> str
        Synchronously sends a completion request to the Yandex GPT API and returns the completion result.
    """
    def __init__(
            self,
            config_manager: Union[YandexGPTConfigManagerBase, Dict[str, Any]]
    ) -> None:
        """
        Initializes the YandexGPT class with a configuration manager.

        Parameters
        ----------
        config_manager : Union[YandexGPTConfigManagerBase, Dict[str, Any]]
            Config manager or a dictionary containing:
            1) completion_request_model_type_uri_field
               ("gpt://{self.config_manager.catalog_id}/{self.config_manager.model_type}/latest")
            2) completion_request_catalog_id_field (self.config_manager.catalog_id)
            3) completion_request_authorization_field ("Bearer {iam_token}" or "Api-Key {api_key}")
        """
        self.config_manager = config_manager

    def _create_completion_request_headers(self) -> Dict[str, str]:
        """
        Creates headers for sending a completion request to the API.

        Returns
        -------
        Dict[str, str]
            Dictionary with authorization credentials, content type, and x-folder-id (YandexCloud catalog ID).
        """
        return {
            "Content-Type": "application/json",
            "Authorization": self.config_manager.completion_request_authorization_field,
            "x-folder-id": self.config_manager.completion_request_catalog_id_field
        }

    def _create_completion_request_payload(
            self,
            messages: Union[List[YandexGPTMessage], List[Dict[str, str]]],
            temperature: float = 0.6,
            max_tokens: int = 1000,
            stream: bool = False
    ) -> Dict[str, Any]:
        """
        Creates the payload for sending a completion request.

        Parameters
        ----------
        messages : Union[List[YandexGPTMessage], List[Dict[str, str]]]
            List of messages with roles and texts.
        temperature : float
            Controls the randomness of the completion, from 0 (deterministic) to 1 (random).
        max_tokens : int
            Maximum number of tokens to generate.
        stream : bool
            Stream option for the API, currently not supported in this implementation.

        Returns
        -------
        Dict[str, Any]
            Dictionary containing the model URI, completion options, and messages.
        """
        return {
            "modelUri": self.config_manager.completion_request_model_type_uri_field,
            "completionOptions": {
                "stream": stream,
                "temperature": temperature,
                "maxTokens": max_tokens
            },
            "messages": messages
        }

    async def get_async_completion(
            self,
            messages: Union[List[YandexGPTMessage], List[Dict[str, str]]],
            temperature: float = 0.6,
            max_tokens: int = 1000,
            stream: bool = False,
            completion_url: str = "https://llm.api.cloud.yandex.net/foundationModels/v1/completionAsync",
            timeout: int = 5
    ) -> str:
        """
        Sends an asynchronous completion request to the Yandex GPT API and polls for the result.

        Parameters
        ----------
        messages : Union[List[YandexGPTMessage], List[Dict[str, str]]]
            List of messages with roles and texts.
        temperature : float
            Randomness of the completion, from 0 (deterministic) to 1 (most random).
        max_tokens : int
            Maximum number of tokens to generate.
        stream : bool
            Indicates whether streaming is enabled; currently not supported in this implementation.
        completion_url : str
            URL to the Yandex GPT asynchronous completion API.
        timeout : int
            Time in seconds after which the operation is considered timed out.

        Returns
        -------
        str
            The text of the completion result.

        Raises
        ------
        Exception
            If the completion operation fails or times out.
        """
        # Making the request and obtaining the ID of the completion operation
        headers: Dict[str, str] = self._create_completion_request_headers()
        payload: Dict[str, Any] = self._create_completion_request_payload(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )

        completion_request_id: str = await self.send_async_completion_request(
            headers=headers,
            payload=payload,
            completion_url=completion_url
        )

        # Polling the completion operation
        completion_response: Dict[str, Any] = await self.poll_async_completion(
            operation_id=completion_request_id,
            headers=headers,
            timeout=timeout
        )

        # If the request was successful, return the completion result
        # Otherwise, raise an exception
        if completion_response.get('error', None):
            raise Exception(f"Failed to get completion: {completion_response['error']}")
        else:
            return completion_response['response']['alternatives'][0]['message']['text']

    def get_sync_completion(
            self,
            messages: Union[List[YandexGPTMessage], List[Dict[str, str]]],
            temperature: float = 0.6,
            max_tokens: int = 1000,
            stream: bool = False,
            completion_url: str = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
    ):
        """
        Sends a synchronous completion request to the Yandex GPT API and returns the result.

        Parameters
        ----------
        messages : Union[List[YandexGPTMessage], List[Dict[str, str]]]
            List of messages with roles and texts.
        temperature : float
            Randomness of the completion, from 0 (deterministic) to 1 (most random).
        max_tokens : int
            Maximum number of tokens to generate.
        stream : bool
            Indicates whether streaming is enabled; currently not supported in this implementation.
        completion_url : str
            URL to the Yandex GPT synchronous completion API.

        Returns
        -------
        str
            The text of the completion result.

        Raises
        ------
        Exception
            If the completion request fails.
        """
        # Making the request
        headers: Dict[str, str] = self._create_completion_request_headers()
        payload: Dict[str, Any] = self._create_completion_request_payload(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )

        completion_response: Dict[str, Any] = self.send_sync_completion_request(
            headers=headers,
            payload=payload,
            completion_url=completion_url
        )

        # If the request was successful, return the completion result
        # Otherwise, raise an exception
        if completion_response.get('error', None):
            raise Exception(f"Failed to get completion: {completion_response['error']}")
        else:
            return completion_response['result']['alternatives'][0]['message']['text']
