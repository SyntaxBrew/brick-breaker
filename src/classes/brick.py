from typing import Optional

import pygame
from .game_object import GameObject
from .ball import Ball
from src.config import *
import src.state as state
from src.utils import darken
from random import uniform


class Brick(GameObject):
    BRICK_TEXTURE: Optional[pygame.Surface] = None
    CRACK_TEXTURE: Optional[pygame.Surface] = None

    def __init__(self, pos, size, color):
        super().__init__(pos, size, color)
        self._max_hit_points = -1
        self.hit_points = -1
        self.crack_texture = self.get_crack_texture(color)
        self.text_font = pygame.font.Font(FONT_PATH, 20)
        self.text_surface = self.text_font.render(str(self.hit_points), False, pygame.Color("white"))
        self.text_rect = self.text_surface.get_rect()

        self.destroy_sound = pygame.mixer.Sound("assets/audio/brick_destroy.mp3")
        self.destroy_sound.set_volume(0.2)

    def bounce_ball(self, ball: Ball):
        overlap = ball.rect.clip(self.rect)
        ball.rect.center = ball.last_non_colliding_pos
        if abs(overlap.width - overlap.height) <= ball.speed / 2:
            x_side = ball.rect.left >= self.rect.right or ball.rect.right <= self.rect.left
            y_side = ball.rect.top >= self.rect.bottom or ball.rect.bottom <= self.rect.top
            if x_side and y_side:
                ball.bounce_x()
                ball.bounce_y()
            elif x_side:
                ball.bounce_x()
            elif y_side:
                ball.bounce_y()
            return
        if overlap.height < overlap.width:
            ball.bounce_y()
        elif overlap.width < overlap.height:
            ball.bounce_x()

    def set_hit_points(self, hit_points: int):
        self._max_hit_points = hit_points
        self.hit_points = hit_points
        self.image.fill(self.color)
        self.update_crack_texture()
        self.update_text()


    def hit(self, amount: int=1):
        original_hit_points = self.hit_points
        self.hit_points = max(self.hit_points - amount, 0)
        self.image.fill(self.color)
        self.update_crack_texture()
        self.update_text()

        return original_hit_points - self.hit_points

    def update_crack_texture(self):
        progress = self.hit_points / self._max_hit_points
        self.crack_texture.set_alpha(int(255 * (1 - progress ** 2)))
        self.image = self.image.copy()
        self.image.blit(self.crack_texture, (0, 0))

    def update_text(self):
        self.text_surface = self.text_font.render(f"{self.hit_points}", False, state.CURRENT_BRICK_TEXT_COLOR)
        self.image.blit(self.text_surface, (
            self.rect.width // 8 - self.text_rect.width // 8,
            self.rect.height // 2 - self.text_rect.height // 2,
        ))

    def is_destroyed(self):
        return self.hit_points == 0

    def draw_to(self, screen: pygame.Surface):
        super().draw_to(screen)
        pygame.draw.rect(screen, darken(self.color, 2), self.rect, 2)

    @classmethod
    def get_brick_texture(cls):
        if cls.BRICK_TEXTURE is None:
            cls.BRICK_TEXTURE = pygame.image.load("assets/images/brick.png").convert_alpha()
        return cls.BRICK_TEXTURE

    @classmethod
    def get_crack_texture(cls, color: pygame.Color):
        if cls.CRACK_TEXTURE is None:
            cls.CRACK_TEXTURE = pygame.transform.scale(
                pygame.image.load("assets/images/crack.png"),
                (BRICK_WIDTH * 4, BRICK_HEIGHT * 4)
            ).convert_alpha()
           # cls.CRACK_TEXTURE.fill(darken(color, 1))
        return cls.CRACK_TEXTURE

brick_sprites = pygame.sprite.Group()