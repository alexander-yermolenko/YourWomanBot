import os
import random
import json
import configparser
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import time

# Load API token from config.ini
config = configparser.ConfigParser()
config.read('config.ini')
TOKEN = config['telegram']['token']

# Folder paths
FOLDERS = {
    'mywoman': 'real-women',
    'myanimewoman': 'anime-women',
    'mysexywoman': 'sexy-women',
    'mysexyanimewoman': 'sexy-anime-women'
}

# Dictionary to store the last time each user used any command
user_timestamps = {}

# Cooldown period in seconds (1 minute = 60 seconds)
COOLDOWN = 60

# Load quotes from quotes.json
with open('quotes.json', 'r', encoding='utf-8') as f:
    QUOTES = json.load(f)

# Generic function to handle all commands
async def send_woman(update: Update, context: ContextTypes.DEFAULT_TYPE, command: str) -> None:
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id  # Unique ID for each user
    message_id = update.message.message_id  # ID of the command message
    
    # Check if user is on cooldown
    current_time = time.time()
    last_used = user_timestamps.get(user_id, 0)
    time_since_last = current_time - last_used
    
    if time_since_last < COOLDOWN:
        remaining_time = int(COOLDOWN - time_since_last)
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Please wait {remaining_time} more seconds before using /{command} again!",
            reply_to_message_id=message_id
        )
        return
    
    folder = FOLDERS[command]
    try:
        # Get list of images from the specified folder
        images = [f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
        if not images:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"No images found in the {folder} folder!",
                reply_to_message_id=message_id
            )
            return
        
        # Pick a random image and quote
        image_path = os.path.join(folder, random.choice(images))
        quote = random.choice(QUOTES)
        
        with open(image_path, 'rb') as photo:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=quote,
                reply_to_message_id=message_id
            )
        
        # Update the user's last used timestamp
        user_timestamps[user_id] = current_time
    
    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Oops! Something went wrong: {str(e)}",
            reply_to_message_id=message_id
        )

# Specific command handlers
async def mywoman(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_woman(update, context, 'mywoman')

async def myanimewoman(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_woman(update, context, 'myanimewoman')

async def mysexywoman(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_woman(update, context, 'mysexywoman')

async def mysexyanimewoman(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_woman(update, context, 'mysexyanimewoman')

# Main function to set up the bot
def main():
    # Create the Application and pass it your bot's token
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("mywoman", mywoman))
    application.add_handler(CommandHandler("myanimewoman", myanimewoman))
    application.add_handler(CommandHandler("mysexywoman", mysexywoman))
    application.add_handler(CommandHandler("mysexyanimewoman", mysexyanimewoman))

    # Start the bot
    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()