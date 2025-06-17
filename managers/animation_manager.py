import pygame
from typing import Dict, List, Tuple, Optional
import json

class AnimationManager:
    def __init__(self):
        self.sprites: Dict[str, pygame.Surface] = {}
        self.animations: List[dict] = []
        self.floating_texts: List[dict] = []

    def load_sprite_sheet(self, path: str, sprite_size: Tuple[int, int]) -> List[pygame.Surface]:
        try:
            sheet = pygame.image.load(path).convert_alpha()
            sprites = []
            sheet_width = sheet.get_width()
            sheet_height = sheet.get_height()
            
            for y in range(0, sheet_height, sprite_size[1]):
                for x in range(0, sheet_width, sprite_size[0]):
                    sprite = sheet.subsurface((x, y, sprite_size[0], sprite_size[1]))
                    sprites.append(sprite)
            return sprites
        except Exception as e:
            print(f"Error loading sprite sheet {path}: {e}")
            return []

    def add_floating_text(self, text: str, pos: Tuple[int, int], color: Tuple[int, int, int], duration: int = 1000):
        self.floating_texts.append({
            'text': text,
            'pos': list(pos),
            'color': color,
            'start_time': pygame.time.get_ticks(),
            'duration': duration,
            'velocity': [0, -1]  # pixels per frame
        })

    def update_floating_texts(self):
        current_time = pygame.time.get_ticks()
        self.floating_texts = [
            text for text in self.floating_texts
            if current_time - text['start_time'] < text['duration']
        ]
        
        for text in self.floating_texts:
            text['pos'][0] += text['velocity'][0]
            text['pos'][1] += text['velocity'][1]

    def draw_floating_texts(self, screen: pygame.Surface, font: pygame.font.Font):
        for text in self.floating_texts:
            alpha = 255 * (1 - (pygame.time.get_ticks() - text['start_time']) / text['duration'])
            text_surface = font.render(text['text'], True, text['color'])
            text_surface.set_alpha(alpha)
            screen.blit(text_surface, text['pos'])
