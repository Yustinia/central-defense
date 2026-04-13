import math
import random
from abc import abstractmethod

import pygame
from typing_extensions import override

from const.COLORS import BLUE


class Bullet(pygame.sprite.Sprite):
    def __init__(self, radius, x_cor, y_cor, tar_x, tar_y, color, speed=10) -> None:
        super().__init__()

        self.radius = radius
        self.speed = speed
        self.tar_x = tar_x
        self.tar_y = tar_y
        self.color = color

        angle = math.atan2(tar_y - y_cor, tar_x - x_cor)
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed

        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (radius, radius), radius)
        self.rect = self.image.get_rect(center=(x_cor, y_cor))

    def update(self, borders):
        self.rect.x += self.dx
        self.rect.y += self.dy

        for border in borders:
            if self.rect.colliderect(border):
                self.kill()

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class WeaponTemplate:
    def __init__(self) -> None:
        self.shoot_cd = 100
        self.shoot_timer = 0
        self.damage = 10

    @abstractmethod
    def shoot(self):
        pass

    def _on_cooldown(self):
        now = pygame.time.get_ticks()
        if now - self.shoot_timer < self.shoot_cd:
            return True

        self.shoot_timer = now
        return False


class Pistol(WeaponTemplate):
    def __init__(self, projectile_grp, player_rect) -> None:
        super().__init__()

        self.shoot_cd = 150
        self.damage = 20
        self.projectile_grp = projectile_grp
        self.rect = player_rect

    @override
    def shoot(self, tar_x, tar_y):
        if self._on_cooldown():
            return

        bullet = Bullet(5, self.rect.centerx, self.rect.centery, tar_x, tar_y, BLUE)
        self.projectile_grp.add(bullet)


class Shotgun(WeaponTemplate):
    def __init__(self, projectile_grp, player_rect) -> None:
        super().__init__()

        self.shoot_cd = 750
        self.damage = 40
        self.projectile_grp = projectile_grp
        self.rect = player_rect

    @override
    def shoot(self, tar_x, tar_y):
        if self._on_cooldown():
            return

        spread = 15
        pellets = 4
        base_angle = math.degrees(
            math.atan2(tar_y - self.rect.centery, tar_x - self.rect.centerx)
        )

        for i in range(pellets):
            offset = (i - pellets // 2) * spread  # e.g. -30, -15, 0, 15, 30
            angle = math.radians(base_angle + offset)
            tar_x_off = self.rect.centerx + math.cos(angle) * 100
            tar_y_off = self.rect.centery + math.sin(angle) * 100
            self.projectile_grp.add(
                Bullet(
                    10,
                    self.rect.centerx,
                    self.rect.centery,
                    tar_x_off,
                    tar_y_off,
                    BLUE,
                    20,
                )
            )


class MachineGun(WeaponTemplate):
    def __init__(self, projectile_grp, player_rect) -> None:
        super().__init__()

        self.shoot_cd = 25
        self.damage = 10
        self.projectile_grp = projectile_grp
        self.rect = player_rect

    @override
    def shoot(self, tar_x, tar_y):
        if self._on_cooldown():
            return

        base_angle = math.atan2(tar_y - self.rect.centery, tar_x - self.rect.centerx)
        deviation = random.uniform(-0.15, 0.15)  # radians
        angle = base_angle + deviation

        tar_x_off = self.rect.centerx + math.cos(angle) * 100
        tar_y_off = self.rect.centery + math.sin(angle) * 100

        bullet = Bullet(
            2, self.rect.centerx, self.rect.centery, tar_x_off, tar_y_off, BLUE, 30
        )
        self.projectile_grp.add(bullet)
