import random
from abc import ABC, abstractmethod

import pygame

from const.COLORS import GREEN
from src.Items import HealthPack


class BaseItemSpawner(ABC):
    def __init__(self, spawn_cd, group_type) -> None:
        self.spawn_cd = spawn_cd
        self.spawn_timer = 0
        self.group = (
            pygame.sprite.Group()
            if group_type == "group"
            else pygame.sprite.GroupSingle()
        )

    @abstractmethod
    def try_spawn(self, win_wd, win_ht): ...

    def timer(self):
        now = pygame.time.get_ticks()
        if now - self.spawn_timer < self.spawn_cd:
            return False
        self.spawn_timer = now
        return True


class HealthPackSpawner(BaseItemSpawner):
    def __init__(self) -> None:
        super().__init__(spawn_cd=25000, group_type="single")

    def try_spawn(self, win_wd, win_ht):
        if not self.timer():
            return

        rand_hp_x = random.randint(40, win_wd - 40)
        rand_hp_y = random.randint(120, win_ht - 40)
        self.group.add(HealthPack(60, rand_hp_x, rand_hp_y, GREEN))
