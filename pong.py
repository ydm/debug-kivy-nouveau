#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

from random import randint

import kivy
kivy.require('1.7.2')

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import (NumericProperty,
                             ObjectProperty,)
from kivy.uix.widget import Widget
from kivy.vector import Vector


def signum(x):
    return (x > 0) - (x < 0)


class Ball(Widget):
    velocity = [0, 0]

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos
        self.velocity = [x + (.025 * signum(x)) for x in self.velocity]

    def bounce(self, top, right, bottom, left):
        if self.x <= left or self.right >= right:
            self.velocity[0] *= -1
            return True
        if self.y <= bottom or self.top >= top:
            self.velocity[1] *= -1
            return True
        return False


class Paddle(Widget):

    _last = None
    _pressed = None
    key_down = 'down'
    key_up = 'up'
    score = NumericProperty(0)

    def __init__(self, **kwargs):

        super(Paddle, self).__init__(**kwargs)

        self._keyboard = Window.request_keyboard(lambda: None, self)
        self._keyboard.bind(on_key_down=self.on_key_down,
                            on_key_up=self.on_key_up)

    def move(self):
        if self._pressed is not None:
            if self._pressed == self.key_up:
                self.y += 10
            elif self._pressed == self.key_down:
                self.y -= 10

    # Keyboard
    def on_key_up(self, keyboard, keycode):
        self._pressed = None

    def on_key_down(self, keyboard, keycode, text, modifiers):
        key = keycode[1]
        if key == self.key_up:
            self._pressed = self.key_up
            return True
        elif key == self.key_down:
            self._pressed = self.key_down
            return True
        return False


    # Mouse
    def on_touch_down(self, e):
        if self.collide_point(*e.pos):
            self._last = e.y

    def on_touch_move(self, e):
        if self._last is not None:
            self.y -= self._last - e.y
            self._last = e.y

    def on_touch_up(self, e):
        self._last = None

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            ball.velocity[0] *= -1
            return True


class PongGame(Widget):
    ball = ObjectProperty(None)
    player_left = ObjectProperty(None)
    player_right = ObjectProperty(None)

    # A list of methods that bounce a ball
    bouncers = []

    def __init__(self, **kwargs):
        super(PongGame, self).__init__(**kwargs)
        self.bouncers.append(self.player_left.bounce_ball)
        self.bouncers.append(self.player_right.bounce_ball)
        self.bouncers.append(
            lambda ball: ball.bounce(self.height, self.width, 0, 0)
        )

    def update(self, dt):
        # Check for end of game
        if self.ball.x <= 0:
            self.player_right.score += 1
            self.serve_ball()
            return

        if self.ball.right >= self.width:
            self.player_left.score += 1
            self.serve_ball()
            return

        # Bounce
        any(b(self.ball) for b in self.bouncers)
        self.ball.move()
        self.player_left.move()
        self.player_right.move()

    def serve_ball(self):
        self.ball.center = self.center
        self.ball.velocity = Vector(5, 0).rotate(randint(0, 360))


class PongApp(App):

    def build(self):
        game = PongGame()
        game.serve_ball()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game


if __name__ == '__main__':
    PongApp().run()
