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
    """
    Base class for YaGPT configuration management. It handles configurations related to model type, catalog ID, IAM
    token, and API key for authorization when making requests to the completion endpoint.

    Attributes
    ----------
    model_type : Optional[str]
        The model type to use. Supported values include 'yandexgpt', 'yandexgpt-lite', 'summarization'.
    catalog_id : Optional[str]
        The Catalog ID on YandexCloud to be used.
    iam_token : Optional[str]
        The IAM token for authorization. Either `iam_token` or `api_key` is used for authorization. If both are
        provided, `iam_token` will be preferred. More details on getting an IAM token can be found here:
        https://yandex.cloud/ru/docs/iam/operations/iam-token/create-for-sa
    api_key : Optional[str]
        The API key for authorization. More details on getting an API key can be found here:
        https://yandex.cloud/ru/docs/iam/operations/api-key/create
    """
    def __init__(
            self,
            model_type: Optional[str] = None,
            catalog_id: Optional[str] = None,
            iam_token: Optional[str] = None,
            api_key: Optional[str] = None,
    ) -> None:
        """
        Initializes a new instance of the YandexGPTConfigManagerBase class.

        Parameters
        ----------
        model_type : Optional[str], optional
            Model type to use.
        catalog_id : Optional[str], optional
            Catalog ID on YandexCloud to use.
        iam_token : Optional[str], optional
            IAM token for authorization.
        api_key : Optional[str], optional
            API key for authorization.
        """
        self.model_type: Optional[str] = model_type
        self.catalog_id: Optional[str] = catalog_id
        self.iam_token: Optional[str] = iam_token
        self.api_key: Optional[str] = api_key

    @property
    def completion_request_authorization_field(self) -> str:
        """
        Returns the authorization field for the completion request header based on the IAM token or API key.

        Raises
        ------
        ValueError
            If neither IAM token nor API key is set.

        Returns
        -------
        str
            The authorization field for the completion request header in the form of "Bearer {iam_token}" or
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
        Returns the catalog ID field for the completion request header.

        Raises
        ------
        ValueError
            If catalog_id is not set.

        Returns
        -------
        str
            The catalog ID field for the completion request header.
        """
        # Checking if catalog_id is set and returning the catalog id field string
        if self.catalog_id:
            return self.catalog_id
        else:
            raise ValueError("Catalog ID is not set")

    @property
    def completion_request_model_type_uri_field(self) -> str:
        """
        Returns the model type URI field for the completion request payload.

        Raises
        ------
        ValueError
            If model_type or catalog_id is not set or if model_type is not in the available models.

        Returns
        -------
        str
            The model type URI field for the completion request header in the URI format.
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
    """
    Class for configuring the YandexGPT model using an API key. It supports setting model type, catalog ID, and API key
    directly or through environment variables. The class allows for configuration flexibility by providing the option to
    use environmental variables for model type (`YANDEX_GPT_MODEL_TYPE`), catalog ID (`YANDEX_GPT_CATALOG_ID`), and API
    key (`YANDEX_GPT_API_KEY`), which can override the constructor values if set.

    Attributes
    ----------
    model_type : Optional[str]
        The model type to use. Supported values include 'yandexgpt', 'yandexgpt-lite', 'summarization'.
    catalog_id : Optional[str]
        The Catalog ID on YandexCloud to be used.
    api_key : Optional[str]
        The API key for authorization. More details on obtaining an API key can be found here:
        https://yandex.cloud/ru/docs/iam/operations/api-key/create
    """
    def __init__(
            self,
            model_type: Optional[str] = None,
            catalog_id: Optional[str] = None,
            api_key: Optional[str] = None,
    ) -> None:
        """
        Initializes a new instance of the YandexGPTConfigManagerForAPIKey class.

        Parameters
        ----------
        model_type : Optional[str], optional
            Model type to use.
        catalog_id : Optional[str], optional
            Catalog ID on YandexCloud to use.
        api_key : Optional[str], optional
            API key for authorization.
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
        Sets configuration parameters from environment variables if they are not provided in the constructor.
        """
        self.model_type = os.environ.get("YANDEX_GPT_MODEL_TYPE", self.model_type)
        self.catalog_id = os.environ.get("YANDEX_GPT_CATALOG_ID", self.catalog_id)
        self.api_key = os.environ.get("YANDEX_GPT_API_KEY", self.api_key)

    def _check_config(self) -> None:
        """
        Ensures that the necessary configuration parameters are set, raising a ValueError if any are missing.
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
    """
    Class for configuring the YandexGPT model using an IAM token. It handles configurations involving model type,
    catalog ID, and IAM token, with options for direct input or initialization via environment variables. The class
    provides several pathways for initializing these configurations:

    1. Directly through constructor parameters.
    2. Through environment variables `YANDEX_GPT_MODEL_TYPE`, `YANDEX_GPT_CATALOG_ID`, and `YANDEX_GPT_IAM_TOKEN`.
    3. Automatically generating the IAM token using the environment variables `YANDEX_GPT_IAM_URL`,
       `YANDEX_GPT_SERVICE_ACCOUNT_ID`, `YANDEX_GPT_SERVICE_ACCOUNT_KEY_ID`, `YANDEX_GPT_CATALOG_ID`, and
       `YANDEX_GPT_PRIVATE_KEY`.

    Attributes
    ----------
    model_type : Optional[str]
        The model type to use. Supported values include 'yandexgpt', 'yandexgpt-lite', 'summarization'.
    catalog_id : Optional[str]
        The Catalog ID on YandexCloud to be used.
    iam_token : Optional[str]
        The IAM token for authorization. Details on obtaining an IAM token can be found here:
        https://yandex.cloud/ru/docs/iam/operations/iam-token/create-for-sa
    """
    def __init__(
            self,
            model_type: Optional[str] = None,
            catalog_id: Optional[str] = None,
            iam_token: Optional[str] = None,
    ) -> None:
        """
        Initializes a new instance of the YandexGPTConfigManagerForIAMToken class.

        Parameters
        ----------
        model_type : Optional[str], optional
            Model type to use.
        catalog_id : Optional[str], optional
            Catalog ID on YandexCloud to use.
        iam_token : Optional[str], optional
            IAM token for authorization.
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
        Sets config from environment variables or tries to generate the IAM token using additional environment variables
        if not directly provided.
        """
        self.model_type = os.environ.get("YANDEX_GPT_MODEL_TYPE", self.model_type)
        self.catalog_id = os.environ.get("YANDEX_GPT_CATALOG_ID", self.catalog_id)
        self.iam_token = os.environ.get("YANDEX_GPT_IAM_TOKEN", self.iam_token)

        if not self.iam_token:
            # If IAM token is not set, trying to initialize from config and private key
            self._set_iam_from_env_config_and_private_key()

    def _set_iam_from_env_config_and_private_key(self) -> None:
        """
        Generates and sets IAM token from environment variables if not provided.
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
        Generates and swaps a JWT token to an IAM token.

        Parameters
        ----------
        service_account_id : str
            Service account ID
        private_key : str
            Private key
        key_id : str
            Service account key ID
        url : str
            IAM URL for token request

        Returns
        -------
        str
            The IAM token
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
        Swaps a JWT token for an IAM token by making a POST request to the Yandex IAM service.

        Parameters
        ----------
        jwt_token : str
            The JWT token to be swapped.
        url : str, optional
            The URL to send the JWT token to, by default set to Yandex IAM token service endpoint.

        Returns
        -------
        str
            The IAM token received in response.

        Raises
        ------
        Exception
            If the request fails or does not return a successful response.
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
        Ensures that the necessary configuration parameters are set, raising a ValueError if any are missing.
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
    A specialized configuration manager for YandexGPT that handles base64-encoded private keys. This is particularly
    useful in environments like Docker where special characters (e.g., newline) in environment variables can cause
    issues. The private key is expected to be set in the YANDEX_GPT_PRIVATE_KEY_BASE64 environment variable.

    Inherits attributes from YandexGPTConfigManagerForIAMToken.
    """
    def _set_iam_from_env_config_and_private_key(self) -> None:
        """
        Overrides the base method to generate and set the IAM token using a base64-encoded private key from
        environment variables.

        Raises
        ------
        ValueError
            If any required environment variables are missing.
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
