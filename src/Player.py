import pygame
from typing_extensions import override

from const.COLORS import BLUE, GREEN, RED, WHITE, YELLOW
from const.FONTS import REGULAR
from src.Abilities import BulletBurst, Dash, PassiveHeal, Shield
from src.Entities import BoxEntity
from src.Weapons import LaserGun, MachineGun, Pistol, Shotgun


class Player(BoxEntity):
    def __init__(
        self,
        x_cor,
        y_cor,
        projectile_grp,
        beam_grp,
        speed=1,
        win_wd: int = 40,
        win_ht: int = 40,
        color=BLUE,
    ) -> None:
        super().__init__(win_wd, win_ht, x_cor, y_cor, color)

        self.health = self.max_health = 500
        self.speed = speed
        self.dx, self.dy = 0, 0
        self.friction = 0.85

        self.min_health = 250
        self.dmg_cd = 125
        self.dmg_timer = 0

        self.projectile_grp = projectile_grp
        self.beam_grp = beam_grp

        # Weapons
        self.pistol = Pistol(
            self.projectile_grp,
            self.rect,
        )
        self.shotgun = Shotgun(
            self.projectile_grp,
            self.rect,
        )
        self.machinegun = MachineGun(
            self.projectile_grp,
            self.rect,
        )
        self.lasergun = LaserGun(self.beam_grp, self.rect)

        # Abilities
        self.dash_ab = Dash()
        self.passive_heal_ab = PassiveHeal()
        self.shield_ab = Shield()
        self.bullet_burst_ab = BulletBurst()

        # States
        self.is_alive = True

    @override
    def update(self, keys, borders):
        self.shield_ab.update()
        self._update_visual()
        self._passive_heal()

        self._movement(keys)
        self._collision(borders)

    def _update_visual(self):
        if self.shield_ab.is_active:
            self.image.fill(YELLOW)
        else:
            self.image.fill(BLUE)

    def _passive_heal(self):
        if self.passive_heal_ab.is_ready():
            self.health = min(
                self.health + self.passive_heal_ab.heal_amt, self.max_health
            )

    def take_damage(self, amount):
        now = pygame.time.get_ticks()
        if now - self.dmg_timer < self.dmg_cd:
            return self.is_alive
        self.dmg_timer = now

        if self.shield_ab.is_active:
            self.shield_ab.durability -= amount
            if self.shield_ab.durability <= 0:
                self.shield_ab.is_active = False
            return self.is_alive

        self.health -= amount

        if self.health <= 10 or self.health <= 0:
            self.is_alive = False

        return self.is_alive

    def _movement(self, keys):
        if keys[pygame.K_a]:
            self.dx -= self.speed
        if keys[pygame.K_d]:
            self.dx += self.speed
        if keys[pygame.K_w]:
            self.dy -= self.speed
        if keys[pygame.K_s]:
            self.dy += self.speed

        if keys[pygame.K_SPACE]:
            self.dx, self.dy = self.dash_ab.do_dash(self.dx, self.dy)

        if keys[pygame.K_q]:
            self.shield_ab.activate()

        if keys[pygame.K_e]:
            if self.bullet_burst_ab.is_ready():
                self.bullet_burst_ab.burst(
                    self.projectile_grp,
                    self.rect.centerx,
                    self.rect.centery,
                )

    def _collision(self, borders):
        self.rect.x += int(self.dx)
        for border in borders:
            if self.rect.colliderect(border.rect):
                self.rect.x -= int(self.dx)
                self.dx = 0

        self.rect.y += int(self.dy)
        for border in borders:
            if self.rect.colliderect(border.rect):
                self.rect.y -= int(self.dy)
                self.dy = 0

        self.dx *= self.friction
        self.dy *= self.friction
