import sys
from time import sleep

from settings import Settings

from game_stats import GameStats
from scoreboard import Scoreboard
from ship import Ship
from bullet import Bullet
from alien import Alien
from button import Button

import pygame

class AlienInvasion:
    """Класс для управления ресурсами и поведением игры."""

    def __init__(self):
        """Инициализирует игру и создает игровые ресурсы."""
        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = Settings()

        self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height

        pygame.display.set_caption("Alien invasion")

        # Создание экземпляра для хранения игровой статистики.
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        # Цвет фона.
        self.bg_color = (230, 230, 230)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        # Игра 'Инопланетное вторжение' запускается в неактивном состоянии.
        self.game_active = False

        # Создание кнопки Play.
        self.play_button = Button(self, "Play")

    def _create_fleet(self):
        """Создание флота пришельцев"""
        # Создание пришельца и длбавление других пока остается место
        # Расстояние между пришельцами одну ширину и одну высоту пришельца
        import random
        alien = Alien(self)
        alien_width, alien_height  = alien.rect.size

        # Четкие границы экрана
        margin = alien_width
        available_width = self.settings.screen_width - (2 * margin)
        # Считаем макс кол-во колонок, которые физически влезут 
        max_cols = int(available_width // (2 * alien_width))
        
        row_number = 0
        current_y = alien_height

        
        while current_y < (self.settings.screen_height - 4 * alien_height):
            # Сужаем границы ряда с каждым шагом, чтобы получилась пирамида
            # Ряд 0: от қ до max_cols
            # Ряд 1: от 1 до max_cols - 1 и тд
            for col_number in range(row_number, max_cols - row_number):
                current_x = margin + col_number * (2 * alien_width)

                rand = random.random()
                if rand < 0.6:
                    alien_type = 'green'
                elif rand < 0.85:
                    alien_type = 'red'
                else:
                    alien_type = 'yellow'

                self._create_alien(current_x, current_y, alien_type)
    
            # Конец ряда сбрасываем значение х и инкремитируем значение у
            current_y += 2 * alien_height
            row_number += 1

    def _create_alien(self, x_position, y_position, alien_type):
        """Создает пришельца и размещает его в ряду"""
        new_alien = Alien(self, alien_type)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def run_game(self):
        """Запускает основной цикл игры."""
        while True:
            self._check_events()

            # Режим берсерка при аномалии:
            if self.stats.score >= 42:
                self.settings.ship_speed = 12.0
                self.settings.bullet_speed = 18.0    

            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()
            # Отображение последнего прорисованного экрана.
            pygame.display.flip()
            self.clock.tick(60)


    def _update_bullets(self):
            """Обновляет позиции снарядов и удаляет старые снаряды."""
            # Обновление позиции снарядов.
            self.bullets.update()
            # Удаление снарядов, вышедших за край экрана.
            for bullet in self.bullets.copy():
                if bullet.rect.bottom <= 0:
                    self.bullets.remove(bullet)

            self._check_bullet_alien_collisions()


    def _check_bullet_alien_collisions(self): 
            """Обрабатывает коллизии снарядов с пришельцами"""
            # Удаление снарядов и пришельцев, участвующих в коллизиях.
            collisions = pygame.sprite.groupcollide(
                self.bullets, self.aliens, True, True)
            if collisions:
                for aliens in collisions.values():
                    for alien in aliens:
                        # берем баллы из конкретного взорванного пришельца
                        self.stats.score += alien.points
                self.sb.prep_score()
                self.sb.check_high_score()
                 
            if not self.aliens:
                # Уничтожение существующих снарядов и создание нового флота.
                self.bullets.empty()
                self._create_fleet()
                self.settings.increase_speed()

                # Увеличение уровня.
                self.stats.level += 1
                self.sb.prep_level()
    
    def _check_aliens_bottom(self):
        """Проверяет, добрались ли пришельцы до нижнего края экрана."""
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                # Происходит то же, что при столкновении с кораблем.
                self._ship_hit()
                break


    def _update_aliens(self):
        """Обновляет позиции всех пришельцев. Включает хаос при счете >=42."""
        import random
        self._check_fleet_edges()
        self.aliens.update()

        if self.stats.score >= 42:
            for alien in self.aliens.sprites():
                # Случайное смещение по осям Х и Y для каждого пришельца
                alien.x += random.randint(-8, 8)
                alien.rect.y += random.randint(-6, 6)
                alien.rect.x = alien.x
        # Проверка колизий "Пришелец-корабль".
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # Проверить, сталкиваются ли пришельцы с нижним краем экрана.
        self._check_aliens_bottom()

    def _check_fleet_edges(self):
        """Реагирует на достижение пришельцем края экрана."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Опускает весь флот и меняет его направление."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= - 1


    def _check_events(self):
            # Отслеживание событий клавиатуры и мыши.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                elif event.type == pygame.KEYDOWN:
                    self._check_keydown_events(event)

                elif event.type == pygame.KEYUP:
                    self._check_keyup_events(event)   

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    self._check_play_button(mouse_pos)


    def _check_play_button(self, mouse_pos):
        """Запускает новую игру при нажатии кнопки Play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        # Проверяем, что кликнули по кнопке и игра сейчас не активна.
        if button_clicked and not self.game_active:
            self._start_game()
        # Просто вызывыем новый метод.            

    def _start_game(self):
        """Разгружает логику старта игры для вызова кнопкой мыши или клавишей P."""
        # Сброс игровых настроек (скорость и т.д.)
        self.settings.initialize_dynamic_settings()

        # Сброс игровой статистики.
        self.stats.reset_stats()
        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()
        self.game_active = True

        # Очистка групп aliens and bullets.
        self.bullets.empty()
        self.aliens.empty()

        # Создание нового флота и размещение корабля в центре.
        self._create_fleet()
        self.ship.center_ship()

        # Указатель мыши скрывается.
        pygame.mouse.set_visible(False)


    def _check_keydown_events(self, event):
        """Реагирует на нажатия клавиш."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

        # Добавляем проверку для клавиши Р
        elif event.key == pygame.K_p:
            if not self.game_active:
                self._start_game()

    
    def _fire_bullet(self):
        """Создание нового снаряда и включение его в группу bullets."""
        # Если аномалия включена, стреляем игнорируя bullets_allowed
        if self.stats.score >= 42 or len(self.bullets) < self.settings.bullets_allowed:    
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)


    def _ship_hit(self):
        """Обрабатывает столкновение коробля с пришельцем."""
        if self.stats.ships_left > 0:
            # Уменьшение ships_left и обновление панели счета.
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            # Очистка групп aliens и bullets.
            self.aliens.empty()
            self.bullets.empty()

            # Создание нового флота и размещение коробля в центре.
            self._create_fleet()
            self.ship.center_ship()

            # Пауза.
            sleep(0.5)

        else:
            self.game_active = False
            pygame.mouse.set_visible(True)

    def _check_keyup_events(self,event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _update_screen(self):
        """При каждом проходе цикла перерисовывается экран."""
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.ship.blitme()
        self.aliens.draw(self.screen)

        # Вывод информации о счете.
        self.sb.show_score()

        # Кнопка Play отображается в том случае, если игра неактивна.
        if not self.game_active:
            self.play_button.draw_button()


if __name__ == '__main__':
    # Создание экземпляра и запуск игры.
    ai = AlienInvasion()
    ai.run_game()