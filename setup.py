from setuptools import setup, find_packages


with open('requirements.txt') as f:
    requirements = f.read().splitlines()


setup(
    name='yandexgpt-python',
    version='0.2.0',
    author='Gregory Matsnev',
    author_email='grigorij1m@gmail.com',
    description='A Python SDK for interacting with the YandexGPT API.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/allseeteam/yandexgpt-python',
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
