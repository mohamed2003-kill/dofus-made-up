from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import pygame


@dataclass
class Effect:
    name: str
    type: str  # 'buff' or 'debuff'
    stat: str  # 'ap', 'mp', 'damage', etc.
    value: int
    duration: int
    source: str  # name of the character who applied the effect


@dataclass
class Spell:
    name: str
    ap_cost: int
    range_min: int
    range_max: int
    requires_los: bool
    effect_type: str
    effect_value: int
    area_of_effect: str

    def can_cast(self, caster: "Character", target_pos: Tuple[int, int]) -> bool:
        if caster.ap < self.ap_cost:
            return False
        distance = abs(caster.position[0] - target_pos[0]) + abs(
            caster.position[1] - target_pos[1]
        )
        return self.range_min <= distance <= self.range_max


class Character:
    def __init__(self, name: str, team: str, position: Tuple[int, int]):
        self.name = name
        self.team = team
        self.position = position
        self.max_hp = 100
        self.current_hp = self.max_hp
        self.max_movement_points = 3
        self.movement_points = self.max_movement_points
        self.max_action_points = 5
        self.action_points = self.max_action_points
        self.spells: Dict[str, dict] = {}

        # New attributes
        self.sprite_sheet_path: Optional[str] = None
        self.sprite_size: Tuple[int, int] = (32, 32)
        self.current_sprites: Dict[str, List[pygame.Surface]] = {}
        self.current_animation: str = "idle"
        self.animation_frame = 0
        self.effects: List[Effect] = []

    @property
    def is_alive(self) -> bool:
        return self.current_hp > 0

    def take_damage(self, amount: int) -> int:
        # Calculate actual damage after effects
        for effect in self.effects:
            if effect.type == "buff" and effect.stat == "defense":
                amount = max(0, amount - effect.value)

        self.current_hp = max(0, self.current_hp - amount)
        return amount

    def heal(self, amount: int) -> int:
        # Calculate actual healing after effects
        for effect in self.effects:
            if effect.type == "buff" and effect.stat == "healing":
                amount = amount + effect.value

        old_hp = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        return self.current_hp - old_hp

    def add_effect(self, effect: Effect):
        self.effects.append(effect)

    def remove_effect(self, effect: Effect):
        self.effects.remove(effect)

    def update_effects(self):
        # Update effect durations and remove expired effects
        self.effects = [effect for effect in self.effects if effect.duration > 0]
        for effect in self.effects:
            effect.duration -= 1

    def get_stat_with_effects(self, stat: str) -> int:
        base_value = getattr(self, f"max_{stat}", 0)
        for effect in self.effects:
            if effect.stat == stat:
                if effect.type == "buff":
                    base_value += effect.value
                else:  # debuff
                    base_value = max(0, base_value - effect.value)
        return base_value

    def start_turn(self) -> None:
        self.update_effects()
        self.action_points = self.get_stat_with_effects("action_points")
        self.movement_points = self.get_stat_with_effects("movement_points")

    def load_sprites(self, animation_frames: Dict[str, List[int]]):
        if not self.sprite_sheet_path:
            return

        try:
            sheet = pygame.image.load(self.sprite_sheet_path).convert_alpha()
            for anim_name, frames in animation_frames.items():
                self.current_sprites[anim_name] = []
                for frame in frames:
                    x = (frame * self.sprite_size[0]) % sheet.get_width()
                    y = ((frame * self.sprite_size[0]) // sheet.get_width()) * self.sprite_size[1]
                    sprite = sheet.subsurface((x, y, self.sprite_size[0], self.sprite_size[1]))
                    self.current_sprites[anim_name].append(sprite)
        except Exception as e:
            print(f"Error loading sprites for {self.name}: {e}")

    def get_current_sprite(self) -> Optional[pygame.Surface]:
        if self.current_animation in self.current_sprites:
            sprites = self.current_sprites[self.current_animation]
            if sprites:
                return sprites[self.animation_frame % len(sprites)]
        return None


class Warrior(Character):
    def __init__(self, name: str, team: str, position: Tuple[int, int]):
        super().__init__(name, team, position)
        self.max_hp = 120
        self.current_hp = self.max_hp
        self.spells = {
            "Slash": {
                "damage": 20,
                "range": 1,
                "ap_cost": 3,
                "requires_target": True,
            },
            "Shield": {
                "defense": 10,
                "range": 0,
                "ap_cost": 2,
                "requires_target": False,
            },
        }


class Archer(Character):
    def __init__(self, name: str, team: str, position: Tuple[int, int]):
        super().__init__(name, team, position)
        self.max_hp = 80
        self.current_hp = self.max_hp
        self.spells = {
            "Arrow Shot": {
                "damage": 15,
                "range": 4,
                "ap_cost": 2,
                "requires_target": True,
            },
            "Poison Arrow": {
                "damage": 10,
                "dot_damage": 5,
                "range": 3,
                "ap_cost": 3,
                "requires_target": True,
            },
        }


class Player(Character):
    def __init__(self, name: str, position: Tuple[int, int]):
        super().__init__(name, "player", position)
        self.max_hp = 120
        self.current_hp = self.max_hp
        self.spells = {
            "Fireball": {
                "damage": 20,
                "range": 4,
                "ap_cost": 3,
                "requires_target": True,
                "color": (255, 100, 0),
            },
            "Ice Bolt": {
                "damage": 15,
                "range": 3,
                "ap_cost": 2,
                "requires_target": True,
                "color": (0, 200, 255),
            },
        }


class Monster(Character):
    def __init__(
        self, name: str, position: Tuple[int, int], monster_type: str = "normal"
    ):
        super().__init__(name, "enemy", position)
        if monster_type == "boss":
            self.max_hp = 200
            self.spells = {
                "Dark Strike": {
                    "damage": 35,
                    "range": 3,
                    "ap_cost": 3,
                    "requires_target": True,
                    "color": (128, 0, 128),
                },
                "Shadow Bolt": {
                    "damage": 20,
                    "range": 4,
                    "ap_cost": 2,
                    "requires_target": True,
                    "color": (75, 0, 130),
                },
            }
        else:
            self.max_hp = 100
            self.spells = {
                "Bite": {
                    "damage": 25,
                    "range": 1,
                    "ap_cost": 2,
                    "requires_target": True,
                    "color": (255, 0, 0),
                }
            }
        self.current_hp = self.max_hp
