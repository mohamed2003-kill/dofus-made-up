import pygame
import random
from typing import List, Tuple, Optional, Set
from models import Character, Player, Monster
from game_board import GameBoard


class GameManager:
    def __init__(self):
        self.board = GameBoard(10, 10)
        self.player: Character = None
        self.monsters: List[Character] = []
        self.current_turn = 0
        self.all_characters = []
        self.selected_spell = None
        self.selected_character = None
        self.turn_order = []
        self.current_player_index = 0
        self.highlighted_cells: Set[Tuple[int, int]] = set()

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
            "game_over_bg": (0, 0, 0, 180),
            "win_text": (0, 255, 0),
            "lose_text": (255, 0, 0),
        }
        self.game_over = False
        self.game_won = False

    def init_pygame(self, screen):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.font = pygame.font.Font(None, 24)

    def setup_game(self, screen):
        self.init_pygame(screen)

        self.player = Player("Hero", (1, 1))

        self.monsters = [
            Monster("Boss Monster", (8, 8), "boss"),
            Monster("Monster 1", (7, 7)),
            Monster("Monster 2", (8, 7)),
            Monster("Monster 3", (2, 1)),
        ]

        self.all_characters = [self.player] + self.monsters
        self.turn_order = self.all_characters.copy()

        for char in self.all_characters:
            self.board.add_character(char, char.position)

    def handle_mouse_click(self, pos):
        mouse_x, mouse_y = pos
        grid_x = (mouse_x - self.GRID_OFFSET_X) // self.CELL_SIZE
        grid_y = (mouse_y - self.GRID_OFFSET_Y) // self.CELL_SIZE

        if 0 <= grid_x < self.board.width and 0 <= grid_y < self.board.height:
            clicked_pos = (grid_x, grid_y)
            current_char = self.turn_order[self.current_player_index]

            if current_char == self.player:
                if self.selected_spell and clicked_pos in self.highlighted_cells:
                    spell = current_char.spells[self.selected_spell]
                    if self.cast_spell(current_char, spell, clicked_pos):
                        self.selected_spell = None
                        self.highlighted_cells.clear()
                elif not self.selected_spell and clicked_pos in self.highlighted_cells:
                    self.move_character(current_char, clicked_pos)
                    self.highlighted_cells.clear()

    def handle_key_press(self, key):
        current_char = self.turn_order[self.current_player_index]
        if current_char == self.player:
            if key == pygame.K_F1:
                self.end_turn()
            elif pygame.K_1 <= key <= pygame.K_9:
                self.highlighted_cells.clear()
                spell_index = key - pygame.K_1
                if spell_index < len(current_char.spells):
                    spell_name = list(current_char.spells.keys())[spell_index]
                    spell = current_char.spells[spell_name]
                    if spell["ap_cost"] <= current_char.action_points:
                        self.selected_spell = spell_name
                        self.highlight_spell_range(current_char, spell)
            elif key == pygame.K_ESCAPE:
                self.selected_spell = None
                self.highlighted_cells.clear()
                self.highlight_movement_range(current_char)

    def highlight_movement_range(self, character: Character):
        self.highlighted_cells = set(
            self.board.get_movable_positions(
                character.position, character.movement_points
            )
        )

    def highlight_spell_range(self, character: Character, spell: dict):
        self.highlighted_cells.clear()
        range_val = spell["range"]
        for x in range(
            max(0, character.position[0] - range_val),
            min(self.board.width, character.position[0] + range_val + 1),
        ):
            for y in range(
                max(0, character.position[1] - range_val),
                min(self.board.height, character.position[1] + range_val + 1),
            ):
                if (x, y) != character.position:
                    distance = abs(x - character.position[0]) + abs(
                        y - character.position[1]
                    )
                    if distance <= range_val:
                        if spell["requires_target"]:
                            if self.board.get_character_at((x, y)):
                                self.highlighted_cells.add((x, y))
                        else:
                            self.highlighted_cells.add((x, y))

    def cast_spell(
        self, character: Character, spell: dict, target_pos: Tuple[int, int]
    ) -> bool:
        if spell["ap_cost"] > character.action_points:
            return False

        target = self.board.get_character_at(target_pos)
        if target:
            damage = spell.get("damage", 0)
            target.current_hp -= damage
            character.action_points -= spell["ap_cost"]

            if target.current_hp <= 0 and target in self.monsters:
                self.monsters.remove(target)
                self.board.remove_character(target.position)
                self.turn_order.remove(target)
                self.all_characters.remove(target)
            return True
        return False

    def move_character(self, character: Character, new_pos: Tuple[int, int]):
        if character.movement_points > 0:
            old_pos = character.position

            distance = abs(new_pos[0] - old_pos[0]) + abs(new_pos[1] - old_pos[1])
            if distance <= character.movement_points:
                self.board.remove_character(character.position)
                character.position = new_pos
                self.board.add_character(character, new_pos)
                character.movement_points -= distance

    def end_turn(self):
        self.current_player_index = (self.current_player_index + 1) % len(
            self.turn_order
        )
        current_char = self.turn_order[self.current_player_index]
        current_char.movement_points = current_char.max_movement_points
        current_char.action_points = current_char.max_action_points
        self.selected_spell = None
        self.highlighted_cells.clear()

        if current_char == self.player:
            self.highlight_movement_range(current_char)

    def draw_grid(self):
        for x in range(self.board.width):
            for y in range(self.board.height):
                rect = pygame.Rect(
                    self.GRID_OFFSET_X + x * self.CELL_SIZE,
                    self.GRID_OFFSET_Y + y * self.CELL_SIZE,
                    self.CELL_SIZE,
                    self.CELL_SIZE,
                )
                pygame.draw.rect(self.screen, self.COLORS["grid"], rect, 1)

                if (x, y) in self.highlighted_cells:
                    highlight_surface = pygame.Surface(
                        (self.CELL_SIZE, self.CELL_SIZE), pygame.SRCALPHA
                    )
                    color = (
                        self.COLORS["highlight_attack"]
                        if self.selected_spell
                        else self.COLORS["highlight_move"]
                    )
                    pygame.draw.rect(
                        highlight_surface, color, highlight_surface.get_rect()
                    )
                    self.screen.blit(highlight_surface, rect)

    def draw_characters(self):
        for char in self.all_characters:
            x = self.GRID_OFFSET_X + char.position[0] * self.CELL_SIZE
            y = self.GRID_OFFSET_Y + char.position[1] * self.CELL_SIZE

            color = (
                self.COLORS["player"] if char.team == "player" else self.COLORS["enemy"]
            )
            if char == self.turn_order[self.current_player_index]:
                pygame.draw.rect(
                    self.screen,
                    self.COLORS["selected"],
                    (x, y, self.CELL_SIZE, self.CELL_SIZE),
                )

            pygame.draw.circle(
                self.screen,
                color,
                (x + self.CELL_SIZE // 2, y + self.CELL_SIZE // 2),
                self.CELL_SIZE // 3,
            )

            hp_rect = pygame.Rect(x, y - 10, self.CELL_SIZE, 5)
            pygame.draw.rect(self.screen, self.COLORS["hp_bar_bg"], hp_rect)
            fill_width = int((char.current_hp / char.max_hp) * self.CELL_SIZE)
            hp_fill_rect = pygame.Rect(x, y - 10, fill_width, 5)
            pygame.draw.rect(self.screen, self.COLORS["hp_bar_fill"], hp_fill_rect)

    def draw_spell_panel(self):
        panel_rect = pygame.Rect(
            0, self.height - self.SPELL_HEIGHT, self.width, self.SPELL_HEIGHT
        )
        pygame.draw.rect(self.screen, self.COLORS["spell_panel"], panel_rect)

        current_char = self.turn_order[self.current_player_index]
        if current_char == self.player:
            x_offset = 10
            for i, (spell_name, spell) in enumerate(current_char.spells.items()):
                color = (
                    spell["color"]
                    if spell_name == self.selected_spell
                    else self.COLORS["text"]
                )
                text = f"{i+1}: {spell_name} (AP: {spell['ap_cost']})"
                text_surface = self.font.render(text, True, color)
                self.screen.blit(
                    text_surface, (x_offset, self.height - self.SPELL_HEIGHT + 10)
                )
                x_offset += text_surface.get_width() + 20

    def draw_status_panel(self):
        current_char = self.turn_order[self.current_player_index]
        status_text = f"AP: {current_char.action_points}/{current_char.max_action_points} | MP: {current_char.movement_points}/{current_char.max_movement_points}"
        text_surface = self.font.render(status_text, True, self.COLORS["ap_mp"])
        self.screen.blit(text_surface, (10, self.height - self.SPELL_HEIGHT - 30))

        y_offset = 10
        for i, char in enumerate(self.turn_order):
            color = (
                self.COLORS["current_turn"]
                if i == self.current_player_index
                else self.COLORS["text"]
            )
            text = f"{char.name} - HP: {char.current_hp}/{char.max_hp}"
            text_surface = self.font.render(text, True, color)
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 25

    def draw_game_over_screen(self):

        bg_rect = pygame.Rect(0, 0, self.width, self.height)
        pygame.draw.rect(self.screen, self.COLORS["game_over_bg"], bg_rect)

        current_char = self.turn_order[self.current_player_index]
        if self.game_won:
            text = "You Win!"
            color = self.COLORS["win_text"]
        else:
            text = "Game Over"
            color = self.COLORS["lose_text"]
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text_surface, text_rect)

    def check_game_over(self):
        if self.player.current_hp <= 0:
            self.game_over = True
            self.game_won = False
        elif len(self.monsters) == 0:
            self.game_over = True
            self.game_won = True
        return self.game_over

    def draw_game_over(self):

        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(overlay, self.COLORS["game_over_bg"], overlay.get_rect())
        self.screen.blit(overlay, (0, 0))

        font = pygame.font.Font(None, 74)
        if self.game_won:
            text = font.render("Victory!", True, self.COLORS["win_text"])
        else:
            text = font.render("Game Over", True, self.COLORS["lose_text"])

        text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text, text_rect)

        font_small = pygame.font.Font(None, 36)
        restart_text = font_small.render(
            "Press R to restart", True, self.COLORS["text"]
        )
        restart_rect = restart_text.get_rect(
            center=(self.width // 2, self.height // 2 + 50)
        )
        self.screen.blit(restart_text, restart_rect)

    def draw(self):
        self.screen.fill(self.COLORS["background"])
        self.draw_grid()
        self.draw_characters()
        self.draw_spell_panel()
        self.draw_status_panel()

        if self.game_over:
            self.draw_game_over()

        pygame.display.flip()

    def run_game(self):
        clock = pygame.time.Clock()
        running = True

        if self.turn_order[0] == self.player:
            self.highlight_movement_range(self.player)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.game_over and event.key == pygame.K_r:

                        self.__init__()
                        self.setup_game(self.screen)
                        continue
                    else:
                        self.handle_key_press(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                    if event.button == 1:
                        self.handle_mouse_click(event.pos)

            if not self.game_over:

                current_char = self.turn_order[self.current_player_index]
                if current_char in self.monsters:

                    self.handle_monster_turn(current_char)

                self.check_game_over()

            self.draw()
            clock.tick(60)

    def handle_monster_turn(self, monster: Character):

        if self.can_attack_player(monster):
            spell = list(monster.spells.values())[0]
            self.cast_spell(monster, spell, self.player.position)
        else:

            if monster.movement_points > 0:
                path = self.board.get_path(monster.position, self.player.position)
                if len(path) > 1:
                    self.move_character(monster, path[1])

        self.end_turn()

    def can_attack_player(self, monster: Character) -> bool:
        if not monster.spells:
            return False
        spell = list(monster.spells.values())[0]
        distance = abs(monster.position[0] - self.player.position[0]) + abs(
            monster.position[1] - self.player.position[1]
        )
        return distance <= spell["range"]

    def update(self):
        self.check_game_over()
        if self.game_over:

            pass
