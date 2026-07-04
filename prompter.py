import json
import os
from datetime import datetime

class EnhancedPrompter:
    def __init__(self, learning_file="learning_data.json"):
        self.learning_file = learning_file
        self.load_learning_data()
        self.negative_keywords = [
            "castanets", "xylophone", "glockenspiel", "bright percussion",
            "sharp high-pitched sounds", "abrupt changes", "distracting vocals",
            "overly bright melodies", "sudden tempo shifts", "jarring sounds",
            "harsh noise", "sudden glitches"
        ]

    def load_learning_data(self):
        if os.path.exists(self.learning_file):
            try:
                with open(self.learning_file, "r") as f:
                    self.data = json.load(f)
            except json.JSONDecodeError:
                self._initialize_default_data()
        else:
            self._initialize_default_data()

    def _initialize_default_data(self):
        self.data = {
            "parameters": {"weirdness": 0.5, "style_influence": 0.7},
            "history": [],
            "banned_keywords": ["castanets", "xylophone"],
            "risky_keywords": {"lofi": "causes clutch noises, use specific textures instead"},
            "successful_descriptors": ["warm analog texture", "vinyl crackle", "mellow beat", "subtle distortion"]
        }
        self.save_learning_data()

    def save_learning_data(self):
        with open(self.learning_file, "w") as f:
            json.dump(self.data, f, indent=4)

    def generate_timestamp_title(self, base_name="Chill_Lo-fi"):
        now = datetime.now()
        timestamp = now.strftime("%Y_%m_%d_%H_%M_%S")
        return f"{timestamp}_{base_name}"

    def optimize_prompt(self, raw_prompt):
        optimized = raw_prompt.lower()
        if "lofi" in optimized or "lo-fi" in optimized:
            replacement = ", ".join(self.data.get("successful_descriptors", ["warm analog texture", "mellow beat"]))
            optimized = optimized.replace("lofi", replacement).replace("lo-fi", replacement)
        for banned in self.data.get("banned_keywords", []):
            optimized = optimized.replace(banned, "")
        negative_part = " --no " + " --no ".join(self.negative_keywords)
        return optimized.strip() + negative_part

    def get_current_params(self):
        return self.data["parameters"]

    def update_learning(self, score, params_used, feedback=""):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "score": score,
            "params": params_used,
            "feedback": feedback
        }
        self.data["history"].append(entry)
        if score < 0.6:
            if "clutch noise" in feedback.lower() or "harsh" in feedback.lower():
                self.data["parameters"]["weirdness"] = max(0, self.data["parameters"]["weirdness"] - 0.1)
            else:
                self.data["parameters"]["weirdness"] = min(1, self.data["parameters"]["weirdness"] + 0.05)
        self.save_learning_data()

    def generate_full_prompt_package(self, base_idea):
        optimized_prompt = self.optimize_prompt(base_idea)
        params = self.get_current_params()
        title = self.generate_timestamp_title()
        return {
            "title": title,
            "prompt": optimized_prompt,
            "weirdness": params["weirdness"],
            "style_influence": params["style_influence"]
        }
