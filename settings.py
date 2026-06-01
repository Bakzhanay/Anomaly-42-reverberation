class Settings:
    """Класс для настройки всей игры "Инопланетное вторжение"."""

    def __init__(self):
        """Инициализирует статические настройки игры."""
        # Параметры экрана.
        self.screen_width = 1100
        self.screen_height = 700
        self.bg_color = (15, 61, 71)

        # Настройки коробля.
        self.ship_speed = 1.5
        self.ship_limit = 3

        # Параметры снаряда.
        self.bullet_speed = 5
        self.bullet_width = 2
        self.bullet_height = 15
        self.bullet_color = (255, 215, 0)
        self.bullets_allowed = 3

        # Настройки пришельцев
        self.alien_speed = 5
        self.fleet_drop_speed = 10
        # fleet_direction = 1 обозночает движение вправо; а -1 - влево.
        self.fleet_direction = 1

        # Темп ускорения игры
        self.speedup_scale = 1.1
        # Темп роста стоимости пришельцев.
        self.score_scale = 1.5

    
    def initialize_dynamic_settings(self):
        """Инициализирует настройки, изменяющиейся в игре"""
        self.ship_speed = 5.0
        self.bullet_speed = 2.5
        self.alien_speed = 5.0

        # fleet_direction = 1 обозночает движение вправо; а -1 - влево.
        self.fleet_direction = 1

        # Подсчет очков
        self.alien_points = 1

    def increase_speed(self):
        """Увеличивает настройки скорости и стоимость пришельцев."""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale

        self.alien_points = int(self.alien_points * self.score_scale)
        print(self.alien_points)

        
