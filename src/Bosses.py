import math
import random

import pygame

from const.COLORS import BLACK, BLUE, GREEN, ORANGE, PLAT, RED, VIOLET, WHITE, YELLOW
from const.FONTS import REGULAR
from src.Enemies import Sniper
from src.Entities import GlassEntity, StarEntity
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
        self.phase = 1  # [1, 2, 3, 4]

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
            1: {},
            2: {},
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
        mov_params = self.movement_params[self.phase]

        match self.phase:
            case 1:
                self._chase(
                    tar_x,
                    tar_y,
                    mov_params["friction"],
                    mov_params["accel"],
                )
            case 2:
                self._wander(
                    borders,
                    mov_params["friction"],
                    mov_params["accel"],
                )
            case 3:
                self._chase(
                    tar_x,
                    tar_y,
                    mov_params["friction"],
                    mov_params["accel"],
                )
            case 4:
                self._wander(
                    borders,
                    mov_params["friction"],
                    mov_params["accel"],
                )

    # ==================
    # ATTACK ROUTING
    # ==================

    def _attack(self, tar_x, tar_y):
        dist = math.hypot(tar_x - self.rect.centerx, tar_y - self.rect.centery)

        enemy_params = self.spawn_enemy_params[self.phase]

        match self.phase:
            case 1:
                self._ranged_atk(tar_x, tar_y)
                self._burst_atk()
            case 2:
                if dist <= 300:
                    self._burst_atk()
                    self._ranged_atk(tar_x, tar_y)
                elif dist <= 500:
                    self._varied_burst_atk()
                    self._ranged_atk(tar_x, tar_y)
                else:
                    self._varied_burst_atk()
            case 3:
                if dist <= 500:
                    self._spawn_enemies(enemy_params["spawn_enemy_cd"])
                    self._burst_atk()
                else:
                    self._varied_burst_atk()
            case 4:
                self._spawn_enemies(enemy_params["spawn_enemy_cd"])
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
                        self.color,
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
                        self.color,
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

    def draw_health_bar(self, win_wd, screen):
        bar_wd = 400
        bar_ht = 20
        gap = 5

        bar_rect = pygame.Rect(0, 0, bar_wd, bar_ht)
        bar_rect.midtop = (win_wd // 2, 40)

        fill_wd = int(self.health / self.max_health * bar_wd)
        pygame.draw.rect(screen, RED, (bar_rect.x, bar_rect.y, fill_wd, bar_ht))
        pygame.draw.rect(screen, WHITE, bar_rect, 2)

        font = pygame.font.Font(REGULAR, 40)
        name_img = font.render("Venus", True, WHITE)
        name_img.set_alpha(128)
        name_rect = name_img.get_rect(midtop=(bar_rect.centerx, bar_rect.bottom + gap))
        screen.blit(name_img, name_rect)


class MilkyWay(GlassEntity):
    PHASE_THRESHOLDS = {
        4: 0.20,
        3: 0.40,
        2: 0.75,
        1: 1.00,
    }

    def __init__(
        self,
        x_cor,
        y_cor,
        projectile_grp,
        health=15000,
        damage=25,
        size=250,
        color=VIOLET,
        speed=5,
    ) -> None:
        super().__init__(size, x_cor, y_cor, color)

        self.projectile_grp = projectile_grp
        self.orig_image = self.image

        self.health = self.max_health = health
        self.damage = damage
        self.phase = 1

        self.speed = speed
        self.dx = self.speed
        self.dy = self.speed
        self.friction = 0.92
        self.accel = 0.60

        self.angle = 0
        self.rot_spd = 1
        self.rot_dir = 1  # 1 = clockwise, -1 = counterclockwise
        self.rot_switch_cd = 5000
        self.rot_switch_timer = pygame.time.get_ticks()

        self.bullet_rot_params = {
            1: {
                "bullet_arms": 4,
                "speed": 5,
                "rad": 6,
                "bullet_cd": 500,
            },
            2: {},
            3: {
                "bullet_arms": 8,
                "speed": 10,
                "rad": 8,
                "bullet_cd": 250,
            },
            4: {
                "bullet_arms": 16,
                "speed": 5,
                "rad": 6,
                "bullet_cd": 1100,
            },
        }
        self.bullet_rot_timer = 0

        self.rainfall_params = {
            1: {},
            2: {
                "speed": (5, 6, 7, 8, 10),
                "rad": 6,
                "bullet_cd": 700,
                "bullet_count": (2, 4, 6, 8),
            },
            3: {},
            4: {
                "speed": (7, 8, 9, 10, 11, 12, 13),
                "rad": 8,
                "bullet_cd": 250,
                "bullet_count": (4, 6, 8),
            },
        }
        self.rainfall_timer = 0

        self.burst_atk_timer = 0
        self.burst_atk_cd = 1300

    # ==================
    # CORE
    # ==================

    def update(self, win_wd, win_ht, tar_x, tar_y, borders):
        self._update_phase()
        self._movement(tar_x, tar_y, borders)
        self._attack(win_wd, win_ht, tar_x, tar_y)

        self._handle_rotation()

    def _update_phase(self):
        health_pct = self.health / self.max_health
        for phase, threshold in self.PHASE_THRESHOLDS.items():
            if health_pct <= threshold:
                self.phase = phase
                break

    def _handle_rotation(self):
        now = pygame.time.get_ticks()

        if now - self.rot_switch_timer > self.rot_switch_cd:
            self.rot_dir *= -1
            self.rot_switch_timer = now

        self.angle = (self.angle + (self.rot_spd * self.rot_dir)) % 360

        self.image = pygame.transform.rotozoom(self.orig_image, self.angle, 1.0)
        self.rect = self.image.get_rect(center=(self.x_cor, self.y_cor))
        self.mask = pygame.mask.from_surface(self.image)

        self.x_cor, self.y_cor = self.rect.center

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
                pass
            case 2:
                pass
            case 3:
                pass
            case 4:
                pass

    # ==================
    # ATTACK ROUTING
    # ==================

    def _attack(self, win_wd, win_ht, tar_x, tar_y):
        dist = math.hypot(tar_x - self.rect.centerx, tar_y - self.rect.centery)

        bullet_rot = self.bullet_rot_params[self.phase]
        rf_params = self.rainfall_params[self.phase]

        match self.phase:
            case 1:
                self._bullet_rotation(
                    bullet_rot["bullet_arms"],
                    bullet_rot["speed"],
                    bullet_rot["rad"],
                    bullet_rot["bullet_cd"],
                )
            case 2:
                self._burst_atk()
                self._rainfall(
                    win_wd,
                    win_ht,
                    random.choice(rf_params["speed"]),
                    rf_params["rad"],
                    rf_params["bullet_cd"],
                    random.choice(rf_params["bullet_count"]),
                )
            case 3:
                if dist > 500:
                    self._burst_atk()
                self._bullet_rotation(
                    bullet_rot["bullet_arms"],
                    bullet_rot["speed"],
                    bullet_rot["rad"],
                    bullet_rot["bullet_cd"],
                )
            case 4:
                self._rainfall(
                    win_wd,
                    win_ht,
                    random.choice(rf_params["speed"]),
                    rf_params["rad"],
                    rf_params["bullet_cd"],
                    random.choice(rf_params["bullet_count"]),
                )
                self._bullet_rotation(
                    bullet_rot["bullet_arms"],
                    bullet_rot["speed"],
                    bullet_rot["rad"],
                    bullet_rot["bullet_cd"],
                )

    # ==================
    # MOVEMENTS
    # ==================

    # ==================
    # ATTACKS
    # ==================

    def _bullet_rotation(self, bullet_arms=4, speed=5, rad=6, bullet_cd=250):
        now = pygame.time.get_ticks()
        if now - self.bullet_rot_timer < bullet_cd:
            return
        self.bullet_rot_timer = now

        for i in range(bullet_arms):
            arm_angle_deg = self.angle + (i * (360 / bullet_arms))
            arm_angle_rad = math.radians(arm_angle_deg)

            spawn_x = self.rect.centerx
            spawn_y = self.rect.centery

            dist_to_target = 100
            target_x = spawn_x + math.cos(arm_angle_rad) * dist_to_target
            target_y = spawn_y + math.sin(arm_angle_rad) * dist_to_target

            bullet = Bullet(
                radius=rad,
                x_cor=spawn_x,
                y_cor=spawn_y,
                tar_x=target_x,
                tar_y=target_y,
                color=self.color,
                damage=self.damage,
                speed=speed,
            )
            self.projectile_grp.add(bullet)

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
                        5,
                        self.rect.centerx,
                        self.rect.centery,
                        tar_x_off,
                        tar_y_off,
                        self.color,
                        self.damage,
                        speed=ring_spd,
                    )
                )

    def _rainfall(self, win_wd, win_ht, speed=5, rad=6, bullet_cd=700, bullet_count=16):
        now = pygame.time.get_ticks()
        if now - self.rainfall_timer < bullet_cd:
            return
        self.rainfall_timer = now

        border_padding = 40
        for i in range(bullet_count):
            start_x = random.randint(border_padding, win_wd - border_padding)
            start_y = border_padding

            target_x = start_x
            target_y = win_ht

            spawn_bullet = Bullet(
                rad,
                start_x,
                start_y,
                target_x,
                target_y,
                self.color,
                self.damage,
                speed,
            )
            self.projectile_grp.add(spawn_bullet)

    def _spawn_enemies(self, enemy_cd):
        pass

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

    def draw_health_bar(self, win_wd, screen):
        bar_wd = 400
        bar_ht = 20
        gap = 5

        bar_rect = pygame.Rect(0, 0, bar_wd, bar_ht)
        bar_rect.midtop = (win_wd // 2, 40)

        fill_wd = int(self.health / self.max_health * bar_wd)
        pygame.draw.rect(screen, RED, (bar_rect.x, bar_rect.y, fill_wd, bar_ht))
        pygame.draw.rect(screen, WHITE, bar_rect, 2)

        font = pygame.font.Font(REGULAR, 40)
        name_img = font.render("Milky Way", True, WHITE)
        name_img.set_alpha(128)
        name_rect = name_img.get_rect(midtop=(bar_rect.centerx, bar_rect.bottom + gap))
        screen.blit(name_img, name_rect)
