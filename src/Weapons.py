import math

import pygame


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
