Configuration Managers Module
=============================

Overview
--------

The Configuration Managers module provides a set of classes designed to configure and manage settings for the YandexGPT Python SDK. These classes enable various authentication methods, including API keys and IAM tokens, and can be used in conjunction with the :doc:`YandexGPT` and :doc:`YandexGPTThread` classes for seamless integration into Yandex GPT applications.

Classes
-------

The following classes are available in this module:

- :doc:`YandexGPTConfigManagerBase`: The base configuration manager for general settings.
- :doc:`YandexGPTConfigManagerForAPIKey`: For configurations using an API key.
- :doc:`YandexGPTConfigManagerForIAMToken`: To configure using an IAM token.
- :doc:`YandexGPTConfigManagerForIAMTokenWithBase64Key`: Specialized for configurations using a base64-encoded private key.

Each configuration manager can be used to set up the Yandex GPT model type, catalog ID, and authentication details. For detailed class documentation, refer to their respective sections.

Examples
--------

The following examples show how to use configuration managers with the YandexGPT and YandexGPTThread classes:

Using API Key for Authentication
--------------------------------

.. code-block:: python

    from yandex_gpt import YandexGPT, YandexGPTConfigManagerForAPIKey

    # Setup configuration with direct parameters (use environment variables if they are set)
    config = YandexGPTConfigManagerForAPIKey(
        model_type="yandexgpt",
        catalog_id="your_catalog_id",
        api_key="your_api_key"
    )

    # Instantiate YandexGPT with the configuration
    yandex_gpt = YandexGPT(config_manager=config)

    # Async function to get completion from YandexGPT
    async def get_completion():
        messages = [{"role": "user", "text": "Hello, world!"}]
        completion = await yandex_gpt.get_async_completion(messages=messages)
        print(completion)

    # Run the async function to obtain the response
    import asyncio
    asyncio.run(get_completion())

Using IAM Token for Authentication
----------------------------------

.. code-block:: python

    from dotenv import load_dotenv
    from yandex_gpt import YandexGPT, YandexGPTConfigManagerForIAMToken

    # Load environment variables for IAM token generation
    load_dotenv('path/to/your/.env.file')

    # Setup configuration using environment variables for IAM token generation
    config = YandexGPTConfigManagerForIAMToken()

    # Instantiate YandexGPT with the configuration
    yandex_gpt = YandexGPT(config_manager=config)

    # Async function to get completion from YandexGPT
    async def get_completion():
        messages = [{"role": "user", "text": "Hello, world!"}]
        completion = await yandex_gpt.get_async_completion(messages=messages)
        print(completion)

    # Run the async function to obtain the response
    import asyncio
    asyncio.run(get_completion())

Note
----

In the examples above, replace `'your_catalog_id'`, `'your_api_key'`, and `'path/to/your/.env.file'` with your actual Yandex Cloud catalog ID, API key, and path to your `.env` file respectively.

Module Structure
----------------

.. toctree::
   :maxdepth: 3

   YandexGPTConfigManagerBase
   YandexGPTConfigManagerForAPIKey
   YandexGPTConfigManagerForIAMToken
   YandexGPTConfigManagerForIAMTokenWithBase64Key
