import pygame


class GameObject(pygame.sprite.Sprite):
    def __init__(self, pos: tuple[int, int], size: tuple[int, int], color: pygame.Color, image=None):
        super().__init__()
        self.image = pygame.Surface(size)
        self.image.fill(color)
        if image is not None:
            self.image = pygame.transform.scale(image, size)

        self.original_image = self.image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.color = color

        # Custom Properties
        self.velocity_x = 0
        self.velocity_y = 0

    def update(self):
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

    def draw_to(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)

    def resize(self, size: tuple[int, int]):
        original_pos = self.rect.center
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect()
        self.rect.center = original_pos

    def restore(self):
        original_pos = self.rect.center
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = original_pos
