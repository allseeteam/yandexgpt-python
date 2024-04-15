YandexGPTThread Module
======================

Overview
--------

The YandexGPTThread module provides the :doc:`YandexGPTThread` class, a specialized extension of the :doc:`YandexGPT` class from the `yandex_gpt` module. It is designed to handle asynchronous messaging and state management for conversation threads, suitable for real-time interactive applications.

The :doc:`YandexGPTThread` class allows for both synchronous and asynchronous interaction with the Yandex GPT model, making it a flexible solution for managing conversations in various application scenarios.

Features
--------

The :doc:`YandexGPTThread` class includes several key features:

- **Thread Management**: Simplifies the creation and ongoing management of conversation threads.
- **Asynchronous Communication**: Supports non-blocking operations by allowing asynchronous interactions with the Yandex GPT model.
- **Synchronous Execution**: Provides synchronous methods for immediate response requirements.
- **Message Handling**: Facilitates the addition of new messages to the conversation thread and provides access to them in an ordered manner.
- **Status Tracking**: Monitors the status and health of the thread, including its operational state and any encountered errors.

Usage
-----

The following example demonstrates how to utilize the :doc:`YandexGPTThread` class for managing a conversation thread with the Yandex GPT model. Configuration is done via the :doc:`YandexGPTConfigManagerForIAMToken`, which is detailed in the :doc:`config_manager` documentation.

First, ensure that the required environment variables for IAM token generation are set. These can be loaded using the `dotenv` library, if they are stored in a `.env` file.

Below is a simple script that initializes a :doc:`YandexGPTThread` instance, sends a user message to the thread, and then processes the conversation asynchronously:

.. code-block:: python

    # Import the required classes
    import asyncio
    from dotenv import load_dotenv
    from yandex_gpt import YandexGPTThread, YandexGPTConfigManagerForIAMToken

    # Load environment variables for IAM token generation
    load_dotenv('path/to/your/.env.file')

    # Create an instance of the YandexGPTThread with IAM Token configuration
    yandex_gpt_thread = YandexGPTThread(
        config_manager=YandexGPTConfigManagerForIAMToken()
    )

    # Add a user message to the thread
    yandex_gpt_thread.add_message(role='user', text='Hello, Yandex GPT!')

    # Execute the thread asynchronously
    asyncio.run(yandex_gpt_thread.run_async())

    # Retrieve and print the latest message from the thread, typically the response
    print(yandex_gpt_thread.messages[-1]['text'])

Note that the last line retrieves the text of the last message, which is usually the model's response. Replace `'path/to/your/.env.file'` with the actual path to your `.env` file that contains the necessary environment variables.

Module Structure
----------------

.. toctree::
   :maxdepth: 3

   YandexGPTThread
