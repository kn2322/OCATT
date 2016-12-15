from kivy.animation import Animation
from kivy.uix.label import Label


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
