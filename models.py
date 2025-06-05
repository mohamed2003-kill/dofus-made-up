from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass


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

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> None:
        self.hp = max(0, self.hp - amount)

    def heal(self, amount: int) -> None:
        self.hp = min(self.max_hp, self.hp + amount)

    def start_turn(self) -> None:
        self.ap = self.max_ap
        self.mp = self.max_mp

    def can_move_to(self, new_pos: Tuple[int, int], board: "GameBoard") -> bool:
        if not board.is_valid_position(new_pos):
            return False
        if board.is_occupied(new_pos):
            return False
        distance = abs(self.position[0] - new_pos[0]) + abs(
            self.position[1] - new_pos[1]
        )
        return distance <= self.mp

    def move_to(self, new_pos: Tuple[int, int]) -> None:
        distance = abs(self.position[0] - new_pos[0]) + abs(
            self.position[1] - new_pos[1]
        )
        self.mp -= distance
        self.position = new_pos


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
