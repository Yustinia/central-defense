import pygame
from typing_extensions import override

from const.COLORS import BLUE, RED, WHITE, YELLOW, GREEN
from src.Abilities import Dash, Shield
from src.Entities import BoxEntity
from src.Weapons import MachineGun, Pistol, Shotgun


class Player(BoxEntity):
    def __init__(
        self, win_wd, win_ht, x_cor, y_cor, color, projectile_grp, speed=1
    ) -> None:
        super().__init__(win_wd, win_ht, x_cor, y_cor, color)

        self.health = self.max_health = 500
        self.speed = speed
        self.dx, self.dy = 0, 0
        self.friction = 0.85

        self.min_health = 250
        self.dmg_cd = 250
        self.dmg_timer = 0

        self.projectile_grp = projectile_grp

        # Weapons
        self.pistol = Pistol(
            self.projectile_grp,
            self.rect,
        )
        self.shotgun = Shotgun(
            self.projectile_grp,
            self.rect,
        )
        self.machinegun = MachineGun(
            self.projectile_grp,
            self.rect,
        )

        # Abilities
        self.dash_ab = Dash()
        self.shield_ab = Shield()

        # States
        self.is_alive = True

    @override
    def update(self, keys, borders):
        self.shield_ab.update()
        self._update_visual()

        self._movement(keys)
        self._collision(borders)

    def _update_visual(self):
        if self.shield_ab.is_active:
            self.image.fill(YELLOW)
        else:
            self.image.fill(BLUE)

    def take_damage(self, amount):
        now = pygame.time.get_ticks()
        if now - self.dmg_timer < self.dmg_cd:
            return self.is_alive
        self.dmg_timer = now

        if self.shield_ab.is_active:
            self.shield_ab.durability -= amount
            if self.shield_ab.durability <= 0:
                self.shield_ab.is_active = False
            return self.is_alive

        self.health -= amount

        if self.health <= 0 or self.health == 0:
            self.health = 0
            self.is_alive = False

        return self.is_alive

    def _movement(self, keys):
        if keys[pygame.K_a]:
            self.dx -= self.speed
        if keys[pygame.K_d]:
            self.dx += self.speed
        if keys[pygame.K_w]:
            self.dy -= self.speed
        if keys[pygame.K_s]:
            self.dy += self.speed

        if keys[pygame.K_SPACE]:
            self.dx, self.dy = self.dash_ab.do_dash(self.dx, self.dy)

        if keys[pygame.K_e]:
            self.shield_ab.activate()

    def _collision(self, borders):
        self.rect.x += int(self.dx)
        for border in borders:
            if self.rect.colliderect(border.rect):
                self.rect.x -= int(self.dx)
                self.dx = 0

        self.rect.y += int(self.dy)
        for border in borders:
            if self.rect.colliderect(border.rect):
                self.rect.y -= int(self.dy)
                self.dy = 0

        self.dx *= self.friction
        self.dy *= self.friction

    def draw_health_bar(self, win_wd, win_ht, screen):
        bar_wd = win_wd // 4
        bar_ht = 20

        bar_rect = pygame.Rect(0, 0, bar_wd, bar_ht)
        bar_rect.center = (win_wd // 3, win_ht - 60)

        fill_wd = int(self.health / self.max_health * bar_wd)

        health_pct = self.health / self.max_health
        if health_pct <= 0.25:
            fill_color = RED
        elif health_pct <= 0.50:
            fill_color = YELLOW
        else:
            fill_color = BLUE

        pygame.draw.rect(screen, fill_color, (bar_rect.x, bar_rect.y, fill_wd, bar_ht))
        pygame.draw.rect(screen, WHITE, bar_rect, 1)

    def draw_shield_bar(self, win_wd, win_ht, screen):
        bar_wd = win_wd // 4
        bar_ht = 20

        bar_rect = pygame.Rect(0, 0, bar_wd, bar_ht)
        bar_rect.center = ((2 * win_wd) // 3, win_ht - 60)

        if not self.shield_ab.can_be_activated and not self.shield_ab.is_active:

            now = pygame.time.get_ticks()
            elapsed = now - self.shield_ab.shield_timer
            progress = min(elapsed / self.shield_ab.shield_cd, 1.0)

            fill_wd = int(progress * bar_wd)
            fill_color = RED

        elif self.shield_ab.is_active:
            fill_wd = int(
                self.shield_ab.durability / self.shield_ab.durability_init * bar_wd
            )
            fill_color = YELLOW

        else:
            fill_wd = bar_wd
            fill_color = GREEN

        pygame.draw.rect(screen, fill_color, (bar_rect.x, bar_rect.y, fill_wd, bar_ht))
        pygame.draw.rect(screen, WHITE, bar_rect, 1)
