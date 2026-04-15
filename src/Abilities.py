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


class Shield:
    def __init__(self) -> None:
        self.shield_cd = 30000
        self.shield_timer = 0
        self.shield_duration = 12000
        self.active_timer = 0
        self.is_active = False
        self.durability = self.durability_init = 150
        self.can_be_activated = False

    def update(self):
        now = pygame.time.get_ticks()

        if self.is_active and now - self.active_timer > self.shield_duration:
            self.is_active = False
            self.can_be_activated = False
            self.shield_timer = now

        if not self.can_be_activated and now - self.shield_timer > self.shield_cd:
            self.can_be_activated = True

    def activate(self):
        if not self.can_be_activated:
            return

        now = pygame.time.get_ticks()
        self.is_active = True
        self.can_be_activated = False
        self.shield_timer = now
        self.active_timer = now
        self.durability = self.durability_init


class PassiveHeal:
    def __init__(self) -> None:
        self.heal_cd = 12000
        self.heal_amt = 10
        self.heal_timer = 0
        self.is_active = True

    def is_ready(self):
        now = pygame.time.get_ticks()
        if now - self.heal_timer > self.heal_cd:
            self.heal_timer = now
            return True

        return False
