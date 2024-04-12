# YandexGPT Python SDK

## Introduction
The YandexGPT Python SDK provides an easy-to-use interface for interacting with the Yandex GPT API. It includes asynchronous methods for sending requests to the Yandex GPT API, handling authentication, and processing responses. This SDK is designed to simplify the integration of Yandex GPT functionalities into Python applications.

## Table of Contents
- [Introduction](#Introduction)
- [Features](#Features)
- [Installation using pip](#Installation-using-pip)
- [Local installation using pip](#Local-installation-using-pip)
- [Usage](#Usage)
- [Configuration](#Configuration)
- [Examples](#Examples)
- [Troubleshooting](#Troubleshooting)
- [Contributors](#Contributors)
- [License](#License)

## Features
- Asynchronous API calls to Yandex GPT.
- Easy configuration of API credentials and model parameters.
- Supports multiple GPT models.
- Includes utility for managing API request headers and payload.

The SDK depends on several Python libraries for its operation. These dependencies are specified in the [requirements.txt](requirements.txt) file.

## Installation using pip
To install the YandexGPT Python SDK as a package using pip, run the following command:
```shell
pip install yandexgpt-python
```

## Local installation using pip
If you want to install the SDK locally (for example, if you want to modify SDK code), you can do so by cloning the repository and running the setup script:
```shell
git clone https://github.com/allseeteam/yandexgpt-python.git
cd yandexgpt-python
pip install -e .
```

## Usage
The YandexGPT SDK is designed for asynchronous operation. To use it, instantiate the [YandexGPT](yandex_gpt/yandex_gpt.py) class with a configuration manager that includes your Yandex Cloud catalog ID, API key/IAM token, and the desired GPT model type. Currently, the supported model types are:
- yandexgpt
- yandexgpt-lite
- summarization

## Configuration
Configuration for the YandexGPT SDK involves setting up the model type, catalog ID, and API key/IAM token. This can be done through the [YandexGPTConfigManagerBase](yandex_gpt/config_manager.py) class or [its subclasses](yandex_gpt/config_manager.py), which allows for easy management of these settings either directly or via environment variables (see examples in [env](env) directory).

## Examples
### Using API key for authentication
```python
from yandex_gpt import YandexGPT, YandexGPTConfigManagerForAPIKey

# Setup configuration (input fields may be empty if they are set in environment variables)
config = YandexGPTConfigManagerForAPIKey(model_type="yandexgpt", catalog_id="your_catalog_id", api_key="your_api_key")

# Instantiate YandexGPT
yandex_gpt = YandexGPT(config_manager=config)

# Async function to get completion
async def get_completion():
    messages = [{"role": "user", "text": "Hello, world!"}]
    completion = await yandex_gpt.get_async_completion(messages=messages)
    print(completion)

# Run the async function
import asyncio
asyncio.run(get_completion())
```

### Using IAM token for authentication
```python
from dotenv import load_dotenv
from yandex_gpt import YandexGPT, YandexGPTConfigManagerForAPIKey

# Load environment variables
load_dotenv('../env/.env.iam_token_generation')

# Setup configuration (input fields are empty, because iam_token will be generated from environment variables)
config = YandexGPTConfigManagerForIAMToken()

# Instantiate YandexGPT
yandex_gpt = YandexGPT(config_manager=config)

# Async function to get completion
async def get_completion():
    messages = [{"role": "user", "text": "Hello, world!"}]
    completion = await yandex_gpt.get_async_completion(messages=messages)
    print(completion)

# Run the async function
import asyncio
asyncio.run(get_completion())
```


## Troubleshooting
For any issues related to the configuration or usage of the SDK, ensure that the catalog ID, API key, and model type are correctly set and that the environment variables (if used) are properly configured.

## Contributors
This project is developed and maintained by Gregory Matsnev. Contributions are welcome.

## License
This project is licensed under the MIT License. For more information, see the LICENSE file in the project's GitHub repository.
