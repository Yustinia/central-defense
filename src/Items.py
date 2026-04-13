from src.Entities import BoxEntity


class HealthPack(BoxEntity):
    def __init__(self, ent_wd, ent_ht, x_cor, y_cor, color) -> None:
        super().__init__(ent_wd, ent_ht, x_cor, y_cor, color)

        self.heal_amt = 50

    def heal(self, player):
        player.health += self.heal_amt
