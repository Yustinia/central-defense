import pygame
import math
import random
from typing_extensions import override

from const.COLORS import BLACK, DARK_ORANGE, ORANGE, WHITE
from src.Gameplay import Background, Border, BoxEntity, CircEntity
from src.Weapons import Bullet


class Player(BoxEntity):
    def __init__(self, win_wd, win_ht, x_cor, y_cor, color, speed=1) -> None:
        super().__init__(win_wd, win_ht, x_cor, y_cor, color)

        self.speed = speed
        self.dx, self.dy = 0, 0
        self.friction = 0.85

        self.shoot_cd = 50
        self.shoot_timer = 0

        self.dash_spd = 5
        self.dash_cd = 1000
        self.dash_timer = 0

    @override
    def update(self, keys, borders):
        self._movement(keys)
        self._collision(borders)

    def shoot(self, tar_x, tar_y, bullets_grp):
        if len(bullets_grp) >= 10:
            return

        now = pygame.time.get_ticks()
        if now - self.shoot_timer < self.shoot_cd:
            return
        self.shoot_timer = now

        bullet = Bullet(5, self.rect.centerx, self.rect.centery, tar_x, tar_y, ORANGE)
        bullets_grp.add(bullet)

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
        self.friction = 0.98
        self.accel = 0.5

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

        self.header_ft = pygame.font.Font("assets/fonts/GoboldRegular.otf", 30)

    def update(self):
        keys = pygame.key.get_pressed()

        self._spawn_enemy()

        self.player.update(keys, self.borders)
        self.bullets.update(self.borders)
        self.enemies.update(self.player.rect.centerx, self.player.rect.centery)

        if pygame.mouse.get_pressed()[0]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.player.shoot(mouse_x, mouse_y, self.bullets)

        hits = pygame.sprite.groupcollide(self.bullets, self.enemies, True, False)

        for bullet, enemies_hit in hits.items():
            for enemy in enemies_hit:
                enemy.take_dmg(25)

    def draw(self, screen):
        self.bg.draw(screen)

        for enemy in self.enemies:
            enemy.draw(screen)

        for border in self.borders:
            border.draw(screen)

        for bullet in self.bullets:
            bullet.draw(screen)

        self.player.draw(screen)

        self._render_text(screen)

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

        self.enemies.add(Enemy(20, x, y, ORANGE, random.randint(2, 4)))

    def _render_text(self, screen):
        header_img = self.header_ft.render(f"Central Defense", True, BLACK)
        header_rect = header_img.get_rect(center=(self.win_wd // 2, 30))
        screen.blit(header_img, header_rect)


class GameManager:
    def __init__(self, disp_wd, disp_ht) -> None:
        self.disp_wd = disp_wd
        self.disp_ht = disp_ht
        self.screen = pygame.display.set_mode((self.disp_wd, self.disp_ht))
        caption = pygame.display.set_caption("Central Defense")
        self.clock = pygame.time.Clock()

        self.game_running = True

        # instantiate game objects
        self.game = Game(self.disp_wd, self.disp_ht)

    def event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_running = False

    def update(self):
        self.game.update()

    def draw(self):
        self.game.draw(self.screen)

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
    gm = GameManager(disp_wd, disp_ht)
    gm.runner(60)
