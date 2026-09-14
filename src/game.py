import math
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
pygame.init()
pygame.display.set_caption("Breakout")
icon_surface = pygame.transform.scale(pygame.image.load("assets/images/icon.png"), (32, 32))
pygame.display.set_icon(icon_surface)

from sys import exit
from typing import Optional
from time import time
from random import randint, choices
from typing import Optional

from config import *
from utils import get_distance, darken
import src.state as state

from classes.ball import Ball
from classes.paddle import Paddle
from classes.brick import Brick
from classes.powerup import ExtraTime, ExtraLife, SizeIncrease, ExtraBall, DoublePoints, DoubleDamage, DoubleLuck

TOTAL_PADDING_WIDTH = (BRICKS_PER_ROW - 1) * BRICK_PADDING
TOTAL_WIDTH = BRICKS_PER_ROW * BRICK_WIDTH + TOTAL_PADDING_WIDTH
START_X = (SCREEN_WIDTH - TOTAL_WIDTH) // 2
COLOR_LEN = len(BRICK_COLORS)

class Game:
    POWERUPS = [
        ExtraTime,
        ExtraLife,
        ExtraBall,
        SizeIncrease,
        DoublePoints,
        DoubleDamage,
        DoubleLuck
    ]
    POWERUPS_WEIGHT = [
        100,
        25,
        75,
        100,
        75,
        75,
        10,
    ]
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        now = time()
        self.lives = 3
        self.game_over = False
        self.game_won = False
        self.last_died = float("inf")
        self.last_started = now
        self.time_limit = TIME_LIMIT
        self.current_score = 0
        self.luck = 1
        self.hit_point_score_multiplier = HIT_POINT_SCORE_MULTIPLIER
        self.ball_damage_multiplier = BALL_DAMAGE_MULTIPLIER

        self.paddles = []
        self.balls = []
        self.bricks = []
        self.powerups = []
        self.used_powerups = {}
        self.ball_count = 0
        self.brick_count = 0

        self.music_channel = pygame.mixer.find_channel()
        self.background_music = pygame.mixer.Sound("assets/audio/background_music.mp3")
        self.background_music.set_volume(0.1)
        self.music_channel.play(self.background_music, -1)

        self.death_text_font = pygame.font.Font(FONT_PATH, 64)
        self.death_text_surface: Optional[pygame.Surface] = None
        self.death_text_rect: Optional[pygame.Rect] = None
        self.update_death_screen_text("")

        self.game_over_timer_font = pygame.font.Font(FONT_PATH, 32)
        self.game_over_timer_surface: Optional[pygame.Surface] = None
        self.game_over_timer_rect: Optional[pygame.Rect] = None
        self.update_game_over_timer_text(now)

        self.death_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.death_overlay.fill(pygame.Color("black"))
        self.death_overlay.set_alpha(128)

        self.win_text_font = pygame.font.Font(FONT_PATH, 64)
        self.win_text_surface: Optional[pygame.Surface] = None
        self.win_text_rect: Optional[pygame.Rect] = None
        self.update_win_screen_text("")

        self.win_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.win_overlay.fill(pygame.Color("black"))
        self.win_overlay.set_alpha(128)

        self.score_text_font = pygame.font.Font(FONT_PATH, 32)
        self.score_text_surface: Optional[pygame.Surface] = None
        self.score_text_rect: Optional[pygame.Rect] = None
        self.update_current_score_text()

        self.lives_text_font = pygame.font.Font(FONT_PATH, 24)
        self.lives_text_surface: Optional[pygame.Surface] = None
        self.lives_text_rect: Optional[pygame.Rect] = None
        self.update_lives_text()

        self.timer_text_font = pygame.font.Font(FONT_PATH, 32)
        self.timer_text_surface: Optional[pygame.Surface] = None
        self.timer_text_rect: Optional[pygame.Rect] = None
        self.update_timer_text(now)


        self.paddles.append(
            Paddle(
                (SCREEN_CENTERX, SCREEN_HEIGHT - PADDLE_SIZE[1] // 2 - 20),
                PADDLE_SIZE,
                pygame.Color(0, 0, 128, 0)
            )
        )

        for _ in range(BALL_COUNT):
            self.spawn_ball()
        self.spawn_bricks()

    def restart(self, now: float):
        self.last_died = float("inf")
        self.paddles.clear()
        self.balls.clear()
        self.ball_count = 0

        self.paddles.append(
            Paddle(
                (SCREEN_CENTERX, SCREEN_HEIGHT - PADDLE_SIZE[1] // 2 - 20),
                PADDLE_SIZE,
                pygame.Color(0, 0, 128, 0)
            )
        )
        for _ in range(BALL_COUNT):
            self.spawn_ball()

        self.update_current_score_text()
        self.update_timer_text(now)

    def reset(self, now):
        self.game_over = False
        self.lives = 3
        self.current_score = 0

        self.last_died = float("inf")
        self.last_started = now
        self.ball_count = 0
        self.brick_count = 0

        self.paddles.clear()
        self.balls.clear()
        self.bricks.clear()

        for powerup in self.used_powerups.values():
            powerup.revert(self, now)

        self.powerups.clear()
        self.used_powerups.clear()

        self.paddles.append(
            Paddle(
                (SCREEN_CENTERX, SCREEN_HEIGHT - PADDLE_SIZE[1] // 2 - 20),
                PADDLE_SIZE,
                pygame.Color(0, 0, 128, 0)
            )
        )
        for _ in range(BALL_COUNT):
            self.spawn_ball()
        self.spawn_bricks()

        self.update_current_score_text()
        self.update_lives_text()
        self.update_timer_text(now)

        self.music_channel.stop()
        self.music_channel.play(self.background_music, -1)

    def spawn_ball(
        self,
        pos=(SCREEN_CENTERX, SCREEN_CENTERY + (BRICK_ROWS * (BRICK_HEIGHT + BRICK_PADDING)) // 4),
        ball_size=BALL_SIZE,
        color=None
    ):
        self.ball_count += 1
        ball = Ball(
            pos,
            BALL_SIZE,
            pygame.Color(0, 0, 0)
        )
        if color is not None:
            ball.image.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
        ball.velocity_y = BALL_SPEED
        ball.normalize_velocity()
        self.balls.append(ball)

    def spawn_paddle(self, pos=(SCREEN_CENTERX, SCREEN_HEIGHT - PADDLE_SIZE[1] // 2 - 20), size=PADDLE_SIZE, color=None):
        paddle =  Paddle(
            pos,
            size,
            pygame.Color(0, 0, 128, 0)
        )
        if color is not None:
            paddle.image.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
        self.paddles.append(paddle)

    def remove_ball(self, ball: Ball):
        self.ball_count -= 1
        ball.die()

    def spawn_random_powerup(self, pos: tuple[int, int]):
        powerup = choices(self.POWERUPS, self.POWERUPS_WEIGHT)[0](pos, POWERUP_SIZE)
        powerup.velocity_y = POWERUP_SPEED
        self.powerups.append(powerup)

    def increment_lives(self, amount=1):
        self.lives += 1
        self.update_lives_text()

    def decrement_lives(self, amount=1):
        self.lives -= 1
        self.update_lives_text()

    def update_timer_text(self, now: float):
        time_elapsed = now - self.last_started
        self.timer_text_surface = self.timer_text_font.render(
            f"Time: {max(0, self.time_limit - time_elapsed):.0f}s",
            False,
            pygame.Color("white")
        )
        self.timer_text_rect = self.timer_text_surface.get_rect()
        self.timer_text_rect.x, self.timer_text_rect.y = SCREEN_WIDTH - self.timer_text_rect.width - 4, 4

    def is_timer_over(self, now: float):
        return now - self.last_started >= self.time_limit

    def update_current_score_text(self):
        self.score_text_surface = self.score_text_font.render(
            f"Score: {self.current_score} {f"({self.hit_point_score_multiplier}x)" if self.hit_point_score_multiplier > 1 else ""}",
            False,
            state.CURRENT_SCORE_TEXT_COLOR
        )
        self.score_text_rect = self.score_text_surface.get_rect()
        self.score_text_rect.x, self.score_text_rect.y = 4, 4

    def update_game_over_timer_text(self, now: float):
        self.game_over_timer_surface = self.game_over_timer_font.render(
            f"{GAME_OVER_TIME - (now - self.last_died):.2f}s",
            False,
            pygame.Color("yellow") if self.game_won else pygame.Color("red")
        )
        self.game_over_timer_rect = self.game_over_timer_surface.get_rect()
        self.game_over_timer_rect.center = (
            self.death_text_rect.centerx,
            self.death_text_rect.centery + self.death_text_rect.height
        )

    def update_death_screen_text(self, text: str):
        self.death_text_surface = self.death_text_font.render(
            text,
            False,
            pygame.Color("red")
        )
        self.death_text_rect = self.death_text_surface.get_rect()
        self.death_text_rect.center = (SCREEN_CENTERX, SCREEN_CENTERY - 32)

    def update_win_screen_text(self, text: str):
        self.win_text_surface = self.win_text_font.render(
            text,
            False,
            pygame.Color("yellow")
        )
        self.win_text_rect = self.win_text_surface.get_rect()
        self.win_text_rect.center = (SCREEN_CENTERX, SCREEN_CENTERY - 32)

    def update_lives_text(self):
        self.lives_text_surface = self.lives_text_font.render(
            f"Lives: {self.lives}",
            False,
            pygame.Color("white")
        )
        self.lives_text_rect = self.lives_text_surface.get_rect()
        self.lives_text_rect.center = (
            SCREEN_CENTERX,
            self.lives_text_rect.height
        )

    def increment_score(self, amount=1):
        self.current_score += amount * self.hit_point_score_multiplier
        self.update_current_score_text()

    def trigger_game_over(self, now: float):
        self.last_died = now
        self.game_won = False
        self.game_over = True

    def trigger_game_won(self, now: float):
        self.last_died = now
        self.game_won = True
        self.game_over = True

    def loop(self):
        now = time()
        self.handle_events(now)
        if now - self.last_died >= GAME_OVER_TIME:
            self.quit()
        if (self.current_score >= WINNING_SCORE or self.brick_count <= 0) and not self.game_over:
            self.update_win_screen_text("YOU WIN")
            self.trigger_game_won(now)
        if self.is_timer_over(now) and not self.game_over:
            self.trigger_game_over(now)
            self.update_death_screen_text("NO TIME")

        for ball in self.balls:
            if ball.is_dead:
                continue
            ball.update()
            if ball.is_out_of_bounds() and not ball.is_dead:
                self.remove_ball(ball)
            self.handle_paddle_collisions(ball)
            self.handle_brick_collisions(ball, now)
            if not ball.is_colliding:
                ball.last_non_colliding_pos = ball.rect.center
        self.balls[:] = [ball for ball in self.balls if not ball.is_dead]

        if self.ball_count == 0 and not self.game_over:
            self.decrement_lives()
            if self.lives > 0:
                self.ball_count = -1
            else:
                self.trigger_game_over(now)
                self.update_death_screen_text("NO BALLS")

        mouse = pygame.mouse
        if mouse.get_focused():
            self.paddles[0].set_pos(mouse.get_pos())

        for powerup in self.powerups:
            powerup.update()
            if powerup.is_out_of_bounds():
                powerup.is_active = False
        self.powerups[:] = [powerup for powerup in self.powerups if powerup.is_active]

        for paddle in self.paddles:
            self.handle_powerup_collisions(paddle, now)

        for powerup in list(self.used_powerups.values()):
            if powerup.has_duration_ended(now):
                powerup.revert(self, now)
                del self.used_powerups[powerup.name]

        self.screen.fill(BACKGROUND_COLOR)
        self.draw_all(now)
        pygame.display.update()
        self.clock.tick(FRAME_RATE)

    def draw_all(self, now: float):
        for ball in self.balls:
            ball.draw_to(self.screen)
        for paddle in self.paddles:
            paddle.draw_to(self.screen)
        self.paddles[0].draw_to(self.screen)
        for brick in self.bricks:
            brick.draw_to(self.screen)
        for powerup in self.powerups:
            powerup.draw_to(self.screen)

        if self.game_over:
            self.update_game_over_timer_text(now)
            if self.game_won:
                self.screen.blit(self.win_overlay, (0, 0))
                self.screen.blit(self.win_text_surface, self.win_text_rect)
                self.screen.blit(self.game_over_timer_surface, self.game_over_timer_rect)
            else:
                self.screen.blit(self.death_overlay, (0, 0))
                self.screen.blit(self.death_text_surface, self.death_text_rect)
                self.screen.blit(self.game_over_timer_surface, self.game_over_timer_rect)
        else:
            self.update_timer_text(now)

        self.screen.blit(self.timer_text_surface, self.timer_text_rect)
        self.screen.blit(self.score_text_surface, self.score_text_rect)
        self.screen.blit(self.lives_text_surface, self.lives_text_rect)

    def handle_powerup_collisions(self, paddle: Paddle, now: float):
        collided_powerups = []
        for index in paddle.rect.collidelistall(self.powerups):
            collided_powerups.append(self.powerups[index])
        for powerup in collided_powerups:
            powerup.apply(self, now)
            if powerup.duration != 0:
                self.used_powerups.update({powerup.name: powerup})
            self.powerups.remove(powerup)

    def handle_paddle_collisions(self, ball: Ball):
        colliding_paddles = ball.rect.collidelistall(self.paddles)
        if not colliding_paddles:
            return
        ball.is_colliding = True
        for index in colliding_paddles:
            paddle = self.paddles[index]
            paddle.bounce_ball(ball)
            break

    def handle_brick_collisions(self, ball: Ball, now: float):
        colliding_bricks = ball.rect.collidelistall(self.bricks)
        if not colliding_bricks:
            return

        closest_brick: Optional[Brick] = None
        closest_distance = float("inf")
        ball.is_colliding = True

        for index in colliding_bricks:
            brick = self.bricks[index]
            closest_x = max(brick.rect.left, min(ball.rect.centerx, brick.rect.right))
            closest_y = max(brick.rect.top, min(ball.rect.centery, brick.rect.bottom))
            distance = get_distance(ball.rect.center, (closest_x, closest_y))
            if distance < closest_distance:
                closest_distance = distance
                closest_brick = brick

        if closest_brick is not None:
            closest_brick.bounce_ball(ball)
            if ball.can_hit_brick(now):
                ball.last_hit_brick = now
                damage_dealt = closest_brick.hit(ball.hit_damage * self.ball_damage_multiplier)
                self.increment_score(damage_dealt)
            if closest_brick.is_destroyed():
                if randint(0, 100) <= POWERUP_CHANCE * self.luck:
                    self.spawn_random_powerup(closest_brick.rect.center)
                self.brick_count -= 1
                closest_brick.destroy_sound.play()

        self.bricks[:] = [brick for brick in self.bricks if not brick.is_destroyed()]

    def spawn_bricks(self):
        start_y = self.score_text_rect.height + BRICK_HEIGHT // 2
        for y in range(BRICK_ROWS):
            row = BRICK_ROWS - y
            hit_points = math.ceil(row / 2)
            for x in range(BRICKS_PER_ROW):
                brick = Brick(
                    (
                        START_X + x * (BRICK_WIDTH + BRICK_PADDING) + BRICK_WIDTH // 2,
                        start_y + y * (BRICK_HEIGHT + BRICK_PADDING) + BRICK_HEIGHT // 2
                    ),
                    BRICK_SIZE,
                    pygame.Color(
                        darken(BRICK_COLORS[COLOR_LEN-1 - int(((row + 1) / BRICK_ROWS) * COLOR_LEN-1)], 0.5)
                    )
                )
                brick.set_hit_points(hit_points)
                self.bricks.append(brick)
        self.brick_count = len(self.bricks)

    def handle_events(self, now: float):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Game.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    if self.game_over:
                        self.reset(now)
                    elif self.ball_count == -1:
                        self.restart(now)
                if event.key == pygame.K_m:
                    if self.music_channel.get_busy():
                        self.music_channel.stop()
                    else:
                        self.music_channel.play(self.background_music, -1)

    @staticmethod
    def quit():
        pygame.quit()
        exit()
