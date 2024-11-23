import telebot
import requests
from datetime import datetime, timedelta

BOT_TOKEN = '7902761696:AAF-ZcqFdOXxbRD7rc07UzvT6-jHziJ20rU'
bot = telebot.TeleBot(BOT_TOKEN)

# Zodiac signs and their date ranges
ZODIAC_SIGNS = {
    "Aries": "March 21 - April 19",
    "Taurus": "April 20 - May 20",
    "Gemini": "May 21 - June 20",
    "Cancer": "June 21 - July 22",
    "Leo": "July 23 - August 22",
    "Virgo": "August 23 - September 22",
    "Libra": "September 23 - October 22",
    "Scorpio": "October 23 - November 21",
    "Sagittarius": "November 22 - December 21",
    "Capricorn": "December 22 - January 19",
    "Aquarius": "January 20 - February 18",
    "Pisces": "February 19 - March 20"
}

# Define the valid date range
today = datetime.now()
max_fetch_date = today.strftime("%Y-%m-%d")  # Format: yyyy-mm-dd
min_fetch_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")  # One year back

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    introduction = (
        "🌟 Welcome to ASTRA - Astrology & Stars Telegram Responsive Assistant! 🌟\n\n"
        "I can provide you with daily horoscopes based on your zodiac sign.\n"
        "Just type /horoscope to get started!"
    )
    bot.reply_to(message, introduction)

def get_daily_horoscope(sign: str, day: str) -> dict:
    """Get daily horoscope for a zodiac sign."""
    url = "https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily"
    params = {"sign": sign, "day": day}
    response = requests.get(url, params)
    return response.json()

@bot.message_handler(commands=['horoscope'])
def sign_handler(message):
    # Create a keyboard for zodiac sign options
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for sign in ZODIAC_SIGNS.keys():
        markup.add(sign)
    
    # Create a plain text format for zodiac signs and their date ranges
    zodiac_info = (
        "🔮 What's your zodiac sign?\n\n"
        "If you're unsure, here are the date ranges for each sign:\n\n"
        "* Aries               :  21 Mar  -  19 Apr *  \n"
        "* Taurus           :  20 Apr  -  20 May * \n"
        "* Gemini           :  21 May  -  20 Jun *  \n"
        "* Cancer            :  21 Jun  -  22 Jul  * \n"
        "* Leo                  :  23 Jul  -  22 Aug * \n"
        "* Virgo               :  23 Aug  -  22 Sep * \n"
        "* Libra               :  23 Sep  -  22 Oct * \n"
        "* Scorpio           :  23 Oct  -  21 Nov * \n"
        "* Sagittarius    :  22 Nov  -  21 Dec * \n"
        "* Capricorn      :  22 Dec  -  19 Jan * \n"
        "* Aquarius       :  20 Jan  -  18 Feb * \n"
        "* Pisces              : 19 Feb  - 20 Mar * \n\n"
        "Please select your zodiac sign from the options below:"
    )
    
    sent_msg = bot.send_message(message.chat.id, zodiac_info, parse_mode="Markdown", reply_markup=markup)
    bot.register_next_step_handler(sent_msg, day_handler)

def day_handler(message):
    sign = message.text.capitalize()
    # Create a keyboard for date options
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("Today", "Tomorrow", "Yesterday", "Specific Date (yyyy-mm-dd)")
    
    text = (
        "📅 What day do you want to know?\n\n"
        "Choose one of the options below:"
    )
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)
    bot.register_next_step_handler(sent_msg, fetch_horoscope, sign)

def fetch_horoscope(message, sign):
    day = message.text
    if day == "Specific Date (yyyy-mm-dd)":
        text = "Please enter the date in the format yyyy-mm-dd. \n\nNote: The date should be in the past upto 1 Year."
        sent_msg = bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(sent_msg, fetch_horoscope_with_specific_date, sign)
    else:
        if day == "Today":
            day = datetime.now().strftime("%Y-%m-%d")
        elif day == "Tomorrow":
            day = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        elif day == "Yesterday":
            day = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        if min_fetch_date <= day <= max_fetch_date:
            horoscope = get_daily_horoscope(sign, day)
            if horoscope.get("success"):
                data = horoscope["data"]
                horoscope_message = (
                    f"✨ *Horoscope for {sign} on {data['date']}* ✨\n\n"
                    f"{data['horoscope_data']}\n\n"
                    "🌌 Wishing you a day filled with positivity and good vibes! 🌌"
                )
                bot.send_message(message.chat.id, horoscope_message, parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, "⚠️ Sorry, I couldn't retrieve the horoscope. \n Please try again later.")
        else:
            bot.send_message(message.chat.id, f"⚠️ Sorry, your date is out of Range [ {min_fetch_date}   to   {max_fetch_date} ]. \n Please try again later.")

def fetch_horoscope_with_specific_date(message, sign):
    day = message.text
    try:
        datetime.strptime(day, "%Y-%m-%d")  # Validate date format
        if min_fetch_date <= day <= max_fetch_date:
            horoscope = get_daily_horoscope(sign, day)
            if horoscope.get("success"):
                data = horoscope["data"]
                horoscope_message = (
                    f"✨ *Horoscope for {sign} on {data['date']}* ✨\n\n"
                    f"{data['horoscope_data']}\n\n"
                    "🌌 Wishing you a day filled with positivity and good vibes! 🌌"
                )
                bot.send_message(message.chat.id, horoscope_message, parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, "⚠️ Sorry, I couldn't retrieve the horoscope. Please try again later.")
        else:
            bot.send_message(message.chat.id, f"⚠️ Sorry, your date is out of Range [ {min_fetch_date}   to   {max_fetch_date} ]. \n Please try again later.")
    except ValueError:
        bot.send_message(message.chat.id, "⚠️ Invalid date format. Please use [YYYY-MM-DD] format next time")

# Start polling to listen for messages

print(" Go to ASTRA bot : https://t.me/only_ASTRA_bot ")

bot.infinity_polling()

