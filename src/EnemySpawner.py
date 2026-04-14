import pygame

from abc import ABC, abstractmethod


class BaseEnemySpawner(ABC):
    def __init__(self, hard_lim, to_spawn, to_spawn_init, spawn_cd) -> None:
        self.hard_lim = hard_lim
        self.to_spawn, self.to_spawn_init = to_spawn, to_spawn_init
        self.spawned = 0
        self.spawn_cd, self.spawn_cd_init = spawn_cd, spawn_cd
        self.spawn_timer = 0
        self.group = pygame.sprite.Group()

    @property
    def all_spawned(self) -> bool:
        return self.spawned >= self.to_spawn

    @property
    def all_dead(self) -> bool:
        return len(self.group) == 0

    def reset(self):
        self.spawned = 0

    @abstractmethod
    def try_spawn(self, win_wd, win_ht): ...

    @abstractmethod
    def next_round(self): ...
