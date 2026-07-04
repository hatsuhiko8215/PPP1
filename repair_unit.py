class SelfHealingAI:
    def check_health(self):
        return "OK"

    def handle_error(self, error_message):
        print(f"Error: {error_message}")
        return "logged"
