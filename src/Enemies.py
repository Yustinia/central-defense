import math
import random

import pygame

from const.COLORS import GREEN, WHITE
from src.Entities import CircEntity, TriEntity


class Chaser(CircEntity):
    def __init__(self, radius, x_cor, y_cor, color, speed=2) -> None:
        super().__init__(radius, x_cor, y_cor, color)

        self.speed = speed
        self.dx, self.dy = 0, 0
        self.health = self.max_health = 100
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
    def __init__(self, radius, x_cor, y_cor, color, speed=3) -> None:
        super().__init__(radius, x_cor, y_cor, color)

        self.health = self.max_health = 10
        self.dx = speed * random.choice([-3, -2, -1, 1, 2, 3])
        self.dy = speed * random.choice([-3, -2, -1, 1, 2, 3])

    def update(self, borders):
        self._collision(borders)

    def _collision(self, borders):
        self.rect.x += int(self.dx)
        for border in borders:
            if self.rect.colliderect(border.rect):
                self.rect.x -= int(self.dx)
                self.dx *= -1

        self.rect.y += int(self.dy)
        for border in borders:
            if self.rect.colliderect(border.rect):
                self.rect.y -= int(self.dy)
                self.dy *= -1

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
    def __init__(self, radius, x_cor, y_cor, color, speed=1) -> None:
        super().__init__(radius, x_cor, y_cor, color)

        self.speed = speed
        self.dx, self.dy = 0, 0
        self.health = self.max_health = 1000
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
    def __init__(self, size, x_cor, y_cor, color, speed=50) -> None:
        super().__init__(size, x_cor, y_cor, color)

        self.speed = speed
        self.dx, self.dy = 0, 0
        self.health = self.max_health = 100

        self.fuse_duration = 2000
        self.spawn_time = pygame.time.get_ticks()
        self.is_fused = True

    def update(self, tar_x, tar_y, borders):
        now = pygame.time.get_ticks()
        if self.is_fused:
            if now - self.spawn_time > self.fuse_duration:
                self.is_fused = False

                angle = math.atan2(tar_y - self.rect.centery, tar_x - self.rect.centerx)
                self.dx = math.cos(angle) * self.speed
                self.dy = math.sin(angle) * self.speed
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
