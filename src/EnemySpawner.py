import random
from abc import ABC, abstractmethod

import pygame

from const.COLORS import ORANGE, VIOLET, YELLOW
from src.Enemies import Bouncer, Chaser, Tank, Sniper


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
    def next_round(self, round_counter): ...


class ChaserSpawner(BaseEnemySpawner):
    def __init__(self) -> None:
        super().__init__(hard_lim=20, to_spawn=2, to_spawn_init=2, spawn_cd=3700)

    def try_spawn(self, win_wd, win_ht):
        if self.spawned >= self.to_spawn:
            return

        now = pygame.time.get_ticks()
        if now - self.spawn_timer < self.spawn_cd:
            return
        self.spawn_timer = now

        side = random.choice(["left", "right", "top", "bottom"])
        if side == "left":
            x, y = -20, random.randint(-20, win_ht + 20)
        elif side == "right":
            x, y = win_wd + 20, random.randint(-20, win_ht + 20)
        elif side == "top":
            x, y = random.randint(-20, win_wd + 20), -20
        else:
            x, y = random.randint(-20, win_wd + 20), win_ht + 20

        self.group.add(Chaser(20, x, y, ORANGE))
        self.spawned += 1

    def next_round(self, round_counter):
        self.to_spawn = min(self.to_spawn_init + round_counter, self.hard_lim)
        self.spawn_cd = max(self.spawn_cd - 400, self.spawn_cd_init // 5)

        self.reset()


class BouncerSpawner(BaseEnemySpawner):
    def __init__(self) -> None:
        super().__init__(hard_lim=7, to_spawn=0, to_spawn_init=-2, spawn_cd=5600)

    def try_spawn(self, win_wd, win_ht):
        if self.spawned >= self.to_spawn:
            return

        now = pygame.time.get_ticks()
        if now - self.spawn_timer < self.spawn_cd:
            return
        self.spawn_timer = now

        for i in range(3):
            side = random.choice(["left", "right", "top", "bottom"])

            if side == "left":
                x, y = 40, random.randint(120, win_ht - 40)
            elif side == "right":
                x, y = win_wd - 40, random.randint(120, win_ht - 40)
            elif side == "top":
                x, y = random.randint(40, win_wd - 40), 120
            else:
                x, y = random.randint(40, win_wd - 40), win_ht - 40

            self.group.add(Bouncer(10, x, y, VIOLET))

        self.spawned += 1

    def next_round(self, round_counter):
        if round_counter >= 3:
            self.to_spawn = min(
                self.to_spawn_init + round_counter,
                self.hard_lim,
            )
            self.spawn_cd = max(self.spawn_cd - 700, self.spawn_cd_init // 3)
        else:
            self.to_spawn = 0

        self.reset()


class TankSpawner(BaseEnemySpawner):
    def __init__(self) -> None:
        super().__init__(hard_lim=5, to_spawn=0, to_spawn_init=0, spawn_cd=5000)

        self.every_round = 5

    def try_spawn(self, win_wd, win_ht):
        if self.spawned >= self.to_spawn:
            return

        now = pygame.time.get_ticks()
        if now - self.spawn_timer < self.spawn_cd:
            return
        self.spawn_timer = now

        side = random.choice(["left", "right", "top", "bottom"])
        if side == "left":
            x, y = -20, random.randint(-20, win_ht + 20)
        elif side == "right":
            x, y = win_wd + 20, random.randint(-20, win_ht + 20)
        elif side == "top":
            x, y = random.randint(-20, win_wd + 20), -20
        else:
            x, y = random.randint(-20, win_wd + 20), win_ht + 20

        self.group.add(Tank(50, x, y, VIOLET))
        self.spawned += 1

    def next_round(self, round_counter):
        if round_counter % self.every_round == 0:
            self.to_spawn = min(
                self.to_spawn_init + (round_counter // 5),
                self.hard_lim,
            )
        else:
            self.to_spawn = 0

        self.reset()


class SniperSpawner(BaseEnemySpawner):
    def __init__(self) -> None:
        super().__init__(hard_lim=8, to_spawn=0, to_spawn_init=-8, spawn_cd=4750)

        self.pref_round = 10

    def try_spawn(self, win_wd, win_ht):
        if self.spawned >= self.to_spawn:
            return

        now = pygame.time.get_ticks()
        if now - self.spawn_timer < self.spawn_cd:
            return
        self.spawn_timer = now

        side = random.choice(["left", "right", "top", "bottom"])

        if side == "left":
            x, y = 40, random.randint(120, win_ht - 40)
        elif side == "right":
            x, y = win_wd - 40, random.randint(120, win_ht - 40)
        elif side == "top":
            x, y = random.randint(40, win_wd - 40), 120
        else:
            x, y = random.randint(40, win_wd - 40), win_ht - 40

        self.group.add(Sniper(20, x, y, YELLOW))
        self.spawned += 1

    def next_round(self, round_counter):
        if round_counter >= self.pref_round:
            self.to_spawn = min(self.to_spawn_init + round_counter, self.hard_lim)
            self.spawn_cd = max(self.spawn_cd - 200, self.spawn_cd_init // 2)
        else:
            self.to_spawn = 0

        self.reset()
