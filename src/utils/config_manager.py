import json
import os

class ConfigManager:
    def __init__(self, config_dir="configs"):
        self.config_dir = config_dir
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

    def save_config(self, name, config_dict):
        file_path = os.path.join(self.config_dir, f"{name}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=4, ensure_ascii=False)
        return file_path

    def load_config(self, name):
        file_path = os.path.join(self.config_dir, f"{name}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def list_configs(self):
        configs = []
        for file in os.listdir(self.config_dir):
            if file.endswith(".json"):
                configs.append(file.replace(".json", ""))
        return configs
