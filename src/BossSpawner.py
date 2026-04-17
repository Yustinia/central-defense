from abc import ABC, abstractmethod

import pygame

from src.Bosses import Venus


class BaseBossSpawner(ABC):
    def __init__(self) -> None:
        self.group = pygame.sprite.Group()
        self.spawned = 0

    @property
    def all_spawned(self):
        return True

    @property
    def all_dead(self) -> bool:
        return len(self.group) == 0

    def reset(self):
        self.spawned = 0

    @abstractmethod
    def try_spawn(self, win_wd, win_ht, round_counter): ...


class VenusSpawner(BaseBossSpawner):
    def __init__(self, projectile_grp) -> None:
        super().__init__()

        self.projectile_grp = projectile_grp
        self.pref_round = 1

    def try_spawn(self, win_wd, win_ht, round_counter):
        if round_counter < self.pref_round:
            return

        if self.spawned:
            return

        center_x, center_y = win_wd // 2, win_ht // 2
        self.group.add(
            Venus(
                center_x,
                center_y,
                self.projectile_grp,
            )
        )

        self.spawned += 1
