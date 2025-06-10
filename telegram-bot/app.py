import torch
torch.set_num_threads(1)
torch.set_num_interop_threads(1)

import telebot
from telebot import types
from data.constants import *
from bot.history_collector import HistoryCollector
from bot.rag_parser import RAG_Parser
from keys import *
from bot.model import LLM

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

COMMANDS = [telebot.types.BotCommand(name, desc) for name, desc in COMMAND_DESCRIPTION.items()]

bot.set_my_commands(COMMANDS)

def render_button_options(chat_id):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    btns = []
    for command, label in COMMAND_TO_PRETY_NAME.items():
        btn = types.InlineKeyboardButton(text=label, callback_data=command)
        btns.append(btn)

    keyboard.add(*btns)
    
    bot.send_message(chat_id, "What would you like to do?", reply_markup=keyboard)  

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = WELCOME_TEXT
    bot.send_message(message.chat.id, welcome_text, parse_mode='Markdown')
    render_button_options(message.chat.id)

def handle_start_conversation(call):
    chat_id = call.message.chat.id
    bot.send_message(chat_id, CONVERSATION_BEGINING)
    bot.register_next_step_handler(call.message, handle_user_problem)
    history_collector.add_model_message(CONVERSATION_BEGINING, chat_id)

def handle_help(call):
    chat_id = call.message.chat.id
    help_text = HELP_TEXT
    for cmd in COMMANDS:
        help_text += f"/{cmd.command} - {cmd.description}\n"
    bot.send_message(chat_id, help_text)
    render_button_options(chat_id)

def handle_default(call):
    bot.send_message(call.message.chat.id, "🚧 This option is not implemented.")

CALLBACK_HANDLERS = {
    START_CONVERSATION: handle_start_conversation,
    HELP_COMMAND: handle_help,
}

def handle_user_problem(message):
    chat_id = message.chat.id
    user_input = message.text
    history_collector.add_user_message(user_input, chat_id)

    rag_prompt = rag_parser.generate_prompt(user_input)
    full_prompt = build_prompt(rag_prompt, chat_id)
    bot_response = model(full_prompt)

    bot.send_message(chat_id, bot_response)
    history_collector.add_model_message(bot_response, chat_id)
    bot.register_next_step_handler(message, handle_user_problem)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    handler = CALLBACK_HANDLERS.get(call.data, handle_default)
    handler(call)

def build_prompt(rag_prompt, chat_id):
    full_prompt = rag_prompt + '\n\n' + history_collector.get_formatted_history(chat_id) + '\n' + 'AI: '
    return full_prompt

if __name__ == "__main__":
    history_collector = HistoryCollector()
    print('Loading model...')
    model = LLM(MODEL_NAME)
    print('Model loaded successfully')
    print("Loading FAISS index...")
    rag_parser = RAG_Parser(INDEX_PATH, METADATA_PATH, model)
    print("FAISS imported successfully.")
    bot.polling(none_stop=True)