import math
import random

import pygame

from const.COLORS import BLACK, BLUE, GREEN, ORANGE, PLAT, RED, VIOLET, WHITE, YELLOW
from const.FONTS import REGULAR
from src.Enemies import Sniper
from src.Entities import GlassEntity, StarEntity
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

        self.dx, self.dy = 0, 0
        self.movement_params = {
            1: {},
            2: {
                "friction": 0.92,
                "accel": 0.50,
            },
            3: {
                "friction": 0.95,
                "accel": 0.70,
            },
            4: {
                "friction": 0.97,
                "accel": 3.00,
            },
            5: {
                "friction": 0.90,
                "accel": 0.50,
            },
            6: {
                "friction": 0.90,
                "accel": 0.50,
            },
            7: {
                "friction": 0.92,
                "accel": 0.60,
            },
            8: {
                "friction": 0.92,
                "accel": 0.90,
            },
            9: {
                "friction": 0.97,
                "accel": 3.00,
            },
            10: {
                "friction": 0.95,
                "accel": 0.70,
            },
            11: {
                "friction": 0.95,
                "accel": 0.80,
            },
            12: {
                "friction": 0.90,
                "accel": 0.50,
            },
            13: {
                "friction": 0.92,
                "accel": 0.90,
            },
            14: {
                "friction": 0.97,
                "accel": 3.00,
            },
            15: {},
        }  # friction and accel

        # atk timers
        self.burst_atk_timer = 0
        self.burst_atk_params = {
            1: {},
            2: {
                "cd": 1520,
                "bul_count": 6,
                "rad": 8,
                "ring_spd": (3, 5),
            },
            3: {
                "cd": 760,
                "bul_count": 6,
                "rad": 6,
                "ring_spd": (2, 6),
            },
            4: {},
            5: {},
            6: {},
            7: {
                "cd": 760,
                "bul_count": 6,
                "rad": 8,
                "ring_spd": (3, 5),
            },
            8: {
                "cd": 380,
                "bul_count": 8,
                "rad": 6,
                "ring_spd": (3, 6),
            },
            9: {},
            10: {
                "cd": 760,
                "bul_count": 8,
                "rad": 6,
                "ring_spd": (3, 6),
            },
            11: {},
            12: {},
            13: {
                "cd": 760,
                "bul_count": 8,
                "rad": 8,
                "ring_spd": (4, 9),
            },
            14: {},
            15: {},
        }

        self.spawn_enemy_timer = 0
        self.spawn_sniper_params = {
            1: {},
            2: {},
            3: {},
            4: {},
            5: {},
            6: {},
            7: {
                "cd": 1520,
            },
            8: {
                "cd": 380,
            },
            9: {},
            10: {
                "cd": 760,
            },
            11: {
                "cd": 760,
            },
            12: {},
            13: {},
            14: {},
            15: {},
        }  # spawn_sniper_cd

        self.rainfall_timer = 0
        self.rainfall_params = {
            1: {},
            2: {},
            3: {},
            4: {},
            5: {
                "cd": 760,
                "bul_count": 6,
                "rad": 8,
                "speed": (5, 6, 7, 8, 9, 10),
                "reverse": False,
            },
            6: {
                "cd": 760,
                "bul_count": 6,
                "rad": 8,
                "speed": (5, 6, 7, 8, 9, 10),
                "reverse": True,
            },
            7: {},
            8: {},
            9: {},
            10: {},
            11: {},
            12: {},
            13: {
                "cd": 380,
                "bul_count": 6,
                "rad": 8,
                "speed": (5, 6, 7, 8, 9, 10),
                "reverse": False,
            },
            14: {},
            15: {},
        }

        self.bullet_rot_timer = 0
        self.rot_switch_timer = pygame.time.get_ticks()
        self.angle = 0
        self.rot_dir = 1
        self.rot_switch_cd = 5000
        self.bullet_rot_params = {
            1: {},
            2: {},
            3: {},
            4: {
                "arms": 8,
                "speed": 10,
                "rad": 10,
                "cd": 95,
                "rot_spd": 2,
            },
            5: {
                "arms": 6,
                "speed": 5,
                "rad": 10,
                "cd": 380,
                "rot_spd": 2,
            },
            6: {
                "arms": 6,
                "speed": 5,
                "rad": 10,
                "cd": 380,
                "rot_spd": 2,
            },
            7: {},
            8: {},
            9: {
                "arms": 8,
                "speed": 10,
                "rad": 10,
                "cd": 95,
                "rot_spd": 2,
            },
            10: {},
            11: {},
            12: {
                "arms": 8,
                "speed": 10,
                "rad": 10,
                "cd": 380,
                "rot_spd": 4,
            },
            13: {},
            14: {
                "arms": 8,
                "speed": 10,
                "rad": 10,
                "cd": 95,
                "rot_spd": 2,
            },
            15: {},
        }

        self.block_timer = 0
        self.block_params = {
            1: {},
            2: {},
            3: {},
            4: {},
            5: {},
            6: {},
            7: {"cd": 760, "speed": (5, 10, 15, 20), "box_count": 1},
            8: {},
            9: {},
            10: {"cd": 760, "speed": (5, 10, 15, 20), "box_count": 3},
            11: {"cd": 380, "speed": (5, 10, 15, 20), "box_count": 3},
            12: {"cd": 380, "speed": (5, 10, 15, 20), "box_count": 3},
            13: {},
            14: {},
            15: {},
        }

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
        self._update_rotation(self.bullet_rot_params[self.phase])

        self._movement(tar_x, tar_y, borders)
        self._attack(tar_x, tar_y, borders)

    def _update_rotation(self, params):
        if not params:
            return

        now = pygame.time.get_ticks()
        self.angle = (self.angle + params["rot_spd"] * self.rot_dir) % 360

        if now - self.rot_switch_timer > self.rot_switch_cd:
            self.rot_switch_timer = now
            self.rot_dir *= -1

    def _update_phase(self):
        pos = pygame.mixer.music.get_pos()
        print(pos)
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

    def _movement(self, tar_x, tar_y, borders):
        dist = math.hypot(tar_x - self.rect.centerx, tar_y - self.rect.centery)

        mov_params = self.movement_params[self.phase]

        match self.phase:
            case 1:
                pass
            case 2:
                self._chase(
                    tar_x,
                    tar_y,
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
            case 4:  # short break
                self._center(borders, mov_params["friction"], mov_params["accel"])
            case 5:
                self._center(borders, mov_params["friction"], mov_params["accel"])
            case 6:
                self._center(borders, mov_params["friction"], mov_params["accel"])
            case 7:
                self._wander(borders, mov_params["friction"], mov_params["accel"])
            case 8:
                self._wander(borders, mov_params["friction"], mov_params["accel"])
            case 9:
                self._center(borders, mov_params["friction"], mov_params["accel"])
            case 10:
                self._chase(
                    tar_x,
                    tar_y,
                    mov_params["friction"],
                    mov_params["accel"],
                )
            case 11:
                self._chase(
                    tar_x,
                    tar_y,
                    mov_params["friction"],
                    mov_params["accel"],
                )
            case 12:
                self._center(borders, mov_params["friction"], mov_params["accel"])
            case 13:
                self._wander(borders, mov_params["friction"], mov_params["accel"])
            case 14:
                self._center(borders, mov_params["friction"], mov_params["accel"])

    # ==================
    # ATTACK ROUTING
    # ==================

    def _attack(self, tar_x, tar_y, borders):
        dist = math.hypot(tar_x - self.rect.centerx, tar_y - self.rect.centery)

        burst_atk_params = self.burst_atk_params[self.phase]
        rain_params = self.rainfall_params[self.phase]
        bullet_rot_params = self.bullet_rot_params[self.phase]
        sn_params = self.spawn_sniper_params[self.phase]
        blk_params = self.block_params[self.phase]

        match self.phase:
            case 1:
                pass
            case 2:
                self._ranged_atk(tar_x, tar_y)
                self._burst_atk(
                    burst_atk_params["cd"],
                    burst_atk_params["bul_count"],
                    burst_atk_params["rad"],
                    burst_atk_params["ring_spd"],
                )
            case 3:
                self._ranged_atk(tar_x, tar_y)
                self._burst_atk(
                    burst_atk_params["cd"],
                    burst_atk_params["bul_count"],
                    burst_atk_params["rad"],
                    burst_atk_params["ring_spd"],
                )
            case 4:
                self._bullet_rotation(
                    bullet_rot_params["arms"],
                    bullet_rot_params["speed"],
                    bullet_rot_params["rad"],
                    bullet_rot_params["cd"],
                )
            case 5:
                self._bullet_rainfall(
                    borders,
                    rain_params["cd"],
                    rain_params["bul_count"],
                    rain_params["rad"],
                    rain_params["speed"],
                    rain_params["reverse"],
                )
                self._bullet_rotation(
                    bullet_rot_params["arms"],
                    bullet_rot_params["speed"],
                    bullet_rot_params["rad"],
                    bullet_rot_params["cd"],
                )
            case 6:
                self._bullet_rainfall(
                    borders,
                    rain_params["cd"],
                    rain_params["bul_count"],
                    rain_params["rad"],
                    rain_params["speed"],
                    rain_params["reverse"],
                )
                self._bullet_rotation(
                    bullet_rot_params["arms"],
                    bullet_rot_params["speed"],
                    bullet_rot_params["rad"],
                    bullet_rot_params["cd"],
                )
            case 7:
                self._burst_atk(
                    burst_atk_params["cd"],
                    burst_atk_params["bul_count"],
                    burst_atk_params["rad"],
                    burst_atk_params["ring_spd"],
                )
                self._spawn_snipers(sn_params["cd"])
                self._block(
                    borders,
                    blk_params["cd"],
                    blk_params["speed"],
                    blk_params["box_count"],
                )
            case 8:
                self._burst_atk(
                    burst_atk_params["cd"],
                    burst_atk_params["bul_count"],
                    burst_atk_params["rad"],
                    burst_atk_params["ring_spd"],
                )
                self._spawn_snipers(sn_params["cd"])
            case 9:
                self._bullet_rotation(
                    bullet_rot_params["arms"],
                    bullet_rot_params["speed"],
                    bullet_rot_params["rad"],
                    bullet_rot_params["cd"],
                )
            case 10:
                self._spawn_snipers(sn_params["cd"])
                self._block(
                    borders,
                    blk_params["cd"],
                    blk_params["speed"],
                    blk_params["box_count"],
                )
                self._burst_atk(
                    burst_atk_params["cd"],
                    burst_atk_params["bul_count"],
                    burst_atk_params["rad"],
                    burst_atk_params["ring_spd"],
                )
            case 11:
                self._block(
                    borders,
                    blk_params["cd"],
                    blk_params["speed"],
                    blk_params["box_count"],
                )
                self._ranged_atk(tar_x, tar_y)
                self._spawn_snipers(sn_params["cd"])
            case 12:
                self._bullet_rotation(
                    bullet_rot_params["arms"],
                    bullet_rot_params["speed"],
                    bullet_rot_params["rad"],
                    bullet_rot_params["cd"],
                )
                self._block(
                    borders,
                    blk_params["cd"],
                    blk_params["speed"],
                    blk_params["box_count"],
                )
            case 13:
                self._burst_atk(
                    burst_atk_params["cd"],
                    burst_atk_params["bul_count"],
                    burst_atk_params["rad"],
                    burst_atk_params["ring_spd"],
                )
                self._bullet_rainfall(
                    borders,
                    rain_params["cd"],
                    rain_params["bul_count"],
                    rain_params["rad"],
                    rain_params["speed"],
                    rain_params["reverse"],
                )
            case 14:
                self._bullet_rotation(
                    bullet_rot_params["arms"],
                    bullet_rot_params["speed"],
                    bullet_rot_params["rad"],
                    bullet_rot_params["cd"],
                )
            case 15:
                pass

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

    def _center(self, borders, friction, accel):
        border_sprites = borders.sprites()
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

    def _ranged_atk(self, tar_x, tar_y):
        self.pistol.shoot(tar_x, tar_y)

    def _burst_atk(
        self,
        cd: int,
        bul_count: int,
        rad: int,
        ring_spd,
    ):
        now = pygame.time.get_ticks()
        if now - self.burst_atk_timer < cd:
            return
        self.burst_atk_timer = now

        self._bullet_ring(bul_count, rad, ring_spd)

    def _bullet_ring(self, bul_count, rad, ring_spd):
        bullet_count = bul_count
        angle_step = 360 / bullet_count
        for i in range(bullet_count):
            angle = math.radians(angle_step * i)
            tar_x_off = self.rect.centerx + math.cos(angle) * 100
            tar_y_off = self.rect.centery + math.sin(angle) * 100
            for bullet_circ_speed in ring_spd:
                self.projectile_grp.add(
                    Bullet(
                        rad,
                        self.rect.centerx,
                        self.rect.centery,
                        tar_x_off,
                        tar_y_off,
                        self.color,
                        self.damage,
                        speed=bullet_circ_speed,
                    )
                )

    def _spawn_snipers(self, enemy_cd):
        now = pygame.time.get_ticks()
        if now - self.spawn_enemy_timer < enemy_cd:
            return
        self.spawn_enemy_timer = now

        spawn_sniper = Sniper(
            self.rect.centerx,
            self.rect.centery,
        )

        self.sniper_grp.add(spawn_sniper)

    def _bullet_rainfall(self, borders, cd, bul_count, rad, speed, reverse):
        now = pygame.time.get_ticks()
        if now - self.rainfall_timer < cd:
            return
        self.rainfall_timer = now

        border_sprites = borders.sprites()
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

        for i in range(bul_count):
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

    def _block(self, borders, cd, speed, box_count):
        now = pygame.time.get_ticks()
        if now - self.block_timer < cd:
            return
        self.block_timer = now

        border_sprites = borders.sprites()
        left_border = border_sprites[0]
        right_border = border_sprites[1]
        top_border = border_sprites[2]
        bottom_border = border_sprites[3]

        padding = 10

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

        self.angle = 0
        self.rot_dir = 1  # 1 = clockwise, -1 = counterclockwise
        self.rot_switch_timer = pygame.time.get_ticks()
        self.bullet_rot_timer = 0
        self.bullet_rot_params = {
            1: {
                "bullet_arms": 4,
                "speed": 5,
                "rad": 6,
                "bullet_cd": self.FOURTH,
            },
            2: {
                "bullet_arms": 6,
                "speed": 7,
                "rad": 6,
                "bullet_cd": self.FOURTH,
            },
            3: {},
            4: {},
            5: {
                "bullet_arms": 10,
                "speed": 10,
                "rad": 6,
                "bullet_cd": self.FOURTH,
            },
            6: {
                "bullet_arms": 14,
                "speed": 12,
                "rad": 10,
                "bullet_cd": self.FOURTH,
            },
            7: {},
            8: {},
            9: {},
            10: {
                "bullet_arms": 12,
                "speed": 8,
                "rad": 8,
                "bullet_cd": self.FOURTH,
            },
            11: {
                "bullet_arms": 12,
                "speed": 8,
                "rad": 8,
                "bullet_cd": self.FOURTH,
            },
            12: {},
        }

        self.rotation_params = {
            1: {
                "rot_switch_cd": self.DOUBLE,
                "rot_spd": 1,
            },
            2: {
                "rot_switch_cd": self.DOUBLE,
                "rot_spd": 2,
            },
            3: {
                "rot_switch_cd": self.DOUBLE,
                "rot_spd": 1,
            },
            4: {
                "rot_switch_cd": self.DOUBLE,
                "rot_spd": 1,
            },
            5: {
                "rot_switch_cd": self.DOUBLE,
                "rot_spd": 2,
            },
            6: {
                "rot_switch_cd": self.DOUBLE,
                "rot_spd": 3,
            },
            7: {
                "rot_switch_cd": self.DOUBLE,
                "rot_spd": 1,
            },
            8: {
                "rot_switch_cd": self.DOUBLE,
                "rot_spd": 1,
            },
            9: {
                "rot_switch_cd": self.DOUBLE,
                "rot_spd": 1,
            },
            10: {
                "rot_switch_cd": self.DOUBLE,
                "rot_spd": 3,
            },
            11: {
                "rot_switch_cd": self.DOUBLE,
                "rot_spd": 3,
            },
            12: {
                "rot_switch_cd": self.DOUBLE,
                "rot_spd": 1,
            },
        }

        self.rainfall_timer = 0
        self.rainfall_params = {
            1: {},
            2: {
                "cd": self.HALF,
                "bul_count": 6,
                "rad": 8,
                "speed": (5, 6, 7, 8, 9, 10),
                "reverse": False,
            },
            3: {},
            4: {},
            5: {
                "cd": self.HALF,
                "bul_count": 6,
                "rad": 8,
                "speed": (5, 6, 7, 8, 9, 10),
                "reverse": False,
            },
            6: {
                "cd": self.HALF,
                "bul_count": 6,
                "rad": 8,
                "speed": (5, 6, 7, 8, 9, 10),
                "reverse": True,
            },
            7: {},
            8: {},
            9: {},
            10: {
                "cd": self.HALF,
                "bul_count": 6,
                "rad": 8,
                "speed": (5, 6, 7, 8, 9, 10),
                "reverse": False,
            },
            11: {
                "cd": self.HALF,
                "bul_count": 6,
                "rad": 8,
                "speed": (5, 6, 7, 8, 9, 10),
                "reverse": True,
            },
            12: {},
        }

        self.burst_atk_timer = 0
        self.burst_atk_index = 0
        self.burst_atk_params = {
            1: {},
            2: {},
            3: {
                "cd": self.FOURTH,
                "bul_count": (6, 8, 12, 18),
                "rad": 8,
                "ring_spd": 5,
            },
            4: {
                "cd": self.EIGHT,
                "bul_count": (12, 15, 19),
                "rad": 8,
                "ring_spd": 8,
            },
            5: {},
            6: {},
            7: {},
            8: {},
            9: {
                "cd": self.WHOLE,
                "bul_count": (6, 12),
                "rad": 8,
                "ring_spd": 5,
            },
            10: {
                "cd": self.HALF,
                "bul_count": (6, 12),
                "rad": 8,
                "ring_spd": 5,
            },
            11: {
                "cd": self.HALF,
                "bul_count": (6, 12),
                "rad": 8,
                "ring_spd": 5,
            },
            12: {},
        }

        self.block_timer = 0
        self.block_params = {
            1: {},
            2: {},
            3: {},
            4: {},
            5: {},
            6: {},
            7: {},
            8: {"cd": self.EIGHT, "speed": (5, 10, 15, 20), "box_count": 2},
            9: {"cd": self.EIGHT, "speed": (5, 10, 15, 20), "box_count": 3},
            10: {},
            11: {},
            12: {},
        }

    # ==================
    # CORE
    # ==================

    def update(self, tar_x, tar_y, borders):
        self._update_phase()
        self._movement(tar_x, tar_y, borders)
        self._attack(tar_x, tar_y, borders)

        params = self.rotation_params[self.phase]
        self._handle_rotation(params)

    def _update_phase(self):
        pos = pygame.mixer.music.get_pos()
        print(pos)
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

        self.angle = (self.angle + (params["rot_spd"] * self.rot_dir)) % 360

        self.image = pygame.transform.rotozoom(self.orig_image, self.angle, 1.0)
        self.rect = self.image.get_rect(center=(self.x_cor, self.y_cor))
        self.mask = pygame.mask.from_surface(self.image)

        self.x_cor, self.y_cor = self.rect.center

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

    def _attack(self, tar_x, tar_y, borders):
        dist = math.hypot(tar_x - self.rect.centerx, tar_y - self.rect.centery)

        bullet_rot = self.bullet_rot_params[self.phase]
        rain_params = self.rainfall_params[self.phase]
        burst_params = self.burst_atk_params[self.phase]
        blk_params = self.block_params[self.phase]

        match self.phase:
            case 1:
                self._bullet_rotation(
                    bullet_rot["bullet_arms"],
                    bullet_rot["speed"],
                    bullet_rot["rad"],
                    bullet_rot["bullet_cd"],
                )
            case 2:
                self._bullet_rotation(
                    bullet_rot["bullet_arms"],
                    bullet_rot["speed"],
                    bullet_rot["rad"],
                    bullet_rot["bullet_cd"],
                )
                self._bullet_rainfall(
                    borders,
                    rain_params["cd"],
                    rain_params["bul_count"],
                    rain_params["rad"],
                    rain_params["speed"],
                    rain_params["reverse"],
                )
            case 3:
                self._burst_atk(
                    burst_params["cd"],
                    burst_params["bul_count"],
                    burst_params["rad"],
                    burst_params["ring_spd"],
                )
            case 4:
                self._burst_atk(
                    burst_params["cd"],
                    burst_params["bul_count"],
                    burst_params["rad"],
                    burst_params["ring_spd"],
                )
            case 5:
                self._bullet_rotation(
                    bullet_rot["bullet_arms"],
                    bullet_rot["speed"],
                    bullet_rot["rad"],
                    bullet_rot["bullet_cd"],
                )
                self._bullet_rainfall(
                    borders,
                    rain_params["cd"],
                    rain_params["bul_count"],
                    rain_params["rad"],
                    rain_params["speed"],
                    rain_params["reverse"],
                )
            case 6:
                self._bullet_rotation(
                    bullet_rot["bullet_arms"],
                    bullet_rot["speed"],
                    bullet_rot["rad"],
                    bullet_rot["bullet_cd"],
                )
                self._bullet_rainfall(
                    borders,
                    rain_params["cd"],
                    rain_params["bul_count"],
                    rain_params["rad"],
                    rain_params["speed"],
                    rain_params["reverse"],
                )
            case 7:
                pass
            case 8:
                self._block(
                    borders,
                    blk_params["cd"],
                    blk_params["speed"],
                    blk_params["box_count"],
                )
            case 9:
                self._block(
                    borders,
                    blk_params["cd"],
                    blk_params["speed"],
                    blk_params["box_count"],
                )
                self._burst_atk(
                    burst_params["cd"],
                    burst_params["bul_count"],
                    burst_params["rad"],
                    burst_params["ring_spd"],
                )
            case 10:
                self._bullet_rotation(
                    bullet_rot["bullet_arms"],
                    bullet_rot["speed"],
                    bullet_rot["rad"],
                    bullet_rot["bullet_cd"],
                )
                self._bullet_rainfall(
                    borders,
                    rain_params["cd"],
                    rain_params["bul_count"],
                    rain_params["rad"],
                    rain_params["speed"],
                    rain_params["reverse"],
                )
            case 11:
                self._bullet_rotation(
                    bullet_rot["bullet_arms"],
                    bullet_rot["speed"],
                    bullet_rot["rad"],
                    bullet_rot["bullet_cd"],
                )
                self._bullet_rainfall(
                    borders,
                    rain_params["cd"],
                    rain_params["bul_count"],
                    rain_params["rad"],
                    rain_params["speed"],
                    rain_params["reverse"],
                )

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
        bul_count: int,
        rad: int,
        ring_spd,
    ):
        now = pygame.time.get_ticks()
        if now - self.burst_atk_timer < cd:
            return
        self.burst_atk_timer = now

        count = bul_count[self.burst_atk_index % len(bul_count)]
        self._bullet_ring(count, rad, ring_spd)
        self.burst_atk_index += 1

    def _bullet_ring(self, bul_count, rad, ring_spd):
        for i in range(bul_count):
            angle_step = 360 / bul_count
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
                    speed=ring_spd,
                )
            )

    def _bullet_rainfall(self, borders, cd, bul_count, rad, speed, reverse):
        now = pygame.time.get_ticks()
        if now - self.rainfall_timer < cd:
            return
        self.rainfall_timer = now

        border_sprites = borders.sprites()
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

        for i in range(bul_count):
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

    def _block(self, borders, cd, speed, box_count):
        now = pygame.time.get_ticks()
        if now - self.block_timer < cd:
            return
        self.block_timer = now

        border_sprites = borders.sprites()
        left_border = border_sprites[0]
        right_border = border_sprites[1]
        top_border = border_sprites[2]
        bottom_border = border_sprites[3]

        padding = 10

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
