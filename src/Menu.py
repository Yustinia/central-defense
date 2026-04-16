import pygame

from const.COLORS import BLACK, BLUE, ORANGE, WHITE
from const.FONTS import BOLD, REGULAR
from src.Core import Background, Border
from src.Player import Player


class MainMenu:
    def __init__(self, win_wd, win_ht) -> None:
        self.win_wd = win_wd
        self.win_ht = win_ht

        bg_color = BLACK
        self.bg = Background(self.win_wd, self.win_ht, bg_color)
        flr_thickness = 200
        self.flr = Border(
            self.win_wd,
            flr_thickness,
            0,
            self.win_ht - flr_thickness,
            WHITE,
        )
        ply_wd, ply_ht = 100, 100
        padding = 10
        self.player = Player(
            self.win_wd // 2,
            self.flr.rect.top - (ply_ht // 2) - padding,
            BLUE,
            None,
            1,
            ply_wd,
            ply_ht,
        )

        self.header_ft = pygame.font.Font(BOLD, 120)
        self.sub_ft = pygame.font.Font(REGULAR, 50)

    def draw(self, screen):
        self.bg.draw(screen)
        self.flr.draw(screen)
        self.player.draw(screen)

        header_img = self.header_ft.render("CENTRAL DEFENSE", True, WHITE)
        header_cor_x, header_cor_y = self.win_wd // 2, 120
        header_rect = header_img.get_rect(center=(header_cor_x, header_cor_y))

        sub_img = self.sub_ft.render("Click to Start", True, BLACK)
        sub_cor_x, sub_cor_y = self.flr.rect.centerx, self.flr.rect.centery
        sub_rect = sub_img.get_rect(center=(sub_cor_x, sub_cor_y))

        screen.blit(header_img, header_rect)

        if (pygame.time.get_ticks() // 1000) % 2 == 0:
            screen.blit(sub_img, sub_rect)


class GameOver:
    def __init__(self, win_wd, win_ht) -> None:
        self.win_wd = win_wd
        self.win_ht = win_ht

        bg_color = ORANGE
        self.bg = Background(self.win_wd, self.win_ht, bg_color)

        self.header_ft = pygame.font.Font(BOLD, 130)
        self.sub_ft = pygame.font.Font(REGULAR, 40)

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


class PlayingState:
    def __init__(self, win_wd, win_ht) -> None:
        self.win_wd = win_wd
        self.win_ht = win_ht

        self.round_state_ft = pygame.font.Font(REGULAR, 90)
        self.current_weap_ft = pygame.font.Font(REGULAR, 30)

    def render_round(self, round_counter, screen):
        round_counter_img = self.round_state_ft.render(
            f"ROUND {round_counter}", True, WHITE
        )
        round_counter_img.set_alpha(8)
        round_counter_rect = round_counter_img.get_rect(
            center=(self.win_wd // 2, self.win_ht // 2)
        )

        screen.blit(round_counter_img, round_counter_rect)

    def render_current_weap(self, current_weap, screen):
        current_weap_img = self.current_weap_ft.render(current_weap, True, WHITE)
        current_weap_img.set_alpha(32)
        current_weap_rect = current_weap_img.get_rect(
            midbottom=(self.win_wd // 2, self.win_ht - 80)
        )

        screen.blit(current_weap_img, current_weap_rect)


class PauseMenu:
    def __init__(self, win_wd, win_ht) -> None:
        self.win_wd = win_wd
        self.win_ht = win_ht

        # Semi-transparent overlay
        self.overlay = pygame.Surface((win_wd, win_ht))
        self.overlay.set_alpha(180)
        self.overlay.fill(BLACK)

        self.header_ft = pygame.font.Font(BOLD, 100)
        self.sub_ft = pygame.font.Font(REGULAR, 40)

    def draw(self, screen):
        screen.blit(self.overlay, (0, 0))

        header_img = self.header_ft.render("PAUSED", True, WHITE)
        header_rect = header_img.get_rect(center=(self.win_wd // 2, self.win_ht // 2))
        screen.blit(header_img, header_rect)

        esc_img = self.sub_ft.render("Press ESC to Resume", True, WHITE)
        esc_rect = esc_img.get_rect(
            centerx=self.win_wd // 2, top=header_rect.bottom + 50
        )

        quit_img = self.sub_ft.render("Q to Quit", True, WHITE)
        quit_rect = quit_img.get_rect(
            centerx=self.win_wd // 2, top=esc_rect.bottom + 25
        )

        if (pygame.time.get_ticks() // 1000) % 2 == 0:
            screen.blit(esc_img, esc_rect)
            screen.blit(quit_img, quit_rect)
