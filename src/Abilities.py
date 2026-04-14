import pygame

from const.COLORS import WHITE, YELLOW
from src.Entities import OctEntity


class Dash:
    def __init__(self) -> None:
        self.dash_spd = 5
        self.dash_cd = 500
        self.dash_timer = 0

    def do_dash(self, dx, dy):
        now = pygame.time.get_ticks()
        if now - self.dash_timer < self.dash_cd:
            return dx, dy
        if dx == 0 and dy == 0:
            return dx, dy
        self.dash_timer = now

        return dx * self.dash_spd, dy * self.dash_spd


class Shield(OctEntity):
    def __init__(self, size, x_cor, y_cor, color) -> None:
        super().__init__(size, x_cor, y_cor, color)

        self.shield_cd = 30000
        self.shield_timer = 0
        self.shield_duration = 12000
        self.active_timer = 0
        self.is_active = False
        self.durability = self.durability_init = 150
        self.can_be_activated = False

    def update(self, player_x, player_y):
        self.movement(player_x, player_y)

        now = pygame.time.get_ticks()
        if self.is_active and now - self.active_timer > self.shield_duration:
            self.is_active = False
            self.can_be_activated = False
            self.shield_timer = now

        if not self.can_be_activated and now - self.shield_timer > self.shield_cd:
            self.can_be_activated = True

    def movement(self, player_x, player_y):
        self.rect.center = (player_x, player_y)

    def activate(self):
        if not self.can_be_activated:
            return

        now = pygame.time.get_ticks()
        self.is_active = True
        self.can_be_activated = False
        self.shield_timer = now
        self.active_timer = now
        self.durability = self.durability_init

    def draw(self, screen):
        if self.is_active:
            screen.blit(self.image, self.rect)
