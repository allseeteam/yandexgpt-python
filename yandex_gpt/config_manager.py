import base64
import os
import time
from typing import (
    Optional,
    List, Dict, Any
)

import jwt
import requests


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


class YandexGPTConfigManagerForIAMToken(YandexGPTConfigManagerBase):
    def __init__(
            self,
            model_type: Optional[str] = None,
            catalog_id: Optional[str] = None,
            iam_token: Optional[str] = None,
    ) -> None:
        """
        Class for YaGPT configuration using IAM token. It contains model type, catalog ID and IAM token, which are used
        for authorization when making requests to the completion endpoint.

        For initialization, you can ether:
        1) Provide model type, IAM token, and catalog ID directly as constructor parameters;
        2) Use YANDEX_GPT_MODEL_TYPE, YANDEX_GPT_CATALOG_ID and YANDEX_GPT_IAM_TOKEN environment variables for direct
        initialization;
        3) Use YANDEX_GPT_IAM_URL, YANDEX_GPT_SERVICE_ACCOUNT_ID, YANDEX_GPT_SERVICE_ACCOUNT_KEY_ID,
        YANDEX_GPT_CATALOG_ID and YANDEX_GPT_PRIVATE_KEY environment variables for generating IAM token;

        :param model_type: model type to use. Supported values: 'yandexgpt', 'yandexgpt-lite', 'summarization'.
        :param catalog_id: Catalog ID on YandexCloud to use.
        :param iam_token: IAM token to use (how to get IAM token:
        https://yandex.cloud/ru/docs/iam/operations/iam-token/create-for-sa).
        """
        # Setting model type, catalog ID and IAM token from the constructor
        super().__init__(
            model_type=model_type,
            catalog_id=catalog_id,
            iam_token=iam_token
        )

        # Setting model type, catalog ID and IAM token using one of options
        self._set_config()

        # Checking if model type, catalog ID and API key are set
        self._check_config()

    def _set_config(self) -> None:
        """
        Sets model type, IAM token, and catalog id or tries to initialize them from environment variables.
        """
        if self.iam_token and self.catalog_id and self.model_type:
            # If all parameters are set, do nothing
            return
        else:
            # Trying to initialize from environment variables
            self._set_config_from_env_vars()

    def _set_config_from_env_vars(self) -> None:
        """
        Sets config from environment variables. If environment variables are not set, default values will be used. If
        IAM token is not set in environment variables, trying to generate it using environment variables.
        """
        self.model_type = os.environ.get("YANDEX_GPT_MODEL_TYPE", self.model_type)
        self.catalog_id = os.environ.get("YANDEX_GPT_CATALOG_ID", self.catalog_id)
        self.iam_token = os.environ.get("YANDEX_GPT_IAM_TOKEN", self.iam_token)

        if not self.iam_token:
            # If IAM token is not set, trying to initialize from config and private key
            self._set_iam_from_env_config_and_private_key()

    def _set_iam_from_env_config_and_private_key(self) -> None:
        """
        Generates and sets IAM token from environment variables.
        """
        # Getting environment variables
        iam_url: str = os.getenv("YANDEX_GPT_IAM_URL", "https://iam.api.cloud.yandex.net/iam/v1/tokens")
        service_account_id: Optional[str] = os.getenv("YANDEX_GPT_SERVICE_ACCOUNT_ID", None)
        service_account_key_id: Optional[str] = os.getenv("YANDEX_GPT_SERVICE_ACCOUNT_KEY_ID", None)
        catalog_id: Optional[str] = os.getenv("YANDEX_GPT_CATALOG_ID", None)
        private_key: Optional[str] = os.getenv("YANDEX_GPT_PRIVATE_KEY", None)

        # Checking environment variables
        if not all([iam_url, service_account_id, service_account_key_id, catalog_id, private_key]):
            raise ValueError("One or more environment variables for IAM token generation are missing.")

        # Generating JWT token
        jwt_token: str = self._generate_jwt_token(
            service_account_id=service_account_id,
            private_key=private_key,
            key_id=service_account_key_id,
            url=iam_url,
        )

        # Swapping JWT token to IAM
        self.iam_token = self._swap_jwt_to_iam(jwt_token, iam_url)

    @staticmethod
    def _generate_jwt_token(
            service_account_id: str,
            private_key: str,
            key_id: str,
            url: str = "https://iam.api.cloud.yandex.net/iam/v1/tokens",
    ) -> str:
        """
        Generates JWT token from service account id, private key, and key id.
        :param service_account_id: service account id
        :param private_key: private key
        :param key_id: key id
        :param url: url for swapping JWT token to IAM request
        :return: encoded JWT token
        """
        # Generating JWT token
        now: int = int(time.time())
        payload: Dict[str, Any] = {
            "aud": url,
            "iss": service_account_id,
            "iat": now,
            "exp": now + 360,
        }
        encoded_token: str = jwt.encode(
            payload,
            private_key,
            algorithm="PS256",
            headers={"kid": key_id}
        )
        return encoded_token

    @staticmethod
    def _swap_jwt_to_iam(
            jwt_token: str, url: str = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
    ) -> str:
        """
        Swaps JWT token to IAM token.
        :param jwt_token: encoded JWT token
        :param url: url for swapping JWT token to IAM request
        :return: IAM token
        """
        headers: Dict[str, str] = {"Content-Type": "application/json"}
        data: Dict[str, str] = {"jwt": jwt_token}
        # Swapping JWT token to IAM
        response: requests.Response = requests.post(
            url,
            headers=headers,
            json=data
        )
        if response.status_code == 200:
            # If succeeded to get IAM token return it
            return response.json()["iamToken"]
        else:
            # If failed to get IAM token raise an exception
            raise Exception(f"Failed to get IAM token. Status code: {response.status_code}\n{response.text}")

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
        elif not self.iam_token:
            raise ValueError(
                "IAM token is not set. You can ether provide it in the constructor or set in YANDEX_GPT_IAM_TOKEN "
                "environment variable or generate it automatically by setting YANDEX_GPT_SERVICE_ACCOUNT_ID, "
                "YANDEX_GPT_SERVICE_ACCOUNT_KEY_ID, YANDEX_GPT_CATALOG_ID and YANDEX_GPT_PRIVATE_KEY environment "
                "variables"
            )


