___

# Prerequisites
Before running this project, you need to setup the following:

* Start a Redis database with RediSearch (redis-stack) - see the [Redis README](development/redis docker/README.md) or TL;DR:
  * Install and run [Docker](https://docs.docker.com/get-docker/)
  * Run `docker compose up -d` in the [redis docker](development/redis docker) directory
* Set up your Python environment
  * Download and install [Python](https://www.python.org/downloads/) (any version should work, I am using 3.11.0)
  * Create a virtual environment (optional, but recommended) - Run `python -m venv venv` in the project root directory
  * install libraries in [requirements.txt](gpt-ltm/requirements.txt) - Run `pip install -r requirements.txt` in the project root directory
* Get your [OpenAI API key](https://platform.openai.com/account/api-keys) - Either add it to your environment variables or paste it into the [config.py](gpt-ltm/config.py) file
<br/><br/>
___

## Deploying the Library

* Create a new Python environment: `python -m venv venv`
* Test installation of the package, run `pip install .` in the project root directory
* Test the functions using the [test.py](test.py) file
* Install build tools: `pip install build`
* Build the package: `python -m build`
* Install twine: `pip install twine`
* Upload the package to PyPI: `python -m twine upload --repository testpypi dist/*`
* Enter **username** and **password**
* Uninstall using `pip uninstall gpt-ltm`
* Install from testpypi using `pip install -i https://test.pypi.org/simple/ gpt-ltm`

<br/><br/>
___
