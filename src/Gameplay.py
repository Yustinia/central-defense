from abc import ABC, abstractmethod

import pygame


class Background:
    def __init__(self, win_wd, win_ht, color) -> None:
        self.win_wd = win_wd
        self.win_ht = win_ht
        self.color = color

        self.image = pygame.Surface((self.win_wd, self.win_ht))
        self.image.fill(self.color)
        self.rect = self.image.get_rect(topleft=(0, 0))

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Border(pygame.sprite.Sprite):
    def __init__(self, bor_wd, bor_ht, x_cor, y_cor, color) -> None:
        super().__init__()

        self.bor_wd = bor_wd
        self.bor_ht = bor_ht
        self.x_cor = x_cor
        self.y_cor = y_cor
        self.color = color

        self.image = pygame.Surface((self.bor_wd, self.bor_ht))
        self.image.fill(self.color)
        self.rect = self.image.get_rect(topleft=(self.x_cor, self.y_cor))

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class BoxEntity(ABC, pygame.sprite.Sprite):
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

    def update(self, keys, borders):
        self._movement(keys)
        self._collision(borders)

    @abstractmethod
    def _movement(self, keys):
        pass

    def _collision(self, borders):
        pass


class CircEntity(ABC, pygame.sprite.Sprite):
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

    def update(self, keys, borders):
        self._movement(keys)
        self._collision(borders)

    @abstractmethod
    def _movement(self, keys):
        pass

    def _collision(self, borders):
        pass
