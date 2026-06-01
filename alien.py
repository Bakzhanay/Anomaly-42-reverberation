import pygame
from pygame.sprite import Sprite
import random

class Alien(Sprite):
    """Класс для управления пришельцами."""

    def __init__(self, ai_game, alien_type = 'green'):
        """Инициализирует пришельца и задает его начальную позицию."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.type = alien_type

        self.ai_game = ai_game
        
        # Загрузка картинки в зависимости от типа
        if self.type == 'green':
            self.image_right = pygame.image.load('images/alien_green.png')
            self.points = 1
        elif self.type == 'red':
            self.image_right = pygame.image.load('images/alien_red.png')
            self.points = 3
        elif self.type == 'yellow':
            self.image_right = pygame.image.load('images/alien_yellow.png')
            self.points = 5

        self.rect = self.image_right.get_rect() 
        # Создаем отзеркаленную копию 
        self.image_left = pygame.transform.flip(self.image_right, True, False)
        # Изначально пришелец смотрит вправо
        self.image = self.image_right

        # Каждый новый пришелец появляется в верхнем левом углу экрана.
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height 
        #Сохранение точной горизонтальной позиции пришельца.
        self.x = float(self.rect.x)

    def check_edges(self):
        """Возвращает True, если пришелец находится у края экрана."""
        screen_rect = self.screen.get_rect()
        if self.x >= (screen_rect.right - self.rect.width) and self.settings.fleet_direction == 1:
            return True
        
        if self.x <=0 and self.settings.fleet_direction == -1:
            return True

    def update(self):
        """Перемещает пришельца вправо"""
        self.x += (self.settings.alien_speed * self.settings.fleet_direction)
        self.rect.x = self.x

        if self.ai_game.stats.score >= 42:
            import random
            self.rect.x += random.randint(-3, 3)

    # Меняем картину в зависимости от направления
        if self.settings.fleet_direction == 1:
            self.image = self.image_right # Плывем направо
        else:
            self.image = self.image_left #Плывем налево

