import pygame
from typing_extensions import override

from const.COLORS import BLACK, BLUE, CYAN, GREEN, ORANGE, RED, VIOLET, WHITE, YELLOW
from const.FONTS import REGULAR, SUBTITLE_SZ
from src.Abilities import Dash
from src.Core import Background, Border
from src.EnemySpawner import BouncerSpawner, ChaserSpawner, SniperSpawner, TankSpawner
from src.Entities import BoxEntity
from src.ItemSpawner import HealthPackSpawner
from src.Menu import GameOver, MainMenu
from src.Weapons import MachineGun, Pistol, Shotgun


class Player(BoxEntity):
    def __init__(
        self, win_wd, win_ht, x_cor, y_cor, color, projectile_grp, speed=1
    ) -> None:
        super().__init__(win_wd, win_ht, x_cor, y_cor, color)

        self.health = 500
        self.speed = speed
        self.dx, self.dy = 0, 0
        self.friction = 0.85

        self.min_health = 250
        self.dmg_cd = 250
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
        thickness = 20
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
            ply_wd, ply_ht, self.win_wd // 2, self.win_ht // 2, BLUE, self.projectiles
        )

        # OBJECTS
        self.hp_pack = HealthPackSpawner()

        # ENEMY SPAWNERS
        self.chaser_spawner = ChaserSpawner()
        self.bouncer_spawner = BouncerSpawner()
        self.tank_spawner = TankSpawner()
        self.sniper_spawner = SniperSpawner()

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

        self.hp_pack.try_spawn(self.win_wd, self.win_ht)

        # SPAWNER UPDATES
        self.chaser_spawner.try_spawn(self.win_wd, self.win_ht)
        if self.round_counter >= self.bouncer_spawner.pref_round:
            self.bouncer_spawner.try_spawn(self.win_wd, self.win_ht)
        if self.round_counter % self.tank_spawner.every_round == 0:
            self.tank_spawner.try_spawn(self.win_wd, self.win_ht)
        if self.round_counter >= self.sniper_spawner.pref_round:
            self.sniper_spawner.try_spawn(self.win_wd, self.win_ht)

        self.player.update(keys, self.borders)
        self.projectiles.update(self.borders)

        self.chaser_spawner.group.update(
            self.player.rect.centerx,
            self.player.rect.centery,
        )
        self.bouncer_spawner.group.update(self.borders)
        self.tank_spawner.group.update(
            self.player.rect.centerx,
            self.player.rect.centery,
        )
        self.sniper_spawner.group.update(
            self.player.rect.centerx,
            self.player.rect.centery,
            self.borders,
        )

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

        # OBJECTS
        hp_acq = pygame.sprite.spritecollide(self.player, self.hp_pack.group, False)
        for pack in self.hp_pack.group:
            if self.player.health >= self.player.min_health:
                pack.kill()
            elif hp_acq:
                pack.heal(self.player)
                pack.kill()

        # ENEMY PROJECTILE HITMARKS
        enemy_spawners = (
            self.chaser_spawner,
            self.bouncer_spawner,
            self.tank_spawner,
            self.sniper_spawner,
        )
        for spawner in enemy_spawners:
            hitmarks = pygame.sprite.groupcollide(
                self.projectiles, spawner.group, True, False
            )
            for projectile, enemies_hit in hitmarks.items():
                for enemy in enemies_hit:
                    enemy.take_dmg(current_weapon.damage)

        # ENEMY PLAYER CONTACT
        kill_on_contact = [self.bouncer_spawner, self.sniper_spawner]
        for spawner in enemy_spawners:
            player_enemy_hitmarks = pygame.sprite.spritecollide(
                self.player, spawner.group, spawner in kill_on_contact
            )
            if player_enemy_hitmarks:
                if spawner == self.sniper_spawner:
                    self.player.take_damage(50)
                else:
                    self.player.take_damage(10)
                    if not self.player.is_alive:
                        return False

        # ROUND IMPLEMENTATION
        all_spawned = (
            self.chaser_spawner.all_spawned
            and self.bouncer_spawner.all_spawned
            and self.tank_spawner.all_spawned
            and self.sniper_spawner.all_spawned
        )
        all_dead = (
            self.chaser_spawner.all_dead
            and self.bouncer_spawner.all_dead
            and self.tank_spawner.all_dead
            and self.sniper_spawner.all_dead
        )

        if all_spawned and all_dead:
            self.round_counter += 1

            self.chaser_spawner.next_round(self.round_counter)
            self.bouncer_spawner.next_round(self.round_counter)
            self.tank_spawner.next_round(self.round_counter)
            self.sniper_spawner.next_round(self.round_counter)

        return True

    def draw(self, screen):
        spawners = (
            self.chaser_spawner,
            self.bouncer_spawner,
            self.tank_spawner,
            self.sniper_spawner,
        )

        self.bg.draw(screen)

        self.hp_pack.group.draw(screen)

        for projectile in self.projectiles:
            projectile.draw(screen)

        self.player.draw(screen)

        for spawner in spawners:
            for enemy in spawner.group:
                enemy.draw(screen)
                enemy.draw_health_bar(screen)

        for border in self.borders:
            border.draw(screen)

        self._show_weap_state(screen)
        self._show_round(screen)
        self._show_ply_hp(screen)

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
    # STATES = ["MAINMENU", "PLAYING", "GAMEOVER"]

    def __init__(self, disp_wd, disp_ht, current_state) -> None:
        self.disp_wd = disp_wd
        self.disp_ht = disp_ht
        self.screen = pygame.display.set_mode(
            (self.disp_wd, self.disp_ht), pygame.FULLSCREEN
        )
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
    pygame.init()

    disp_info = pygame.display.Info()
    disp_wd, disp_ht = disp_info.current_w, disp_info.current_h
    gm = GameManager(disp_wd, disp_ht, "MAINMENU")
    gm.runner(60)
