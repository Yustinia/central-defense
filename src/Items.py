import pygame

from const.COLORS import GREEN
from sounds.effects.SOUNDS import HEAL
from src.Entities import CrossEntity


class HealthPack(CrossEntity):
    def __init__(self, x_cor, y_cor, color=GREEN, size=60) -> None:
        super().__init__(size, x_cor, y_cor, color)

        self.heal_amt = 300

        self.heal_sfx = pygame.mixer.Sound(HEAL)
        self.heal_sfx.set_volume(0.2)

    def heal(self, player):
        player.health = min(player.health + self.heal_amt, player.max_health)
        self.heal_sfx.play()
