from random import uniform

import pygame
from .game_object import GameObject
from src.config import *
import src.state as state
from src.utils import darken


class PowerUp(GameObject):
    def __init__(self, pos, size, color, image, name):
        super().__init__(pos, size, color, image)
        self.name = name
        self.last_used = float("inf")
        self.is_active = True
        self.duration = 0

    def apply(self, game, now: float):
        pass

    def revert(self, game, now: float):
        pass

    def is_out_of_bounds(self):
        return self.rect.top > SCREEN_HEIGHT

    def has_duration_ended(self, now: float):
        return now - self.last_used >= self.duration

class ExtraLife(PowerUp):
    def __init__(self, pos, size):
        super().__init__(pos, size, pygame.Color("red"), pygame.image.load("assets/images/heart.png").convert_alpha(), "ExtraLife")

    def apply(self, game, now: float):
        game.increment_lives(1)

class ExtraTime(PowerUp):
    def __init__(self, pos, size):
        super().__init__(pos, size, pygame.Color("light blue"), pygame.image.load("assets/images/clock.png").convert_alpha(), "ExtraTime")

    def apply(self, game, now: float):
        game.last_started += 20

class ExtraBall(PowerUp):
    def __init__(self, pos, size):
        super().__init__(pos, size, pygame.Color("green"), pygame.image.load("assets/images/present.png").convert_alpha(), "ExtraBall")

    def apply(self, game, now: float):
        paddle = game.paddles[0]
        game.spawn_ball((paddle.rect.centerx, paddle.rect.centery - BALL_SIZE[1] * 2), BALL_SIZE, pygame.Color("green"))

class DoublePoints(PowerUp):
    def __init__(self, pos, size):
        super().__init__(pos, size, pygame.Color("green"), pygame.image.load("assets/images/coin.png").convert_alpha(), "DoublePoints")
        self.duration = 15

    def apply(self, game, now: float):
        self.last_used = now
        game.hit_point_score_multiplier = min(game.hit_point_score_multiplier * 2, MAX_HIT_POINT_SCORE_MULTIPLIER)
        state.CURRENT_SCORE_TEXT_COLOR = pygame.Color("yellow")
        game.update_current_score_text()

    def revert(self, game, now: float):
        game.hit_point_score_multiplier = HIT_POINT_SCORE_MULTIPLIER
        state.CURRENT_SCORE_TEXT_COLOR = SCORE_TEXT_COLOR
        game.update_current_score_text()

class SizeIncrease(PowerUp):
    def __init__(self, pos, size):
        super().__init__(pos, size, pygame.Color("green"), pygame.image.load("assets/images/plus_sign.png").convert_alpha(), "SizeIncrease")
        self.duration = 15

    def apply(self, game, now: float):
        self.last_used = now
        paddle = game.paddles[0]
        paddle.resize((paddle.rect.width + 64, PADDLE_SIZE[1]))

    def revert(self, game, now: float):
        game.paddles[0].restore()

class DoubleDamage(PowerUp):
    def __init__(self, pos, size):
        super().__init__(pos, size, pygame.Color("red"), pygame.image.load("assets/images/fist.png").convert_alpha(), "DoubleDamage")
        self.duration = 15

    def apply(self, game, now: float):
        self.last_used = now
        game.ball_damage_multiplier = min(game.ball_damage_multiplier * 2, MAX_BALL_DAMAGE_MULTIPLIER)

    def revert(self, game, now: float):
        game.ball_damage_multiplier = 1

class DoubleLuck(PowerUp):
    def __init__(self, pos, size):
        super().__init__(pos, size, pygame.Color("red"), pygame.image.load("assets/images/clover.png").convert_alpha(), "DoubleLuck")
        self.duration = 15

    def apply(self, game, now: float):
        self.last_used = now
        game.luck = min(game.luck * 2, 3)

    def revert(self, game, now: float):
        game.luck = 1


