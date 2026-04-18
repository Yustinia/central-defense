import math
import random

import pygame

from const.COLORS import GREEN, ORANGE, RED, VIOLET, WHITE, YELLOW, BLUE
from src.Entities import CircEntity, OctEntity, TriEntity, DiamondEntity
from src.Weapons import Bullet, Pistol


class Chaser(CircEntity):
    def __init__(
        self,
        x_cor,
        y_cor,
        color=ORANGE,
        radius=20,
        health=100,
        damage=10,
    ) -> None:
        super().__init__(radius, x_cor, y_cor, color)

        self.dx, self.dy = 0, 0
        self.health = self.max_health = health
        self.damage = damage
        self.friction = random.uniform(0.94, 0.99)
        self.accel = random.uniform(0.50, 0.90)

    def update(self, tar_x, tar_y):
        self._movement(tar_x, tar_y)

    def _movement(self, tar_x, tar_y):
        angle = math.atan2(tar_y - self.rect.centery, tar_x - self.rect.centerx)

        self.dx += math.cos(angle) * self.accel
        self.dy += math.sin(angle) * self.accel
        self.dx *= self.friction
        self.dy *= self.friction

        self.rect.x += int(self.dx)
        self.rect.y += int(self.dy)

    def take_dmg(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()

    def draw_health_bar(self, screen):
        bar_wd = 80
        bar_ht = 20

        bar_x = self.rect.centerx - (bar_wd // 2)
        bar_y = self.rect.top - (bar_ht * 2)

        fill_wd = int(self.health / self.max_health * bar_wd)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, fill_wd, bar_ht))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_wd, bar_ht), 1)


class Bouncer(CircEntity):
    def __init__(
        self,
        x_cor,
        y_cor,
        color=VIOLET,
        radius=10,
        health=10,
        damage=10,
        max_bounces=5,
        speed=3,
    ) -> None:
        super().__init__(radius, x_cor, y_cor, color)

        self.health = self.max_health = health
        self.dx = speed * random.choice([-3, -2, -1, 1, 2, 3])
        self.dy = speed * random.choice([-3, -2, -1, 1, 2, 3])
        self.damage = damage

        self.max_bounces = max_bounces
        self.current_bounce_count = 0

    def update(self, borders):
        if self.current_bounce_count >= self.max_bounces:
            self.kill()

        self._collision(borders)

    def _collision(self, borders):
        x_bounced, y_bounced = False, False

        self.rect.x += int(self.dx)
        for border in borders:
            if self.rect.colliderect(border.rect):
                self.rect.x -= int(self.dx)
                self.dx *= -1
                x_bounced = True
                break

        self.rect.y += int(self.dy)
        for border in borders:
            if self.rect.colliderect(border.rect):
                self.rect.y -= int(self.dy)
                self.dy *= -1
                y_bounced = True
                break

        if x_bounced:
            self.current_bounce_count += 1
        if y_bounced:
            self.current_bounce_count += 1

    def take_dmg(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()

    def draw_health_bar(self, screen):
        bar_wd = 80
        bar_ht = 20

        bar_x = self.rect.centerx - (bar_wd // 2)
        bar_y = self.rect.top - (bar_ht * 2)

        fill_wd = int(self.health / self.max_health * bar_wd)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, fill_wd, bar_ht))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_wd, bar_ht), 1)


class Tank(CircEntity):
    def __init__(
        self,
        x_cor,
        y_cor,
        color=VIOLET,
        radius=50,
        health=1000,
        damage=10,
    ) -> None:
        super().__init__(radius, x_cor, y_cor, color)

        self.dx, self.dy = 0, 0
        self.health = self.max_health = health
        self.damage = damage
        self.friction = 0.92
        self.accel = 0.3

    def update(self, tar_x, tar_y):
        self._movement(tar_x, tar_y)

    def _movement(self, tar_x, tar_y):
        angle = math.atan2(tar_y - self.rect.centery, tar_x - self.rect.centerx)

        self.dx += math.cos(angle) * self.accel
        self.dy += math.sin(angle) * self.accel
        self.dx *= self.friction
        self.dy *= self.friction

        self.rect.x += int(self.dx)
        self.rect.y += int(self.dy)

    def take_dmg(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()

    def draw_health_bar(self, screen):
        bar_wd = 80
        bar_ht = 20

        bar_x = self.rect.centerx - (bar_wd // 2)
        bar_y = self.rect.top - (bar_ht * 2)

        fill_wd = int(self.health / self.max_health * bar_wd)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, fill_wd, bar_ht))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_wd, bar_ht), 1)


