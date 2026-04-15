import math
import random

import pygame

from const.COLORS import GREEN, WHITE
from src.Entities import CircEntity, TriEntity
from src.Weapons import Pistol


class Chaser(CircEntity):
    def __init__(
        self, x_cor, y_cor, color, radius=20, health=100, damage=10, speed=2
    ) -> None:
        super().__init__(radius, x_cor, y_cor, color)

        self.speed = speed
        self.dx, self.dy = 0, 0
        self.health = self.max_health = health
        self.damage = damage
        self.friction = random.uniform(0.94, 0.99)
        self.accel = random.uniform(0.50, 0.90)

    def update(self, tar_x, tar_y):
        self._movement(tar_x, tar_y)

    def _movement(self, tar_x, tar_y):
        angle = math.atan2(tar_y - self.rect.centery, tar_x - self.rect.centerx)

        self.dx += math.cos(angle) * self.accel
        self.dy += math.sin(angle) * self.accel
        self.dx *= self.friction
        self.dy *= self.friction

        self.rect.x += int(self.dx)
        self.rect.y += int(self.dy)

    def take_dmg(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()

    def draw_health_bar(self, screen):
        bar_wd = 80
        bar_ht = 20

        bar_x = self.rect.centerx - (bar_wd // 2)
        bar_y = self.rect.top - (bar_ht * 2)

        fill_wd = int(self.health / self.max_health * bar_wd)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, fill_wd, bar_ht))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_wd, bar_ht), 1)


class Bouncer(CircEntity):
    def __init__(
        self,
        x_cor,
        y_cor,
        color,
        radius=10,
        health=10,
        damage=10,
        max_bounces=5,
        speed=3,
    ) -> None:
        super().__init__(radius, x_cor, y_cor, color)

        self.health = self.max_health = health
        self.dx = speed * random.choice([-3, -2, -1, 1, 2, 3])
        self.dy = speed * random.choice([-3, -2, -1, 1, 2, 3])
        self.damage = damage

        self.max_bounces = max_bounces
        self.current_bounce_count = 0

    def update(self, borders):
        if self.current_bounce_count >= self.max_bounces:
            self.kill()

        self._collision(borders)

    def _collision(self, borders):
        x_bounced, y_bounced = False, False

        self.rect.x += int(self.dx)
        for border in borders:
            if self.rect.colliderect(border.rect):
                self.rect.x -= int(self.dx)
                self.dx *= -1
                x_bounced = True
                break

        self.rect.y += int(self.dy)
        for border in borders:
            if self.rect.colliderect(border.rect):
                self.rect.y -= int(self.dy)
                self.dy *= -1
                y_bounced = True
                break

        if x_bounced:
            self.current_bounce_count += 1
        if y_bounced:
            self.current_bounce_count += 1

    def take_dmg(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()

    def draw_health_bar(self, screen):
        bar_wd = 80
        bar_ht = 20

        bar_x = self.rect.centerx - (bar_wd // 2)
        bar_y = self.rect.top - (bar_ht * 2)

        fill_wd = int(self.health / self.max_health * bar_wd)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, fill_wd, bar_ht))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_wd, bar_ht), 1)


class Tank(CircEntity):
    def __init__(
        self, x_cor, y_cor, color, radius=50, health=1000, damage=10, speed=1
    ) -> None:
        super().__init__(radius, x_cor, y_cor, color)

        self.speed = speed
        self.dx, self.dy = 0, 0
        self.health = self.max_health = health
        self.damage = damage
        self.friction = 0.92
        self.accel = 0.3

    def update(self, tar_x, tar_y):
        self._movement(tar_x, tar_y)

    def _movement(self, tar_x, tar_y):
        angle = math.atan2(tar_y - self.rect.centery, tar_x - self.rect.centerx)

        self.dx += math.cos(angle) * self.accel
        self.dy += math.sin(angle) * self.accel
        self.dx *= self.friction
        self.dy *= self.friction

        self.rect.x += int(self.dx)
        self.rect.y += int(self.dy)

    def take_dmg(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()

    def draw_health_bar(self, screen):
        bar_wd = 80
        bar_ht = 20

        bar_x = self.rect.centerx - (bar_wd // 2)
        bar_y = self.rect.top - (bar_ht * 2)

        fill_wd = int(self.health / self.max_health * bar_wd)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, fill_wd, bar_ht))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_wd, bar_ht), 1)


class Sniper(TriEntity):
    def __init__(
        self,
        x_cor,
        y_cor,
        color,
        size=20,
        health=25,
        damage=25,
        fuse_duration=2000,
        speed=50,
    ) -> None:
        super().__init__(size, x_cor, y_cor, color)

        self.speed = speed
        self.dx, self.dy = 0, 0
        self.health = self.max_health = health
        self.damage = damage

        self.fuse_duration = fuse_duration
        self.spawn_time = pygame.time.get_ticks()
        self.is_fused = True

        # Store original image for rotation
        self.original_image = self.image
        self.angle = 0

    def update(self, tar_x, tar_y, borders):
        now = pygame.time.get_ticks()
        if self.is_fused:
            self.angle = math.degrees(
                math.atan2(tar_y - self.rect.centery, tar_x - self.rect.centerx)
            )
            self.angle = -self.angle - 90
            self.image = pygame.transform.rotate(self.original_image, self.angle)
            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center

            if now - self.spawn_time > self.fuse_duration:
                self.is_fused = False
                rad = math.radians(-self.angle - 90)
                self.dx = math.cos(rad) * self.speed
                self.dy = math.sin(rad) * self.speed
            else:
                self._collision(borders)
                return

        self.rect.x += int(self.dx)
        self.rect.y += int(self.dy)
        self._collision(borders)

    def take_dmg(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()

    def _collision(self, borders):
        for border in borders:
            if self.rect.colliderect(border.rect):
                self.kill()

    def draw_health_bar(self, screen):
        bar_wd = 80
        bar_ht = 20

        bar_x = self.rect.centerx - (bar_wd // 2)
        bar_y = self.rect.top - (bar_ht * 2)

        fill_wd = int(self.health / self.max_health * bar_wd)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, fill_wd, bar_ht))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_wd, bar_ht), 1)


class Shooter(CircEntity):
    def __init__(
        self,
        x_cor,
        y_cor,
        color,
        projectile_grp,
        radius=20,
        health=150,
        damage=10,
    ) -> None:
        super().__init__(radius, x_cor, y_cor, color)

        self.health = self.max_health = 150
        self.projectile_grp = projectile_grp
        self.pistol = Pistol(
            self.projectile_grp,
            self.rect,
            500,
            50,
            self.color,
        )
        self.damage = 10

    def update(self, tar_x, tar_y):
        self.pistol.shoot(tar_x, tar_y)

    def take_dmg(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()

    def draw(self, screen):
        super().draw(screen)

    def draw_health_bar(self, screen):
        bar_wd = 80
        bar_ht = 20

        bar_x = self.rect.centerx - (bar_wd // 2)
        bar_y = self.rect.top - (bar_ht * 2)

        fill_wd = int(self.health / self.max_health * bar_wd)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, fill_wd, bar_ht))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_wd, bar_ht), 1)
