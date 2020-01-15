# refresher-bot
Telegram bot that takes your url and notifies you of updates on the web page.

# Configuring
First, create a virtual environment with necessary packages:

```sh
pipenv install
```

You should have [MongoDB](https://www.mongodb.com/) been installed.

Then put your telegram API and bot API keys into the [bot's config file](config/bot.yaml).

Also there are [MongoDB's](config/mongodb.yaml) and [monitoring's](config/monitoring.yaml) config files with a parameters' clarification.

# Usage
Start a bot with the following command:

```sh
pipenv run python main.py
```
