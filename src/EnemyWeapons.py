import math
from abc import ABC, abstractmethod

import pygame
from typing_extensions import override

from const.COLORS import RED


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
        self.rect.x += int(self.dx)
        self.rect.y += int(self.dy)

        for border in borders:
            if self.rect.colliderect(border):
                self.kill()

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class WeaponTemplate(ABC):
    def __init__(self) -> None:
        self.shoot_cd = 100
        self.shoot_timer = 0
        self.damage = 10

    @abstractmethod
    def shoot(self, tar_x, tar_y): ...

    def _on_cooldown(self):
        now = pygame.time.get_ticks()
        if now - self.shoot_timer < self.shoot_cd:
            return True

        self.shoot_timer = now
        return False


class Pistol(WeaponTemplate):
    def __init__(self, projectile_grp, player_rect) -> None:
        super().__init__()

        self.shoot_cd = 500
        self.damage = 75
        self.projectile_grp = projectile_grp
        self.rect = player_rect

    @override
    def shoot(self, tar_x, tar_y):
        if self._on_cooldown():
            return

        bullet = Bullet(5, self.rect.centerx, self.rect.centery, tar_x, tar_y, RED)
        self.projectile_grp.add(bullet)
