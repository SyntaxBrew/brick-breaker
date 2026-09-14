from typing import Optional

import pygame
from math import sqrt
from .game_object import GameObject
from src.config import *
from time import time


class Ball(GameObject):
    BALL_TEXTURE: Optional[pygame.Surface] = None

    def __init__(self, pos, size, color):
        super().__init__(pos, size, color, self.get_ball_texture())
        self.speed = BALL_SPEED
        self.hit_damage = BALL_DAMAGE
        self.last_hit_brick = time()
        self.brick_hit_cooldown = 0.03

        self.last_non_colliding_pos = pos
        self.is_colliding = False
        self.is_dead = False

        self.bounce_sound = pygame.mixer.Sound("assets/audio/ball_bounce.mp3")
        self.bounce_sound.set_volume(0.1)
        self.destroy_sound = pygame.mixer.Sound("assets/audio/ball_destroy.mp3")

    def is_out_of_bounds(self):
        return self.rect.top > SCREEN_HEIGHT

    def can_hit_brick(self, now: float):
        return now - self.last_hit_brick >= self.brick_hit_cooldown

    def normalize_velocity(self):
        magnitude = sqrt(self.velocity_x ** 2 + self.velocity_y ** 2)
        if magnitude != 0:
            self.velocity_x = self.velocity_x / magnitude * self.speed
            self.velocity_y = self.velocity_y / magnitude * self.speed

    def bounce_x(self):
        self.velocity_x = -self.velocity_x
        self.bounce_sound.play()

    def bounce_y(self):
        self.velocity_y = -self.velocity_y
        self.bounce_sound.play()

    def update(self):
        super().update()
        self.is_colliding = False
        if self.rect.top < 0:
            self.rect.top = 0
            self.bounce_y()
        # if self.rect.bottom > SCREEN_HEIGHT:
        #self.rect.bottom = SCREEN_HEIGHT
        #self.bounce_y()
        if self.rect.left < 0:
            self.rect.left = 0
            self.bounce_x()
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.bounce_x()

    def die(self):
        self.destroy_sound.play()
        self.is_dead = True

    def draw_to(self, screen: pygame.Surface):
        super().draw_to(screen)
        #pygame.draw.rect(screen, pygame.Color("white"), self.rect, 2)

    @classmethod
    def get_ball_texture(cls):
        if cls.BALL_TEXTURE is None:
            cls.BALL_TEXTURE = pygame.image.load("assets/images/ball.png").convert_alpha()
        return cls.BALL_TEXTURE

ball_sprites = pygame.sprite.Group()