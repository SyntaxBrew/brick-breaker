from typing import Optional

import pygame

from .game_object import GameObject
from .ball import Ball
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.utils import clamp

class Paddle(GameObject):
    PADDLE_TEXTURE: Optional[pygame.Surface] = None

    def __init__(self, pos, size, color):
        super().__init__(pos, size, color, self.get_paddle_texture())
        self.speed = 6
        self.y_lock = pos[1]
        self.min_x = self.rect.width // 2
        self.max_x = SCREEN_WIDTH - self.rect.width // 2
        self.hit_sound = pygame.mixer.Sound("assets/audio/paddle_hit.mp3")
        self.hit_sound.set_volume(0.1)

    def bounce_ball(self, ball: Ball):
        distance_from_center = ball.rect.centerx - self.rect.centerx
        ball.rect.center = ball.last_non_colliding_pos
        ball.velocity_x = clamp((distance_from_center / self.rect.width) * ball.speed, -ball.speed, ball.speed)
        ball.bounce_y()
        if ball.rect.y <= self.rect.y:
            ball.rect.bottom = self.rect.top
        else:
            ball.rect.top = self.rect.bottom
        ball.normalize_velocity()
        self.hit_sound.play()

    def set_pos(self, pos: tuple[int, int]):
        self.rect.center = (
            clamp(pos[0], self.min_x, self.max_x),
            self.y_lock
        )

    def update(self):
        super().update()

    def draw_to(self, screen: pygame.Surface):
        super().draw_to(screen)

    def resize(self, size: tuple[int, int]):
        super().resize(size)
        self.min_x = self.rect.width // 2
        self.max_x = SCREEN_WIDTH - self.rect.width // 2

    def restore(self):
        super().restore()
        self.min_x = self.rect.width // 2
        self.max_x = SCREEN_WIDTH - self.rect.width // 2

    @classmethod
    def get_paddle_texture(cls):
        if cls.PADDLE_TEXTURE is None:
            cls.PADDLE_TEXTURE = pygame.image.load("assets/images/paddle.png").convert_alpha()
        return cls.PADDLE_TEXTURE

paddle_sprites = pygame.sprite.Group()