class YandexGPTConfigManagerForIAMTokenWithBase64Key(YandexGPTConfigManagerForIAMToken):
    """
    This class is modified version of YandexGPTConfigManagerForIAMToken for handling base64-encoded private key set in
    YANDEX_GPT_PRIVATE_KEY_BASE64 environment variable. It may be useful when dealing with docker because there is no
    special characters like '\n' which can break key parsing to docker container environment.
    """
    def _set_iam_from_env_config_and_private_key(self) -> None:
        """
        Generates and sets IAM token from environment variables.
        """
        # Getting environment variables
        iam_url: str = os.getenv("YANDEX_GPT_IAM_URL", "https://iam.api.cloud.yandex.net/iam/v1/tokens")
        service_account_id: Optional[str] = os.getenv("YANDEX_GPT_SERVICE_ACCOUNT_ID", None)
        service_account_key_id: Optional[str] = os.getenv("YANDEX_GPT_SERVICE_ACCOUNT_KEY_ID", None)
        catalog_id: Optional[str] = os.getenv("YANDEX_GPT_CATALOG_ID", None)
        private_key_base64: Optional[str] = os.getenv("YANDEX_GPT_PRIVATE_KEY_BASE64", None)

        # Checking environment variables
        if not all([iam_url, service_account_id, service_account_key_id, catalog_id, private_key_base64]):
            raise ValueError("One or more environment variables for IAM token generation are missing.")

        # Decoding private key
        private_key_bytes: bytes = base64.b64decode(private_key_base64)
        private_key: str = private_key_bytes.decode("utf-8")

        # Generating JWT token
        jwt_token: str = self._generate_jwt_token(
            service_account_id=service_account_id,
            private_key=private_key,
            key_id=service_account_key_id,
            url=iam_url,
        )

        # Swapping JWT token to IAM
        self.iam_token = self._swap_jwt_to_iam(jwt_token, iam_url)
