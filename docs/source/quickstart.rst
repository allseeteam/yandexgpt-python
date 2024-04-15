Quickstart Guide
================

This quickstart guide provides an introduction to the YandexGPT Python SDK, helping you get up and running quickly.

Obtaining Credentials
---------------------

To use the Yandex GPT API, you need to authenticate your requests using either an IAM token or an API key.

- **IAM Token**: An IAM token is a short-lived token used to authenticate against the Yandex Cloud services. `Learn how to obtain an IAM token <https://yandex.cloud/ru/docs/iam/operations/iam-token/create-for-sa>`_.

- **API Key**: An API key is a permanent key used to authenticate your requests. `Learn how to obtain an API key <https://yandex.cloud/ru/docs/iam/operations/api-key/create>`_.

Remember to handle your tokens and keys securely and never expose them in your code or version control systems.

SDK Components
--------------

- **YandexGPT Class**: The :doc:`YandexGPT` class is the main interface to the Yandex GPT API. It provides methods to send both synchronous and asynchronous requests for text completions.

- **Configuration Managers**: Configuration managers are used to set up and manage the necessary settings for the :doc:`YandexGPT` class, such as authentication and model details. For more information, see the :doc:`config_manager`.

- **Threads**: The SDK offers the :doc:`YandexGPTThread` class to manage conversation threads, allowing for maintaining the context of a conversation. For more details, refer to the :doc:`thread`.

Environmental Setup
-------------------

The `/env` directory contains `.env.example` files for each configuration manager. Copy the relevant example file to create your own `.env` file with the necessary credentials and settings.

Examples
--------

Here are quick examples to show how each component can be used:

**Setting up a Configuration Manager**

.. code-block:: python

    from yandex_gpt import YandexGPTConfigManagerForAPIKey

    # Initialize the configuration manager with model type, catalog ID, and API key
    config_manager = YandexGPTConfigManagerForAPIKey(
        model_type="yandexgpt",
        catalog_id="your_catalog_id",
        api_key="your_api_key"
    )

**Using the YandexGPT Class**

.. code-block:: python

    from yandex_gpt import YandexGPT

    # Initialize YandexGPT with a configuration manager
    yandex_gpt = YandexGPT(config_manager=config_manager)

    # Synchronous completion example
    completion = yandex_gpt.get_sync_completion(messages=[{'role': 'user', 'text': 'Hello!'}])

    print(completion)

**Working with Threads**

.. code-block:: python

    from yandex_gpt import YandexGPTThread

    # Create a thread instance using the same configuration manager
    thread = YandexGPTThread(config_manager=config_manager)

    # Add a message to the thread and run it asynchronously
    thread.add_message(role='user', text='Hello, Yandex GPT!')

    # ... run and interact with the thread

Next Steps
----------

After going through these examples, you're ready to dive deeper into the SDK. Explore the full documentation to learn more about advanced features and best practices for using the YandexGPT Python SDK.
