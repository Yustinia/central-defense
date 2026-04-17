from abc import ABC, abstractmethod

import pygame

from src.Bosses import MilkyWay, Venus


class BaseBossSpawner(ABC):
    def __init__(self, hard_lim, to_spawn, to_spawn_init) -> None:
        self.hard_lim = hard_lim
        self.to_spawn, self.to_spawn_init = to_spawn, to_spawn_init
        self.spawned = 0
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
    def next_round(self, round_counter): ...


class VenusSpawner(BaseBossSpawner):
    def __init__(self, projectile_grp, sniper_grp) -> None:
        super().__init__(hard_lim=1, to_spawn=0, to_spawn_init=1)

        self.projectile_grp = projectile_grp
        self.sniper_grp = sniper_grp
        self.every_round = 25

    def try_spawn(self, win_wd, win_ht):
        if self.spawned >= self.to_spawn:
            return

        center_x, center_y = win_wd // 2, win_ht // 2
        self.group.add(
            Venus(
                center_x,
                center_y,
                self.projectile_grp,
                self.sniper_grp,
            )
        )

        self.spawned += 1

    def next_round(self, round_counter):
        self.reset()

        if round_counter > 0 and round_counter % self.every_round == 0:
            self.to_spawn = self.to_spawn_init
        else:
            self.to_spawn = 0


class MilkyWaySpawner(BaseBossSpawner):
    def __init__(self, projectile_grp, exploder_grp) -> None:
        super().__init__(hard_lim=1, to_spawn=1, to_spawn_init=1)

        self.projectile_grp = projectile_grp
        self.exploder_grp = exploder_grp
        self.every_round = 20

    def try_spawn(self, win_wd, win_ht):
        if self.spawned >= self.to_spawn:
            return

        center_x, center_y = win_wd // 2, win_ht // 2
        self.group.add(
            MilkyWay(
                center_x,
                center_y,
                self.projectile_grp,
                self.exploder_grp,
            )
        )

        self.spawned += 1

    def next_round(self, round_counter):
        self.reset()

        if round_counter > 0 and round_counter % self.every_round == 0:
            self.to_spawn = self.to_spawn_init
        else:
            self.to_spawn = 0
