import os
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv('DISCORD_EMAIL')
PASSWORD = os.getenv('DISCORD_PASSWORD')
GUILD_ID = os.getenv('DISCORD_GUILD_ID')
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')
OFFSET_MINUTES = int(os.getenv('CRON_OFFSET'))
BOT_NAME = os.getenv("BOT_NAME")
LOG_LEVEL = int(os.getenv('LOG_LEVEL', 20))