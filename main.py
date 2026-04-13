import random

import pygame
from typing_extensions import override

from const.COLORS import BLACK, DARK_ORANGE, ORANGE, WHITE
from const.FONTS import REGULAR, SUBTITLE_SZ
from src.Abilities import Dash
from src.Core import Background, Border
from src.Enemies import Chaser
from src.Gameplay import BoxEntity
from src.Menu import GameOver, MainMenu
from src.Weapons import MachineGun, Pistol, Shotgun


class Player(BoxEntity):
    def __init__(
        self, win_wd, win_ht, x_cor, y_cor, color, projectile_grp, speed=1
    ) -> None:
        super().__init__(win_wd, win_ht, x_cor, y_cor, color)

        self.health = 200
        self.speed = speed
        self.dx, self.dy = 0, 0
        self.friction = 0.85

        self.dmg_cd = 1000
        self.dmg_timer = 0

        self.projectile_grp = projectile_grp

        # Weapons
        self.pistol = Pistol(self.projectile_grp, self.rect)
        self.shotgun = Shotgun(self.projectile_grp, self.rect)
        self.machinegun = MachineGun(self.projectile_grp, self.rect)

        # Abilities
        self.dash_ab = Dash()

        # States
        self.is_alive = True

    @override
    def update(self, keys, borders):
        self._movement(keys)
        self._collision(borders)

    def take_damage(self, amount):
        now = pygame.time.get_ticks()
        if now - self.dmg_timer < self.dmg_cd:
            return self.is_alive
        self.dmg_timer = now

        self.health -= amount

        if self.health <= 0:
            self.is_alive = False
            return self.is_alive

        return self.is_alive

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

        if keys[pygame.K_SPACE]:
            self.dx, self.dy = self.dash_ab.do_dash(self.dx, self.dy)

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


class Game:
    def __init__(self, win_wd, win_ht) -> None:
        self.win_wd = win_wd
        self.win_ht = win_ht
        self.bg = Background(self.win_wd, self.win_ht, BLACK)

        # GAME BORDER
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

        # PELLETS
        self.projectiles = pygame.sprite.Group()

        # PLAYER
        ply_wd, ply_ht = 40, 40
        self.player = Player(
            ply_wd, ply_ht, self.win_wd // 2, self.win_ht // 2, ORANGE, self.projectiles
        )

        # ENEMIES
        self.chaser_spawn_cd = 2000
        self.chaser_spawn_timer = 0
        self.chasers = pygame.sprite.Group()

        # WEAPON
        self.current_weapon_counter = 0
        self.current_weap_state = "PISTOL"  # [PISTOL, SHOTGUN, MACHINEGUN]

        # ROUNDS
        self.round_counter = 1

        # FONTS
        self.subtitle_ft = pygame.font.Font(REGULAR, SUBTITLE_SZ)

    def event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            self.current_weapon_counter = (self.current_weapon_counter + 1) % 3
            match self.current_weapon_counter:
                case 0:
                    self.current_weap_state = "PISTOL"
                case 1:
                    self.current_weap_state = "SHOTGUN"
                case 2:
                    self.current_weap_state = "MACHINEGUN"

    def update(self):
        keys = pygame.key.get_pressed()

        self._spawn_chaser()

        self.player.update(keys, self.borders)
        self.projectiles.update(self.borders)
        self.chasers.update(self.player.rect.centerx, self.player.rect.centery)

        if pygame.mouse.get_pressed()[0]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            match self.current_weap_state:
                case "PISTOL":
                    self.player.pistol.shoot(mouse_x, mouse_y)
                case "SHOTGUN":
                    self.player.shotgun.shoot(mouse_x, mouse_y)
                case "MACHINEGUN":
                    self.player.machinegun.shoot(mouse_x, mouse_y)

        current_weapon = getattr(self.player, self.current_weap_state.lower())
        chaser_hitmarks = pygame.sprite.groupcollide(
            self.projectiles, self.chasers, True, False
        )
        for projectile, chasers_hit in chaser_hitmarks.items():
            for enemy in chasers_hit:
                enemy.take_dmg(current_weapon.damage)

        player_chaser_hitmarks = pygame.sprite.spritecollide(
            self.player, self.chasers, False
        )
        if player_chaser_hitmarks:
            self.player.take_damage(10)
            if not self.player.is_alive:
                return False
        return True

    def draw(self, screen):
        self.bg.draw(screen)

        for chaser in self.chasers:
            chaser.draw(screen)

        for border in self.borders:
            border.draw(screen)

        self._show_weap_state(screen)
        self._show_round(screen)
        self._show_ply_hp(screen)

        for projectile in self.projectiles:
            projectile.draw(screen)

        self.player.draw(screen)

    def _spawn_chaser(self):
        now = pygame.time.get_ticks()
        if now - self.chaser_spawn_timer < self.chaser_spawn_cd:
            return
        self.chaser_spawn_timer = now

        side = random.choice(["left", "right", "top", "bottom"])
        if side == "left":
            x, y = -20, random.randint(0, self.win_ht)
        elif side == "right":
            x, y = self.win_wd + 20, random.randint(0, self.win_ht)
        elif side == "top":
            x, y = random.randint(0, self.win_wd), -20
        else:
            x, y = random.randint(0, self.win_wd), self.win_ht + 20

        self.chasers.add(Chaser(20, x, y, ORANGE))

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

    def _show_ply_hp(self, screen):
        ply_hp_img = self.subtitle_ft.render(f"HP: {self.player.health}", True, BLACK)
        ply_hp_rect = ply_hp_img.get_rect(center=(self.win_wd // 2, 40))

        screen.blit(ply_hp_img, ply_hp_rect)


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
            self.game.event(event)

            if event.type == pygame.QUIT:
                self.game_running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.current_state in ["MAINMENU", "GAMEOVER"]:
                    self.current_state = "PLAYING"

    def update(self):
        match self.current_state:
            case "MAINMENU":
                pass
            case "PLAYING":
                is_player_alive = self.game.update()

                if not is_player_alive:
                    self.current_state = "GAMEOVER"
                    self.game = Game(self.disp_wd, self.disp_ht)

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
