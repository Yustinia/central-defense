import pygame


class Dash:
    def __init__(self) -> None:
        self.dash_spd = 5
        self.dash_cd = 500
        self.dash_timer = 0

    def do_dash(self, dx, dy):
        now = pygame.time.get_ticks()
        if now - self.dash_timer < self.dash_cd:
            return dx, dy
        if dx == 0 and dy == 0:
            return dx, dy
        self.dash_timer = now

        return dx * self.dash_spd, dy * self.dash_spd
