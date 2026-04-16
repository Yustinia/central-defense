import math
import random
from abc import ABC, abstractmethod

import pygame
from typing_extensions import override

from const.COLORS import PLAT, RED


class Bullet(pygame.sprite.Sprite):
    def __init__(
        self, radius, x_cor, y_cor, tar_x, tar_y, color=PLAT, damage=10, speed=10
    ) -> None:
        super().__init__()

        self.radius = radius
        self.speed = speed
        self.damage = damage
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

    @abstractmethod
    def shoot(self, tar_x, tar_y): ...

    def _on_cooldown(self):
        now = pygame.time.get_ticks()
        if now - self.shoot_timer < self.shoot_cd:
            return True

        self.shoot_timer = now
        return False


class Pistol(WeaponTemplate):
    def __init__(
        self,
        projectile_grp,
        player_rect,
        rad=5,
        shoot_cd=150,
        damage=20,
        color=PLAT,
        speed=10,
    ) -> None:
        super().__init__()

        self.rad = rad
        self.shoot_cd = shoot_cd
        self.damage = damage
        self.speed = speed
        self.color = color
        self.projectile_grp = projectile_grp
        self.rect = player_rect

    @override
    def shoot(self, tar_x, tar_y):
        if self._on_cooldown():
            return

        bullet = Bullet(
            self.rad,
            self.rect.centerx,
            self.rect.centery,
            tar_x,
            tar_y,
            self.color,
            self.damage,
            self.speed,
        )
        self.projectile_grp.add(bullet)


class Shotgun(WeaponTemplate):
    def __init__(
        self,
        projectile_grp,
        player_rect,
        rad=10,
        shoot_cd=750,
        damage=40,
        color=PLAT,
        speed=20,
    ) -> None:
        super().__init__()

        self.rad = rad
        self.shoot_cd = shoot_cd
        self.damage = damage
        self.speed = speed
        self.color = color
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
                    self.rad,
                    self.rect.centerx,
                    self.rect.centery,
                    tar_x_off,
                    tar_y_off,
                    self.color,
                    self.damage,
                    self.speed,
                )
            )


class MachineGun(WeaponTemplate):
    def __init__(
        self,
        projectile_grp,
        player_rect,
        rad=5,
        shoot_cd=25,
        damage=10,
        color=PLAT,
        speed=30,
    ) -> None:
        super().__init__()

        self.rad = rad
        self.shoot_cd = shoot_cd
        self.damage = damage
        self.speed = speed
        self.color = color
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
            self.rad,
            self.rect.centerx,
            self.rect.centery,
            tar_x_off,
            tar_y_off,
            self.color,
            self.damage,
            self.speed,
        )
        self.projectile_grp.add(bullet)


class Laser(pygame.sprite.Sprite):
    def __init__(
        self,
        x_cor,
        y_cor,
        tar_x,
        tar_y,
        thickness=4,
        color=RED,
        damage=5,
        duration=25,
    ) -> None:
        super().__init__()

        self.x_cor = x_cor
        self.y_cor = y_cor
        self.tar_x = tar_x
        self.tar_y = tar_y
        self.spawned = pygame.time.get_ticks()

        self.thickness = thickness
        self.color = color
        self.damage = damage
        self.duration = duration

        dx = tar_x - x_cor
        dy = tar_y - y_cor
        length = math.hypot(dx, dy)
        angle = math.degrees(math.atan2(dy, dx))

        self.image = pygame.Surface((length, self.thickness), pygame.SRCALPHA)
        self.image.fill(self.color)
        self.image = pygame.transform.rotate(self.image, -angle)
        self.rect = self.image.get_rect(center=(x_cor + dx / 2, y_cor + dy / 2))
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, borders):
        now = pygame.time.get_ticks()
        if now - self.spawned > self.duration:
            self.kill()

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class LaserGun(WeaponTemplate):
    def __init__(
        self,
        beam_grp,
        player_rect,
        thickness=8,
        shoot_cd=25,
        damage=2,
        duration=25,
        color=RED,
    ) -> None:
        super().__init__()

        self.beam_grp = beam_grp
        self.player_rect = player_rect

        self.thickness = thickness
        self.shoot_cd = shoot_cd
        self.damage = damage
        self.duration = duration
        self.color = color

    @override
    def shoot(self, tar_x, tar_y):
        if self._on_cooldown():
            return

        self.beam_grp.add(
            Laser(
                self.player_rect.centerx,
                self.player_rect.centery,
                tar_x,
                tar_y,
                self.thickness,
                self.color,
                self.damage,
                self.duration,
            )
        )
