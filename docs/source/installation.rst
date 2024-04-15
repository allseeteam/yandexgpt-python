Installation Guide
==================

This section outlines the steps required to install and set up the YandexGPT Python SDK in your development environment.

Installation Steps
------------------

1. Install the YandexGPT Python SDK using pip:

.. code-block:: bash

    pip install yandexgpt-python

2. (Optional) Set up a virtual environment:

If you prefer to use a virtual environment to manage your project's dependencies separately, you can create one using the following commands:

.. code-block:: bash

    python -m venv myenv
    source myenv/bin/activate  # On Windows use `myenv\\Scripts\\activate`

3. Install the SDK within your virtual environment:

.. code-block:: bash

    pip install yandexgpt-python

Local Installation
------------------

If you wish to install the SDK locally (for example, to modify the SDK code), follow these steps:

1. Clone the repository:

.. code-block:: bash

    git clone https://github.com/allseeteam/yandexgpt-python.git

2. Navigate to the cloned directory:

.. code-block:: bash

    cd yandexgpt-python

3. Install the package in editable mode:

.. code-block:: bash

    pip install -e .

This installation method allows you to make changes to the SDK and see them reflected immediately without needing to reinstall the package.

Next Steps
----------

After installing the SDK, you can proceed to the :doc:`quickstart` or explore the comprehensive documentation for detailed information on using the SDK.
