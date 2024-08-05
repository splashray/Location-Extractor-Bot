import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from location_service import LocationService
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Initialize the LocationService
location_service = LocationService()

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Welcome! Use /countries, /states <country_code>, or /cities <country_code> <state_code> to fetch location data.')

async def get_countries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        countries = location_service.all_countries()
        # Number of countries to display per page
        PAGE_SIZE = 50
        # Current page number
        page = int(context.args[0]) if context.args else 1
        start = (page - 1) * PAGE_SIZE
        end = start + PAGE_SIZE
        
        countries_list = [f"{country['name']} ({country['iso2']})" for country in countries[start:end]]
        message = "\n".join(countries_list)
        
        # Add pagination buttons
        keyboard = []
        if start > 0:
            keyboard.append([InlineKeyboardButton("Previous", callback_data=f'prev_{page - 1}')])
        if end < len(countries):
            keyboard.append([InlineKeyboardButton("Next", callback_data=f'next_{page + 1}')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.message:
            await update.message.reply_text(f"Countries (Page {page}):\n{message}", reply_markup=reply_markup)
        else:
            await update.callback_query.message.edit_text(f"Countries (Page {page}):\n{message}", reply_markup=reply_markup)
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch countries: {e}")
        await update.message.reply_text("Failed to fetch countries. Please try again later.")

async def get_states(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /states <country_code>")
        return
    
    country_code = context.args[0]
    try:
        states = location_service.all_states_by_country(country_code)
        # Sort states alphabetically by their names
        states_sorted = sorted(states, key=lambda x: x['name'])
        
        # Format the states
        formatted_states = [f"{state['name']} ({state['iso2']})" for state in states_sorted]
        message = "\n".join(formatted_states)
        
        await update.message.reply_text(f"States in {country_code}:\n{message}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch states: {e}")
        await update.message.reply_text("Failed to fetch states. Please try again later.")
    except Exception as e:
        logger.error(f"An unexpected error occurred while fetching states: {e}")
        await update.message.reply_text("An unexpected error occurred. Please try again later.")

async def get_cities(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text("Usage: /cities <country_code> <state_code>")
        return
    
    country_code, state_code = context.args
    try:
        cities = location_service.all_cities_in_state_and_country(country_code, state_code)
        # Format the cities
        formatted_cities = [f"{city['name']}" for city in cities]
        message = "\n".join(formatted_cities)
        
        await update.message.reply_text(f"Cities in {state_code}, {country_code}:\n{message}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch cities: {e}")
        await update.message.reply_text("Failed to fetch cities. Please try again later.")
    except Exception as e:
        logger.error(f"An unexpected error occurred while fetching cities: {e}")
        await update.message.reply_text("An unexpected error occurred. Please try again later.")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    query_data = query.data.split('_')
    action = query_data[0]
    page = int(query_data[1])
    
    if action == 'prev' or action == 'next':
        context.args = [page]
        # Edit the existing message with updated content
        await get_countries(query, context)

def main():
    # Create the Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("countries", get_countries))
    application.add_handler(CommandHandler("states", get_states))
    application.add_handler(CommandHandler("cities", get_cities))
    application.add_handler(CallbackQueryHandler(button))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
