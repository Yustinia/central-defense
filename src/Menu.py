import pygame

from const.COLORS import BLACK, ORANGE, WHITE
from const.FONTS import BOLD, HEADER_SZ, REGULAR, SUBTITLE_SZ
from src.Core import Background


class MainMenu:
    def __init__(self, win_wd, win_ht) -> None:
        self.win_wd = win_wd
        self.win_ht = win_ht

        bg_color = BLACK
        self.bg = Background(self.win_wd, self.win_ht, bg_color)

        self.header_ft = pygame.font.Font(BOLD, HEADER_SZ)
        self.sub_ft = pygame.font.Font(REGULAR, SUBTITLE_SZ)

    def draw(self, screen):
        self.bg.draw(screen)

        header_img = self.header_ft.render("CENTRAL DEFENSE", True, WHITE)
        header_cor_x, header_cor_y = self.win_wd // 2, (self.win_ht // 2) - 50
        header_rect = header_img.get_rect(center=(header_cor_x, header_cor_y))

        sub_img = self.sub_ft.render("Click to Start", True, WHITE)
        sub_cor_x, sub_cor_y = self.win_wd // 2, (self.win_ht // 2) + 50
        sub_rect = sub_img.get_rect(center=(sub_cor_x, sub_cor_y))

        screen.blit(header_img, header_rect)

        if (pygame.time.get_ticks() // 500) % 2 == 0:
            screen.blit(sub_img, sub_rect)


class GameOver:
    def __init__(self, win_wd, win_ht) -> None:
        self.win_wd = win_wd
        self.win_ht = win_ht

        bg_color = ORANGE
        self.bg = Background(self.win_wd, self.win_ht, bg_color)

        self.header_ft = pygame.font.Font(BOLD, HEADER_SZ)
        self.sub_ft = pygame.font.Font(REGULAR, SUBTITLE_SZ)

    def draw(self, screen):
        self.bg.draw(screen)

        header_img = self.header_ft.render("GAME OVER", True, WHITE)
        header_cor_x, header_cor_y = self.win_wd // 2, (self.win_ht // 2) - 50
        header_rect = header_img.get_rect(center=(header_cor_x, header_cor_y))

        sub_img = self.sub_ft.render("Click to Start", True, WHITE)
        sub_cor_x, sub_cor_y = self.win_wd // 2, (self.win_ht // 2) + 50
        sub_rect = sub_img.get_rect(center=(sub_cor_x, sub_cor_y))

        screen.blit(header_img, header_rect)
        screen.blit(sub_img, sub_rect)
