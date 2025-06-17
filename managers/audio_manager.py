import pygame
import os
from typing import Dict, Optional

class AudioManager:
    def __init__(self):
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music: Optional[str] = None
        self.sound_enabled = True
        self.music_enabled = True
        pygame.mixer.init()

    def load_sound(self, name: str, file_path: str) -> bool:
        try:
            if os.path.exists(file_path):
                self.sounds[name] = pygame.mixer.Sound(file_path)
                return True
        except:
            print(f"Failed to load sound: {file_path}")
        return False

    def play_sound(self, name: str):
        if self.sound_enabled and name in self.sounds:
            self.sounds[name].play()

    def play_music(self, file_path: str, loop: bool = True):
        if self.music_enabled and os.path.exists(file_path):
            try:
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play(-1 if loop else 0)
                self.music = file_path
            except:
                print(f"Failed to play music: {file_path}")

    def stop_music(self):
        pygame.mixer.music.stop()
        self.music = None

    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled

    def toggle_music(self):
        self.music_enabled = not self.music_enabled
        if self.music_enabled and self.music:
            self.play_music(self.music)
        else:
            self.stop_music()
