from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label

from widgets import FlashingText


class TitleScreen(Screen):
    def __init__(self, input_handler=None, **kw):
        super(TitleScreen, self).__init__(**kw)
        title_text = Label(text='There is only [i]One Room[/i] for [b]Top Chicken[/b]... [size=36sp]And you have [b]10[/b] battles to get there...[/size]', text_size=Window.size, markup=True, valign='top', font_size='40sp')
        title_text2 = Label(text='[i][b][sub]One[/sub] Cock at The [sup]Top[/sup][/b][/i]', markup=True, font_size='72sp')
        press_enter = FlashingText(interval=1.25, text='Press ENTER to start', font_size='36sp', y=-100)
        title_text3 = Label(pos=(0, -150), text='By Kevin Xin for Ludum Dare 37', markup=True, font_size='24sp')
        title_text4 = Label(pos=(0, -175), text='Music Credits to Kevin MacLeod (incompetech.com)', markup=True, font_size='20sp')
        title_text5 = Label(pos=(-300, 0), text='Controls: WASD Abilities: JKL Navigation: Enter', text_size=(Window.width/4, Window.height), markup=True, font_size='24sp')
        self.add_widget(title_text)
        self.add_widget(title_text2)
        self.add_widget(title_text3)
        self.add_widget(title_text4)
        self.add_widget(title_text5)
        self.add_widget(press_enter)

        self.input_handler = input_handler
        self.input_handler.keyboard.bind(on_key_down=self._on_key_down)

    # These two make the key events on this widget on accessible here.
    def on_pre_enter(self):
        self.input_handler.keyboard.bind(on_key_down=self._on_key_down)
        pass

    def on_pre_leave(self):
        self.input_handler.keyboard.unbind(on_key_down=self._on_key_down)
        pass

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        code, key = keycode
        if key == 'enter':
            # self.parent.shop()
            self.parent.start_game()
