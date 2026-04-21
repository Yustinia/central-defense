import math
import random

import pygame

from const.COLORS import BLACK, BLUE, GREEN, ORANGE, PLAT, RED, VIOLET, WHITE, YELLOW
from const.FONTS import REGULAR
from src.Enemies import Sniper
from src.Entities import GlassEntity, OmenEntity, StarEntity
from src.Weapons import Block, Bullet, Pistol


class Venus(StarEntity):
    SONG_PHASES = {
        15: (117408, 126670),  # end
        14: (114260, 117408),  # outro
        13: (101805, 114260),  # drop 4
        12: (89308, 101805),  # drop 3
        11: (76798, 89308),  # drop 2
        10: (64400, 76798),  # drop 1
        9: (62776, 64400),  # pre-drop
        8: (58174, 62776),  # build
        7: (51919, 58174),  # verse 3
        6: (39466, 51919),  # verse 2
        5: (26989, 39466),  # verse 1
        4: (25399, 26989),  # short break
        3: (14467, 25399),  # intro 2
        2: (2005, 14467),  # intro
        1: (0, 2005),  # fade in
    }

    def __init__(
        self,
        x_cor,
        y_cor,
        projectile_grp,
        sniper_grp,
        obs_grp,
        size=120,
        color=RED,
        num_points=5,
        depth_ratio=0.4,
        damage=25,
    ) -> None:
        super().__init__(size, x_cor, y_cor, color, num_points, depth_ratio)

        self.projectile_grp = projectile_grp
        self.sniper_grp = sniper_grp
        self.obs_grp = obs_grp

        self.damage = damage
        self.phase = 1  # [1 ... 14]

        self.tar_x, self.tar_y = 0, 0
        self.borders = None

        self.dx, self.dy = 0, 0
        self.wander_target_x = self.rect.centerx
        self.wander_target_y = self.rect.centery
        self.wander_cd = 2000
        self.wander_timer = 0

        self.phase_movements = {
            1: [],
            2: [(self._chase, {"friction": 0.92, "accel": 0.50})],
            3: [(self._chase, {"friction": 0.95, "accel": 0.70})],
            4: [(self._center, {"friction": 0.97, "accel": 3.00})],
            5: [(self._center, {"friction": 0.90, "accel": 0.50})],
            6: [(self._center, {"friction": 0.90, "accel": 0.50})],
            7: [(self._wander, {"friction": 0.92, "accel": 0.60})],
            8: [(self._wander, {"friction": 0.92, "accel": 0.90})],
            9: [(self._center, {"friction": 0.97, "accel": 3.00})],
            10: [(self._chase, {"friction": 0.95, "accel": 0.70})],
            11: [(self._chase, {"friction": 0.95, "accel": 0.80})],
            12: [(self._center, {"friction": 0.90, "accel": 0.50})],
            13: [(self._wander, {"friction": 0.92, "accel": 0.90})],
            14: [(self._center, {"friction": 0.97, "accel": 3.00})],
            15: [],
        }

        self.burst_atk_timer = 0
        self.burst_atk_index = 0
        self.rainfall_timer = 0
        self.bullet_rot_timer = 0
        self.rot_switch_timer = pygame.time.get_ticks()
        self.angle = 0
        self.rot_dir = 1
        self.rot_switch_cd = 5000
        self.block_timer = 0
        self.spawn_enemy_timer = 0

        self.phase_rot_speeds = {
            4: 2,
            5: 2,
            6: 2,
            9: 2,
            12: 4,
            14: 2,
        }
        self.phase_attacks = {
            1: [],
            2: [
                (self._ranged_atk, {}),
                (
                    self._burst_atk,
                    {
                        "cd": 1520,
                        "bullet_count": (6, 8),
                        "rad": 8,
                        "ring_speed": (3, 5),
                    },
                ),
            ],
            3: [
                (self._ranged_atk, {}),
                (
                    self._burst_atk,
                    {"cd": 760, "bullet_count": (6, 8), "rad": 6, "ring_speed": (2, 6)},
                ),
            ],
            4: [(self._bullet_rotation, {"arms": 8, "speed": 10, "rad": 10, "cd": 95})],
            5: [
                (
                    self._bullet_rainfall,
                    {
                        "cd": 760,
                        "bullet_count": 6,
                        "rad": 8,
                        "speed": (5, 6, 7, 8, 9, 10),
                        "reverse": False,
                    },
                ),
                (self._bullet_rotation, {"arms": 6, "speed": 5, "rad": 10, "cd": 380}),
            ],
            6: [
                (
                    self._bullet_rainfall,
                    {
                        "cd": 760,
                        "bullet_count": 6,
                        "rad": 8,
                        "speed": (5, 6, 7, 8, 9, 10),
                        "reverse": True,
                    },
                ),
                (self._bullet_rotation, {"arms": 6, "speed": 5, "rad": 10, "cd": 380}),
            ],
            7: [
                (
                    self._burst_atk,
                    {
                        "cd": 760,
                        "bullet_count": (6, 10),
                        "rad": 8,
                        "ring_speed": (3, 5),
                    },
                ),
                (self._spawn_snipers, {"cd": 1520}),
                (self._block, {"cd": 760, "speed": (5, 10, 15, 20), "box_count": 1}),
            ],
            8: [
                (
                    self._burst_atk,
                    {
                        "cd": 380,
                        "bullet_count": (8, 12),
                        "rad": 6,
                        "ring_speed": (3, 6),
                    },
                ),
                (self._spawn_snipers, {"cd": 380}),
            ],
            9: [(self._bullet_rotation, {"arms": 8, "speed": 10, "rad": 10, "cd": 95})],
            10: [
                (self._spawn_snipers, {"cd": 760}),
                (self._block, {"cd": 760, "speed": (5, 10, 15, 20), "box_count": 1}),
                (
                    self._burst_atk,
                    {"cd": 760, "bullet_count": 8, "rad": 6, "ring_speed": (3, 6)},
                ),
            ],
            11: [
                (self._block, {"cd": 380, "speed": (5, 10, 15, 20), "box_count": 2}),
                (self._ranged_atk, {}),
                (self._spawn_snipers, {"cd": 760}),
            ],
            12: [
                (self._bullet_rotation, {"arms": 8, "speed": 10, "rad": 10, "cd": 380}),
                (self._block, {"cd": 380, "speed": (5, 10, 15, 20), "box_count": 3}),
            ],
            13: [
                (
                    self._burst_atk,
                    {
                        "cd": 760,
                        "bullet_count": (10, 14),
                        "rad": 8,
                        "ring_speed": (4, 9),
                    },
                ),
                (
                    self._bullet_rainfall,
                    {
                        "cd": 380,
                        "bullet_count": 6,
                        "rad": 8,
                        "speed": (5, 6, 7, 8, 9, 10),
                        "reverse": False,
                    },
                ),
            ],
            14: [
                (self._bullet_rotation, {"arms": 8, "speed": 10, "rad": 10, "cd": 95})
            ],
            15: [],
        }

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

        # states
        self.music_started = False

    # ==================
    # CORE
    # ==================

    def update(self, tar_x, tar_y, borders):
        self.tar_x, self.tar_y = tar_x, tar_y
        self.borders = borders

        self._update_phase()

        rot_params = next(
            (
                params
                for func, params in self.phase_attacks.get(self.phase, [])
                if func == self._bullet_rotation
            ),
            None,
        )
        if rot_params:
            rot_params = {
                **rot_params,
                "rot_speed": self.phase_rot_speeds.get(self.phase, 1),
            }
        self._update_rotation(rot_params)

        self._movement()
        self._attack()

    def _update_rotation(self, params):
        if not params:
            return

        now = pygame.time.get_ticks()
        self.angle = (self.angle + params["rot_speed"] * self.rot_dir) % 360

        if now - self.rot_switch_timer > self.rot_switch_cd:
            self.rot_switch_timer = now
            self.rot_dir *= -1

    def _update_phase(self):
        if not self.music_started:
            return

        if not self.alive():
            return

        pos = pygame.mixer.music.get_pos()
        for phase, (start, end) in self.SONG_PHASES.items():
            if start <= pos < end:
                self.phase = phase
                break

        last_phase = max(self.SONG_PHASES)
        end_time = self.SONG_PHASES[last_phase][1]
        buffer = 100
        if pos >= end_time - buffer:
            self._explode()

    # ==================
    # MOVEMENT ROUTING
    # ==================

    def _movement(self):
        dist = math.hypot(
            self.tar_x - self.rect.centerx, self.tar_y - self.rect.centery
        )

        for func, params in self.phase_movements.get(self.phase, []):
            func(**params)

    # ==================
    # ATTACK ROUTING
    # ==================

    def _attack(self):
        dist = math.hypot(
            self.tar_x - self.rect.centerx, self.tar_y - self.rect.centery
        )

        for func, params in self.phase_attacks.get(self.phase, []):
            func(**params)

    # ==================
    # MOVEMENTS
    # ==================

    def _chase(self, friction, accel):
        angle = math.atan2(
            self.tar_y - self.rect.centery, self.tar_x - self.rect.centerx
        )

        self.dx += math.cos(angle) * accel
        self.dy += math.sin(angle) * accel
        self.dx *= friction
        self.dy *= friction

        self.rect.x += int(self.dx)
        self.rect.y += int(self.dy)

    def _wander(self, friction, accel):
        now = pygame.time.get_ticks()

        dist = math.hypot(
            self.wander_target_x - self.rect.centerx,
            self.wander_target_y - self.rect.centery,
        )
        if dist < 20 or now - self.wander_timer > self.wander_cd:
            self.wander_timer = now

            border_sprites = self.borders.sprites()

            left_border = border_sprites[0]
            right_border = border_sprites[1]
            top_border = border_sprites[2]
            bottom_border = border_sprites[3]

            self.wander_target_x = random.randint(
                left_border.rect.right + 50, right_border.rect.left - 50
            )
            self.wander_target_y = random.randint(
                top_border.rect.bottom + 50, bottom_border.rect.top - 50
            )

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

    def _center(self, friction, accel):
        border_sprites = self.borders.sprites()

        left_border = border_sprites[0]
        right_border = border_sprites[1]
        top_border = border_sprites[2]
        bottom_border = border_sprites[3]

        center_x = (left_border.rect.right + right_border.rect.left) // 2
        center_y = (top_border.rect.bottom + bottom_border.rect.top) // 2

        angle = math.atan2(
            center_y - self.rect.centery,
            center_x - self.rect.centerx,
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

    def _ranged_atk(self):
        self.pistol.shoot(self.tar_x, self.tar_y)

    def _burst_atk(
        self,
        cd,
        bullet_count,
        rad,
        ring_speed,
    ):
        now = pygame.time.get_ticks()
        if now - self.burst_atk_timer < cd:
            return
        self.burst_atk_timer = now

        counts = bullet_count if isinstance(bullet_count, tuple) else (bullet_count,)
        count = counts[self.burst_atk_index % len(counts)]
        self._bullet_ring(count, rad, ring_speed)
        self.burst_atk_index += 1

    def _bullet_ring(self, bullet_count, rad, ring_speed):
        angle_step = 360 / bullet_count
        for i in range(bullet_count):
            angle = math.radians(angle_step * i)
            tar_x_off = self.rect.centerx + math.cos(angle) * 100
            tar_y_off = self.rect.centery + math.sin(angle) * 100
            for circ_speed in ring_speed:
                self.projectile_grp.add(
                    Bullet(
                        rad,
                        self.rect.centerx,
                        self.rect.centery,
                        tar_x_off,
                        tar_y_off,
                        self.color,
                        self.damage,
                        speed=circ_speed,
                    )
                )

    def _spawn_snipers(self, cd):
        now = pygame.time.get_ticks()
        if now - self.spawn_enemy_timer < cd:
            return
        self.spawn_enemy_timer = now

        spawn_sniper = Sniper(
            self.rect.centerx,
            self.rect.centery,
        )

        self.sniper_grp.add(spawn_sniper)

    def _bullet_rainfall(self, cd, bullet_count, rad, speed, reverse):
        now = pygame.time.get_ticks()
        if now - self.rainfall_timer < cd:
            return
        self.rainfall_timer = now

        border_sprites = self.borders.sprites()
        top_border = border_sprites[2]
        bottom_border = border_sprites[3]
        left_border = border_sprites[0]
        right_border = border_sprites[1]

        padding = 20
        min_x = left_border.rect.right + padding
        max_x = right_border.rect.left - padding

        if reverse:
            start_y = bottom_border.rect.top - padding
            end_y = top_border.rect.top
        else:
            start_y = top_border.rect.bottom + padding
            end_y = bottom_border.rect.bottom

        for i in range(bullet_count):
            x = random.randint(min_x, max_x)
            self.projectile_grp.add(
                Bullet(
                    rad,
                    x,
                    start_y,
                    x,
                    end_y,
                    self.color,
                    self.damage,
                    random.choice(speed),
                )
            )

    def _bullet_rotation(self, arms, speed, rad, cd):
        now = pygame.time.get_ticks()
        if now - self.bullet_rot_timer < cd:
            return
        self.bullet_rot_timer = now

        for i in range(arms):
            arm_angle_deg = self.angle + (i * (360 / arms))
            arm_angle_rad = math.radians(arm_angle_deg)

            tar_x = self.rect.centerx + math.cos(arm_angle_rad) * 100
            tar_y = self.rect.centery + math.sin(arm_angle_rad) * 100
            self.projectile_grp.add(
                Bullet(
                    rad,
                    self.rect.centerx,
                    self.rect.centery,
                    tar_x,
                    tar_y,
                    self.color,
                    self.damage,
                    speed,
                )
            )

    def _block(self, cd, speed, box_count):
        now = pygame.time.get_ticks()
        if now - self.block_timer < cd:
            return
        self.block_timer = now

        border_sprites = self.borders.sprites()
        left_border = border_sprites[0]
        right_border = border_sprites[1]
        top_border = border_sprites[2]
        bottom_border = border_sprites[3]

        padding = 20

        min_x = left_border.rect.right + padding
        max_x = right_border.rect.left - padding
        min_y = top_border.rect.bottom + padding
        max_y = bottom_border.rect.top - padding

        orientation = random.choice(["horizontal", "vertical"])
        size = 40

        for i in range(box_count):
            if orientation == "horizontal":
                direction = random.choice(["top_to_bottom", "bottom_to_top"])
                x = random.randint(min_x, max_x)
                if direction == "top_to_bottom":
                    y = min_y
                    dy, dx = random.choice(speed), 0
                else:
                    y = max_y
                    dy, dx = -random.choice(speed), 0
                block = Block(self.obs_grp, x, y, size, self.color, self.damage)

            else:
                direction = random.choice(["left_to_right", "right_to_left"])
                y = random.randint(min_y, max_y)
                if direction == "left_to_right":
                    x = min_x
                    dx, dy = random.choice(speed), 0
                else:
                    x = max_x
                    dx, dy = -random.choice(speed), 0
                block = Block(self.obs_grp, x, y, size, self.color, self.damage)

            block.dx = dx
            block.dy = dy
            self.obs_grp.add(block)

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

    def draw_duration_bar(self, win_wd, screen):
        bar_wd = 400
        bar_ht = 20
        gap = 5

        bar_rect = pygame.Rect(0, 0, bar_wd, bar_ht)
        bar_rect.midtop = (win_wd // 2, 40)

        last_phase = max(self.SONG_PHASES)
        end_time = self.SONG_PHASES[last_phase][1]
        pos = pygame.mixer.music.get_pos()
        progress = min(pos / end_time, 1.0)

        fill_wd = int(progress * bar_wd)
        pygame.draw.rect(screen, RED, (bar_rect.x, bar_rect.y, fill_wd, bar_ht))
        pygame.draw.rect(screen, WHITE, bar_rect, 2)

        font = pygame.font.Font(REGULAR, 40)
        name_img = font.render("Venus", True, WHITE)
        name_img.set_alpha(128)
        name_rect = name_img.get_rect(midtop=(bar_rect.centerx, bar_rect.bottom + gap))
        screen.blit(name_img, name_rect)


class MilkyWay(GlassEntity):
    EIGHT = 165
    FOURTH = 330
    HALF = 659
    WHOLE = 1319
    DOUBLE = 2638

    SONG_PHASES = {
        12: (101146, 107180),  # outro
        11: (90591, 101146),  # drop 6
        10: (80095, 90591),  # drop 5
        9: (69626, 80095),  # bridge 2
        8: (59119, 69626),  # bridge 1
        7: (57844, 59119),  # short break
        6: (47338, 57844),  # drop 4
        5: (36810, 47338),  # drop 3
        4: (26306, 36810),  # drop 2
        3: (15840, 26306),  # drop 1
        2: (5333, 15840),  # build
        1: (0, 5333),  # intro
    }

    def __init__(
        self,
        x_cor,
        y_cor,
        projectile_grp,
        obs_grp,
        damage=25,
        size=250,
        color=VIOLET,
        speed=5,
    ) -> None:
        super().__init__(size, x_cor, y_cor, color)

        self.projectile_grp = projectile_grp
        self.obs_grp = obs_grp
        self.orig_image = self.image

        self.damage = damage
        self.phase = 1

        self.speed = speed
        self.dx = self.speed
        self.dy = self.speed
        self.friction = 0.92
        self.accel = 0.60

        self.tar_x, self.tar_y = 0, 0
        self.borders = None

        self.angle = 0
        self.rot_dir = 1
        self.rot_switch_timer = pygame.time.get_ticks()
        self.bullet_rot_timer = 0
        self.burst_atk_timer = 0
        self.burst_atk_index = 0
        self.rainfall_timer = 0
        self.block_timer = 0

        self.phase_attacks = {
            1: [
                (
                    self._bullet_rotation,
                    {"bullet_arms": 4, "speed": 5, "rad": 6, "bullet_cd": self.FOURTH},
                )
            ],
            2: [
                (
                    self._bullet_rotation,
                    {"bullet_arms": 6, "speed": 7, "rad": 6, "bullet_cd": self.FOURTH},
                ),
                (
                    self._bullet_rainfall,
                    {
                        "cd": self.HALF,
                        "bullet_count": 6,
                        "rad": 8,
                        "speed": (5, 6, 7, 8, 9, 10),
                        "reverse": False,
                    },
                ),
            ],
            3: [
                (
                    self._burst_atk,
                    {
                        "cd": self.FOURTH,
                        "bullet_count": (6, 8, 12, 18),
                        "rad": 8,
                        "ring_speed": 5,
                    },
                )
            ],
            4: [
                (
                    self._burst_atk,
                    {
                        "cd": self.EIGHT,
                        "bullet_count": (12, 15, 19),
                        "rad": 8,
                        "ring_speed": 8,
                    },
                )
            ],
            5: [
                (
                    self._bullet_rotation,
                    {
                        "bullet_arms": 10,
                        "speed": 10,
                        "rad": 6,
                        "bullet_cd": self.FOURTH,
                    },
                ),
                (
                    self._bullet_rainfall,
                    {
                        "cd": self.HALF,
                        "bullet_count": 6,
                        "rad": 8,
                        "speed": (5, 6, 7, 8, 9, 10),
                        "reverse": False,
                    },
                ),
            ],
            6: [
                (
                    self._bullet_rotation,
                    {
                        "bullet_arms": 14,
                        "speed": 12,
                        "rad": 10,
                        "bullet_cd": self.FOURTH,
                    },
                ),
                (
                    self._bullet_rainfall,
                    {
                        "cd": self.HALF,
                        "bullet_count": 6,
                        "rad": 8,
                        "speed": (5, 6, 7, 8, 9, 10),
                        "reverse": True,
                    },
                ),
            ],
            8: [
                (
                    self._block,
                    {"cd": self.EIGHT, "speed": (5, 10, 15, 20), "box_count": 1},
                )
            ],
            9: [
                (
                    self._block,
                    {"cd": self.EIGHT, "speed": (5, 10, 15, 20), "box_count": 2},
                ),
                (
                    self._burst_atk,
                    {
                        "cd": self.WHOLE,
                        "bullet_count": (6, 12),
                        "rad": 8,
                        "ring_speed": 5,
                    },
                ),
            ],
            10: [
                (
                    self._bullet_rotation,
                    {"bullet_arms": 12, "speed": 8, "rad": 8, "bullet_cd": self.FOURTH},
                ),
                (
                    self._bullet_rainfall,
                    {
                        "cd": self.HALF,
                        "bullet_count": 6,
                        "rad": 8,
                        "speed": (5, 6, 7, 8, 9, 10),
                        "reverse": False,
                    },
                ),
                (
                    self._burst_atk,
                    {
                        "cd": self.HALF,
                        "bullet_count": (6, 12),
                        "rad": 8,
                        "ring_speed": 5,
                    },
                ),
            ],
            11: [
                (
                    self._bullet_rotation,
                    {"bullet_arms": 12, "speed": 8, "rad": 8, "bullet_cd": self.FOURTH},
                ),
                (
                    self._bullet_rainfall,
                    {
                        "cd": self.HALF,
                        "bullet_count": 6,
                        "rad": 8,
                        "speed": (5, 6, 7, 8, 9, 10),
                        "reverse": True,
                    },
                ),
                (
                    self._burst_atk,
                    {
                        "cd": self.HALF,
                        "bullet_count": (6, 12),
                        "rad": 8,
                        "ring_speed": 5,
                    },
                ),
            ],
        }

        self.phase_rotations = {
            1: {"rot_switch_cd": self.DOUBLE, "rot_speed": 1},
            2: {"rot_switch_cd": self.DOUBLE, "rot_speed": 2},
            3: {"rot_switch_cd": self.DOUBLE, "rot_speed": 1},
            4: {"rot_switch_cd": self.DOUBLE, "rot_speed": 1},
            5: {"rot_switch_cd": self.DOUBLE, "rot_speed": 2},
            6: {"rot_switch_cd": self.DOUBLE, "rot_speed": 3},
            7: {"rot_switch_cd": self.DOUBLE, "rot_speed": 1},
            8: {"rot_switch_cd": self.DOUBLE, "rot_speed": 1},
            9: {"rot_switch_cd": self.DOUBLE, "rot_speed": 1},
            10: {"rot_switch_cd": self.DOUBLE, "rot_speed": 3},
            11: {"rot_switch_cd": self.DOUBLE, "rot_speed": 3},
            12: {"rot_switch_cd": self.DOUBLE, "rot_speed": 1},
        }

        # states
        self.music_started = False

    # ==================
    # CORE
    # ==================

    def update(self, tar_x, tar_y, borders):
        self.tar_x = tar_x
        self.tar_y = tar_y
        self.borders = borders

        self._update_phase()
        self._movement()
        self._attack()

        params = self.phase_rotations.get(self.phase)
        self._handle_rotation(params)

    def _update_phase(self):
        if not self.music_started:
            return

        if not self.alive():
            return

        pos = pygame.mixer.music.get_pos()
        for phase, (start, end) in self.SONG_PHASES.items():
            if start <= pos < end:
                self.phase = phase
                break

        last_phase = max(self.SONG_PHASES)
        end_time = self.SONG_PHASES[last_phase][1]
        buffer = 100
        if pos >= end_time - buffer:
            self._explode()

    def _handle_rotation(self, params):
        if not params:
            return

        now = pygame.time.get_ticks()

        if now - self.rot_switch_timer > params["rot_switch_cd"]:
            self.rot_dir *= -1
            self.rot_switch_timer = now

        self.angle = (self.angle + (params["rot_speed"] * self.rot_dir)) % 360

        self.image = pygame.transform.rotozoom(self.orig_image, self.angle, 1.0)
        self.rect = self.image.get_rect(center=(self.x_cor, self.y_cor))
        self.mask = pygame.mask.from_surface(self.image)

        self.x_cor, self.y_cor = self.rect.center

    # ==================
    # MOVEMENT ROUTING
    # ==================

    def _movement(self):
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

    def _attack(self):
        dist = math.hypot(
            self.tar_x - self.rect.centerx, self.tar_y - self.rect.centery
        )

        for func, params in self.phase_attacks.get(self.phase, []):
            func(**params)

    # ==================
    # MOVEMENTS
    # ==================

    # ==================
    # ATTACKS
    # ==================

    def _bullet_rotation(self, bullet_arms, speed, rad, bullet_cd):
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

    def _burst_atk(
        self,
        cd: int,
        bullet_count: int,
        rad: int,
        ring_speed,
    ):
        now = pygame.time.get_ticks()
        if now - self.burst_atk_timer < cd:
            return
        self.burst_atk_timer = now

        count = bullet_count[self.burst_atk_index % len(bullet_count)]
        self._bullet_ring(count, rad, ring_speed)
        self.burst_atk_index += 1

    def _bullet_ring(self, bullet_count, rad, ring_speed):
        for i in range(bullet_count):
            angle_step = 360 / bullet_count
            angle = math.radians(angle_step * i)
            tar_x_off = self.rect.centerx + math.cos(angle) * 100
            tar_y_off = self.rect.centery + math.sin(angle) * 100
            self.projectile_grp.add(
                Bullet(
                    rad,
                    self.rect.centerx,
                    self.rect.centery,
                    tar_x_off,
                    tar_y_off,
                    self.color,
                    self.damage,
                    speed=ring_speed,
                )
            )

    def _bullet_rainfall(self, cd, bullet_count, rad, speed, reverse):
        now = pygame.time.get_ticks()
        if now - self.rainfall_timer < cd:
            return
        self.rainfall_timer = now

        border_sprites = self.borders.sprites()
        top_border = border_sprites[2]
        bottom_border = border_sprites[3]
        left_border = border_sprites[0]
        right_border = border_sprites[1]

        padding = 20
        min_x = left_border.rect.right + padding
        max_x = right_border.rect.left - padding

        if reverse:
            start_y = bottom_border.rect.top - padding
            end_y = top_border.rect.top
        else:
            start_y = top_border.rect.bottom + padding
            end_y = bottom_border.rect.bottom

        for i in range(bullet_count):
            x = random.randint(min_x, max_x)
            self.projectile_grp.add(
                Bullet(
                    rad,
                    x,
                    start_y,
                    x,
                    end_y,
                    self.color,
                    self.damage,
                    random.choice(speed),
                )
            )

    def _block(self, cd, speed, box_count):
        now = pygame.time.get_ticks()
        if now - self.block_timer < cd:
            return
        self.block_timer = now

        border_sprites = self.borders.sprites()
        left_border = border_sprites[0]
        right_border = border_sprites[1]
        top_border = border_sprites[2]
        bottom_border = border_sprites[3]

        padding = 20

        min_x = left_border.rect.right + padding
        max_x = right_border.rect.left - padding
        min_y = top_border.rect.bottom + padding
        max_y = bottom_border.rect.top - padding

        orientation = random.choice(["horizontal", "vertical"])
        size = 40

        for i in range(box_count):
            if orientation == "horizontal":
                direction = random.choice(["top_to_bottom", "bottom_to_top"])
                x = random.randint(min_x, max_x)
                if direction == "top_to_bottom":
                    y = min_y
                    dy, dx = random.choice(speed), 0
                else:
                    y = max_y
                    dy, dx = -random.choice(speed), 0
                block = Block(self.obs_grp, x, y, size, self.color, self.damage)

            else:
                direction = random.choice(["left_to_right", "right_to_left"])
                y = random.randint(min_y, max_y)
                if direction == "left_to_right":
                    x = min_x
                    dx, dy = random.choice(speed), 0
                else:
                    x = max_x
                    dx, dy = -random.choice(speed), 0
                block = Block(self.obs_grp, x, y, size, self.color, self.damage)

            block.dx = dx
            block.dy = dy
            self.obs_grp.add(block)

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

    def draw_duration_bar(self, win_wd, screen):
        bar_wd = 400
        bar_ht = 20
        gap = 5

        bar_rect = pygame.Rect(0, 0, bar_wd, bar_ht)
        bar_rect.midtop = (win_wd // 2, 40)

        last_phase = max(self.SONG_PHASES)
        end_time = self.SONG_PHASES[last_phase][1]
        pos = pygame.mixer.music.get_pos()
        progress = min(pos / end_time, 1.0)

        fill_wd = int(progress * bar_wd)
        pygame.draw.rect(screen, RED, (bar_rect.x, bar_rect.y, fill_wd, bar_ht))
        pygame.draw.rect(screen, WHITE, bar_rect, 2)

        font = pygame.font.Font(REGULAR, 40)
        name_img = font.render("Milky Way", True, WHITE)
        name_img.set_alpha(128)
        name_rect = name_img.get_rect(midtop=(bar_rect.centerx, bar_rect.bottom + gap))
        screen.blit(name_img, name_rect)


class Omen(OmenEntity):
    DOUBLE = 2759
    WHOLE = 1379
    HALF = 690
    THIRD = 460
    QUARTER = 345
    SIXTH = 230
    EIGHTH = 172
    SIXTEENTH = 86

    SONG_PHASES = {
        67: (163584, 164769),  # END
        66: (162717, 163584),  # OUTRO
        65: (161336, 162717),  # DRUMROLL
        64: (159956, 161336),  # DROP END
        63: (157199, 159956),  # DROP
        62: (156510, 157199),  # BURST
        61: (152717, 156510),  # DROP
        60: (152033, 152717),  # BURST
        59: (150990, 152033),  # BRASS
        58: (148929, 150990),  # DROP
        57: (146173, 148929),  # DROP
        56: (145822, 146173),  # BURST
        55: (141676, 145822),  # DROP
        54: (140997, 141676),  # BURST
        53: (139957, 140997),  # BRASS
        52: (135127, 139957),  # DROP
        51: (134785, 135127),  # BURST
        50: (134440, 134785),  # REST
        49: (129618, 134440),  # DROP
        48: (128236, 129618),  # PREDROP
        47: (125482, 128236),  # BUILDUP 2
        46: (122706, 125482),  # BUILDUP
        45: (118241, 122706),  # RISE
        44: (117192, 118241),  # FAKE DROP
        43: (115787, 117192),  # PREDROP
        42: (114431, 115787),  # BUILDUP 3
        41: (111677, 114431),  # BUILDUP 2
        40: (106151, 111677),  # BUILDUP
        39: (95160, 106151),  # INTERLUDE
        38: (93766, 95160),  # DRUMROLL
        37: (92403, 93766),  # DROP END
        36: (89644, 92403),  # DROP
        35: (88953, 89644),  # BURST
        34: (85159, 88953),  # DROP
        33: (84474, 85159),  # BURST
        32: (83434, 84474),  # BRASS
        31: (81368, 83434),  # DROP
        30: (78613, 81368),  # DROP
        29: (78257, 78613),  # BURST
        28: (74126, 78257),  # DROP
        27: (73091, 74126),  # BREAK
        26: (72107, 73091),  # GLITCH
        25: (71716, 72107),  # BURST
        24: (67573, 71716),  # DROP BREAK
        23: (66875, 67573),  # BURST
        22: (63088, 66875),  # DROP
        21: (62406, 63088),  # BURST
        20: (61370, 62406),  # BRASS
        19: (59300, 61370),  # DROP
        18: (56540, 59300),  # DROP
        17: (56191, 56540),  # BURST
        16: (52060, 56191),  # DROP
        15: (51019, 52060),  # REST
        14: (49644, 51019),  # PREDROP 3
        13: (48937, 49644),  # PREDROP 2
        12: (47919, 48937),  # RISE 3
        11: (47566, 47919),  # BURST
        10: (46540, 47566),  # RISE 2
        9: (46188, 46540),  # BURST
        8: (45165, 46188),  # RISE 1
        7: (44134, 45165),  # FAKE DROP
        6: (42721, 44134),  # KILL THEM ALL
        5: (41365, 42721),  # BUILDUP 3
        4: (38613, 41365),  # BUILDUP 2
        3: (33095, 38613),  # BUILDUP 1
        2: (22025, 33095),  # VERSE
        1: (0, 22025),  # INTRO
    }

    def __init__(
        self,
        x_cor,
        y_cor,
        projectile_grp,
        obs_grp,
        damage=25,
        size=120,
        color=ORANGE,
        rotation=0,
    ) -> None:
        super().__init__(size, x_cor, y_cor, color, rotation)

        self.projectile_grp = projectile_grp
        self.obs_grp = obs_grp
        self.damage = damage

        self.phase = 1

        self.dx, self.dy = 0, 0
        self.tar_x, self.tar_y = 0, 0
        self.rot_speed = 0
        self.borders = None
        self.orbit_angle = 0

        self.phase_movements = {
            1: [
                (
                    self._orbit,
                    {
                        "radius": 50,
                        "orbit_speed": 1,
                        "friction": 0.90,
                        "accel": 0.50,
                        "reverse": False,
                    },
                ),
                (self._rotate, {"rot_speed": 1}),
            ],
            2: [
                (self._center, {"friction": 0.92, "accel": 0.80}),
                (self.lerp_rotation_to_zero, {}),
            ],
            3: [
                (self._center, {"friction": 0.92, "accel": 0.80}),
                (self.lerp_rotation_to_zero, {}),
            ],
            4: [
                (self._center, {"friction": 0.92, "accel": 0.80}),
                (self.lerp_rotation_to_zero, {}),
            ],
            5: [
                (self._center, {"friction": 0.92, "accel": 0.80}),
                (self.lerp_rotation_to_zero, {}),
            ],
            6: [
                (self._center, {"friction": 0.92, "accel": 0.80}),
                (self.lerp_rotation_to_zero, {}),
            ],
            7: [
                (self._center, {"friction": 0.92, "accel": 0.80}),
                (self.lerp_rotation_to_zero, {}),
            ],
            8: [
                (self._center, {"friction": 0.92, "accel": 0.80}),
                (self._rotate, {"rot_speed": 4}),
            ],
            9: [
                (self._center, {"friction": 0.92, "accel": 0.80}),
                (self.lerp_rotation_to_zero, {}),
            ],
            10: [
                (self._center, {"friction": 0.92, "accel": 0.80}),
                (self._rotate, {"rot_speed": -6}),
            ],
            11: [
                (self._center, {"friction": 0.92, "accel": 0.80}),
                (self.lerp_rotation_to_zero, {}),
            ],
            12: [
                (self._center, {"friction": 0.92, "accel": 0.80}),
                (self._rotate, {"rot_speed": 8}),
            ],
            13: [
                (self._center, {"friction": 0.92, "accel": 0.80}),
                (self.lerp_rotation_to_zero, {}),
            ],
            14: [
                (self._center, {"friction": 0.92, "accel": 0.80}),
                (self.lerp_rotation_to_zero, {}),
            ],
            15: [
                (self._center, {"friction": 0.92, "accel": 0.80}),
                (self.lerp_rotation_to_zero, {}),
            ],
            16: [
                (self._anchor, {"anchor": "top", "speed": 50}),
                (self.lerp_rotation_to_zero, {"speed": 10}),
            ],
            17: [],
            18: [],
            19: [
                (self._center, {"friction": 0.92, "accel": 0.92}),
                (self._rotate, {"rot_speed": 6}),
            ],
            20: [
                (self._center, {"friction": 0.92, "accel": 0.92}),
                (self.lerp_rotation_to_zero, {}),
            ],
            21: [
                (self._center, {"friction": 0.92, "accel": 0.92}),
                (self.lerp_rotation_to_zero, {}),
            ],
            22: [
                (self._anchor, {"anchor": "bot", "speed": 50}),
                (self.lerp_rotation_to, {"target": 180, "speed": 10}),
            ],
            23: [],
            24: [
                (
                    self._orbit,
                    {
                        "radius": 50,
                        "orbit_speed": 1,
                        "friction": 0.90,
                        "accel": 0.50,
                        "reverse": False,
                    },
                ),
                (self._rotate, {"rot_speed": 1}),
            ],
            25: [
                (self._center, {"friction": 0.92, "accel": 0.92}),
                (self.lerp_rotation_to_zero, {}),
            ],
            26: [
                (self._center, {"friction": 0.92, "accel": 0.92}),
                (self._rotate, {"rot_speed": -8}),
            ],
            27: [
                (self._center, {"friction": 0.92, "accel": 0.92}),
                (self.lerp_rotation_to_zero, {}),
            ],
            28: [
                (self._anchor, {"anchor": "right", "speed": 50}),
                (self.lerp_rotation_to, {"target": 270, "speed": 10}),
            ],
            31: [
                (self._center, {"friction": 0.92, "accel": 0.92}),
                (self._rotate, {"rot_speed": -6}),
            ],
            32: [
                (self._center, {"friction": 0.92, "accel": 0.92}),
                (self.lerp_rotation_to_zero, {}),
            ],
            33: [
                (self._center, {"friction": 0.92, "accel": 0.92}),
                (self.lerp_rotation_to_zero, {}),
            ],
            34: [
                (self._anchor, {"anchor": "left", "speed": 50}),
                (self.lerp_rotation_to, {"target": 90, "speed": 10}),
            ],
            36: [
                (
                    self._orbit,
                    {
                        "radius": 100,
                        "orbit_speed": 1,
                        "friction": 0.90,
                        "accel": 0.50,
                        "reverse": True,
                    },
                ),
                (self._rotate, {"rot_speed": 4}),
            ],
            37: [
                (self._center, {"friction": 0.92, "accel": 0.92}),
                (self.lerp_rotation_to_zero, {}),
            ],
            38: [
                (self._center, {"friction": 0.92, "accel": 0.92}),
                (self.lerp_rotation_to_zero, {}),
            ],
            39: [
                (
                    self._orbit,
                    {
                        "radius": 200,
                        "orbit_speed": 1,
                        "friction": 0.92,
                        "accel": 0.80,
                        "reverse": True,
                    },
                ),
                (self._rotate, {"rot_speed": -1}),
            ],
            40: [
                (self._center, {"friction": 0.92, "accel": 0.80}),
                (self.lerp_rotation_to_zero, {}),
            ],
            41: [
                (self._center, {"friction": 0.92, "accel": 0.80}),
                (self.lerp_rotation_to_zero, {}),
            ],
            42: [
                (self._center, {"friction": 0.92, "accel": 0.80}),
                (self.lerp_rotation_to_zero, {}),
            ],
            43: [
                (self._center, {"friction": 0.92, "accel": 0.80}),
                (self.lerp_rotation_to_zero, {}),
            ],
            44: [
                (self._center, {"friction": 0.92, "accel": 0.80}),
                (self.lerp_rotation_to_zero, {}),
            ],
            45: [
                (
                    self._orbit,
                    {
                        "radius": 200,
                        "orbit_speed": 2,
                        "friction": 0.92,
                        "accel": 0.80,
                        "reverse": False,
                    },
                ),
                (self._rotate, {"rot_speed": 2}),
            ],
            46: [
                (
                    self._orbit,
                    {
                        "radius": 100,
                        "orbit_speed": 4,
                        "friction": 0.92,
                        "accel": 0.80,
                        "reverse": False,
                    },
                ),
                (self._rotate, {"rot_speed": 4}),
            ],
            47: [
                (
                    self._orbit,
                    {
                        "radius": 50,
                        "orbit_speed": 8,
                        "friction": 0.92,
                        "accel": 0.80,
                        "reverse": False,
                    },
                ),
                (self._rotate, {"rot_speed": 8}),
            ],
            48: [
                (self._center, {"friction": 0.92, "accel": 0.92}),
                (self._rotate, {"rot_speed": -4}),
            ],
            49: [  # drop
                (self._anchor, {"anchor": "top", "speed": 50}),
                (self.lerp_rotation_to_zero, {"speed": 10}),
            ],
            50: [
                (self._center, {"friction": 0.92, "accel": 0.92}),
                (self._rotate, {"rot_speed": 4}),
            ],
            51: [
                (self._center, {"friction": 0.92, "accel": 0.92}),
                (self._rotate, {"rot_speed": -8}),
            ],
            52: [  # drop
                (self._anchor, {"anchor": "bot", "speed": 50}),
                (self.lerp_rotation_to, {"target": 180, "speed": 10}),
            ],
            53: [
                (self._center, {"friction": 0.92, "accel": 0.92}),
                (self.lerp_rotation_to_zero, {}),
            ],
            54: [
                (self._center, {"friction": 0.92, "accel": 0.92}),
                (self.lerp_rotation_to_zero, {}),
            ],
            55: [
                (self._anchor, {"anchor": "right", "speed": 50}),
                (self.lerp_rotation_to, {"target": 270, "speed": 10}),
            ],
            58: [
                (self._center, {"friction": 0.92, "accel": 0.92}),
                (self._rotate, {"rot_speed": -6}),
            ],
            59: [
                (self._center, {"friction": 0.92, "accel": 0.92}),
                (self.lerp_rotation_to_zero, {}),
            ],
            60: [
                (self._center, {"friction": 0.92, "accel": 0.92}),
                (self.lerp_rotation_to_zero, {}),
            ],
            61: [
                (self._anchor, {"anchor": "left", "speed": 50}),
                (self.lerp_rotation_to, {"target": 90, "speed": 10}),
            ],
            63: [
                (
                    self._orbit,
                    {
                        "radius": 100,
                        "orbit_speed": 1,
                        "friction": 0.90,
                        "accel": 0.50,
                        "reverse": True,
                    },
                ),
                (self._rotate, {"rot_speed": 4}),
            ],
            64: [
                (self._center, {"friction": 0.92, "accel": 0.92}),
                (self.lerp_rotation_to_zero, {}),
            ],
            65: [
                (self._center, {"friction": 0.92, "accel": 0.92}),
                (self.lerp_rotation_to_zero, {}),
            ],
            66: [
                (self._center, {"friction": 0.92, "accel": 0.92}),
                (self._rotate, {"rot_speed": 8}),
            ],
            67: [
                (self._center, {"friction": 0.92, "accel": 0.92}),
                (self.lerp_rotation_to_zero, {"speed": 10}),
            ],
        }

        self.wander_target_x = self.rect.centerx
        self.wander_target_y = self.rect.centery
        self.wander_cd = 2000
        self.wander_timer = 0

        # attacks
        self.bullet_rot_timer = 0
        self.burst_atk_timer = 0
        self.burst_atk_index = 0
        self.block_timer = 0
        self.rainfall_timer = 0
        self.bullet_enclosure_timer = 0

        self.phase_attacks = {
            1: [
                (
                    self._bullet_rotation,
                    {"bullet_arms": 8, "speed": 8, "rad": 6, "bullet_cd": self.EIGHTH},
                ),
            ],
            2: [
                (
                    self._bullet_rainfall,
                    {
                        "cd": self.QUARTER,
                        "bullet_count": 6,
                        "rad": 8,
                        "speed": (5, 6, 7, 8, 9, 10),
                        "reverse": False,
                    },
                ),
                (
                    self._burst_atk,
                    {
                        "cd": self.QUARTER,
                        "bullet_count": (5, 7, 10),
                        "rad": 8,
                        "ring_speed": 8,
                    },
                ),
            ],
            3: [  # BUILDUP 1
                (
                    self._block,
                    {
                        "cd": self.EIGHTH,
                        "speed": (16, 20),
                        "box_count": 1,
                    },
                ),
                (
                    self._burst_atk,
                    {
                        "cd": self.EIGHTH,
                        "bullet_count": (12, 6, 6, 12, 6, 6, 6, 6),
                        "rad": 12,
                        "ring_speed": 12,
                    },
                ),
            ],
            4: [  # BUILDUP 2
                (
                    self._block,
                    {
                        "cd": self.EIGHTH,
                        "speed": (16, 20),
                        "box_count": 2,
                    },
                ),
                (
                    self._burst_atk,
                    {
                        "cd": self.EIGHTH,
                        "bullet_count": (12, 6, 6, 12, 6, 6, 6, 6),
                        "rad": 12,
                        "ring_speed": 12,
                    },
                ),
            ],
            5: [  # BUILDUP 3
                (
                    self._block,
                    {
                        "cd": self.EIGHTH,
                        "speed": (20, 24),
                        "box_count": 2,
                    },
                ),
                (
                    self._burst_atk,
                    {
                        "cd": self.SIXTEENTH,
                        "bullet_count": (12, 18),
                        "rad": 12,
                        "ring_speed": 18,
                    },
                ),
            ],
            6: [  # PREDROP 1
                (
                    self._burst_atk,
                    {
                        "cd": self.THIRD,
                        "bullet_count": (6, 12, 18),
                        "rad": 12,
                        "ring_speed": 18,
                    },
                )
            ],
            7: [  # PREDROP 2
                (
                    self._burst_atk,
                    {
                        "cd": self.QUARTER,
                        "bullet_count": 10,
                        "rad": 8,
                        "ring_speed": 12,
                    },
                )
            ],
            8: [  # RISE 1
                (
                    self._bullet_rotation,
                    {
                        "bullet_arms": 4,
                        "speed": 32,
                        "rad": 12,
                        "bullet_cd": self.SIXTEENTH,
                    },
                )
            ],
            9: [  # BREAK
                (
                    self._burst_atk,
                    {"cd": self.HALF, "bullet_count": 6, "rad": 12, "ring_speed": 12},
                )
            ],
            10: [  # RISE 2
                (
                    self._bullet_rotation,
                    {
                        "bullet_arms": 6,
                        "speed": 32,
                        "rad": 12,
                        "bullet_cd": self.SIXTEENTH,
                    },
                )
            ],
            11: [  # BREAK
                (
                    self._burst_atk,
                    {"cd": self.HALF, "bullet_count": 10, "rad": 12, "ring_speed": 12},
                )
            ],
            12: [  # RISE 3
                (
                    self._bullet_rotation,
                    {
                        "bullet_arms": 8,
                        "speed": 32,
                        "rad": 12,
                        "bullet_cd": self.SIXTEENTH,
                    },
                )
            ],
            13: [  # PREDROP
                (
                    self._burst_atk,
                    {
                        "cd": self.EIGHTH,
                        "bullet_count": (10, 14),
                        "rad": 12,
                        "ring_speed": 18,
                    },
                )
            ],
            14: [  # PREDROP
                (
                    self._burst_atk,
                    {"cd": self.QUARTER, "bullet_count": 8, "rad": 12, "ring_speed": 9},
                )
            ],
            15: [],
            16: [  # DROP
                (
                    self._burst_atk,
                    {
                        "cd": self.EIGHTH,
                        "bullet_count": (32, 14, 14, 14),
                        "rad": 6,
                        "ring_speed": 18,
                    },
                )
            ],
            17: [  # BREAK
                (
                    self._bullet_rainfall,
                    {
                        "cd": self.EIGHTH,
                        "bullet_count": 16,
                        "rad": 8,
                        "speed": (8, 12, 16),
                        "reverse": False,
                    },
                )
            ],
            18: [  # DROP
                (self._block, {"cd": self.QUARTER, "speed": (15, 25), "box_count": 3}),
            ],
            19: [  # DROP
                (
                    self._bullet_enclosure,
                    {
                        "bullet_arms": 12,
                        "speed": 12,
                        "rad": 12,
                        "bullet_cd": self.EIGHTH,
                    },
                )
            ],
            20: [
                (
                    self._burst_atk,
                    {
                        "cd": self.THIRD,
                        "bullet_count": (8, 16, 8),
                        "rad": 8,
                        "ring_speed": 12,
                    },
                )
            ],
            21: [],
            22: [  # DROP
                (
                    self._burst_atk,
                    {
                        "cd": self.EIGHTH,
                        "bullet_count": (32, 14, 14, 14),
                        "rad": 6,
                        "ring_speed": 18,
                    },
                )
            ],
            23: [  # BREAK
                (
                    self._bullet_rainfall,
                    {
                        "cd": self.QUARTER,
                        "bullet_count": 16,
                        "rad": 8,
                        "speed": (8, 12, 16),
                        "reverse": False,
                    },
                )
            ],
            24: [  # BREAK
                (
                    self._burst_atk,
                    {
                        "cd": self.HALF,
                        "bullet_count": (8, 16),
                        "rad": 8,
                        "ring_speed": 12,
                    },
                )
            ],
            25: [
                (
                    self._burst_atk,
                    {
                        "cd": self.HALF,
                        "bullet_count": 8,
                        "rad": 8,
                        "ring_speed": 12,
                    },
                )
            ],
            26: [
                (
                    self._bullet_rotation,
                    {
                        "bullet_arms": 8,
                        "speed": 32,
                        "rad": 6,
                        "bullet_cd": self.SIXTEENTH,
                    },
                )
            ],
            27: [
                (
                    self._burst_atk,
                    {
                        "cd": self.HALF,
                        "bullet_count": 8,
                        "rad": 8,
                        "ring_speed": 12,
                    },
                )
            ],
            28: [  # DROP
                (
                    self._burst_atk,
                    {
                        "cd": self.EIGHTH,
                        "bullet_count": (38, 18, 18, 18),
                        "rad": 6,
                        "ring_speed": 18,
                    },
                ),
                (
                    self._bullet_rainfall,
                    {
                        "cd": self.QUARTER,
                        "bullet_count": 8,
                        "rad": 8,
                        "speed": (12, 16, 19),
                        "reverse": True,
                    },
                ),
            ],
            29: [  # BREAK
                (
                    self._bullet_rainfall,
                    {
                        "cd": self.EIGHTH,
                        "bullet_count": 16,
                        "rad": 8,
                        "speed": (8, 12, 16),
                        "reverse": True,
                    },
                )
            ],
            30: [  # DROP
                (self._block, {"cd": self.QUARTER, "speed": (15, 25), "box_count": 3}),
            ],
            31: [  # DROP
                (
                    self._bullet_enclosure,
                    {
                        "bullet_arms": 12,
                        "speed": 12,
                        "rad": 12,
                        "bullet_cd": self.EIGHTH,
                    },
                )
            ],
            32: [
                (
                    self._burst_atk,
                    {
                        "cd": self.THIRD,
                        "bullet_count": (8, 16, 8),
                        "rad": 8,
                        "ring_speed": 12,
                    },
                )
            ],
            33: [],
            34: [  # DROP
                (
                    self._burst_atk,
                    {
                        "cd": self.EIGHTH,
                        "bullet_count": (38, 18, 18, 18),
                        "rad": 6,
                        "ring_speed": 18,
                    },
                ),
                (
                    self._bullet_rainfall,
                    {
                        "cd": self.QUARTER,
                        "bullet_count": 8,
                        "rad": 8,
                        "speed": (12, 16, 19),
                        "reverse": False,
                    },
                ),
            ],
            35: [  # BREAK
                (
                    self._bullet_rainfall,
                    {
                        "cd": self.QUARTER,
                        "bullet_count": 16,
                        "rad": 8,
                        "speed": (8, 12, 16),
                        "reverse": True,
                    },
                )
            ],
            36: [
                (
                    self._bullet_rotation,
                    {
                        "bullet_arms": 8,
                        "speed": 8,
                        "rad": 12,
                        "bullet_cd": self.QUARTER,
                    },
                )
            ],
            37: [
                (
                    self._burst_atk,
                    {
                        "cd": self.HALF,
                        "bullet_count": (8, 14),
                        "rad": 12,
                        "ring_speed": 18,
                    },
                ),
            ],
            38: [
                (
                    self._burst_atk,
                    {
                        "cd": self.SIXTEENTH,
                        "bullet_count": (4, 6, 8, 10),
                        "rad": 8,
                        "ring_speed": 18,
                    },
                ),
            ],
            39: [
                (
                    self._bullet_rotation,
                    {"bullet_arms": 8, "speed": 8, "rad": 6, "bullet_cd": self.EIGHTH},
                )
            ],
            40: [  # BUILDUP 1
                (
                    self._block,
                    {
                        "cd": self.EIGHTH,
                        "speed": (16, 20),
                        "box_count": 1,
                    },
                ),
                (
                    self._burst_atk,
                    {
                        "cd": self.EIGHTH,
                        "bullet_count": (12, 6, 6, 12, 6, 6, 6, 6),
                        "rad": 12,
                        "ring_speed": 12,
                    },
                ),
            ],
            41: [  # BUILDUP 2
                (
                    self._block,
                    {
                        "cd": self.EIGHTH,
                        "speed": (16, 20),
                        "box_count": 2,
                    },
                ),
                (
                    self._burst_atk,
                    {
                        "cd": self.EIGHTH,
                        "bullet_count": (12, 6, 6, 12, 6, 6, 6, 6),
                        "rad": 12,
                        "ring_speed": 12,
                    },
                ),
            ],
            42: [  # BUILDUP 3
                (
                    self._block,
                    {
                        "cd": self.EIGHTH,
                        "speed": (20, 24),
                        "box_count": 2,
                    },
                ),
                (
                    self._burst_atk,
                    {
                        "cd": self.SIXTEENTH,
                        "bullet_count": (12, 18),
                        "rad": 12,
                        "ring_speed": 18,
                    },
                ),
            ],
            43: [  # PREDROP 1
                (
                    self._burst_atk,
                    {
                        "cd": self.THIRD,
                        "bullet_count": (6, 12, 18),
                        "rad": 12,
                        "ring_speed": 18,
                    },
                )
            ],
            44: [  # PREDROP 2
                (
                    self._burst_atk,
                    {
                        "cd": self.QUARTER,
                        "bullet_count": 10,
                        "rad": 8,
                        "ring_speed": 12,
                    },
                )
            ],
            45: [  # build 1
                (
                    self._bullet_rotation,
                    {
                        "bullet_arms": 6,
                        "speed": 12,
                        "rad": 8,
                        "bullet_cd": self.SIXTEENTH,
                    },
                )
            ],
            46: [  # build 2
                (
                    self._bullet_rotation,
                    {
                        "bullet_arms": 6,
                        "speed": 12,
                        "rad": 8,
                        "bullet_cd": self.SIXTEENTH,
                    },
                ),
                (
                    self._burst_atk,
                    {
                        "cd": self.QUARTER,
                        "bullet_count": 10,
                        "rad": 8,
                        "ring_speed": 16,
                    },
                ),
            ],
            47: [  # build 3
                (
                    self._bullet_rotation,
                    {
                        "bullet_arms": 12,
                        "speed": 12,
                        "rad": 8,
                        "bullet_cd": self.SIXTEENTH,
                    },
                ),
                (
                    self._burst_atk,
                    {
                        "cd": self.EIGHTH,
                        "bullet_count": 10,
                        "rad": 8,
                        "ring_speed": 16,
                    },
                ),
            ],
            48: [  # predrop
                (
                    self._bullet_enclosure,
                    {
                        "bullet_arms": 18,
                        "speed": 10,
                        "rad": 12,
                        "bullet_cd": self.EIGHTH,
                    },
                ),
                (
                    self._burst_atk,
                    {
                        "cd": self.QUARTER,
                        "bullet_count": (12, 8),
                        "rad": 10,
                        "ring_speed": 8,
                    },
                ),
            ],
            49: [
                (
                    self._burst_atk,
                    {
                        "cd": self.EIGHTH,
                        "bullet_count": (32, 14),
                        "rad": 6,
                        "ring_speed": 18,
                    },
                ),
                (
                    self._bullet_enclosure,
                    {
                        "bullet_arms": 18,
                        "speed": 14,
                        "rad": 8,
                        "bullet_cd": self.QUARTER,
                    },
                ),
            ],
            50: [],
            51: [
                (
                    self._bullet_rotation,
                    {
                        "bullet_arms": 12,
                        "speed": 14,
                        "rad": 8,
                        "bullet_cd": self.SIXTEENTH,
                    },
                ),
            ],
            52: [
                (
                    self._burst_atk,
                    {
                        "cd": self.EIGHTH,
                        "bullet_count": (32, 14),
                        "rad": 6,
                        "ring_speed": 18,
                    },
                ),
                (
                    self._bullet_enclosure,
                    {
                        "bullet_arms": 18,
                        "speed": 14,
                        "rad": 8,
                        "bullet_cd": self.QUARTER,
                    },
                ),
            ],
            53: [
                (
                    self._burst_atk,
                    {
                        "cd": self.THIRD,
                        "bullet_count": (8, 16, 8),
                        "rad": 8,
                        "ring_speed": 12,
                    },
                )
            ],
            54: [],
            55: [  # DROP
                (
                    self._burst_atk,
                    {
                        "cd": self.EIGHTH,
                        "bullet_count": (38, 18, 18, 18),
                        "rad": 6,
                        "ring_speed": 18,
                    },
                ),
                (
                    self._bullet_rainfall,
                    {
                        "cd": self.QUARTER,
                        "bullet_count": 8,
                        "rad": 8,
                        "speed": (12, 16, 19),
                        "reverse": True,
                    },
                ),
            ],
            56: [  # BREAK
                (
                    self._bullet_rainfall,
                    {
                        "cd": self.EIGHTH,
                        "bullet_count": 16,
                        "rad": 8,
                        "speed": (8, 12, 16),
                        "reverse": True,
                    },
                )
            ],
            57: [  # DROP
                (self._block, {"cd": self.QUARTER, "speed": (15, 25), "box_count": 3}),
            ],
            58: [  # DROP
                (
                    self._bullet_enclosure,
                    {
                        "bullet_arms": 12,
                        "speed": 12,
                        "rad": 12,
                        "bullet_cd": self.EIGHTH,
                    },
                )
            ],
            59: [
                (
                    self._burst_atk,
                    {
                        "cd": self.THIRD,
                        "bullet_count": (8, 16, 8),
                        "rad": 8,
                        "ring_speed": 12,
                    },
                )
            ],
            60: [],
            61: [  # DROP
                (
                    self._burst_atk,
                    {
                        "cd": self.EIGHTH,
                        "bullet_count": (38, 18, 18, 18),
                        "rad": 6,
                        "ring_speed": 18,
                    },
                ),
                (
                    self._bullet_rainfall,
                    {
                        "cd": self.QUARTER,
                        "bullet_count": 8,
                        "rad": 8,
                        "speed": (12, 16, 19),
                        "reverse": False,
                    },
                ),
            ],
            62: [  # BREAK
                (
                    self._bullet_rainfall,
                    {
                        "cd": self.QUARTER,
                        "bullet_count": 16,
                        "rad": 8,
                        "speed": (8, 12, 16),
                        "reverse": True,
                    },
                )
            ],
            63: [
                (
                    self._bullet_rotation,
                    {
                        "bullet_arms": 8,
                        "speed": 8,
                        "rad": 12,
                        "bullet_cd": self.QUARTER,
                    },
                )
            ],
            64: [
                (
                    self._burst_atk,
                    {
                        "cd": self.HALF,
                        "bullet_count": (8, 14),
                        "rad": 12,
                        "ring_speed": 18,
                    },
                ),
            ],
            65: [
                (
                    self._burst_atk,
                    {
                        "cd": self.SIXTEENTH,
                        "bullet_count": (4, 6, 8, 10),
                        "rad": 8,
                        "ring_speed": 18,
                    },
                ),
            ],
            66: [
                (
                    self._bullet_rotation,
                    {
                        "bullet_arms": 8,
                        "speed": 12,
                        "rad": 12,
                        "bullet_cd": self.SIXTEENTH,
                    },
                )
            ],
        }

        # states
        self.music_started = False

    # ==================
    # CORE
    # ==================

    def update(self, tar_x, tar_y, borders):
        self.tar_x = tar_x
        self.tar_y = tar_y
        self.borders = borders

        self._update_phase()

        self._movement()
        self._attack()

    def _update_phase(self):
        if not self.music_started:
            return

        if not self.alive():
            return

        pos = pygame.mixer.music.get_pos()
        for phase, (start, end) in self.SONG_PHASES.items():
            if start <= pos < end:
                self.phase = phase
                break

        last_phase = max(self.SONG_PHASES)
        end_time = self.SONG_PHASES[last_phase][1]
        buffer = 100
        if pos >= end_time - buffer:
            self._explode()

    def _rotate(self, rot_speed):
        self.update_rotation(self.rotation + rot_speed)

    # ==================
    # MOVEMENT ROUTING
    # ==================

    def _movement(self):
        dist = math.hypot(
            self.tar_x - self.rect.centerx, self.tar_y - self.rect.centery
        )

        for func, params in self.phase_movements.get(self.phase, []):
            func(**params)

    # ==================
    # ATTACK ROUTING
    # ==================

    def _attack(self):
        dist = math.hypot(
            self.tar_x - self.rect.centerx, self.tar_y - self.rect.centery
        )

        for func, params in self.phase_attacks.get(self.phase, []):
            func(**params)

    # ==================
    # MOVEMENTS
    # ==================

    def _chase(self, friction, accel):
        angle = math.atan2(
            self.tar_y - self.rect.centery, self.tar_x - self.rect.centerx
        )

        self.dx += math.cos(angle) * accel
        self.dy += math.sin(angle) * accel
        self.dx *= friction
        self.dy *= friction

        self.rect.x += int(self.dx)
        self.rect.y += int(self.dy)

    def _wander(self, friction, accel):
        now = pygame.time.get_ticks()

        dist = math.hypot(
            self.wander_target_x - self.rect.centerx,
            self.wander_target_y - self.rect.centery,
        )
        if dist < 20 or now - self.wander_timer > self.wander_cd:
            self.wander_timer = now

            border_sprites = self.borders.sprites()

            left_border = border_sprites[0]
            right_border = border_sprites[1]
            top_border = border_sprites[2]
            bottom_border = border_sprites[3]

            self.wander_target_x = random.randint(
                left_border.rect.right + 50, right_border.rect.left - 50
            )
            self.wander_target_y = random.randint(
                top_border.rect.bottom + 50, bottom_border.rect.top - 50
            )

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

    def _center(self, friction, accel):
        border_sprites = self.borders.sprites()

        left_border = border_sprites[0]
        right_border = border_sprites[1]
        top_border = border_sprites[2]
        bottom_border = border_sprites[3]

        center_x = (left_border.rect.right + right_border.rect.left) // 2
        center_y = (top_border.rect.bottom + bottom_border.rect.top) // 2

        angle = math.atan2(
            center_y - self.rect.centery,
            center_x - self.rect.centerx,
        )
        self.dx += math.cos(angle) * accel
        self.dy += math.sin(angle) * accel
        self.dx *= friction
        self.dy *= friction

        self.rect.x += int(self.dx)
        self.rect.y += int(self.dy)

    def _anchor(self, anchor, speed):
        border_sprites = self.borders.sprites()

        left_border = border_sprites[0]
        right_border = border_sprites[1]
        top_border = border_sprites[2]
        bottom_border = border_sprites[3]

        match anchor:
            case "top":
                self.anchor_target_x, self.anchor_target_y = top_border.rect.midbottom
            case "bot":
                self.anchor_target_x, self.anchor_target_y = bottom_border.rect.midtop
            case "left":
                self.anchor_target_x, self.anchor_target_y = left_border.rect.midright
            case "right":
                self.anchor_target_x, self.anchor_target_y = right_border.rect.midleft

        dist = math.hypot(
            self.anchor_target_x - self.rect.centerx,
            self.anchor_target_y - self.rect.centery,
        )

        if dist <= speed:
            self.rect.centerx = self.anchor_target_x
            self.rect.centery = self.anchor_target_y
            return

        angle = math.atan2(
            self.anchor_target_y - self.rect.centery,
            self.anchor_target_x - self.rect.centerx,
        )
        self.rect.x += int(math.cos(angle) * speed)
        self.rect.y += int(math.sin(angle) * speed)

    def _orbit(self, radius, orbit_speed, friction, accel, reverse=False):
        border_sprites = self.borders.sprites()
        center_x = (border_sprites[0].rect.right + border_sprites[1].rect.left) // 2
        center_y = (border_sprites[2].rect.bottom + border_sprites[3].rect.top) // 2

        direction = -1 if reverse else 1
        self.orbit_angle = (self.orbit_angle + orbit_speed * direction) % 360

        angle_rad = math.radians(self.orbit_angle)
        target_x = center_x + int(math.cos(angle_rad) * radius)
        target_y = center_y + int(math.sin(angle_rad) * radius)

        angle_to_target = math.atan2(
            target_y - self.rect.centery,
            target_x - self.rect.centerx,
        )
        self.dx += math.cos(angle_to_target) * accel
        self.dy += math.sin(angle_to_target) * accel
        self.dx *= friction
        self.dy *= friction

        self.rect.x += int(self.dx)
        self.rect.y += int(self.dy)

    def _move_out(self, side, friction, accel):
        border_sprites = self.borders.sprites()

        left_border = border_sprites[0]
        right_border = border_sprites[1]
        top_border = border_sprites[2]
        bottom_border = border_sprites[3]

        match side:
            case "top":
                tar_x = self.rect.centerx
                tar_y = top_border.rect.top - (self.rect.height * 2)
            case "bot":
                tar_x = self.rect.centerx
                tar_y = bottom_border.rect.bottom + (self.rect.height * 2)
            case "left":
                tar_x = left_border.rect.left - (self.rect.width * 2)
                tar_y = self.rect.centery
            case "right":
                tar_x = right_border.rect.right + (self.rect.width * 2)
                tar_y = self.rect.centery

        angle = math.atan2(tar_y - self.rect.centery, tar_x - self.rect.centerx)

        self.dx += math.cos(angle) * accel
        self.dy += math.sin(angle) * accel
        self.dx *= friction
        self.dy *= friction

        self.rect.x += int(self.dx)
        self.rect.y += int(self.dy)

    # ==================
    # ATTACKS
    # ==================

    def _bullet_rotation(self, bullet_arms, speed, rad, bullet_cd):
        now = pygame.time.get_ticks()
        if now - self.bullet_rot_timer < bullet_cd:
            return
        self.bullet_rot_timer = now

        for i in range(bullet_arms):
            arm_angle_deg = self.rotation + (i * (360 / bullet_arms))
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

    def _bullet_enclosure(self, bullet_arms, speed, rad, bullet_cd):
        now = pygame.time.get_ticks()
        if now - self.bullet_enclosure_timer < bullet_cd:
            return
        self.bullet_enclosure_timer = now

        border_sprites = self.borders.sprites()
        left_border = border_sprites[0]
        right_border = border_sprites[1]
        top_border = border_sprites[2]
        bottom_border = border_sprites[3]

        dist_left = self.rect.centerx - left_border.rect.right
        dist_right = right_border.rect.left - self.rect.centerx
        dist_top = self.rect.centery - top_border.rect.bottom
        dist_bot = bottom_border.rect.top - self.rect.centery

        radius = max(dist_left, dist_right, dist_top, dist_bot)

        for i in range(bullet_arms):
            arm_angle_deg = self.rotation + (i * (360 / bullet_arms))
            arm_angle_rad = math.radians(arm_angle_deg)

            spawn_x = self.rect.centerx + math.cos(arm_angle_rad) * radius
            spawn_y = self.rect.centery + math.sin(arm_angle_rad) * radius

            tar_x = self.rect.centerx
            tar_y = self.rect.centery

            bullet = Bullet(
                radius=rad,
                x_cor=spawn_x,
                y_cor=spawn_y,
                tar_x=tar_x,
                tar_y=tar_y,
                color=self.color,
                damage=self.damage,
                speed=speed,
            )
            self.projectile_grp.add(bullet)

    def _burst_atk(
        self,
        cd,
        bullet_count,
        rad,
        ring_speed,
    ):
        now = pygame.time.get_ticks()
        if now - self.burst_atk_timer < cd:
            return
        self.burst_atk_timer = now

        counts = bullet_count if isinstance(bullet_count, tuple) else (bullet_count,)
        count = counts[self.burst_atk_index % len(counts)]
        self._bullet_ring(count, rad, ring_speed)
        self.burst_atk_index += 1

    def _bullet_ring(self, bullet_count, rad, ring_speed):
        angle_step = 360 / bullet_count

        for i in range(bullet_count):
            angle = math.radians(angle_step * i)
            tar_x_off = self.rect.centerx + math.cos(angle) * 100
            tar_y_off = self.rect.centery + math.sin(angle) * 100
            self.projectile_grp.add(
                Bullet(
                    rad,
                    self.rect.centerx,
                    self.rect.centery,
                    tar_x_off,
                    tar_y_off,
                    self.color,
                    self.damage,
                    speed=ring_speed,
                )
            )

    def _block(self, cd, speed, box_count):
        now = pygame.time.get_ticks()
        if now - self.block_timer < cd:
            return
        self.block_timer = now

        border_sprites = self.borders.sprites()
        left_border = border_sprites[0]
        right_border = border_sprites[1]
        top_border = border_sprites[2]
        bottom_border = border_sprites[3]

        padding = 20

        min_x = left_border.rect.right + padding
        max_x = right_border.rect.left - padding
        min_y = top_border.rect.bottom + padding
        max_y = bottom_border.rect.top - padding

        orientation = random.choice(["horizontal", "vertical"])
        size = 40

        for i in range(box_count):
            if orientation == "horizontal":
                direction = random.choice(["top_to_bottom", "bottom_to_top"])
                x = random.randint(min_x, max_x)
                if direction == "top_to_bottom":
                    y = min_y
                    dy, dx = random.choice(speed), 0
                else:
                    y = max_y
                    dy, dx = -random.choice(speed), 0
                block = Block(self.obs_grp, x, y, size, self.color, self.damage)

            else:
                direction = random.choice(["left_to_right", "right_to_left"])
                y = random.randint(min_y, max_y)
                if direction == "left_to_right":
                    x = min_x
                    dx, dy = random.choice(speed), 0
                else:
                    x = max_x
                    dx, dy = -random.choice(speed), 0
                block = Block(self.obs_grp, x, y, size, self.color, self.damage)

            block.dx = dx
            block.dy = dy
            self.obs_grp.add(block)

    def _bullet_rainfall(self, cd, bullet_count, rad, speed, reverse):
        now = pygame.time.get_ticks()
        if now - self.rainfall_timer < cd:
            return
        self.rainfall_timer = now

        border_sprites = self.borders.sprites()
        top_border = border_sprites[2]
        bottom_border = border_sprites[3]
        left_border = border_sprites[0]
        right_border = border_sprites[1]

        padding = 20
        min_x = left_border.rect.right + padding
        max_x = right_border.rect.left - padding

        if reverse:
            start_y = bottom_border.rect.top - padding
            end_y = top_border.rect.top
        else:
            start_y = top_border.rect.bottom + padding
            end_y = bottom_border.rect.bottom

        for i in range(bullet_count):
            x = random.randint(min_x, max_x)
            self.projectile_grp.add(
                Bullet(
                    rad,
                    x,
                    start_y,
                    x,
                    end_y,
                    self.color,
                    self.damage,
                    random.choice(speed),
                )
            )

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

    def draw_duration_bar(self, win_wd, screen):
        bar_wd = 400
        bar_ht = 20
        gap = 5

        bar_rect = pygame.Rect(0, 0, bar_wd, bar_ht)
        bar_rect.midtop = (win_wd // 2, 40)

        last_phase = max(self.SONG_PHASES)
        end_time = self.SONG_PHASES[last_phase][1]
        pos = pygame.mixer.music.get_pos()
        progress = min(pos / end_time, 1.0)

        fill_wd = int(progress * bar_wd)
        pygame.draw.rect(screen, RED, (bar_rect.x, bar_rect.y, fill_wd, bar_ht))
        pygame.draw.rect(screen, WHITE, bar_rect, 2)

        font = pygame.font.Font(REGULAR, 40)
        name_img = font.render("Omen", True, WHITE)
        name_img.set_alpha(128)
        name_rect = name_img.get_rect(midtop=(bar_rect.centerx, bar_rect.bottom + gap))
        screen.blit(name_img, name_rect)