class Sniper(TriEntity):
    def __init__(
        self,
        x_cor,
        y_cor,
        color=YELLOW,
        size=20,
        health=25,
        damage=25,
        fuse_duration=2000,
        speed=50,
    ) -> None:
        super().__init__(size, x_cor, y_cor, color)

        self.speed = speed
        self.dx, self.dy = 0, 0
        self.health = self.max_health = health
        self.damage = damage

        self.fuse_duration = fuse_duration
        self.spawn_time = pygame.time.get_ticks()
        self.is_fused = True

        # Store original image for rotation
        self.original_image = self.image
        self.angle = 0

    def update(self, tar_x, tar_y, borders):
        now = pygame.time.get_ticks()
        if self.is_fused:
            self.angle = math.degrees(
                math.atan2(tar_y - self.rect.centery, tar_x - self.rect.centerx)
            )
            self.angle = -self.angle - 90
            self.image = pygame.transform.rotate(self.original_image, self.angle)
            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center

            if now - self.spawn_time > self.fuse_duration:
                self.is_fused = False
                rad = math.radians(-self.angle - 90)
                self.dx = math.cos(rad) * self.speed
                self.dy = math.sin(rad) * self.speed
            else:
                self._collision(borders)
                return

        self.rect.x += int(self.dx)
        self.rect.y += int(self.dy)
        self._collision(borders)

    def take_dmg(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()

    def _collision(self, borders):
        for border in borders:
            if self.rect.colliderect(border.rect):
                self.kill()

    def draw_health_bar(self, screen):
        bar_wd = 80
        bar_ht = 20

        bar_x = self.rect.centerx - (bar_wd // 2)
        bar_y = self.rect.top - (bar_ht * 2)

        fill_wd = int(self.health / self.max_health * bar_wd)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, fill_wd, bar_ht))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_wd, bar_ht), 1)


class Shooter(CircEntity):
    def __init__(
        self,
        x_cor,
        y_cor,
        projectile_grp,
        color=RED,
        shoot_cd=500,
        radius=20,
        health=150,
        damage=50,
    ) -> None:
        super().__init__(radius, x_cor, y_cor, color)

        self.health = self.max_health = health
        self.shoot_cd = shoot_cd
        self.damage = damage

        self.projectile_grp = projectile_grp
        self.pistol = Pistol(
            self.projectile_grp,
            self.rect,
            shoot_cd=self.shoot_cd,
            damage=damage,
            color=color,
        )

    def update(self, tar_x, tar_y):
        self.pistol.shoot(tar_x, tar_y)

    def take_dmg(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()

    def draw(self, screen):
        super().draw(screen)

    def draw_health_bar(self, screen):
        bar_wd = 80
        bar_ht = 20

        bar_x = self.rect.centerx - (bar_wd // 2)
        bar_y = self.rect.top - (bar_ht * 2)

        fill_wd = int(self.health / self.max_health * bar_wd)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, fill_wd, bar_ht))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_wd, bar_ht), 1)


class Exploder(OctEntity):
    def __init__(
        self,
        x_cor,
        y_cor,
        projectile_grp,
        color=YELLOW,
        size=50,
        fuse_dur=6000,
        damage=50,
        health=50,
    ) -> None:
        super().__init__(size, x_cor, y_cor, color)

        self.x_cor = x_cor
        self.y_cor = y_cor
        self.color = color
        self.projectile_grp = projectile_grp

        self.fuse_dur = fuse_dur
        self.fuse_timer = pygame.time.get_ticks()
        self.damage = damage
        self.health = self.max_health = health

        self.dx, self.dy = 0, 0
        self.friction = 0.92
        self.accel = 0.32

    def update(self, tar_x, tar_y):
        self.explode_timer()
        self._movement(tar_x, tar_y)

    def _movement(self, tar_x, tar_y):
        angle = math.atan2(tar_y - self.rect.centery, tar_x - self.rect.centerx)

        self.dx += math.cos(angle) * self.accel
        self.dy += math.sin(angle) * self.accel
        self.dx *= self.friction
        self.dy *= self.friction

        self.rect.x += int(self.dx)
        self.rect.y += int(self.dy)

    def explode_timer(self):
        now = pygame.time.get_ticks()
        if now - self.fuse_timer < self.fuse_dur:
            return
        self.fuse_timer = now

        self.explode()

    def explode(self, bullet_count=16):
        angle_step = 360 / bullet_count
        for i in range(bullet_count):
            angle = math.radians(angle_step * i)
            tar_x = self.rect.centerx + math.cos(angle) * 100
            tar_y = self.rect.centery + math.sin(angle) * 100
            self.projectile_grp.add(
                Bullet(
                    5,
                    self.rect.centerx,
                    self.rect.centery,
                    tar_x,
                    tar_y,
                    self.color,
                    self.damage,
                )
            )
        self.kill()

    def take_dmg(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.explode()

    def draw_health_bar(self, screen):
        bar_wd = 80
        bar_ht = 20

        bar_x = self.rect.centerx - (bar_wd // 2)
        bar_y = self.rect.top - (bar_ht * 2)

        fill_wd = int(self.health / self.max_health * bar_wd)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, fill_wd, bar_ht))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_wd, bar_ht), 1)


