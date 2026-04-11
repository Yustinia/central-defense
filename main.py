import pygame
from typing_extensions import override

from const.COLORS import BLACK, DARK_ORANGE, ORANGE, WHITE
from src.Gameplay import Background, Border, BoxEntity
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
    def update(self, keys, borders, bullets_grp):
        self._movement(keys)
        self._collision(borders)
        bullets_grp.update(borders)

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

    def update(self):
        keys = pygame.key.get_pressed()

        self.player.update(keys, self.borders, self.bullets)

        if pygame.mouse.get_pressed()[0]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.player.shoot(mouse_x, mouse_y, self.bullets)

    def draw(self, screen):
        self.bg.draw(screen)

        for border in self.borders:
            border.draw(screen)

        for bullet in self.bullets:
            bullet.draw(screen)

        self.player.draw(screen)


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
