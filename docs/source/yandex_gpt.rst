Yandex GPT Module
=================

Overview
--------
The ``yandex_gpt`` module offers a Python interface for the Yandex Generative Pre-trained Transformer (GPT) API. It facilitates both synchronous and asynchronous communication with the API, streamlining the integration of Yandex GPT services into Python applications.

Classes
-------

The module includes the following classes:

- :doc:`YandexGPTBase`: Provides foundational access to the Yandex GPT API. This base class contains methods for directly interacting with the API endpoints asynchronously and synchronously.

- :doc:`YandexGPT`: Inherits from :doc:`YandexGPTBase` and offers a more accessible interface through a configuration manager. It abstracts setup and request complexities, making API interactions more user-friendly.

Refer to the :doc:`YandexGPT` documentation for comprehensive details on using the primary interface of the model.

Key Features
------------
- **Asynchronous and Synchronous Operations**: Enables both non-blocking asynchronous and blocking synchronous calls to the Yandex GPT API, accommodating various application designs.

- **Configuration Management**: Employs a configuration manager to streamline API settings, enhancing customization and simplicity.

- **Error Handling**: Implements comprehensive error handling strategies for effective API error management.

Usage Examples
--------------
Below is an example demonstrating the use of the :doc:`YandexGPT` class for a synchronous API call:

.. code-block:: python

    from yandex_gpt import YandexGPT
    from typing import List, Dict

    # Define API configuration parameters
    config = {
        "model_type": "yandexgpt",
        "catalog_id": "your_catalog_id",
        "iam_token": "your_iam_token"
    }

    # Instantiate the YandexGPT object with the configuration
    yandex_gpt = YandexGPT(config_manager=config)

    # Create messages and perform a synchronous completion request
    messages: List[Dict[str, str]] = [{'role': 'user', 'text': 'Hello, how can I help you?'}]
    completion = yandex_gpt.get_sync_completion(messages=messages, temperature=0.5, max_tokens=150)

    print("API completion:", completion)

For more advanced configuration options and different authentication methods, refer to the :doc:`config_manager`.

Module structure
----------------

.. toctree::
    :maxdepth: 3

    YandexGPTBase
    YandexGPT
