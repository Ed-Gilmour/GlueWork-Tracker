import yaml

class ConfigHandler:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = None

    def load_config(self):
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    def get_excluded_users(self):
        return self.config.get('excluded_users', [])

    def get_top_count(self):
        return self.config.get('top_count', 10)

    def get_retrieved_days(self):
        return self.config.get('retrieved_days', 30)

    def get_repository(self):
        return self.config.get('repository', "")