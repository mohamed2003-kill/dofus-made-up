import json
import os
from typing import Dict, Any

class DataManager:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.characters_data = {}
        self.spells_data = {}
        self.load_data()

    def load_data(self):
        try:
            with open(os.path.join(self.data_path, 'characters.json'), 'r') as f:
                self.characters_data = json.load(f)
            with open(os.path.join(self.data_path, 'spells.json'), 'r') as f:
                self.spells_data = json.load(f)
        except Exception as e:
            print(f"Error loading game data: {e}")
            self.characters_data = {}
            self.spells_data = {}

    def get_character_data(self, char_type: str, monster_type: str = None) -> Dict[str, Any]:
        if char_type == "player":
            return self.characters_data.get("player", {})
        elif char_type == "monster" and monster_type:
            return self.characters_data.get("monsters", {}).get(monster_type, {})
        return {}

    def get_spells(self, char_type: str, monster_type: str = None) -> Dict[str, Any]:
        if char_type == "player":
            return self.spells_data.get("player_spells", {})
        elif char_type == "monster" and monster_type:
            return self.spells_data.get("monster_spells", {}).get(monster_type, {})
