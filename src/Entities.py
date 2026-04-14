import pygame
from pygame.sprite import _Group


class BoxEntity(pygame.sprite.Sprite):
    def __init__(self, ent_wd, ent_ht, x_cor, y_cor, color) -> None:
        super().__init__()

        self.ent_wd = ent_wd
        self.ent_ht = ent_ht
        self.x_cor = x_cor
        self.y_cor = y_cor
        self.color = color

        self.image = pygame.Surface((self.ent_wd, self.ent_ht))
        self.image.fill(self.color)
        self.rect = self.image.get_rect(center=(self.x_cor, self.y_cor))

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class CircEntity(pygame.sprite.Sprite):
    def __init__(self, radius, x_cor, y_cor, color) -> None:
        super().__init__()

        self.radius = radius
        self.x_cor = x_cor
        self.y_cor = y_cor
        self.color = color

        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            self.image, self.color, (self.radius, self.radius), self.radius
        )
        self.rect = self.image.get_rect(center=(self.x_cor, self.y_cor))

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class CrossEntity(pygame.sprite.Sprite):
    def __init__(self, size, x_cor, y_cor, color) -> None:
        super().__init__()

        self.size = size
        self.x_cor = x_cor
        self.y_cor = y_cor
        self.color = color

        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)

        third = self.size // 3
        # horizontal bar
        pygame.draw.rect(self.image, self.color, (0, third, self.size, third))
        # vertical bar
        pygame.draw.rect(self.image, self.color, (third, 0, third, self.size))

        self.rect = self.image.get_rect(center=(self.x_cor, self.y_cor))

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class TriEntity(pygame.sprite.Sprite):
    def __init__(self, size, x_cor, y_cor, color) -> None:
        super().__init__()

        self.size = size
        self.x_cor = x_cor
        self.y_cor = y_cor
        self.color = color

        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        tri_pts = [
            (self.size // 2, 0),  # top center
            (0, self.size),  # bot left
            (self.size, self.size),  # bot right
        ]
        pygame.draw.polygon(self.image, self.color, tri_pts)
        self.rect = self.image.get_rect(center=(self.x_cor, self.y_cor))

    def draw(self, screen):
        screen.blit(self.image, self.rect)
