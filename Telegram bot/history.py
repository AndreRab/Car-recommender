class HistoryCollector:
    def __init__(self, user_token='user', model_token='model'):
        self.history = {} 
        self.user_token = user_token
        self.model_token = model_token

    def add_message__(self, chat_id, speaker, message):
        if chat_id not in self.history:
            self.history[chat_id] = []
        self.history[chat_id].append((speaker, message))

    def add_user_message(self, message, chat_id):
        self.add_message__(chat_id, self.user_token, message)

    def add_model_message(self, message, chat_id):
        self.add_message__(chat_id, self.model_token, message)

    def get_formatted_history(self, chat_id):
        lines = []
        for speaker, msg in self.history.get(chat_id, []):
            lines.append(f"{speaker}: {msg}")
        return '\n'.join(lines)