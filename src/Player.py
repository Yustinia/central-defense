import pygame
from typing_extensions import override

from const.COLORS import BLACK, BLUE, GREEN, RED, WHITE, YELLOW
from const.FONTS import REGULAR
from sounds.effects.SOUNDS import HURT
from src.Abilities import BulletBurst, Dash, PassiveHeal, Shield
from src.Entities import BoxEntity
from src.Weapons import LaserGun, MachineGun, Pistol, Shotgun


class Player(BoxEntity):
    def __init__(
        self,
        x_cor,
        y_cor,
        projectile_grp,
        beam_grp,
        health=500,
        speed=1,
        win_wd: int = 30,
        win_ht: int = 30,
        color=BLUE,
    ) -> None:
        super().__init__(win_wd, win_ht, x_cor, y_cor, color)

        self.health = self.max_health = health
        self.speed = speed
        self.dx, self.dy = 0, 0
        self.friction = 0.85

        self.dmg_cd = 125
        self.dmg_timer = 0

        self.projectile_grp = projectile_grp
        self.beam_grp = beam_grp

        # Weapons
        self.pistol = Pistol(
            self.projectile_grp,
            self.rect,
        )
        self.shotgun = Shotgun(
            self.projectile_grp,
            self.rect,
        )
        self.machinegun = MachineGun(
            self.projectile_grp,
            self.rect,
        )
        self.lasergun = LaserGun(self.beam_grp, self.rect)

        # Abilities
        self.dash_ab = Dash()
        self.passive_heal_ab = PassiveHeal()
        self.shield_ab = Shield()
        self.bullet_burst_ab = BulletBurst()

        # States
        self.is_alive = True

        # Sounds
        self.hurt_sfx = pygame.mixer.Sound(HURT)
        self.hurt_sfx.set_volume(0.2)

    @override
    def update(self, keys, borders):
        self.shield_ab.update()
        self._update_visual()
        self._passive_heal()

        self._movement(keys)
        self._collision(borders)

    def _update_visual(self):
        if self.shield_ab.is_active:
            self.image.fill(YELLOW)
        else:
            self.image.fill(BLUE)

    def _passive_heal(self):
        if self.passive_heal_ab.is_ready():
            self.health = min(
                self.health + self.passive_heal_ab.heal_amt, self.max_health
            )

    def take_damage(self, amount):
        now = pygame.time.get_ticks()
        if now - self.dmg_timer < self.dmg_cd:
            return self.is_alive
        self.dmg_timer = now

        if self.shield_ab.is_active:
            self.shield_ab.durability -= amount
            if self.shield_ab.durability <= 0:
                self.shield_ab.is_active = False
            return self.is_alive

        self.health -= amount

        if self.health <= 0:
            self.is_alive = False

        self.hurt_sfx.play()

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

        if keys[pygame.K_q]:
            self.shield_ab.activate()

        if keys[pygame.K_e]:
            if self.bullet_burst_ab.is_ready():
                self.bullet_burst_ab.burst(
                    self.projectile_grp,
                    self.rect.centerx,
                    self.rect.centery,
                )

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

    def draw_health_bar(self, win_wd, win_ht, screen):
        bar_wd = 500
        bar_ht = 20
        bot_padding = 5
        top_padding = 10
        side_padding = 8
        font = pygame.font.Font(REGULAR, 30)

        bar_rect = pygame.Rect(0, 0, bar_wd, bar_ht)
        bar_rect.bottom = win_ht - bot_padding
        bar_rect.right = (win_wd // 2) - side_padding

        hp_label = font.render("Health", True, WHITE)
        hp_label.set_alpha(32)
        hp_label_rect = hp_label.get_rect(
            midbottom=(bar_rect.centerx, bar_rect.top - top_padding)
        )

        health_ratio = max(0, self.health) / self.max_health
        current_health_wd = bar_wd * health_ratio

        if health_ratio <= 0.25:
            fill_color = RED
        elif health_ratio <= 0.50:
            fill_color = YELLOW
        else:
            fill_color = GREEN

        pygame.draw.rect(
            screen,
            BLACK,
            bar_rect,
        )  # BG

        fill_rect = pygame.Rect(
            bar_rect.left,
            bar_rect.top,
            current_health_wd,
            bar_ht,
        )
        pygame.draw.rect(
            screen,
            fill_color,
            fill_rect,
        )  # FILL
        pygame.draw.rect(
            screen,
            BLACK,
            bar_rect,
            2,
        )  # BORDER

        screen.blit(hp_label, hp_label_rect)

    def draw_ability_bar(self, win_wd, win_ht, screen):
        bar_wd = 250
        bar_ht = 20
        bot_padding = 5
        top_padding = 10
        side_padding = 8
        gap = 16
        font = pygame.font.Font(REGULAR, 30)

        shield_rect = pygame.Rect(0, 0, bar_wd, bar_ht)
        shield_rect.bottom = win_ht - bot_padding
        shield_rect.left = (win_wd // 2) + side_padding

        shield_label = font.render("Shield [Q]", True, WHITE)
        shield_label.set_alpha(32)
        shield_label_rect = shield_label.get_rect(
            midbottom=(shield_rect.centerx, shield_rect.top - top_padding)
        )

        burst_rect = pygame.Rect(0, 0, bar_wd, bar_ht)
        burst_rect.bottom = win_ht - bot_padding
        burst_rect.left = shield_rect.right + gap

        burst_label = font.render("Burst [E]", True, WHITE)
        burst_label.set_alpha(32)
        burst_label_rect = burst_label.get_rect(
            midbottom=(burst_rect.centerx, burst_rect.top - top_padding)
        )

        # BAR BG
        pygame.draw.rect(screen, BLACK, shield_rect)
        pygame.draw.rect(screen, BLACK, burst_rect)

        # SHIELD FILL
        if not self.shield_ab.can_be_activated and not self.shield_ab.is_active:
            now = pygame.time.get_ticks()
            elapsed = now - self.shield_ab.shield_timer
            progress = min(elapsed / self.shield_ab.shield_cd, 1.0)
            shield_fill = int(progress * bar_wd)
            shield_color = RED
        elif self.shield_ab.is_active:
            shield_fill = int(
                self.shield_ab.durability / self.shield_ab.durability_init * bar_wd
            )
            shield_color = YELLOW
        else:
            shield_fill = bar_wd
            shield_color = GREEN

        # BURST FILL
        now = pygame.time.get_ticks()
        elapsed = now - self.bullet_burst_ab.burst_timer
        progress = min(elapsed / self.bullet_burst_ab.burst_cd, 1.0)
        if progress < 1.0:
            burst_fill = int(progress * bar_wd)
            burst_color = RED
        else:
            burst_fill = bar_wd
            burst_color = GREEN

        # BAR FILL
        pygame.draw.rect(
            screen, shield_color, (shield_rect.x, shield_rect.y, shield_fill, bar_ht)
        )
        pygame.draw.rect(
            screen, burst_color, (burst_rect.x, burst_rect.y, burst_fill, bar_ht)
        )

        # BAR BORDER
        pygame.draw.rect(screen, BLACK, shield_rect, 2)
        pygame.draw.rect(screen, BLACK, burst_rect, 2)

        screen.blit(shield_label, shield_label_rect)
        screen.blit(burst_label, burst_label_rect)

    def display_current_weap(self, win_ht, current_weap, screen):
        bot_padding = 40
        font = pygame.font.Font(REGULAR, 30)

        weap_label = font.render(current_weap, True, WHITE)
        weap_label.set_alpha(32)
        weap_label_rect = weap_label.get_rect(
            bottomleft=(bot_padding, win_ht - bot_padding)
        )

        screen.blit(weap_label, weap_label_rect)
