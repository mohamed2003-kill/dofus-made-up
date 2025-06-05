import pygame
from game_manager import GameManager


def main():

    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    pygame.display.set_caption("Python Tactical Combat")

    game = GameManager()
    game.setup_game(screen)
    game.run_game()

    pygame.quit()


if __name__ == "__main__":
    main()
