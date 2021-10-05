# Eric Santos
import arcade
import pathlib
from enum import auto, Enum, IntEnum
from PIL import Image
from time import sleep


class MoveEnum(Enum):
    NONE = auto()
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


class Dimension(IntEnum):
    WIDTH = 0
    HEIGHT = 1


class Boundaries:

    def __init__(self, x_min: float, x_max: float, y_min: float, y_max: float):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

    def is_within_x_bounds(self, curr_x_pos: float):
        return self.x_min <= curr_x_pos <= self.x_max

    def is_within_y_bounds(self, curr_y_pos: float):
        return self.y_min <= curr_y_pos <= self.y_max

    def has_reached_x_min(self, curr_x_pos: float):
        return self.x_min >= curr_x_pos

    def has_reached_x_max(self, curr_x_pos: float):
        return self.x_max <= curr_x_pos

    def has_reached_y_min(self, curr_y_pos: float):
        return self.y_min >= curr_y_pos

    def has_reached_y_max(self, curr_y_pos: float):
        return self.y_max <= curr_y_pos


class BackgroundSprite(arcade.Sprite):
    def __init__(self, background_path: str, game_window: arcade.Window):
        super().__init__(background_path)
        self.game = game_window
        self.dimensions = Image.open(background_path).size
        self.initial_x = self.dimensions[Dimension.WIDTH] / 2
        self.initial_y = self.game.height / 2
        self.max_left_bound = self.initial_x
        self.max_right_bound = game_window.width - self.initial_x
        self.set_initial_position()

    def set_initial_position(self):
        self.set_position(self.initial_x, self.initial_y)

    def update_position(self, x: float, y: float):
        self.set_position(self.center_x + x, self.center_y + y)


class BulletSprite(arcade.Sprite):
    def __init__(self, bullet_path: str, speed: int, game_window):
        super().__init__(bullet_path)
        self.game = game_window
        self.speed = speed
        self.height = 100
        self.width = 100

    def move(self):
        self.center_x += self.speed


class MinimalSprite(arcade.Sprite):
    def __init__(self, ship_path: str, speed: int, game_window):
        super().__init__(ship_path)
        self.speed = speed
        self.game = game_window

    def move(self, direction: MoveEnum):
        if direction == MoveEnum.UP and self.center_y < self.game.height - 60:
            self.center_y += self.speed
        elif direction == MoveEnum.DOWN and self.center_y > 60:
            self.center_y -= self.speed
        elif direction == MoveEnum.LEFT and self.center_x > 50:
            self.center_x -= self.speed
        elif direction == MoveEnum.RIGHT and self.center_x < self.game.width - 50:
            self.center_x += self.speed
        else:
            pass


class MimimalArcade(arcade.Window):

    def __init__(self, image_name: str, screen_w: int = 500, screen_h: int = 500):
        super().__init__(screen_w, screen_h)
        self.image_path = pathlib.Path.cwd() / 'Assets' / image_name
        self.pict = MinimalSprite(str(self.image_path), speed=10, game_window=self)
        self.background_path = pathlib.Path.cwd() / 'Assets' / 'background1.png'
        self.initial_background = BackgroundSprite(self.background_path.__str__(), self)
        self.bullet_path = pathlib.Path.cwd() / 'Assets' / 'bullet_shot.png'
        self.bullet_sprite = BulletSprite(str(self.bullet_path), speed=3, game_window=self)
        self.direction = MoveEnum.NONE
        self.screen_abs_begin_pos = 25
        self.screen_begin_pos = 25
        self.screen_curr_end = self.screen_begin_pos
        self.screen_end_pos = self.initial_background.dimensions[Dimension.WIDTH] - 25
        self.pictlist = None
        self.shot_sound = arcade.load_sound(pathlib.Path.cwd() / 'Assets' / "laser8.wav")
        self.bullet_list = None


    def setup(self):
        self.pict.center_x = self.width / 2
        self.pict.center_y = self.height / 2
        self.pictlist = arcade.SpriteList()
        self.pictlist.append(self.initial_background)
        self.pictlist.append(self.pict)
        self.bullet_list = arcade.SpriteList()

    def on_update(self, delta_time: float):
        self.pict.move(self.direction)
        if self.initial_background.center_x <= self.initial_background.max_right_bound:
            self.initial_background.update_position(self.initial_background.max_left_bound, 0)
        elif self.initial_background.center_x <= self.initial_background.max_left_bound + 100:
            self.initial_background.update_position(self.initial_background.max_right_bound, 0)
        else:
            self.initial_background.update_position(-1, 0)
        sleep(.06)

    def on_draw(self):
        """ Render the screen. """
        arcade.start_render()
        self.pictlist.draw()
        for bullet in self.bullet_list:
            bullet.draw()
            bullet.move()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        if key == arcade.key.UP or key == arcade.key.W:
            self.direction = MoveEnum.UP
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.direction = MoveEnum.DOWN
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.direction = MoveEnum.RIGHT
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.direction = MoveEnum.LEFT
        elif key == arcade.key.SPACE:
            bullet = BulletSprite(str(self.bullet_path), speed=17, game_window=self)
            start_x = self.pict.center_x
            start_y = self.pict.center_y
            bullet.center_x = start_x
            bullet.center_y = start_y
            self.bullet_list.append(bullet)
            arcade.play_sound(self.shot_sound)

    def on_key_release(self, key: int, modifiers: int):
        """called by arcade for keyup events"""
        if (key == arcade.key.UP or key == arcade.key.W) and \
                self.direction == MoveEnum.UP:
            self.direction = MoveEnum.NONE
        if (key == arcade.key.DOWN or key == arcade.key.S) and \
                self.direction == MoveEnum.DOWN:
            self.direction = MoveEnum.NONE
        if (key == arcade.key.LEFT or key == arcade.key.A) and \
                self.direction == MoveEnum.LEFT:
            self.direction = MoveEnum.NONE
        if (key == arcade.key.RIGHT or key == arcade.key.D) and \
                self.direction == MoveEnum.RIGHT:
            self.direction = MoveEnum.NONE
# test

def main():
    """ Main method """
    window = MimimalArcade("PlayerShip.png")
    window.setup()
    arcade.run()


if __name__ == '__main__':
    main()
