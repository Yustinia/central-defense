import math

import pygame

from const.COLORS import PLAT
from src.Weapons import Bullet


class Dash:
    def __init__(self, dash_spd=5, dash_cd=500) -> None:
        self.dash_spd = dash_spd
        self.dash_cd = dash_cd
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
    def __init__(
        self, shield_cd=30000, shield_duration=12000, shield_durability=150
    ) -> None:
        self.shield_cd = shield_cd
        self.shield_timer = 0
        self.shield_duration = shield_duration
        self.active_timer = 0
        self.is_active = False
        self.durability = self.durability_init = shield_durability
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
    def __init__(self, heal_cd=20000, heal_amt=10) -> None:
        self.heal_cd = heal_cd
        self.heal_amt = heal_amt
        self.heal_timer = 0
        self.is_active = True

    def is_ready(self):
        now = pygame.time.get_ticks()
        if now - self.heal_timer > self.heal_cd:
            self.heal_timer = now
            return True

        return False


class BulletBurst:
    def __init__(self, burst_cd=18000, bullet_count=16) -> None:
        self.burst_cd = burst_cd
        self.burst_timer = 0
        self.bullet_count = bullet_count
        self.is_active = False

    def is_ready(self):
        now = pygame.time.get_ticks()
        if not self.is_active and now - self.burst_timer > self.burst_cd:
            return True
        return False

    def burst(self, projectile_grp, x_cor, y_cor, radius=10, color=PLAT, damage=100):
        now = pygame.time.get_ticks()
        self.burst_timer = now
        self.is_active = True

        angle_step = 360 / self.bullet_count
        for ring_speed in (3, 5, 9):
            for i in range(self.bullet_count):
                angle = math.radians(angle_step * i)
                tar_x = x_cor + math.cos(angle) * 100
                tar_y = y_cor + math.sin(angle) * 100
                projectile_grp.add(
                    Bullet(
                        radius, x_cor, y_cor, tar_x, tar_y, color, damage, ring_speed
                    )
                )

        self.is_active = False
