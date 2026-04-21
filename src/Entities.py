import math

import pygame


class BoxEntity(pygame.sprite.Sprite):
    def __init__(self, ent_wd, ent_ht, x_cor, y_cor, color) -> None:
        super().__init__()

        self.ent_wd = ent_wd
        self.ent_ht = ent_ht
        self.x_cor = x_cor
        self.y_cor = y_cor
        self.color = color

        self.image = pygame.Surface((self.ent_wd, self.ent_ht))
        self.image.fill(self.color)
        self.rect = self.image.get_rect(center=(self.x_cor, self.y_cor))

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class CircEntity(pygame.sprite.Sprite):
    def __init__(self, radius, x_cor, y_cor, color) -> None:
        super().__init__()

        self.radius = radius
        self.x_cor = x_cor
        self.y_cor = y_cor
        self.color = color

        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            self.image, self.color, (self.radius, self.radius), self.radius
        )
        self.rect = self.image.get_rect(center=(self.x_cor, self.y_cor))
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class CrossEntity(pygame.sprite.Sprite):
    def __init__(self, size, x_cor, y_cor, color) -> None:
        super().__init__()

        self.size = size
        self.x_cor = x_cor
        self.y_cor = y_cor
        self.color = color

        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)

        third = self.size // 3
        # horizontal bar
        pygame.draw.rect(self.image, self.color, (0, third, self.size, third))
        # vertical bar
        pygame.draw.rect(self.image, self.color, (third, 0, third, self.size))

        self.rect = self.image.get_rect(center=(self.x_cor, self.y_cor))

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class TriEntity(pygame.sprite.Sprite):
    def __init__(self, size, x_cor, y_cor, color) -> None:
        super().__init__()

        self.size = size
        self.x_cor = x_cor
        self.y_cor = y_cor
        self.color = color

        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        tri_pts = [
            (self.size // 2, 0),  # top center
            (0, self.size),  # bot left
            (self.size, self.size),  # bot right
        ]
        pygame.draw.polygon(self.image, self.color, tri_pts)
        self.rect = self.image.get_rect(center=(self.x_cor, self.y_cor))
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class OctEntity(pygame.sprite.Sprite):
    def __init__(self, size, x_cor, y_cor, color) -> None:
        super().__init__()

        self.size = size
        self.x_cor = x_cor
        self.y_cor = y_cor
        self.color = color

        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)

        center_offset = self.size // 2
        radius = self.size // 2
        oct_pts = []

        for i in range(8):
            angle_deg = 45 * i + 22.5
            angle_rad = math.radians(angle_deg)

            x = center_offset + radius * math.cos(angle_rad)
            y = center_offset + radius * math.sin(angle_rad)
            oct_pts.append((x, y))

        pygame.draw.polygon(self.image, self.color, oct_pts)
        self.rect = self.image.get_rect(center=(self.x_cor, self.y_cor))

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class DiamondEntity(pygame.sprite.Sprite):
    def __init__(self, size, x_cor, y_cor, color) -> None:
        super().__init__()

        self.size = size
        self.x_cor = x_cor
        self.y_cor = y_cor
        self.color = color

        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)

        mid_pt = self.size // 2

        top_tri = [
            (mid_pt, 0),  # top point
            (0, mid_pt),  # left middle
            (self.size, mid_pt),  # right middle
        ]
        bot_tri = [
            (mid_pt, self.size),  # bottom point
            (0, mid_pt),  # left middle
            (self.size, mid_pt),  # right middle
        ]

        pygame.draw.polygon(self.image, self.color, top_tri)
        pygame.draw.polygon(self.image, self.color, bot_tri)

        self.rect = self.image.get_rect(center=(self.x_cor, self.y_cor))
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class StarEntity(pygame.sprite.Sprite):
    def __init__(
        self, size, x_cor, y_cor, color, num_points=5, depth_ratio=0.4
    ) -> None:
        super().__init__()

        self.size = size
        self.x_cor = x_cor
        self.y_cor = y_cor
        self.color = color

        self.num_points = num_points
        self.total_vertices = num_points * 2

        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)

        center_offset = self.size // 2
        outer_radius = self.size // 2
        inner_radius = outer_radius * depth_ratio

        star_pts = []
        angle_step = 360 / self.total_vertices

        for i in range(self.total_vertices):
            angle_rad = math.radians(angle_step * i - 90)

            curr_radius = outer_radius if i % 2 == 0 else inner_radius

            x = center_offset + curr_radius * math.cos(angle_rad)
            y = center_offset + curr_radius * math.sin(angle_rad)
            star_pts.append((x, y))

        pygame.draw.polygon(self.image, self.color, star_pts)

        self.rect = self.image.get_rect(center=(self.x_cor, self.y_cor))
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class GlassEntity(pygame.sprite.Sprite):
    def __init__(self, size, x_cor, y_cor, color) -> None:
        super().__init__()

        self.size = size
        self.x_cor = x_cor
        self.y_cor = y_cor
        self.color = color
        mid_pt = self.size // 2
        gap = 10

        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)

        tri_up = [
            (mid_pt, 0),
            (0, mid_pt - gap),
            (self.size, mid_pt - gap),
        ]
        tri_down = [
            (mid_pt, self.size),
            (0, mid_pt + gap),
            (self.size, mid_pt + gap),
        ]

        pygame.draw.polygon(self.image, self.color, tri_up)
        pygame.draw.polygon(self.image, self.color, tri_down)

        self.rect = self.image.get_rect(center=(self.x_cor, self.y_cor))
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class OmenEntity(pygame.sprite.Sprite):
    def __init__(self, size, x_cor, y_cor, color, rotation=0) -> None:
        super().__init__()

        self.size = size
        self.x_cor = x_cor
        self.y_cor = y_cor
        self.color = color
        self.rotation = rotation

        pad = 10
        self.orig_image = pygame.Surface(
            ((self.size * 3) + pad, (self.size * 2) + pad), pygame.SRCALPHA
        )

        mid_pt = self.size // 2
        width = 3
        inner_tri_pts = [
            ((7 * self.size + 4 * mid_pt) / 6, self.size / 3),
            ((7 * self.size + mid_pt) / 6, (5 * self.size) / 6),
            ((10 * self.size + mid_pt) / 6, (5 * self.size) / 6),
        ]
        base_tri_pts = [
            (self.size + mid_pt, 0),  # top center
            (self.size, self.size),  # bot left
            (self.size * 2, self.size),  # bot right
        ]
        right_tri_pts = [
            ((self.size + mid_pt) + pad, 0),  # top left corn
            (((self.size * 2) + mid_pt) + pad, 0),  # right tip
            ((self.size * 2) + pad, self.size),  # bottom left corn
        ]
        left_tri_pts = [
            ((self.size + mid_pt) - pad, 0),  # top right corn
            (mid_pt - pad, 0),  # left tip
            (self.size - pad, self.size),  # bottom right corn
        ]
        bot_tri_pts = [
            (self.size + mid_pt, (self.size * 2) + pad),  # bot tip
            (self.size, self.size + pad),  # left corn
            (self.size * 2, self.size + pad),  # right corn
        ]

        pygame.draw.polygon(
            self.orig_image,
            self.color,
            inner_tri_pts,
        )
        pygame.draw.polygon(
            self.orig_image,
            self.color,
            base_tri_pts,
            width,
        )
        pygame.draw.polygon(
            self.orig_image,
            self.color,
            right_tri_pts,
        )
        pygame.draw.polygon(
            self.orig_image,
            self.color,
            left_tri_pts,
        )
        pygame.draw.polygon(
            self.orig_image,
            self.color,
            bot_tri_pts,
        )

        self.image = pygame.transform.rotozoom(
            self.orig_image,
            self.rotation,
            1.0,
        )
        self.rect = self.image.get_rect(center=(self.x_cor, self.y_cor))
        self.mask = pygame.mask.from_surface(self.image)

    def update_rotation(self, rotation):
        self.rotation = rotation
        center = self.rect.center
        self.image = pygame.transform.rotozoom(self.orig_image, self.rotation, 1.0)
        self.rect = self.image.get_rect(center=center)
        self.mask = pygame.mask.from_surface(self.image)

    def lerp_rotation_to(self, target, speed=2):
        diff = ((self.rotation - target) + 180) % 360 - 180

        if abs(diff) <= speed:
            self.update_rotation(target)
        elif diff > 0:
            self.update_rotation(self.rotation - speed)
        else:
            self.update_rotation(self.rotation + speed)

    def lerp_rotation_to_zero(self, speed=2):
        self.lerp_rotation_to(0, speed)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
