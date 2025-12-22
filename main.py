import arcade
from pycode.hero import Hero

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 640
SCREEN_TITLE = "Тайловый Уровень — Вау!"
TILE_SCALING = 0.5  # Если тайлы 64x64, а хотим чтобы на экране были 64x64 — ставим 1.0

# ---------- Камера ----------
CAMERA_LERP = 0.12
DEAD_ZONE_W = int(SCREEN_WIDTH * 0.35)
DEAD_ZONE_H = int(SCREEN_HEIGHT * 0.45)


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BROWN_NOSE)

        # Здесь будут жить наши списки спрайтов из карты
        self.wall_list = None
        self.player_list = None
        self.player_sprite = None
        self.physics_engine = None
        self.key = False
        self.get_key = False
        self.door_opened = False
        self.claim_money_sound = arcade.load_sound('sounds/claim_money.wav')
        self.win_sound = arcade.load_sound("sounds/win_sound.wav")
        self.open_door_sound = arcade.load_sound('sounds/open_door.wav')
        
        # Камеры: мир и GUI
        self.world_camera = arcade.camera.Camera2D()  # Камера для игрового мира
        self.gui_camera = arcade.camera.Camera2D()  # Камера для объектов интерфейса

    def setup(self):
        """Настраиваем игру здесь. Вызывается при старте и при рестарте."""
        # Инициализируем списки спрайтов
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()  # Сюда попадёт слой Collision!

        # ===== ВОЛШЕБСТВО ЗАГРУЗКИ КАРТЫ! (почти без магии). =====
        # Грузим тайловую карту
        map_name = "map_tile.tmx"
        # Параметр 'scaling' ОЧЕНЬ важен! Умножает размер каждого тайла
        tile_map = arcade.load_tilemap(map_name, scaling=TILE_SCALING)

        # --- Достаём слои из карты как спрайт-листы ---
        self.key_list = tile_map.sprite_lists["key"]
        # Слой "walls" (стены) — просто для отрисовки
        self.wall_list = tile_map.sprite_lists["walls"]
        # Слой "chests" (сундуки) — красота!
        self.chests_list = tile_map.sprite_lists["money"]
        # Слой "exit" (выходы с уровня) — красота!
        self.exit_list = tile_map.sprite_lists["exit"]
        # САМЫЙ ГЛАВНЫЙ СЛОЙ: "Collision" — наши стены и платформы для физики!
        self.collision_list = tile_map.sprite_lists["collision"]
        self.background_list = tile_map.sprite_lists["background"]
        self.door_list = tile_map.sprite_lists["door"]
        self.door_collision_list = tile_map.sprite_lists["door_collision"]
        # --- Создаём игрока. ---
        # Карту загрузили, теперь создаём героя, который будет по ней бегать
        self.player_sprite = Hero()
        # Ставим игрока куда-нибудь на землю (посмотрите в Tiled, где у вас земля!)
        self.player_sprite.center_x = 128  # Примерные координаты
        self.player_sprite.center_y = 256  # Примерные координаты
        self.player_list.append(self.player_sprite)

        # --- Физический движок ---
        # Используем PhysicsEngineSimple, который знаем и любим
        # Он даст нам движение и коллизии со стенами (self.wall_list)!
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite, self.collision_list
        )
        self.door_engine = arcade.PhysicsEngineSimple(
            self.player_sprite, self.door_list
        )
        arcade.play_sound(self.win_sound)

    def on_draw(self):
        """Отрисовка экрана."""
        self.clear()

        # Рисуем слои карты в правильном порядке (фон -> земля -> платформы -> декорации -> игрок)
        self.world_camera.use()
        self.background_list.draw()
        self.wall_list.draw()
        self.chests_list.draw()
        if not self.door_opened:
            self.door_list.draw()
        if self.key:
            self.key_list.draw()
        self.exit_list.draw()
        self.player_list.draw()
        
        # 2) GUI
        self.gui_camera.use()

        # self.collision_list.draw()  # Обычно НЕ рисуем слой коллизий в финальной игре, но для отладки бывает полезно

    def on_update(self, delta_time):
        """Обновление логики игры."""
        # Обновляем физический движок (двигает игрока и проверяет стены)
        self.physics_engine.update()
        if not self.door_opened:
            self.door_engine.update()
        
        position = (
            self.player_sprite.center_x,
            self.player_sprite.center_y
        )
        self.world_camera.position = arcade.math.lerp_2d(
            self.world_camera.position,
            position,
            CAMERA_LERP  # Плавность следования камеры
        )
        
        coins_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.chests_list)
        if coins_hit_list:
            for coin in coins_hit_list:
                self.chests_list.remove(coin)
                arcade.play_sound(self.claim_money_sound)
        
        if not self.chests_list and not self.get_key:
            self.key = True
            
        get_key = arcade.check_for_collision(self.player_sprite, self.key_list[0])
        if get_key and self.key:
            self.key = False
            self.get_key = True
            arcade.play_sound(self.claim_money_sound)
        
        is_exit = arcade.check_for_collision(self.player_sprite, self.exit_list[0])
        if is_exit:
            self.close()
        
        door_opened = arcade.check_for_collision(self.player_sprite, self.door_collision_list[0])
        if door_opened and self.get_key:
            self.door_opened = True
            self.door_engine = None
            # arcade.play_sound(self.open_door_sound)

        # Двигаем камеру за игроком (центрируем)
        # self.camera.move_to((self.player_sprite.center_x, self.player_sprite.center_y))

    def on_key_press(self, key, modifiers):
        """Обработка нажатий клавиш."""
        # Стандартное управление для PhysicsEngineSimple (как в уроке 2)
        if key == arcade.key.UP or key == arcade.key.W:
            self.player_sprite.change_y = 3
            self.player_sprite.is_walking = True
            self.player_sprite.update_animation()
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = -3
            self.player_sprite.is_walking = True
            self.player_sprite.update_animation()
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -3
            self.player_sprite.is_walking = True
            self.player_sprite.update_animation()
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 3
            self.player_sprite.is_walking = True
            self.player_sprite.update_animation()
        elif key == arcade.key.Q and modifiers in {arcade.key.MOD_COMMAND, arcade.key.MOD_CTRL}:
            self.close()

    def on_key_release(self, key, modifiers):
        """Обработка отпускания клавиш."""
        if key in (arcade.key.UP, arcade.key.DOWN, arcade.key.W, arcade.key.S):
            self.player_sprite.change_y = 0
            self.player_sprite.is_walking = False
        elif key in (arcade.key.LEFT, arcade.key.RIGHT, arcade.key.A, arcade.key.D):
            self.player_sprite.change_x = 0
            self.player_sprite.is_walking = False
        self.player_sprite.update_animation()


def main():
    """Главная функция."""
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
