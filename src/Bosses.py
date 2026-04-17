import math
import random

import pygame

from const.COLORS import BLACK, BLUE, GREEN, ORANGE, PLAT, RED, VIOLET, WHITE, YELLOW
from src.Enemies import Sniper
from src.Entities import StarEntity
from src.Weapons import Bullet, Pistol


class Venus(StarEntity):
    PHASE_THRESHOLDS = {
        4: 0.15,
        3: 0.40,
        2: 0.75,
        1: 1.00,
    }

    def __init__(
        self,
        x_cor,
        y_cor,
        projectile_grp,
        sniper_grp,
        size=120,
        color=RED,
        num_points=5,
        depth_ratio=0.4,
        health=15000,
        damage=25,
    ) -> None:
        super().__init__(size, x_cor, y_cor, color, num_points, depth_ratio)

        self.projectile_grp = projectile_grp
        self.sniper_grp = sniper_grp

        self.health = self.max_health = health
        self.damage = damage
        self.phase = 1  # [1, 2, 3]

        self.dx, self.dy = 0, 0
        self.movement_params = {
            1: {
                "friction": 0.92,
                "accel": 0.50,
            },
            2: {
                "friction": 0.92,
                "accel": 0.30,
            },
            3: {
                "friction": 0.94,
                "accel": 0.88,
            },
            4: {
                "friction": 0.94,
                "accel": 0.90,
            },
        }
        # atk timers
        self.burst_atk_cd = 3000
        self.burst_atk_timer = 0

        self.varied_burst_atk_cd = 800
        self.varied_burst_atk_timer = 0

        self.spawn_enemy_params = {
            3: {"spawn_enemy_cd": 1200},
            4: {"spawn_enemy_cd": 750},
        }
        self.spawn_enemy_timer = 0

        # movement timers
        self.wander_target_x = self.rect.centerx
        self.wander_target_y = self.rect.centery
        self.wander_cd = 2000
        self.wander_timer = 0

        # weapons
        pistol_rad = 10
        pistol_shoot_cd = 250
        pistol_bullet_spd = 20
        self.pistol = Pistol(
            self.projectile_grp,
            self.rect,
            pistol_rad,
            pistol_shoot_cd,
            self.damage,
            self.color,
            pistol_bullet_spd,
        )

    # ==================
    # CORE
    # ==================

    def update(self, tar_x, tar_y, borders):
        self._update_phase()

        self._movement(tar_x, tar_y, borders)
        self._attack(tar_x, tar_y)

    def _update_phase(self):
        health_pct = self.health / self.max_health
        for phase, threshold in self.PHASE_THRESHOLDS.items():
            if health_pct <= threshold:
                self.phase = phase
                break

    def take_dmg(self, amount):
        self.health -= amount
        if self.health <= 0:
            self._explode()

    # ==================
    # MOVEMENT ROUTING
    # ==================

    def _movement(self, tar_x, tar_y, borders):
        match self.phase:
            case 1:
                params = self.movement_params[self.phase]
                self._chase(
                    tar_x,
                    tar_y,
                    params["friction"],
                    params["accel"],
                )
            case 2:
                params = self.movement_params[self.phase]
                self._wander(
                    borders,
                    params["friction"],
                    params["accel"],
                )
            case 3:
                params = self.movement_params[self.phase]
                self._chase(
                    tar_x,
                    tar_y,
                    params["friction"],
                    params["accel"],
                )
            case 4:
                params = self.movement_params[self.phase]
                self._wander(
                    borders,
                    params["friction"],
                    params["accel"],
                )

    # ==================
    # ATTACK ROUTING
    # ==================

    def _attack(self, tar_x, tar_y):
        dist = math.hypot(tar_x - self.rect.centerx, tar_y - self.rect.centery)

        match self.phase:
            case 1:
                self._ranged_atk(tar_x, tar_y)
            case 2:
                if dist <= 300:
                    self._burst_atk()
                elif dist <= 500:
                    self._ranged_atk(tar_x, tar_y)
                else:
                    self._varied_burst_atk()
            case 3:
                params = self.spawn_enemy_params[self.phase]
                if dist <= 500:
                    self._spawn_enemies(params["spawn_enemy_cd"])
                    self._burst_atk()
                else:
                    self._varied_burst_atk()
            case 4:
                params = self.spawn_enemy_params[self.phase]
                self._spawn_enemies(params["spawn_enemy_cd"])
                self._varied_burst_atk()

    # ==================
    # MOVEMENTS
    # ==================

    def _chase(self, tar_x, tar_y, friction, accel):
        angle = math.atan2(tar_y - self.rect.centery, tar_x - self.rect.centerx)

        self.dx += math.cos(angle) * accel
        self.dy += math.sin(angle) * accel
        self.dx *= friction
        self.dy *= friction

        self.rect.x += int(self.dx)
        self.rect.y += int(self.dy)

    def _wander(self, borders, friction, accel):
        now = pygame.time.get_ticks()

        dist = math.hypot(
            self.wander_target_x - self.rect.centerx,
            self.wander_target_y - self.rect.centery,
        )
        if dist < 20 or now - self.wander_timer > self.wander_cd:
            self.wander_timer = now

            left = borders.sprites()[0].rect.right
            right = borders.sprites()[1].rect.left
            top = borders.sprites()[2].rect.bottom
            bottom = borders.sprites()[3].rect.top

            self.wander_target_x = random.randint(left + 50, right - 50)
            self.wander_target_y = random.randint(top + 50, bottom - 50)

        angle = math.atan2(
            self.wander_target_y - self.rect.centery,
            self.wander_target_x - self.rect.centerx,
        )
        self.dx += math.cos(angle) * accel
        self.dy += math.sin(angle) * accel
        self.dx *= friction
        self.dy *= friction

        self.rect.x += int(self.dx)
        self.rect.y += int(self.dy)

    # ==================
    # ATTACKS
    # ==================

    def _ranged_atk(self, tar_x, tar_y):
        self.pistol.shoot(tar_x, tar_y)

    def _burst_atk(self):
        now = pygame.time.get_ticks()
        if now - self.burst_atk_timer < self.burst_atk_cd:
            return
        self.burst_atk_timer = now

        bullet_count = 8
        angle_step = 360 / bullet_count
        for i in range(bullet_count):
            angle = math.radians(angle_step * i)
            tar_x_off = self.rect.centerx + math.cos(angle) * 100
            tar_y_off = self.rect.centery + math.sin(angle) * 100
            for ring_spd in (3, 12):
                self.projectile_grp.add(
                    Bullet(
                        10,
                        self.rect.centerx,
                        self.rect.centery,
                        tar_x_off,
                        tar_y_off,
                        RED,
                        self.damage,
                        speed=ring_spd,
                    )
                )

    def _varied_burst_atk(self):
        now = pygame.time.get_ticks()
        if now - self.varied_burst_atk_timer < self.varied_burst_atk_cd:
            return
        self.varied_burst_atk_timer = now

        bullet_count = 8
        angle_step = 360 / bullet_count
        for i in range(bullet_count):
            angle = math.radians(angle_step * i)
            tar_x_off = self.rect.centerx + math.cos(angle) * 100
            tar_y_off = self.rect.centery + math.sin(angle) * 100
            for ring_spd in (3, 12):
                self.projectile_grp.add(
                    Bullet(
                        5,
                        self.rect.centerx,
                        self.rect.centery,
                        tar_x_off,
                        tar_y_off,
                        RED,
                        self.damage,
                        speed=ring_spd,
                    )
                )

    def _spawn_enemies(self, enemy_cd):
        now = pygame.time.get_ticks()
        if now - self.spawn_enemy_timer < enemy_cd:
            return
        self.spawn_enemy_timer = now

        spawn_sniper = Sniper(
            self.rect.centerx,
            self.rect.centery,
        )

        self.sniper_grp.add(spawn_sniper)

    def _explode(self, bullet_count=16):
        angle_step = 360 / bullet_count
        for i in range(bullet_count):
            angle = math.radians(angle_step * i)
            tar_x = self.rect.centerx + math.cos(angle) * 100
            tar_y = self.rect.centery + math.sin(angle) * 100
            for ring_spd in (3, 5, 9, 12):
                self.projectile_grp.add(
                    Bullet(
                        5,
                        self.rect.centerx,
                        self.rect.centery,
                        tar_x,
                        tar_y,
                        self.color,
                        self.damage,
                        ring_spd,
                    )
                )
        self.kill()

    # ==================
    # DRAW
    # ==================

    def draw_health_bar(self, screen):
        bar_wd = 80
        bar_ht = 20

        bar_x = self.rect.centerx - (bar_wd // 2)
        bar_y = self.rect.top - (bar_ht * 2)

        fill_wd = int(self.health / self.max_health * bar_wd)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, fill_wd, bar_ht))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_wd, bar_ht), 1)
