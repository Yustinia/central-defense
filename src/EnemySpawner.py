import random
from abc import ABC, abstractmethod

import pygame

from src.Enemies import Bouncer, Chaser, Exploder, Shooter, Sniper, Tank


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
    def try_spawn(self, win_wd, win_ht, round_counter): ...

    @abstractmethod
    def next_round(self, round_counter): ...


class ChaserSpawner(BaseEnemySpawner):
    def __init__(self) -> None:
        super().__init__(hard_lim=14, to_spawn=2, to_spawn_init=2, spawn_cd=3700)

        self.down_round = 10

    def try_spawn(self, win_wd, win_ht, round_counter):
        if round_counter >= self.down_round:
            return

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

        self.group.add(Chaser(x, y))
        self.spawned += 1

    def next_round(self, round_counter):
        self.reset()

        if round_counter >= self.down_round:
            self.to_spawn = 0
        else:
            self.to_spawn = min(self.to_spawn_init + round_counter, self.hard_lim)
            self.spawn_cd = max(self.spawn_cd - 400, self.spawn_cd_init // 5)


class BouncerSpawner(BaseEnemySpawner):
    def __init__(self) -> None:
        super().__init__(hard_lim=4, to_spawn=0, to_spawn_init=-2, spawn_cd=5600)

        self.pref_round = 3
        self.down_round = 14

    def try_spawn(self, win_wd, win_ht, round_counter):
        if round_counter < self.pref_round:
            return
        if round_counter >= self.down_round:
            return

        if self.spawned >= self.to_spawn:
            return

        now = pygame.time.get_ticks()
        if now - self.spawn_timer < self.spawn_cd:
            return
        self.spawn_timer = now

        for i in range(3):
            side = random.choice(["left", "right", "top", "bottom"])

            if side == "left":
                x, y = 40, random.randint(40, win_ht - 40)
            elif side == "right":
                x, y = win_wd - 40, random.randint(40, win_ht - 40)
            elif side == "top":
                x, y = random.randint(40, win_wd - 40), 40
            else:
                x, y = random.randint(40, win_wd - 40), win_ht - 40

            self.group.add(Bouncer(x, y))

        self.spawned += 1

    def next_round(self, round_counter):
        self.reset()

        if round_counter >= self.down_round:
            self.to_spawn = 0
        elif round_counter >= self.pref_round:
            self.to_spawn = min(
                self.to_spawn_init + round_counter,
                self.hard_lim,
            )
            self.spawn_cd = max(self.spawn_cd - 700, self.spawn_cd_init // 3)
        else:
            self.to_spawn = 0


class TankSpawner(BaseEnemySpawner):
    def __init__(self) -> None:
        super().__init__(hard_lim=5, to_spawn=0, to_spawn_init=1, spawn_cd=5000)

        self.every_round = 4
        self.down_round = 20

    def try_spawn(self, win_wd, win_ht, round_counter):
        if round_counter % self.every_round != 0:
            return
        if round_counter >= self.down_round:
            return

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

        self.group.add(Tank(x, y))
        self.spawned += 1

    def next_round(self, round_counter):
        self.reset()

        if round_counter >= self.down_round:
            self.to_spawn = 0
        elif round_counter % self.every_round == 0:
            self.to_spawn = min(
                self.to_spawn_init + (round_counter // 6),
                self.hard_lim,
            )
        else:
            self.to_spawn = 0


class SniperSpawner(BaseEnemySpawner):
    def __init__(self) -> None:
        super().__init__(hard_lim=30, to_spawn=0, to_spawn_init=-5, spawn_cd=4750)

        self.pref_round = 7
        self.up_round = 12
        self.down_round = 20

    def try_spawn(self, win_wd, win_ht, round_counter):
        if round_counter < self.pref_round:
            return
        if round_counter >= self.down_round:
            return

        if self.spawned >= self.to_spawn:
            return

        now = pygame.time.get_ticks()
        if now - self.spawn_timer < self.spawn_cd:
            return
        self.spawn_timer = now

        side = random.choice(["left", "right", "top", "bottom"])

        if side == "left":
            x, y = 60, random.randint(60, win_ht - 60)
        elif side == "right":
            x, y = win_wd - 60, random.randint(60, win_ht - 60)
        elif side == "top":
            x, y = random.randint(60, win_wd - 60), 60
        else:
            x, y = random.randint(60, win_wd - 60), win_ht - 60

        self.group.add(Sniper(x, y))
        self.spawned += 1

    def next_round(self, round_counter):
        self.reset()

        if round_counter >= self.down_round:
            self.to_spawn = 0
        elif round_counter >= self.up_round:
            self.to_spawn = min(self.to_spawn_init + round_counter, self.hard_lim)
            self.spawn_cd = max(self.spawn_cd - 800, self.spawn_cd_init // 12)
        elif round_counter >= self.pref_round:
            self.to_spawn = min(self.to_spawn_init + round_counter, self.hard_lim)
            self.spawn_cd = max(self.spawn_cd - 400, self.spawn_cd_init // 2)
        else:
            self.to_spawn = 0


class ShooterSpawner(BaseEnemySpawner):
    def __init__(self, projectile_grp) -> None:
        super().__init__(hard_lim=4, to_spawn=0, to_spawn_init=-9, spawn_cd=4990)

        self.projectile_grp = projectile_grp
        self.pref_round = 10
        self.up_round = 15
        self.down_round = 20

    def try_spawn(self, win_wd, win_ht, round_counter):
        if round_counter < self.pref_round:
            return
        if round_counter >= self.down_round:
            return

        if self.spawned >= self.to_spawn:
            return

        now = pygame.time.get_ticks()
        if now - self.spawn_timer < self.spawn_cd:
            return
        self.spawn_timer = now

        rand_x = random.randint(40, win_wd - 40)
        rand_y = random.randint(40, win_ht - 40)

        self.group.add(Shooter(rand_x, rand_y, self.projectile_grp))
        self.spawned += 1

    def next_round(self, round_counter):
        self.reset()

        if round_counter >= self.down_round:
            self.to_spawn = 0
        elif round_counter >= self.up_round:
            self.to_spawn = min(self.to_spawn_init + round_counter, self.hard_lim)
            self.spawn_cd = max(self.spawn_cd - 400, self.spawn_cd_init)
        elif round_counter >= self.pref_round:
            self.to_spawn = min(self.to_spawn_init + round_counter, self.hard_lim)
        else:
            self.to_spawn = 0


class ExploderSpawner(BaseEnemySpawner):
    def __init__(self, projectile_grp) -> None:
        super().__init__(hard_lim=8, to_spawn=0, to_spawn_init=-11, spawn_cd=3120)

        self.projectile_grp = projectile_grp
        self.pref_round = 13
        self.up_round = 17
        self.down_round = 20

    def try_spawn(self, win_wd, win_ht, round_counter):
        if round_counter < self.pref_round:
            return
        if round_counter >= self.down_round:
            return

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

        self.group.add(Exploder(x, y, self.projectile_grp))
        self.spawned += 1

    def next_round(self, round_counter):
        self.reset()

        if round_counter >= self.down_round:
            self.to_spawn = 0
        elif round_counter >= self.up_round:
            self.to_spawn = min(self.to_spawn_init + round_counter, self.hard_lim)
            self.spawn_cd = max(self.spawn_cd - 500, self.spawn_cd_init // 8)
        elif round_counter >= self.pref_round:
            self.to_spawn = min(self.to_spawn_init + round_counter, self.hard_lim)
            self.spawn_cd = max(self.spawn_cd - 200, self.spawn_cd_init // 4)
        else:
            self.to_spawn = 0
