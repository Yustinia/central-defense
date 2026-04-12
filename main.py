import math
import random

import pygame
from typing_extensions import override

from const.COLORS import BLACK, DARK_ORANGE, ORANGE, WHITE
from const.FONTS import REGULAR, SUBTITLE_SZ
from src.Core import Background, Border
from src.Gameplay import BoxEntity, CircEntity
from src.Menu import GameOver, MainMenu
from src.Weapons import Bullet


class Arsenal:
    def shoot_bullets(self, tar_x, tar_y, bullets_grp):
        self.shoot_cd = 150

        now = pygame.time.get_ticks()
        if now - self.shoot_timer < self.shoot_cd:
            return
        self.shoot_timer = now

        bullet = Bullet(5, self.rect.centerx, self.rect.centery, tar_x, tar_y, ORANGE)
        bullets_grp.add(bullet)

    def shoot_shotgun(self, tar_x, tar_y, bullets_grp):
        self.shoot_cd = 750

        now = pygame.time.get_ticks()
        if now - self.shoot_timer < self.shoot_cd:
            return
        self.shoot_timer = now

        spread = 15
        pellets = 4
        base_angle = math.degrees(
            math.atan2(tar_y - self.rect.centery, tar_x - self.rect.centerx)
        )

        for i in range(pellets):
            offset = (i - pellets // 2) * spread  # e.g. -30, -15, 0, 15, 30
            angle = math.radians(base_angle + offset)
            tar_x_off = self.rect.centerx + math.cos(angle) * 100
            tar_y_off = self.rect.centery + math.sin(angle) * 100
            bullets_grp.add(
                Bullet(
                    10,
                    self.rect.centerx,
                    self.rect.centery,
                    tar_x_off,
                    tar_y_off,
                    ORANGE,
                    20,
                )
            )

    def shoot_machine_gun(self, tar_x, tar_y, bullets_grp):
        self.shoot_cd = 25

        now = pygame.time.get_ticks()
        if now - self.shoot_timer < self.shoot_cd:
            return
        self.shoot_timer = now

        deviation = random.uniform(-0.7, 0.7)

        bullet = Bullet(
            2,
            self.rect.centerx,
            self.rect.centery,
            tar_x,
            tar_y,
            ORANGE,
            30,
        )
        bullets_grp.add(bullet)


class Player(BoxEntity, Arsenal):
    def __init__(self, win_wd, win_ht, x_cor, y_cor, color, speed=1) -> None:
        super().__init__(win_wd, win_ht, x_cor, y_cor, color)

        self.speed = speed
        self.dx, self.dy = 0, 0
        self.friction = 0.85

        self.shoot_timer = 0

        self.dash_spd = 5
        self.dash_cd = 1000
        self.dash_timer = 0

    @override
    def update(self, keys, borders):
        self._movement(keys)
        self._collision(borders)

    @override
    def _movement(self, keys):
        if keys[pygame.K_a]:
            self.dx -= self.speed
        if keys[pygame.K_d]:
            self.dx += self.speed
        if keys[pygame.K_w]:
            self.dy -= self.speed
        if keys[pygame.K_s]:
            self.dy += self.speed

        self._dash(keys)

    def _dash(self, keys):
        now = pygame.time.get_ticks()
        if now - self.dash_timer < self.dash_cd:
            return

        if not keys[pygame.K_SPACE]:
            return

        self.dash_timer = now

        if self.dx == 0 and self.dy == 0:
            return

        self.dx *= self.dash_spd
        self.dy *= self.dash_spd

    @override
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


class Enemy(CircEntity):
    def __init__(self, radius, x_cor, y_cor, color, speed=2) -> None:
        super().__init__(radius, x_cor, y_cor, color)

        self.speed = speed
        self.dx, self.dy = 0, 0
        self.health = 100
        self.friction = random.uniform(0.94, 0.99)
        self.accel = random.uniform(0.50, 0.90)

    def update(self, tar_x, tar_y):
        self._movement(tar_x, tar_y)

    @override
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


class Game:
    def __init__(self, win_wd, win_ht) -> None:
        self.win_wd = win_wd
        self.win_ht = win_ht
        self.bg = Background(self.win_wd, self.win_ht, BLACK)

        thickness = 10
        self.borders = pygame.sprite.Group()
        border_list = [
            Border(thickness, self.win_ht, 0, 0, WHITE),  # left
            Border(thickness, self.win_ht, self.win_wd - thickness, 0, WHITE),  # right
            Border(self.win_wd, 100, 0, 0, WHITE),  # up
            Border(self.win_wd, thickness, 0, self.win_ht - thickness, WHITE),  # down
        ]
        for border in border_list:
            self.borders.add(border)

        self.bullets = pygame.sprite.Group()

        ply_wd = ply_ht = 40
        self.player = Player(ply_wd, ply_ht, self.win_wd // 2, self.win_ht // 2, ORANGE)

        self.max_enemies = 50
        self.enemy_spawn_cd = 2000
        self.enemy_spawn_timer = 0
        self.enemies = pygame.sprite.Group()

        self.current_weapon_counter = 0
        self.current_weap_state = "MACHINEGUN"  # [PISTOL, SHOTGUN, MACHINEGUN]

        self.round_counter = 1

        self.subtitle_ft = pygame.font.Font(REGULAR, SUBTITLE_SZ)

    def update(self):
        keys = pygame.key.get_pressed()

        self._spawn_enemy()

        self.player.update(keys, self.borders)
        self.bullets.update(self.borders)
        self.enemies.update(self.player.rect.centerx, self.player.rect.centery)

        if pygame.mouse.get_pressed()[0]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            match self.current_weap_state:
                case "PISTOL":
                    self.player.shoot_bullets(mouse_x, mouse_y, self.bullets)
                case "SHOTGUN":
                    self.player.shoot_shotgun(mouse_x, mouse_y, self.bullets)
                case "MACHINEGUN":
                    self.player.shoot_machine_gun(mouse_x, mouse_y, self.bullets)

        if pygame.mouse.get_pressed()[2]:
            match self.current_weapon_counter:
                case 0:
                    self.current_weap_state = "PISTOL"
                case 1:
                    self.current_weap_state = "SHOTGUN"
                case 2:
                    self.current_weap_state = "MACHINEGUN"

            self.current_weapon_counter += 1
            if self.current_weapon_counter >= 3:
                self.current_weapon_counter = 0

        hits = pygame.sprite.groupcollide(self.bullets, self.enemies, True, False)

        for bullet, enemies_hit in hits.items():
            for enemy in enemies_hit:
                match self.current_weap_state:
                    case "PISTOL":
                        enemy.take_dmg(20)
                    case "SHOTGUN":
                        enemy.take_dmg(40)
                    case "MACHINEGUN":
                        enemy.take_dmg(10)

    def draw(self, screen):
        self.bg.draw(screen)

        for enemy in self.enemies:
            enemy.draw(screen)

        for border in self.borders:
            border.draw(screen)

        self._show_weap_state(screen)
        self._show_round(screen)

        for bullet in self.bullets:
            bullet.draw(screen)

        self.player.draw(screen)

    def _spawn_enemy(self):
        if len(self.enemies) >= self.max_enemies:
            return
        now = pygame.time.get_ticks()
        if now - self.enemy_spawn_timer < self.enemy_spawn_cd:
            return
        self.enemy_spawn_timer = now

        side = random.choice(["left", "right", "top", "bottom"])
        if side == "left":
            x, y = -20, random.randint(0, self.win_ht)
        elif side == "right":
            x, y = self.win_wd + 20, random.randint(0, self.win_ht)
        elif side == "top":
            x, y = random.randint(0, self.win_wd), -20
        else:
            x, y = random.randint(0, self.win_wd), self.win_ht + 20

        self.enemies.add(Enemy(20, x, y, ORANGE))

    def _show_weap_state(self, screen):
        weap_state_img = self.subtitle_ft.render(
            f"Current Weapon: {self.current_weap_state}", True, BLACK
        )
        weap_state_rect = weap_state_img.get_rect(topleft=(10, 20))

        screen.blit(weap_state_img, weap_state_rect)

    def _show_round(self, screen):
        round_state_img = self.subtitle_ft.render(
            f"Round: {self.round_counter}", True, BLACK
        )
        round_state_rect = round_state_img.get_rect(topright=(self.win_wd - 10, 20))

        screen.blit(round_state_img, round_state_rect)


class GameManager:
    # STATES = ["MAINMENU", "RUNNING", "GAMEOVER"]

    def __init__(self, disp_wd, disp_ht, current_state) -> None:
        self.disp_wd = disp_wd
        self.disp_ht = disp_ht
        self.screen = pygame.display.set_mode((self.disp_wd, self.disp_ht))
        caption = pygame.display.set_caption("Central Defense")
        self.clock = pygame.time.Clock()

        self.game_running = True
        self.current_state = current_state

        # instantiate game objects
        self.game = Game(self.disp_wd, self.disp_ht)

        # instantiate menu objects
        self.main_menu = MainMenu(self.disp_wd, self.disp_ht)
        self.game_over = GameOver(self.disp_wd, self.disp_ht)

    def event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_running = False
            if pygame.mouse.get_pressed()[0]:
                if self.current_state in ["MAINMENU", "GAMEOVER"]:
                    self.current_state = "PLAYING"

    def update(self):
        match self.current_state:
            case "MAINMENU":
                pass
            case "PLAYING":
                self.game.update()
            case "GAMEOVER":
                pass

    def draw(self):
        match self.current_state:
            case "MAINMENU":
                self.main_menu.draw(self.screen)
            case "PLAYING":
                self.game.draw(self.screen)
            case "GAMEOVER":
                self.game_over.draw(self.screen)

    def runner(self, fps):
        while self.game_running:
            self.event()
            self.update()
            self.draw()
            self.clock.tick(fps)
            pygame.display.update()

        pygame.quit()


if __name__ == "__main__":
    disp_wd, disp_ht = 1600, 900

    pygame.init()
    gm = GameManager(disp_wd, disp_ht, "MAINMENU")
    gm.runner(60)
