# mugen-bot

To get running, first have python3 installed. Also, it must be at least Python 3.5 for some of the features included.

Run `python --version` or `python3 --version` to find out the version you have. If it's < 3.5,
then read a guide for your OS on how to install it (I'd recommend putting it as a separate bin file
than your regular `python` or `python3`, or using a version manager.

Then, make sure you have `virtualenv` installed (usually `pip install virtualenv`).

`virtualenv -p /path/to/python3.5/executable venv` (you only need to do this once to create the `venv` directory).

`source venv/bin/activate`

Now, `which python` should point to a local version. `python --version` should be at least 3.5 as well.

`pip install -r requirements.txt`

`cp config.yml.example config.yml`, and fill in the bot key.

`python main.py`

To leave this virtual environment, type `deactivate`.
