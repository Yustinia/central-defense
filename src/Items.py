from const.COLORS import GREEN
from src.Entities import CrossEntity


class HealthPack(CrossEntity):
    def __init__(self, x_cor, y_cor, color=GREEN, size=60) -> None:
        super().__init__(size, x_cor, y_cor, color)

        self.heal_amt = 300

    def heal(self, player):
        player.health = min(player.health + self.heal_amt, player.max_health)
