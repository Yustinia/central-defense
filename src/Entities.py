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
    def __init__(
        self,
        size,
        x_cor,
        y_cor,
        color,
    ) -> None:
        super().__init__()

        self.size = size
        self.x_cor = x_cor
        self.y_cor = y_cor
        self.color = color
        mid_pt = self.size // 2
        gap = 10

        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)

        tri_up = [
            (mid_pt, 0),  # The top peak
            (0, mid_pt - gap),  # Bottom-left of this triangle
            (self.size, mid_pt - gap),  # Bottom-right of this triangle
        ]

        # tri_down (Points toward the bottom of the screen)
        tri_down = [
            (mid_pt, self.size),  # The bottom peak
            (0, mid_pt + gap),  # Top-left of this triangle
            (self.size, mid_pt + gap),  # Top-right of this triangle
        ]

        pygame.draw.polygon(self.image, self.color, tri_up)
        pygame.draw.polygon(self.image, self.color, tri_down)

        self.rect = self.image.get_rect(center=(self.x_cor, self.y_cor))
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
