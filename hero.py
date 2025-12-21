import arcade

PLAYER_IDLE = "demon_idle.png"
PLAYER_WALKING = "demon_walking.png"


class Hero(arcade.Sprite):
    def __init__(self):
        super().__init__()
        
        # Основные характеристики
        self.scale = 0.3
        self.speed = 300
        self.health = 100
        
        # Загрузка текстур
        self.idle_texture = arcade.load_texture(PLAYER_IDLE)
        self.texture = self.idle_texture
        self.walk_texture = arcade.load_texture(PLAYER_WALKING)
        self.is_walking = False

    def update_animation(self, delta_time: float = 1/60):
        """ Обновление анимации """

        if self.is_walking:
            self.texture = self.walk_texture
        else:
            self.texture = self.idle_texture