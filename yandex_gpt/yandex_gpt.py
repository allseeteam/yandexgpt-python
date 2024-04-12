import asyncio
from typing import (
    Dict,
    Any,
    TypedDict,
    List,
    Union
)

import aiohttp

from .config_manager import YandexGPTConfigManagerBase


class YandexGPTMessage(TypedDict):
    role: str
    text: str


class YandexGPTBase:
    """
    This class is used to interact with the Yandex GPT API. Currently, only async methods are implemented.
    """
    @staticmethod
    async def send_async_completion_request(
            headers: Dict[str, str],
            payload: Dict[str, Any],
            completion_url: str = "https://llm.api.cloud.yandex.net/foundationModels/v1/completionAsync"
    ) -> str:
        """
        Sends async request to completion API.
        :param headers: dict with authorization token (IAM), content type, and x-folder-id (YandexCloud catalog ID)
        :param payload: dict with model URI, completion options, and messages
        :param completion_url: URL of the completion API
        :return: ID of the completion operation to poll
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
        Polls async completion operation.
        :param operation_id: ID of the completion operation to poll
        :param headers: dict with authorization token (IAM)
        :param timeout: time after which the operation is considered timed out
        :param poll_url: poll URL
        :return: completion result
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


class YandexGPT(YandexGPTBase):
    def __init__(
            self,
            config_manager: Union[YandexGPTConfigManagerBase, Dict[str, Any]]
    ) -> None:
        """
        This class is used to interact with the Yandex GPT API with easy to use config manager. Currently, only async
        methods are implemented. If you want to get more advanced features, take a look at the YandexGPTBase class.

        :param config_manager: Config manager or a dictionary, containing:
        1) completion_request_model_type_uri_field
        ("gpt://{self.config_manager.catalog_id}/{self.config_manager.model_type}/latest")
        2) completion_request_catalog_id_field (self.config_manager.catalog_id)
        3) completion_request_authorization_field ("Bearer {iam_token}" or "Api-Key {api_key}")
        """
        self.config_manager = config_manager

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
        Sends async completion request to the Yandex GPT API and polls the result.
        :param messages: list of messages with roles and texts (dict or YandexGPTMessage)
        :param temperature: from 0 to 1
        :param max_tokens: maximum number of tokens
        :param stream: IDK whould it work in current realization (keep it False)
        :param completion_url: URL of the completion API
        :param timeout: time after which the operation is considered timed out
        :return: text of the completion
        """
        # Making the request and obtaining the ID of the completion operation
        headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "Authorization": self.config_manager.completion_request_authorization_field,
            "x-folder-id": self.config_manager.completion_request_catalog_id_field
        }
        payload: Dict[str, Any] = {
            "modelUri": self.config_manager.completion_request_model_type_uri_field,
            "completionOptions": {
                "stream": stream,
                "temperature": temperature,
                "maxTokens": max_tokens
            },
            "messages": messages
        }

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
