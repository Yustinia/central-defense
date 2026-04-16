import pygame

from src.Core import Background, Border
from src.EnemySpawner import (
    BouncerSpawner,
    ChaserSpawner,
    ExploderSpawner,
    ShooterSpawner,
    SniperSpawner,
    TankSpawner,
)
from src.BossSpawner import VenusSpawner
from src.ItemSpawner import HealthPackSpawner
from src.Menu import GameOver, MainMenu, PauseMenu, PlayingState
from src.Player import Player


class Game:
    def __init__(self, win_wd, win_ht) -> None:
        self.win_wd = win_wd
        self.win_ht = win_ht
        self.bg = Background(self.win_wd, self.win_ht)

        # GAME BORDER
        thickness = 30
        self.borders = pygame.sprite.Group()
        border_list = [
            Border(thickness, self.win_ht, 0, 0),  # left
            Border(thickness, self.win_ht, self.win_wd - thickness, 0),  # right
            Border(self.win_wd, thickness, 0, 0),  # up
            Border(self.win_wd, thickness, 0, self.win_ht - thickness),  # down
        ]
        for border in border_list:
            self.borders.add(border)

        # EJECTION COLLETCION
        self.player_projectiles = pygame.sprite.Group()
        self.player_beams = pygame.sprite.Group()
        self.enemy_projectiles = pygame.sprite.Group()

        # PLAYER
        self.player = Player(
            self.win_wd // 2,
            self.win_ht // 2,
            self.player_projectiles,
            self.player_beams,
        )

        # OBJECTS
        self.hp_pack = HealthPackSpawner()

        # ENEMY SPAWNERS
        self.chaser_spawner = ChaserSpawner()
        self.bouncer_spawner = BouncerSpawner()
        self.tank_spawner = TankSpawner()
        self.sniper_spawner = SniperSpawner()
        self.shooter_spawner = ShooterSpawner(self.enemy_projectiles)
        self.exploder_spawner = ExploderSpawner(self.enemy_projectiles)

        # BOSS SPAWNERS
        self.venus_spawner = VenusSpawner(
            self.enemy_projectiles,
        )

        # ALL SPAWNERS
        self.all_entity_spawners = (
            self.chaser_spawner,
            self.bouncer_spawner,
            self.tank_spawner,
            self.sniper_spawner,
            self.shooter_spawner,
            self.exploder_spawner,
            self.venus_spawner,
        )

        # WEAPON
        self.current_weapon_counter = 0
        self.current_weap_state = "PISTOL"  # [PISTOL, SHOTGUN, MACHINEGUN, LASERGUN]

        # ROUNDS
        self.round_counter = 1

        # GUI
        self.playing_state = PlayingState(self.win_wd, self.win_ht)

    def event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            self.current_weapon_counter = (self.current_weapon_counter + 1) % 4
            match self.current_weapon_counter:
                case 0:
                    self.current_weap_state = "PISTOL"
                case 1:
                    self.current_weap_state = "SHOTGUN"
                case 2:
                    self.current_weap_state = "MACHINEGUN"
                case 3:
                    self.current_weap_state = "LASERGUN"

    def update(self):
        keys = pygame.key.get_pressed()

        if pygame.mouse.get_pressed()[0]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            match self.current_weap_state:
                case "PISTOL":
                    self.player.pistol.shoot(mouse_x, mouse_y)
                case "SHOTGUN":
                    self.player.shotgun.shoot(mouse_x, mouse_y)
                case "MACHINEGUN":
                    self.player.machinegun.shoot(mouse_x, mouse_y)
                case "LASERGUN":
                    self.player.lasergun.shoot(mouse_x, mouse_y)

        # OBJECT UPDATES
        self.hp_pack.try_spawn(self.win_wd, self.win_ht)

        hp_acq = pygame.sprite.spritecollide(self.player, self.hp_pack.group, False)
        for pack in self.hp_pack.group:
            if self.player.health >= self.player.min_health:
                pack.kill()
            elif hp_acq:
                pack.heal(self.player)
                pack.kill()

        # SPAWNER UPDATES
        for spawner in self.all_entity_spawners:
            spawner.try_spawn(self.win_wd, self.win_ht, self.round_counter)

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
        self.shooter_spawner.group.update(
            self.player.rect.centerx,
            self.player.rect.centery,
        )
        self.exploder_spawner.group.update(
            self.player.rect.centerx,
            self.player.rect.centery,
        )
        self.venus_spawner.group.update(
            self.player.rect.centerx,
            self.player.rect.centery,
            self.borders,
        )

        # PLAYER UPDATES
        self.player.update(keys, self.borders)
        self.player_projectiles.update(self.borders)
        self.player_beams.update(self.borders)

        # ENEMY UPDATES
        self.enemy_projectiles.update(self.borders)

        # PLAYER PROJECTILE HITS ENEMY
        for spawner in self.all_entity_spawners:
            projectile_hitmarks = pygame.sprite.groupcollide(
                self.player_projectiles, spawner.group, True, False
            )
            for projectile, enemies_hit in projectile_hitmarks.items():
                for enemy in enemies_hit:
                    enemy.take_dmg(projectile.damage)

            beam_hitmarks = pygame.sprite.groupcollide(
                self.player_beams,
                spawner.group,
                False,
                False,
                collided=pygame.sprite.collide_mask,
            )
            for beam, enemies_hit in beam_hitmarks.items():
                for enemy in enemies_hit:
                    enemy.take_dmg(beam.damage)

        # ENEMY AND PLAYER CONTACT
        kill_on_contact = [self.bouncer_spawner, self.sniper_spawner]
        for spawner in self.all_entity_spawners:
            player_enemy_hitmarks = pygame.sprite.spritecollide(
                self.player, spawner.group, spawner in kill_on_contact
            )
            if player_enemy_hitmarks:
                enemy = player_enemy_hitmarks[0]
                self.player.take_damage(enemy.damage)

        # ENEMY PROJECTILE AND PLAYER HIT
        enemy_projectile = pygame.sprite.spritecollide(
            self.player,
            self.enemy_projectiles,
            True,
        )
        for bullet in enemy_projectile:
            self.player.take_damage(bullet.damage)

        # ROUND IMPLEMENTATION
        all_spawned = all(spawner.all_spawned for spawner in self.all_entity_spawners)
        all_dead = all(spawner.all_dead for spawner in self.all_entity_spawners)

        if all_spawned and all_dead:
            self.round_counter += 1

            self.chaser_spawner.next_round(self.round_counter)
            self.bouncer_spawner.next_round(self.round_counter)
            self.tank_spawner.next_round(self.round_counter)
            self.sniper_spawner.next_round(self.round_counter)
            self.shooter_spawner.next_round(self.round_counter)
            self.exploder_spawner.next_round(self.round_counter)

        if not self.player.is_alive:
            return False
        return True

    def draw(self, screen):
        self.bg.draw(screen)

        self.playing_state.render_round(self.round_counter, screen)

        self.hp_pack.group.draw(screen)

        for ejection in (
            self.player_projectiles,
            self.player_beams,
            self.enemy_projectiles,
        ):
            ejection.draw(screen)

        self.player.draw(screen)

        for spawner in self.all_entity_spawners:
            for enemy in spawner.group:
                enemy.draw(screen)
                enemy.draw_health_bar(screen)

        for border in self.borders:
            border.draw(screen)

        self.player.draw_health_bar(self.win_wd, self.win_ht, screen)
        self.player.draw_ability_bar(self.win_wd, self.win_ht, screen)
        self.player.display_current_weap(self.win_wd, self.current_weap_state, screen)


