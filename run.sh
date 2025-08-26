#!/usr/bin/with-contenv bash
export TELEGRAM_TOKEN=$(bashio::config 'TELEGRAM_TOKEN')
export MISTRAL_API_KEY=$(bashio::config 'MISTRAL_API_KEY')

python3 /app/bot.py
