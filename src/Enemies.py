import math
import random

from typing_extensions import override

from src.Entities import CircEntity


class Chaser(CircEntity):
    def __init__(self, radius, x_cor, y_cor, color, speed=2) -> None:
        super().__init__(radius, x_cor, y_cor, color)

        self.speed = speed
        self.dx, self.dy = 0, 0
        self.health = 100
        self.friction = random.uniform(0.94, 0.99)
        self.accel = random.uniform(0.50, 0.90)

    @override
    def update(self, tar_x, tar_y):
        self._movement(tar_x, tar_y)

    @override
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


class Bouncer(CircEntity):
    def __init__(self, radius, x_cor, y_cor, color, speed=3) -> None:
        super().__init__(radius, x_cor, y_cor, color)

        self.health = 10
        self.dx = speed * random.choice([-1, 1])
        self.dy = speed * random.choice([-1, 1])

    @override
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
