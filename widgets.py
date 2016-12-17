from kivy.animation import Animation
from kivy.uix.label import Label

from kivy.vector import Vector
from kivy.graphics import Rectangle, Color
from kivy.properties import NumericProperty
from kivy.uix.widget import Widget


class FlashingText(Label):  # For flashing text effect

    # Interval is time for one complete loop
    def __init__(self, interval=1, **kw):
        super(FlashingText, self).__init__(**kw)
        self.interval = interval
        fade_to_black = Animation(opacity=0, duration=interval/2)
        reappear = Animation(opacity=1, duration=interval/2)
        cycle = fade_to_black + reappear  # Sequences animations
        cycle.repeat = True  # Repeat the animations
        self.cycle = cycle
        self.cycle.start(self)


class FloatingHealthBar(Widget):

    max_hp = NumericProperty()
    hp = NumericProperty()

    def __init__(self, padding, user, color, **kw):
        super(FloatingHealthBar, self).__init__(**kw)
        self.padding = padding
        self.offset = Vector(0, 75)
        self.user = user
        self.max_hp = user.max_hp
        self.hp = user.hp
        self.user.bind(hp=self._on_change_hp)
        self.user.bind(center=self._on_change_center)
        self.color = color
        self.size = (150, 10)
        self.instructions = []

        self.update_look()

    def _on_change_hp(self, _, hp):
        self.hp = hp
        self.update_look()

    def _on_change_center(self, _, center):
        self.center = Vector(center) + self.offset
        self.update_look()

    def update_look(self):  # Called on all observer events.
        padding_space = self.padding * (self.max_hp - 1)
        hpblock_width = (self.width - padding_space) / self.max_hp
        # num_colored = self.hp // 1
        instructions = []

        # Health portion underlying.
        instructions.append(Color(0, 0, 0, 1))
        instructions.append(Rectangle(size=self.size, pos=self.pos))
        instructions.append(Color(*self.color))
        hp_ratio = self.hp / self.max_hp
        instructions.append(Rectangle(size=(self.width*hp_ratio, self.height),
                                      pos=self.pos))

        x = self.x + hpblock_width
        instructions.append(Color())
        for i in range(self.max_hp-1):
            instructions.append(Rectangle(size=(self.padding, self.height),
                                          pos=(x, self.y)))
            x += self.padding + hpblock_width
        instructions.append(Color())

        # if self.hp > 0:
        #     instructions.append(Color(*self.color))
        #     instructions.append(Rectangle(size=(hpblock_width, self.height),
        #                                   pos=self.pos))
        # x = self.x + hpblock_width
        # for i in range(self.max_hp-1):
        #     if i > num_colored-2:
        #         c = (0,0,0,1)
        #     else:
        #         c = self.color
        #     instructions.append(Color())
        #     instructions.append(Rectangle(size=(self.padding, self.height),
        #                                   pos=(x, self.y)))
        #     x += self.padding
        #     instructions.append(Color(*c))
        #     instructions.append(Rectangle(size=(hpblock_width, self.height),
        #                                   pos=(x, self.y)))
        #     x += hpblock_width
        #     instructions.append(Color())

        self.instructions = instructions
