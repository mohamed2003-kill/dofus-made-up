import pygame
from typing import Dict, List, Tuple, Optional
import json

class UIManager:
    def __init__(self, screen: pygame.Surface, font_size: int = 24):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.font = pygame.font.Font(None, font_size)
        self.hover_timer = 0
        self.hover_delay = 500  # milliseconds
        self.last_hover_pos = None
        self.tooltip_surface = None
        
        # UI Constants
        self.CELL_SIZE = 60
        self.GRID_OFFSET_X = 50
        self.GRID_OFFSET_Y = 50
        self.SPELL_HEIGHT = 120
        self.COLORS = {
            "background": (20, 20, 30),
            "grid": (40, 40, 60),
            "player": (0, 255, 200),
            "enemy": (255, 50, 50),
            "selected": (255, 255, 0),
            "highlight_move": (100, 100, 255, 128),
            "highlight_attack": (255, 100, 100, 128),
            "spell_panel": (30, 30, 40),
            "text": (255, 255, 255),
            "current_turn": (255, 255, 0),
            "ap_mp": (0, 255, 255),
            "hp_bar_bg": (60, 60, 60),
            "hp_bar_fill": (100, 255, 100),
            "tooltip_bg": (0, 0, 0, 200),
            "tooltip_border": (100, 100, 100)
        }

    def create_tooltip(self, text: str, pos: Tuple[int, int], padding: int = 5) -> pygame.Surface:
        lines = text.split('\n')
        line_surfaces = [self.font.render(line, True, self.COLORS["text"]) for line in lines]
        
        # Calculate tooltip dimensions
        width = max(surface.get_width() for surface in line_surfaces) + padding * 2
        height = sum(surface.get_height() for surface in line_surfaces) + padding * 2
        
        # Create tooltip surface
        tooltip = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(tooltip, self.COLORS["tooltip_bg"], tooltip.get_rect())
        pygame.draw.rect(tooltip, self.COLORS["tooltip_border"], tooltip.get_rect(), 1)
        
        # Draw text lines
        y = padding
        for surface in line_surfaces:
            tooltip.blit(surface, (padding, y))
            y += surface.get_height()
            
        return tooltip

    def update_hover(self, pos: Tuple[int, int], current_time: int):
        if pos != self.last_hover_pos:
            self.hover_timer = current_time
            self.last_hover_pos = pos
        
        return current_time - self.hover_timer >= self.hover_delay

    def draw_character_tooltip(self, char, pos: Tuple[int, int]):
        tooltip_text = (
            f"{char.name}\n"
            f"HP: {char.current_hp}/{char.max_hp}\n"
            f"AP: {char.action_points}/{char.max_action_points}\n"
            f"MP: {char.movement_points}/{char.max_movement_points}"
        )
        self.tooltip_surface = self.create_tooltip(tooltip_text, pos)
        
        # Position tooltip near but not on top of the character
        tooltip_x = pos[0] + 20
        tooltip_y = pos[1] - self.tooltip_surface.get_height() - 10
        
        # Keep tooltip on screen
        if tooltip_x + self.tooltip_surface.get_width() > self.width:
            tooltip_x = self.width - self.tooltip_surface.get_width() - 5
        if tooltip_y < 0:
            tooltip_y = pos[1] + 20
            
        self.screen.blit(self.tooltip_surface, (tooltip_x, tooltip_y))

    def draw_spell_tooltip(self, spell: dict, pos: Tuple[int, int]):
        damage_str = f"Damage: {spell['damage']}" if 'damage' in spell else ""
        healing_str = f"Healing: {spell['healing']}" if 'healing' in spell else ""
        
        tooltip_text = (
            f"{spell['name']}\n"
            f"AP Cost: {spell['ap_cost']}\n"
            f"Range: {spell['range']}\n"
            f"{damage_str}\n{healing_str}\n"
            f"{spell['description']}"
        )
        
        self.tooltip_surface = self.create_tooltip(tooltip_text, pos)
        tooltip_x = pos[0]
        tooltip_y = pos[1] - self.tooltip_surface.get_height() - 10
        
        if tooltip_x + self.tooltip_surface.get_width() > self.width:
            tooltip_x = self.width - self.tooltip_surface.get_width() - 5
        if tooltip_y < 0:
            tooltip_y = pos[1] + 20
            
        self.screen.blit(self.tooltip_surface, (tooltip_x, tooltip_y))