class SplitterShard(DiamondEntity):
    def __init__(
        self,
        x_cor,
        y_cor,
        color=BLUE,
        size=25,
        health=25,
        damage=15,
    ) -> None:
        super().__init__(size, x_cor, y_cor, color)

        self.health = self.max_health = health
        self.damage = damage
        self.dx, self.dy = 0, 0
        self.friction = random.uniform(0.92, 0.98)
        self.accel = random.uniform(0.70, 0.80)

    def update(self, tar_x, tar_y):
        self._movement(tar_x, tar_y)

    def _movement(self, tar_x, tar_y):
        angle = math.atan2(tar_y - self.rect.centery, tar_x - self.rect.centerx)

        self.dx += math.cos(angle) * self.accel
        self.dy += math.sin(angle) * self.accel
        self.dx *= self.friction
        self.dy *= self.friction

        self.rect.x += int(self.dx)
        self.rect.y += int(self.dy)

    def take_dmg(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()

    def draw_health_bar(self, screen):
        bar_wd = 80
        bar_ht = 20

        bar_x = self.rect.centerx - (bar_wd // 2)
        bar_y = self.rect.top - (bar_ht * 2)

        fill_wd = int(self.health / self.max_health * bar_wd)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, fill_wd, bar_ht))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_wd, bar_ht), 1)


class Splitter(DiamondEntity):
    def __init__(
        self,
        x_cor,
        y_cor,
        shard_grp,
        color=BLUE,
        size=50,
        health=50,
        damage=10,
        shard_count=6,
    ) -> None:
        super().__init__(size, x_cor, y_cor, color)

        self.shard_grp = shard_grp
        self.health = self.max_health = health
        self.damage = damage
        self.shard_count = shard_count
        self.dx, self.dy = 0, 0
        self.friction = 0.92
        self.accel = 0.4

        self.wander_cd = 1000
        self.wander_timer = 0
        self.wander_dx, self.wander_dy = 0, 0
        self.is_wandering = True

    def update(self, tar_x, tar_y):
        self._movement(tar_x, tar_y)

    def _movement(self, tar_x, tar_y):
        dist = math.hypot(tar_x - self.rect.centerx, tar_y - self.rect.centery)

        if self.is_wandering and dist > 550:
            self.is_wandering = False
        elif not self.is_wandering and dist < 450:
            self.is_wandering = True

        if self.is_wandering:
            self._wander()
        else:
            self._follow(tar_x, tar_y)

        self.dx *= self.friction
        self.dy *= self.friction
        self.rect.x += int(self.dx)
        self.rect.y += int(self.dy)

    def _follow(self, tar_x, tar_y):
        angle = math.atan2(tar_y - self.rect.centery, tar_x - self.rect.centerx)

        self.dx += math.cos(angle) * self.accel
        self.dy += math.sin(angle) * self.accel

    def _wander(self):
        now = pygame.time.get_ticks()
        if now - self.wander_timer > self.wander_cd:
            self.wander_timer = now
            angle = math.radians(random.randint(0, 360))
            self.wander_dx = math.cos(angle) * self.accel
            self.wander_dy = math.sin(angle) * self.accel

        self.dx += self.wander_dx
        self.dy += self.wander_dy

    def take_dmg(self, amount):
        self.health -= amount
        if self.health <= 0:
            self._split()
            self.kill()

    def _split(self):
        for i in range(self.shard_count):
            offset_x = random.randint(-30, 30)
            offset_y = random.randint(-30, 30)
            self.shard_grp.add(
                SplitterShard(
                    self.rect.centerx + offset_x, self.rect.centery + offset_y
                )
            )

    def draw_health_bar(self, screen):
        bar_wd = 80
        bar_ht = 20

        bar_x = self.rect.centerx - (bar_wd // 2)
        bar_y = self.rect.top - (bar_ht * 2)

        fill_wd = int(self.health / self.max_health * bar_wd)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, fill_wd, bar_ht))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_wd, bar_ht), 1)
