import os
from typing import (
    Optional,
    List
)


# List of available YaGPT models to use (May be needs to be moved to config file in the future)
available_models: List[str] = [
        "yandexgpt",
        "yandexgpt-lite",
        "summarization"
    ]


class YandexGPTConfigManagerBase:
    def __init__(
            self,
            model_type: Optional[str] = None,
            catalog_id: Optional[str] = None,
            iam_token: Optional[str] = None,
            api_key: Optional[str] = None,
    ) -> None:
        """
        Base class for YaGPT configuration. It contains model type, catalog ID, IAM token or API key, which are used for
        authorization when making requests to the completion endpoint.

        :param model_type: model type to use. Supported values: 'yandexgpt', 'yandexgpt-lite', 'summarization'.
        :param catalog_id: Catalog ID on YandexCloud to use.
        :param iam_token: IAM token to use (you provide either iam_token or api_key, if you provide both, iam_token will
        be used in the future) (how to get IAM token:
        https://yandex.cloud/ru/docs/iam/operations/iam-token/create-for-sa).
        :param api_key: API key to use (how to get API key:
        https://yandex.cloud/ru/docs/iam/operations/api-key/create).
        """
        self.model_type: Optional[str] = model_type
        self.catalog_id: Optional[str] = catalog_id
        self.iam_token: Optional[str] = iam_token
        self.api_key: Optional[str] = api_key

    @property
    def completion_request_authorization_field(self) -> str:
        """
        A dynamic property that returns authorization field for the completion request header.
        Either iam_token or api_key must be set, otherwise ValueError will be raised.
        :return: authorization field for the completion request header in the form of a string: "Bearer {iam_token}" or
        "Api-Key {api_key}".
        """
        # Checking if either iam_token or api_key is set and returning the authorization field string
        if self.iam_token:
            return f"Bearer {self.iam_token}"
        elif self.api_key:
            return f"Api-Key {self.api_key}"
        else:
            raise ValueError("IAM token or API key is not set")

    @property
    def completion_request_catalog_id_field(self) -> str:
        """
        A dynamic property that returns catalog id field for the completion request header. If catalog_id is not set,
        ValueError will be raised.
        :return: catalog id field for the completion request header in the form of a string: "{catalog_id}".
        """
        # Checking if catalog_id is set and returning the catalog id field string
        if self.catalog_id:
            return self.catalog_id
        else:
            raise ValueError("Catalog ID is not set")

    @property
    def completion_request_model_type_uri_field(self) -> str:
        """
        A dynamic property that returns model type field for the completion request payload. If model_type or catalog_id
        is not set, ValueError will be raised. If model_type not in available_models, ValueError will be raised.
        :return: model type field for the completion request header in the form of a string:
        "gpt://{self.config_manager.catalog_id}/{self.config_manager.model_type}/latest".
        """
        global available_models

        # Checking if model_type is in available_models
        if self.model_type not in available_models:
            raise ValueError(f"Model type {self.model_type} is not supported. Supported values: {available_models}")

        # Checking if model_type and catalog_id are set and returning the model type URI field string
        if self.model_type and self.catalog_id:
            return f"gpt://{self.catalog_id}/{self.model_type}/latest"
        else:
            raise ValueError("Model type or catalog ID is not set")


class YandexGPTConfigManagerForAPIKey(YandexGPTConfigManagerBase):
    def __init__(
            self,
            model_type: Optional[str] = None,
            catalog_id: Optional[str] = None,
            api_key: Optional[str] = None,
    ) -> None:
        """
        Class for YaGPT configuration using API key. It contains model type, catalog ID and API key, which are used for
        authorization when making requests to the completion endpoint. You can set parameters using the constructor or
        set them in the environment variables: YANDEX_GPT_MODEL_TYPE, YANDEX_GPT_CATALOG_ID and YANDEX_GPT_API_KEY.

        :param model_type: model type to use. Supported values: 'yandexgpt', 'yandexgpt-lite', 'summarization'.
        :param catalog_id: Catalog ID on YandexCloud to use.
        :param api_key: API key to use (how to get API key:
        https://yandex.cloud/ru/docs/iam/operations/api-key/create).
        """
        # Setting model type, catalog ID and API key from the constructor
        super().__init__(
            model_type=model_type,
            catalog_id=catalog_id,
            api_key=api_key
        )

        # Setting model type, catalog ID and API key from the environment variables if they are set
        self._set_config_from_env_vars()

        # Checking if model type, catalog ID and API key are set
        self._check_config()

    def _set_config_from_env_vars(self) -> None:
        """
        Sets config from environment variables. If environment variables are not set, default values will be used.
        """
        self.model_type = os.environ.get("YANDEX_GPT_MODEL_TYPE", self.model_type)
        self.catalog_id = os.environ.get("YANDEX_GPT_CATALOG_ID", self.catalog_id)
        self.api_key = os.environ.get("YANDEX_GPT_API_KEY", self.api_key)

    def _check_config(self) -> None:
        """
        Checks if model type, catalog ID and API key are set. If not, ValueError will be raised.
        """
        if not self.model_type:
            raise ValueError(
                "Model type is not set. You can ether provide it in the constructor or set in YANDEX_GPT_MODEL_TYPE "
                "environment variable"
            )
        elif not self.catalog_id:
            raise ValueError(
                "Catalog ID is not set. You can ether provide it in the constructor or set in YANDEX_GPT_CATALOG_ID "
                "environment variable"
            )
        elif not self.api_key:
            raise ValueError(
                "API key is not set. You can ether provide it in the constructor or set in YANDEX_GPT_API_KEY "
                "environment variable"
            )
