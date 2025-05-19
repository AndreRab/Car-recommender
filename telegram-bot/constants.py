START_COMMAND = 'start'
HELP_COMMAND = 'help'
START_CONVERSATION = 'start_conversation'

COMMAND_TO_PRETY_NAME = {
    START_CONVERSATION: 'I need to talk',
    HELP_COMMAND: 'I want to see all commands'
}

COMMAND_DESCRIPTION = {
    START_COMMAND: 'Start the bot',
    HELP_COMMAND: 'Show help message',
    START_CONVERSATION: "Ask for a Ivanych help"
}

HELP_TEXT = "Here's desctiption of the each command " + "\n\n"
CONVERSATION_BEGINING = "🗣 Please, describe your problem. I'm listening carefully..."
DEFAULT_ANSWER = (
        "👍 I got you and will help you tomorrow.\n"
        "You're not the only one in my life 😉"
    )
WELCOME_TEXT = (
        "👋 Hello! I'm *Ivanych*, your personal car assistant.\n\n"
        "🚗 Need advice on buying, selling, or choosing a car?\n"
        "🛠 Looking for technical info or service tips?\n"
        "📊 Curious about specs, comparisons, or car reviews?\n\n"
        "Just ask — I'm here to help with anything related to cars!\n\n"
        "Type /help to see what I can do."
    )