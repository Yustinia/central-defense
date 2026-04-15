import pygame

from src.Entities import CrossEntity


class HealthPack(CrossEntity):
    def __init__(self, size, x_cor, y_cor, color) -> None:
        super().__init__(size, x_cor, y_cor, color)

        self.heal_amt = 200

    def heal(self, player):
        player.health += self.heal_amt