class GameManager:
    # STATES = ["MAINMENU", "PLAYING", "GAMEOVER", "PAUSED"]

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
        self.pause_menu = PauseMenu(self.disp_wd, self.disp_ht)

    def event(self):
        for event in pygame.event.get():
            self.game.event(event)

            if event.type == pygame.QUIT:
                self.game_running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.current_state in ["MAINMENU", "GAMEOVER"]:
                    self.current_state = "PLAYING"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.current_state == "PLAYING":
                        self.current_state = "PAUSED"
                    elif self.current_state == "PAUSED":
                        self.current_state = "PLAYING"

                if event.key == pygame.K_q:
                    if self.current_state == "PAUSED":
                        self.current_state = "MAINMENU"
                        self.game = Game(self.disp_wd, self.disp_ht)

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

            case "PAUSED":
                pass

    def draw(self):
        match self.current_state:
            case "MAINMENU":
                self.main_menu.draw(self.screen)
            case "PLAYING":
                self.game.draw(self.screen)
            case "GAMEOVER":
                self.game_over.draw(self.screen)
            case "PAUSED":
                self.game.draw(self.screen)
                self.pause_menu.draw(self.screen)

    def runner(self, fps, should_log):
        while self.game_running:
            if should_log:
                logging = {
                    "ROUND": self.game.round_counter,
                    "CHASER": len(self.game.chaser_spawner.group),
                    "BOUNCER": len(self.game.bouncer_spawner.group),
                    "TANK": len(self.game.tank_spawner.group),
                    "SNIPER": len(self.game.sniper_spawner.group),
                    "SHOOTER": len(self.game.shooter_spawner.group),
                    "EXPLODER": len(self.game.exploder_spawner.group),
                }
                for key, value in logging.items():
                    print(f"{key}: {value}")
                print()

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
    gm.runner(60, True)
