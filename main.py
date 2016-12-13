from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.vector import Vector
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.graphics import Rectangle, Color, PushMatrix, PopMatrix, Scale, Translate
from kivy.properties import ListProperty, StringProperty, NumericProperty, ObjectProperty
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from itertools import product, combinations
from collections import OrderedDict
from functools import partial
import random
import math
import os

# Constants
FPS = 60
# Transforming 'stat' values into in game values
SPEED_COEFFICIENT = lambda x: (20 * x) + 400
JUMP_COEFFFICIENT = lambda x: (30 * x) + 1050

Builder.load_string("""
# BoxLayout interface when battling.
<BattleInterface>
    items: items
    orientation: 'vertical'
    Widget:
        size_hint: 1, 0.8
    BoxLayout:
        id: items
        size_hint: 1, 0.2
        orientation: 'horizontal'

<IDisplay>
    top_w: top_w
    orientation: 'vertical'
    canvas:
        Color:
            rgba: self.bgcolor
        Rectangle:
            size: self.size
            pos: self.pos
    canvas.after:
        Color:
            rgba: 1, 1, 1, 0.5
        Rectangle:
            size: root.width, (self.cooldown / self.max_cooldown) * root.height
            pos: self.pos
    Label:
        id: top_w
        size_hint: 1, 0.4
        font_size: '36sp'

<DeathScreen>
    Label:
        pos: 0, 50
        font_size: '96sp'
        text: 'Gameover'
    Label:
        pos: 0, -100
        font_size: '24sp'
        markup: True
        text: 'There was one room for [b][i]TOP COCK[/b][/i], and you are not in that room.'

<VictoryScreen>
    Label:
        font_size: '30sp'
        text: root.display_text
    Label:
        markup: True
        pos: 0, - 40
        font_size: '24sp'
        text: 'You got [i][size=36sp][color=#e6e600]' + str(int(root.gained_money)) + '[/size][/color][/i] Dollars!'

<ShopScreen>
    one: one
    two: two
    three: three
    four: four
    five: five
    six: six
    seven: seven
    eight: eight
    exit: exit
    selection: selection
    health_bar: health_bar
    stat_1: stat_1
    stat_2: stat_2
    stat_3: stat_3

    BoxLayout:
        orientation: 'horizontal'
        BoxLayout:
            orientation: 'vertical'
            size_hint: 0.5, 1
            Image:
                source: 'assets/shopkeeper.png'
                size_hint: 1, 0.8
            # Exit
            Label:
                id: exit
                size_hint: 1, 0.2
                canvas.before:
                    Color:
                        rgb: 128/255, 32/255, 0/255
                    Rectangle:
                        size: self.size
                        pos: self.pos
                font_size: '36sp'
                markup: True
                text: 'Next Battle -> [color=#ff0066]{}[/color]'.format(int(root.battle_num))
        # Shop menu
        BoxLayout:
            size_hint: 0.4, 1
            orientation: 'vertical'
            # Background
            canvas:
                Color:
                    rgba: 1, 1, 1, 0.3
                Rectangle:
                    size: self.size
                    pos: self.pos
            # Shelf items
            GridLayout:
                size_hint: 1, 0.4
                rows: 2
                Widget:
                    id: one
                Widget:
                    id: two
                Widget:
                    id: three
                Widget:
                    id: four
            # Health bar
            BoxLayout:
                id: five
                orientation: 'horizontal'
                size_hint: 1, 0.2
                Widget:
                    size_hint: 0.2, 1
                # Health bar
                BoxLayout:
                    orientation: 'vertical'
                    size_hint: 0.6, 1
                    Widget:
                        size_hint: 1, 0.3
                    Label:
                        # pos is workaround.
                        pos: -100, -100
                        markup: True
                        id: health_bar
                        size_hint: 1, 0.4
                        font_size: '24sp'
                    Widget:
                        size_hint: 1, 0.3
                # Plus Button
                Image:
                    source: 'assets/plus.png'
                    size_hint: 0.2, 1
            # Stats
            BoxLayout:
                size_hint: 1, 0.4
                orientation: 'vertical'
                # These three repeat bc I can't be bothered to properly set up kv.
                BoxLayout:
                    orientation: 'horizontal'
                    # Stat
                    StatLabel:
                        text: 'Speed'
                    # Value
                    StatnumLabel:
                        id: stat_1
                        text: str(0)
                    # Plus button
                    Image:
                        id: six
                        source: 'assets/plus.png'
                        size_hint: 0.3, 1
                BoxLayout:
                    orientation: 'horizontal'
                    # Stat
                    StatLabel:
                        text: 'Jump'
                    # Value
                    StatnumLabel:
                        id: stat_2
                        text: str(0)
                    # Plus button
                    Image:
                        id: seven
                        source: 'assets/plus.png'
                        size_hint: 0.3, 1
                BoxLayout:
                    orientation: 'horizontal'
                    # Stat
                    StatLabel:
                        text: 'Max HP'
                    # Value
                    StatnumLabel:
                        id: stat_3
                        text: str(0)
                    # Plus button
                    Image:
                        id: eight
                        source: 'assets/plus.png'
                        size_hint: 0.3, 1
        # Prices
        BoxLayout:
            orientation: 'vertical'
            size_hint: 0.1, 1
            canvas.before:
                Color:
                    rgb: 97/255, 64/255, 31/255
                Rectangle:
                    size: self.size
                    pos: self.pos
                Color:
            Widget:
                size_hint: 1, 0.4
                canvas:
                    Rectangle:
                        source: 'assets/money.png'
                        pos: self.x, self.top - self.width
                        size: self.width, self.width
            # HP
            PriceLabel:
                size_hint: 1, 0.2
                text: str(root.health_cost)
            PriceLabel:
                size_hint: 1, 0.4 / 3
                text: str(root.stat_1_cost)
            PriceLabel:
                size_hint: 1, 0.4 / 3
                text: str(root.stat_2_cost)
            PriceLabel:
                size_hint: 1, 0.4 / 3
                text: str(root.stat_3_cost)


    # The glowy selection box.
    Widget:
        size: one.size
        pos: one.pos
        size_hint: None, None
        id: selection
        canvas.before:
            Color:
                rgba: 1, 0, 0.4, 1
            BorderImage:
                size: self.width+30, self.height+30
                pos: self.x - 15, self.y - 15
                source: 'assets/border.png'
                border: [1, 1, 1, 1]

    # Money count
    Label:
        markup: True
        text: 'Money: [color=#e6e600]{}[/color]'.format(str(root.money))
        font_size: '36sp'
        pos: -1 * root.width / 2 + 125, root.height / 2 - 450

<StatLabel@Label>
    markup: True
    size_hint: 0.4, 1
    halign: 'left'
    valign: 'middle'
    text_size: self.width - 40, self.height
    font_size: '24sp'

<StatnumLabel@Label>
    markup: True
    size_hint: 0.3, 1
    halign: 'right'
    valign: 'middle'
    text_size: self.width - 40, self.height
    font_size: '24sp'

<PriceLabel@StatnumLabel>
    markup: True
    halign: 'center'
    text_size: self.size
""")


# Misc classes
class FlashingText(Label): # For flashing text effect

    def __init__(self, interval=1, **kw): # Interval is time for one complete loop
        super(FlashingText, self).__init__(**kw)
        self.interval = interval
        fade_to_black = Animation(opacity=0, duration=interval/2)
        reappear = Animation(opacity=1, duration=interval/2)
        cycle = fade_to_black + reappear # Sequences animations
        cycle.repeat = True # Repeat the animations
        self.cycle = cycle
        self.cycle.start(self)

class IDisplay(BoxLayout):

    bgcolor = ListProperty([1,1,1,1])
    key = StringProperty()
    max_cooldown = NumericProperty(1)
    cooldown = NumericProperty()

    def __init__(self, key='', item=None, bgcolor=(1,1,1,1), **kw):
        super(IDisplay, self).__init__(**kw)
        self.key = key
        self.item = item
        self.bgcolor = bgcolor
        
        if self.key:
            self.top_w.text = self.key
        
        bot = Widget(size_hint=(1, 0.6)) # Incase the condition doesn't pass        
        if self.item:
            self.cooldown = self.item.cooldown
            self.item.bind(cooldown=self._on_change_cd)
            self.max_cooldown = self.item.max_cooldown
            self.item.bind(max_cooldown=self._on_change_max_cd)
            if self.item.source:
                bot = Image(size_hint=(1, 0.6), source=self.item.source)
        self.add_widget(bot)

    def _on_change_cd(self, _, cd):
        self.cooldown = cd

    def _on_change_max_cd(self, _, max_cd):
        self.max_cooldown = max_cd

class FloatingHealthBar(Widget):

    max_hp = NumericProperty()
    hp = NumericProperty()

    def __init__(self, padding, user, color,**kw):
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

    def update_look(self): # Called on all observer events.
        padding_space = self.padding * (self.max_hp - 1)
        hpblock_width = (self.width - padding_space) / self.max_hp
        num_colored = self.hp // 1
        instructions = []

        # Health portion underlying.
        instructions.append(Color(0,0,0,1))
        instructions.append(Rectangle(size=self.size, pos=self.pos))
        instructions.append(Color(*self.color))
        hp_ratio = self.hp / self.max_hp
        instructions.append(Rectangle(size=(self.width*hp_ratio, self.height), pos=self.pos))

        x = self.x + hpblock_width
        instructions.append(Color())
        for i in range(self.max_hp-1):
            instructions.append(Rectangle(size=(self.padding, self.height), pos=(x, self.y)))
            x += self.padding + hpblock_width
        instructions.append(Color())
        """
        if self.hp > 0:
            instructions.append(Color(*self.color))
            instructions.append(Rectangle(size=(hpblock_width, self.height), pos=self.pos))
        x = self.x + hpblock_width
        for i in range(self.max_hp-1):
            if i > num_colored-2:
                c = (0,0,0,1)
            else:
                c = self.color
            instructions.append(Color())
            instructions.append(Rectangle(size=(self.padding, self.height), pos=(x, self.y)))
            x += self.padding
            instructions.append(Color(*c))
            instructions.append(Rectangle(size=(hpblock_width, self.height), pos=(x, self.y)))
            x += hpblock_width
            instructions.append(Color())"""
        self.instructions = instructions

class StatBar(BoxLayout):
    pass

class InputHandler(Widget):

    def __init__(self, **kw):
        super(InputHandler, self).__init__(**kw)
        self.keyboard = Window.request_keyboard(
                        self._on_key_close,
                        self
                        )
        self.keyboard.bind(on_key_down=self._on_key_down)
        self.keyboard.bind(on_key_up=self._on_key_up)

        self.key_status = {}

    def _on_key_close(self, **kw):
        print('Keyboard closed')

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        code, key = keycode
        self.key_status.setdefault(key, False)
        self.key_status[key] = True
        #print('"{}" is down'.format(key))

    def _on_key_up(self, keyboard, keycode):
        code, key = keycode
        self.key_status[key] = False
        #print('"{}" is up'.format(key))

INPUT_HANDLER = InputHandler() # Global variable for input data.

# Game data

class GameObject(Widget):
    pass

class Terrain(GameObject):

    opacity = NumericProperty(1)

    def __init__(self, source='', color=[1,1,1], opacity=1, **kw):
        super(Terrain, self).__init__(**kw)
        self.source = source
        self.color = color
        self.opacity = opacity
    
    def update_graphics(self):
        graphics = [Color(*(self.color+[self.opacity])), Rectangle(size=self.size, pos=self.pos, source=self.source)]
        RENDERER.instructions.extend(graphics)

class Entity(GameObject): # Parent of characters and projectiles and such.

    opacity = NumericProperty(1)
    source = StringProperty() # For graphics.

    def __init__(self, opacity=1, color=[1,1,1], **kw):
        super(Entity, self).__init__(**kw)
        self.mass = 0
        self.bounciness = 0
        self.friction = 0
        self.air_friction = 0
        self.can_fall = True
        self.velocity = Vector(0, 0)
        self.in_air = None # Possible states -> True, False
        self.opacity = opacity
        self.color = color

        self.collided_terrain = [] # Cleared at beginning of each frame, list of True/False values.

    def destroy(self):
        BATTLE_WORLD.entity_container.remove(self)

    def update_input(self):
        pass

    def update_physics(self):
        self.in_air = not any(self.collided_terrain) # If on top of any terrain, is on ground.
        self.collided_terrain.clear()

        self.apply_gravity()
        self.apply_friction()
        self.pos = Vector(self.pos) + self.velocity
        #self.terrain_collision() # Terrain collision done from battle_world

    def apply_friction(self): # Only sideways friction for now.
        f = self.friction / FPS
        x = self.velocity.x
        if self.in_air:
            f = self.air_friction / FPS
        else:
            if x < 0:
                if x + f >= 0:
                    self.velocity.x = 0
                else:
                    self.velocity.x += f
            elif x == 0:
                pass
            else:
                if x - f <= 0:
                    self.velocity.x = 0
                else:
                    self.velocity.x -= f

    def apply_gravity(self):
        if self.can_fall and self.in_air:
            gravity = Vector(0, -1) * BATTLE_WORLD.GRAVITY
            self.velocity += gravity / FPS

    def terrain_collision(self, t):
        if t.collide_widget(self):
            ground = False
            x_posneg = t.center_x <= self.center_x
            if x_posneg:
                x_depth = t.right - self.x
            else:
                x_depth = self.right - t.x
            #x_depth = (self.width+t.width)/2 - abs(t.center_x-self.center_x)
            y_posneg = t.center_y <= self.center_y
            if y_posneg:
                y_depth = t.top - self.y
                ground = True
            else:
                y_depth = self.top - t.y 
            #y_depth = (self.height+t.height)/2 - abs(t.center_y-self.center_y)
            
            if x_depth < 0: # False collisions.
                x_depth = 0
            if y_depth < 0:
                y_depth = 0

            if x_depth <= y_depth:
                x_posneg = 1 if x_posneg else -1
                self.x += x_depth * x_posneg
                self.velocity.x *= -1 * self.bounciness
            else:
                y_posneg = 1 if y_posneg else -1
                self.y += y_depth * y_posneg
                self.velocity.y *= -1 * self.bounciness

            self.collided_terrain.append(ground)
            #self.velocity *= -1 * self.bounciness # Bouncy bouncy

    def collide(self, other):
        pass

    def update_graphics(self):
        graphics = [Color(*(self.color+[self.opacity])), Rectangle(size=self.size, pos=self.pos)]
        RENDERER.instructions.extend(graphics)

class Character(Entity):

    hp = NumericProperty()
    max_hp = NumericProperty()
    max_speed = NumericProperty()
    
    def __init__(self, **kw):
        super(Character, self).__init__(**kw)
        self.hp = 0
        self.max_hp = 0
        self.max_speed = 0
        self.side_acceleration = 0
        self.air_side_acceleration = 0
        self.accel_from_max_speed()
        self.bind(max_speed=self.accel_from_max_speed)
        self.jump_impulse = 900
        self.bounciness = 0 # VERY slight bounce :3, set to 1 for hilarity
        self.direction = 1 # For graphical direction
        self.equips = [None, None, None]
        self.source = 'assets/chicken' # All left versions have left appended before the .png
        self.moving = False # Voluntary movement flag, for l/r movement only.
        self.movable = True # Voluntary movement movable.

        #self.damagable = True

    def update_items(self):
        for itm in self.equips:
            if itm:
                itm.update()

    def apply_friction(self): # Only sideways friction for now.
        f = self.friction / FPS
        x = self.velocity.x
        if self.in_air:
            f = self.air_friction / FPS
        elif not self.moving:
            if x < 0:
                if x + f >= 0:
                    self.velocity.x = 0
                else:
                    self.velocity.x += f
            elif x == 0:
                pass
            else:
                if x - f <= 0:
                    self.velocity.x = 0
                else:
                    self.velocity.x -= f

    def receive_damage(self, dmg, other):
        self.hp -= dmg

    def update_graphics(self):
        if self.direction == 1:
            source = self.source
        elif self.direction == -1:
            source = self.source + 'left'
        source = source + '.png'
        # Larger sprites than hitbox
        s = Vector(self.size) * 1.5
        p = self.center_x - (s.x/2), self.y 
        graphics = [Color(*(self.color+[self.opacity])), Rectangle(size=s, pos=p, source=source)]
        RENDERER.instructions.extend(graphics)

    def accel_from_max_speed(self, *args): # As name suggests, returns tuple of values
        max_speed = self.max_speed
        ACCEL_TIME = FPS * 0.2# Time it takes to reach max speed, should be changed to variable soon.
        side_accel = max_speed / ACCEL_TIME
        air_accel = max_speed / ACCEL_TIME / 2
        self.side_acceleration, self.air_side_acceleration = side_accel, air_accel

class EnemyCharacter(Character):

    def __init__(self, speed=0, jump=0, **kw):
        super(EnemyCharacter, self).__init__(**kw)
        self.size = (48, 48)

        self.speed = speed
        self.jump = jump

        self.max_speed = SPEED_COEFFICIENT(speed)
        self.jump_impulse = JUMP_COEFFFICIENT(jump)

        self.friction = self.side_acceleration
        self.air_friction = self.air_side_acceleration / 3
        #self.jump_impulse = 900
        self.equips = [Sword(self), Trebuchet(self), None]

        self.max_hp = 10
        self.hp = self.max_hp

        self.jump_flag = False # Jumping from colliding on side of terrain, reset to false at the end of ai routine of each frame.
        self.randomize(PLAYER_INFO['battle_num'])

    def terrain_collision(self, t):
        if t.collide_widget(self):
            ground = False
            x_posneg = t.center_x <= self.center_x
            if x_posneg:
                x_depth = t.right - self.x
            else:
                x_depth = self.right - t.x
            #x_depth = (self.width+t.width)/2 - abs(t.center_x-self.center_x)
            y_posneg = t.center_y <= self.center_y
            if y_posneg:
                y_depth = t.top - self.y
                ground = True
            else:
                y_depth = self.top - t.y 
            #y_depth = (self.height+t.height)/2 - abs(t.center_y-self.center_y)
            
            if x_depth < 0: # False collisions.
                x_depth = 0
            if y_depth < 0:
                y_depth = 0

            if x_depth <= y_depth:
                x_posneg = 1 if x_posneg else -1
                self.x += x_depth * x_posneg
                self.velocity.x *= -1 * self.bounciness
                self.jump_flag = True
            else:
                y_posneg = 1 if y_posneg else -1
                self.y += y_depth * y_posneg
                self.velocity.y *= -1 * self.bounciness

            self.collided_terrain.append(ground)

    def update_input(self):
        #print(self.velocity)
        x = self.velocity.x
        m = self.max_speed / FPS
        a = self.side_acceleration / FPS
        air_a = self.air_side_acceleration / FPS
        player = BATTLE_WORLD.player
        d = 50 # Distance away from player to stop.

        if self.movable:
            self.moving = True
            if self.in_air:
                if player.right < self.x - d:
                    if x - air_a <= -1 * m:
                        pass
                        #self.velocity.x = -1 * m
                    else:
                        self.velocity.x += -1 * air_a
                    #self.direction = -1
                elif player.x >= self.right + d:
                    if x + air_a >= m:
                        pass
                        #self.velocity.x = 1 * m
                    else:
                        self.velocity.x += 1 * air_a
                    #self.direction = 1
            else:
                if self.jump_flag or player.y > self.y + 100: #or abs(player.x-self.x) > d * 3:
                    self.velocity.y = self.jump_impulse / FPS
                    #if player.right < self.x and x < 0:
                    #    self.velocity.y = self.jump_impulse / FPS
                    #elif player.x > self.x and x > 0:
                    #    self.velocity.y = self.jump_impulse / FPS

                if player.right < self.x - d:
                    if x - a <= -1 * m:
                        pass
                        #self.velocity.x = -1 * m
                    else:
                        self.velocity.x += -1 * a
                    #self.direction = -1
                elif player.x >= self.right + d:
                    if x + a >= m:
                        pass
                        #self.velocity.x = 1 * m
                    else:
                        self.velocity.x += 1 * a
                    #self.direction = 1
                else:
                    self.moving = False
        else:
            self.moving = False

        if player.center_x < self.center_x:
            self.direction = -1
        else:
            self.direction = 1
        self.update_items()
        self.jump_flag = False

        """if self.velocity.x == 0:
            pass
        elif self.velocity.x > 0:
            self.direction = 1
        else:
            self.direction = -1"""

    def receive_damage(self, dmg, other):
        if isinstance(other.user, Item):
            if isinstance(other.user.user, PlayerCharacter):
                if self.hp - dmg < 0:
                    self.hp = 0
                else:
                    self.hp -= dmg
        elif isinstance(other.user, PlayerCharacter):
            if self.hp - dmg < 0:
                self.hp = 0
            else:
                self.hp -= dmg
        #print(self.hp)

    def update_items(self):
        super(EnemyCharacter, self).update_items()
        for i in self.equips:
            if not i:
                continue
            if i.ai_module(BATTLE_WORLD.player): # AI routine to return True/False
                i.use()

    def randomize(self, difficulty): # Randomize ai values ~
        for i in self.equips:
            if i:
                i.randomize(difficulty)
        stat_curve = (difficulty-1)**1.6
        self.speed = int(random.gauss(stat_curve, difficulty))
        self.jump = int(random.gauss(stat_curve*0.5, difficulty))
        self.max_speed = SPEED_COEFFICIENT(self.speed)
        self.jump_impulse = JUMP_COEFFFICIENT(self.jump)
        s = (difficulty-1)*random.gauss(5, 1)
        self.size = Vector(self.size) + Vector(s, s)
        self.max_hp = int(random.gauss(difficulty*10, difficulty))
        self.hp = self.max_hp

class PlayerCharacter(Character):

    def __init__(self, max_speed=400, max_hp=10, hp=10, equips=None, speed=0, jump=0, **kw):
        # Initialized through passing save file kwarg dict.
        super(PlayerCharacter, self).__init__(**kw)
        #self.size = (48, 48)
        #self.max_speed = max_speed
        self.max_speed = SPEED_COEFFICIENT(speed)
        self.jump_impulse = JUMP_COEFFFICIENT(jump)
        
        if equips:
            self.equips = [e(self) for e in equips]#[Sword(self), Trebuchet(self), ChickenBoosters(self)]
        else:
            self.equips = [None,None,None]
        self.keymapping = OrderedDict(zip(['j', 'k', 'l'], self.equips))
        INPUT_HANDLER.keyboard.bind(on_key_down=self._on_key_down)

        self.max_hp = max_hp
        self.hp = hp

        #self.side_acceleration, self.air_side_acceleration = self.accel_from_max_speed(self.max_speed)
        #self.side_acceleration = 30
        #self.air_side_acceleration = 10
        self.friction = self.side_acceleration
        self.air_friction = self.air_side_acceleration / 3
        #self.jump_impulse = 900

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        code, key = keycode
        try:
            self.keymapping[key].use()
        except (AttributeError, KeyError):
            pass

    def update_input(self):
        #print(self.moving)
        #print(self.in_air)
        
        #print(self.velocity)
        x = self.velocity.x
        m = self.max_speed / FPS
        a = self.side_acceleration / FPS
        air_a = self.air_side_acceleration / FPS

        key_a = INPUT_HANDLER.key_status.get('a', False)
        key_d = INPUT_HANDLER.key_status.get('d', False)
        key_w = INPUT_HANDLER.key_status.get('w', False)

        if self.movable:
            if self.in_air:
                if key_a and key_d:
                    pass
                elif key_a:
                    if x - air_a <= -1 * m:
                        pass
                        #self.velocity.x = -1 * m
                    else:
                        self.velocity.x += -1 * air_a
                    self.direction = -1

                elif key_d:
                    if x + air_a >= m:
                        pass
                        #self.velocity.x = 1 * m
                    else:
                        self.velocity.x += 1 * air_a
                    self.direction = 1
            else:
                if key_w:
                    self.velocity.y = self.jump_impulse / FPS

                if key_a and key_d:
                    self.moving = False
                elif key_a:
                    if x - a <= -1 * m:
                        pass
                        #self.velocity.x = -1 * m
                    else:
                        self.velocity.x += -1 * a
                    self.direction = -1
                    self.moving = True

                elif key_d:
                    if x + a >= m:
                        pass
                        #self.velocity.x = 1 * m
                    else:
                        self.velocity.x += 1 * a
                    self.direction = 1
                    self.moving = True
                else:
                    self.moving = False

        """if self.velocity.x == 0:
            pass
        elif self.velocity.x > 0:
            self.direction = 1
        else:
            self.direction = -1"""
        self.update_items()

    def receive_damage(self, dmg, other):
        if isinstance(other.user, Item):
            if isinstance(other.user.user, EnemyCharacter):
                if self.hp - dmg < 0:
                    self.hp = 0
                else:
                    self.hp -= dmg
        elif isinstance(other.user, EnemyCharacter):
            if self.hp - dmg < 0:
                self.hp = 0
            else:
                self.hp -= dmg

# Equipment

class Item(Widget): # Is subclass of widget just for the properties

    max_cooldown = NumericProperty(1)
    cooldown = NumericProperty()

    def __init__(self, user, **kw):
        super(Item, self).__init__(**kw)
        self.slot = 0 # Should be 1, 2, or 3 for close, mid, util
        self.user = user
        self.max_cooldown = FPS # 1 second cooldown
        self.cooldown = 0
        self.source = 'assets/chicken.png'
        #self.ai_gaps = 0.3 * FPS # AI time to cool down.

    def use(self):
        if self.cooldown == 0:
            self.cooldown = self.max_cooldown
            print('{} used item.'.format(self.user))

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1

    def ai_module(self, target):
        return False

    def randomize(self, difficulty): # diff from 1 - 10
        pass

    def ai_cooldown(self, val):
        if type(self.user) == EnemyCharacter:
            return val + (0.3 * FPS)
        else:
            return val

class Sword(Item): # Close range template

    def __init__(self, *args, **kw):
        super(Sword, self).__init__(*args, **kw)
        self.max_cooldown = 0.6 * FPS
        self.size = 75, 75
        self.source = 'assets/sword.png'
        self.damage = 1
        self.duration = 0.2 * FPS
        self.max_recoil_duration = 0.6 * FPS
        self.recoil_duration = 0 # Animation time/how long the user is slowed for
        self.recoil = 0.8 # speed multiplier
        self.anim = None
        self.knockback = 600#800

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1
        if self.recoil_duration > 0:
            self.recoil_duration -= 1
            if self.recoil_duration <= 0:
                self.user.max_speed /= self.recoil

    def use(self):
        if self.cooldown == 0:
            self.user.max_speed *= self.recoil
            self.recoil_duration = self.max_recoil_duration
            self.cooldown = self.max_cooldown
            sword_widget = SwordEntity(self.source, self.damage, self.knockback, self.duration, self.user, size=self.size)
            BATTLE_WORLD.entity_container.append(sword_widget)

    def randomize(self, difficulty): # diff from 1 - 10
        self.max_cooldown = int((0.9 - 0.4/10*difficulty)*FPS)
        self.max_recoil_duration = self.max_cooldown
        s = (1.5/10*difficulty)
        s = random.gauss(s, s/4)
        self.size = Vector(60, 60) + Vector(s, s)
        self.recoil = 0.5 + (0.4/10*difficulty)
        kb = (600/10*difficulty)
        self.knockback = 300 + (random.gauss(5, 2) * kb)

    def ai_module(self, target):
        dx = abs(target.center_x - self.user.center_x)
        dy = abs(target.center_y - self.user.center_y)
        if dx < self.user.width * 5:
            return True
        return False

class SwordEntity(Entity):

    def __init__(self, source, damage, knockback, duration, user, **kw):
        super(SwordEntity, self).__init__(**kw)
        self.can_fall = False
        self.source = source
        self.damage = damage
        self.knockback = knockback
        self.duration = duration
        self.total = duration
        self.user = user
        self.center = self.user.center
        self.hit = [] # Stop repeat dmg

        #self.slow = 0.5
        #self.user.max_speed *= self.slow
        #self.user.velocity *= self.slow # Straight slow instead of slowing accel.
        #self.user.movable = False

        # Attack Animations
        #dist_away = (self.width / 2 + self.user.width / 2) * self.user.direction # Sword distance
        #attack_anim = Animation(center_x=self.user.center_x+dist_away, duration=self.duration/2/60)
        #attack_anim.start(self)

    def update_graphics(self):
        if self.user.direction == 1:
            source = self.source
        elif self.user.direction == -1:
            s = self.source.split('.')
            source = s[0] + 'left.' + s[1]
        graphics = Rectangle(size=self.size, pos=self.pos, source=source)
        RENDERER.instructions.append(graphics)

    def update_input(self):
        super(SwordEntity, self).update_input()
        if self.duration <= 0:
            #print('sword destroyed')
            self.destroy()

        # Constrains sword relative to player.
        ratio = 1.5 - self.duration / self.total
        self.center_x = self.user.center_x + ((self.width / 2 + self.user.width / 2) * self.user.direction) * ratio
        self.center_y = self.user.center_y

        self.duration -= 1

    def collide(self, other):
        #if type(other) == type(self):
        #    self.destroy()

        if type(self.user) == PlayerCharacter:
            t = EnemyCharacter
        elif type(self.user) == EnemyCharacter:
            t = PlayerCharacter
        else:
            raise TypeError('Sword is being used by unsupported type {}'.format(type(self.user)))
        
        if isinstance(other, t):
            if other in self.hit:
                pass
            else:
                other.receive_damage(self.damage, self) # Deals the dps
                if self.user.direction == 1:
                    d = other.x - self.user.right
                elif self.user.direction == -1:
                    d = self.user.x - other.right
                #magnitude_multiplier =  1 - (d / self.width) + 0.33 # 0 - 1 for multiplying
                other.velocity.x += self.knockback / FPS * self.user.direction#self.knockback * magnitude_multiplier / FPS * self.user.direction
                self.hit.append(other)

    def destroy(self):
        #self.user.movable = True
        #self.user.max_speed /= self.slow
        #self.user.velocity /= self.slow
        super(SwordEntity, self).destroy()

class Trebuchet(Item): # Artillery template, greatest siege engine in existence.

    def __init__(self, *args, **kw):
        super(Trebuchet, self).__init__(*args, **kw)
        self.max_cooldown = 2 * FPS
        self.windup_max = 0.5 * FPS
        self.windup = 0
        self.windup_slow = 0.5

        self.rock_size = 50, 50
        self.source = 'assets/90kgrock.png'
        self.damage = 2
        self.duration = 2 * FPS # num seconds after hitting the ground.
        self.anim = None
        self.knockback = 800
        self.angle = 36 # From Vector(1, 0)
        self.speed0 = 1200 # Initial speed

    def use(self):
        if self.cooldown == 0 and self.windup == 0:
            self.user.max_speed *= self.windup_slow # WATCHOUT COUPLED SOLUTION.
            self.windup = self.windup_max
            #print('called')

    def update(self):
        super(Trebuchet, self).update()
        if self.windup > 0:
            self.windup -= 1
            if self.windup == 0:
                self.user.max_speed /= self.windup_slow # WATCHOUT COUPLED SOLUTION.
                self.cooldown = self.max_cooldown
                t_widget = TrebuchetRock(
                self.source, self.damage, self.knockback, self.speed0, self.angle, self.duration, self.user, size=self.rock_size)
                BATTLE_WORLD.entity_container.append(t_widget)

    def ai_module(self, target):
        dx = abs(target.center_x - self.user.center_x)
        dy = abs(target.center_y - self.user.center_y)
        if dy < 400 and dx > self.width * 2:
            return True
        return False

    def randomize(self, difficulty): # diff from 1 - 10
        self.max_cooldown = (3*FPS) - (1.5/10*difficulty*FPS)
        self.max_recoil_duration = self.max_cooldown
        s = (40/10*difficulty)
        s = random.gauss(s, s/4)
        self.rock_size = Vector(40, 40) + Vector(s, s)
        self.windup_slow = 0.2 + (0.5/10*difficulty)
        kb = (600/10*difficulty)
        self.knockback = 600 + (random.gauss(5, 2) * kb)
        self.angle = random.gauss(36, 4)
        self.speed0 = random.gauss(1200, 200)
        self.bounciness = abs(random.gauss(0.5, 0.3))

class TrebuchetRock(Entity):

    def __init__(self, source, damage, knockback, speed, angle, duration, user, **kw):
        super(TrebuchetRock, self).__init__(**kw)
        self.can_fall = True
        self.air_friction = 0
        self.friction = speed / FPS
        self.bounciness = 0.5

        self.source = source
        self.damage = damage
        self.knockback = knockback
        self.duration = duration
        self.user = user
        self.center = self.user.center_x, self.user.center_y + 25

        self.grounded = False # Flag for touching ground

        # Initial velocity.
        self.velocity = (Vector(1, 0)*self.user.direction).rotate(angle*self.user.direction) * speed / FPS
        self.velocity += self.user.velocity # Relative velocity.

        # Attack Animations
        #dist_away = (self.width / 2 + self.user.width / 2) * self.user.direction # Sword distance
        #attack_anim = Animation(center_x=self.user.center_x+dist_away, duration=self.duration/2/60)
        #attack_anim.start(self)

    def update_graphics(self):
        graphics = Rectangle(size=self.size, pos=self.pos, source=self.source)
        RENDERER.instructions.append(graphics)

    def update_input(self):
        super(TrebuchetRock, self).update_input()
        if not self.grounded and not self.in_air:
            self.grounded = True

        if self.grounded:
            self.duration -= 1

        if self.duration <= 0:
            #print('rock destroyed')
            self.destroy()

    def collide(self, other):
        if type(self.user) == PlayerCharacter:
            t = EnemyCharacter
        elif type(self.user) == EnemyCharacter:
            t = PlayerCharacter
        else:
            raise TypeError('Trebuchet is being used by unsupported type {}'.format(type(self.user)))

        if isinstance(other, t):
            other.receive_damage(self.damage, self)
            diff = (Vector(other.center) - self.center).normalize()
            other.velocity += diff * self.knockback / FPS
            #print('rock destroyed')
            self.destroy()

class ChickenBoosters(Item): # Utility template.

    def __init__(self, *args, **kw):
        super(ChickenBoosters, self).__init__(*args, **kw)
        self.max_cooldown = 2 * FPS
        self.source = 'assets/plus.png'
        self.duration = 1 * FPS
        self.remaining = 0
        self.anim = None
        self.accel = 30

    def use(self):
        if self.cooldown == 0:
            self.cooldown = self.max_cooldown
            self.remaining = self.duration

    def update(self):
        super(ChickenBoosters, self).update()
        if self.remaining > 0:
            self.user.moving = True # CAREFUL, update_items() after update_input(), accessing privates.
            self.remaining -= 1
            self.user.velocity.x += self.accel / FPS * self.user.direction

# For reading savefiles with strings for names.
ITEM_CONVERSION_TABLE = {
    'item': Item,
    'sword': Sword,
    'trebuchet': Trebuchet,
    'booster': ChickenBoosters
}

# Real deal things

class ScreenManagement(ScreenManager):
    
    def __init__(self, **kw):
        super(ScreenManagement, self).__init__(**kw)
        self.add_widget(TitleScreen(name='Title Screen'))
        self.title_screen()
        global SCREEN_MANAGEMENT
        SCREEN_MANAGEMENT = self # Globals!!!...

    def title_screen(self): # Change to title screen from whereever.
        self.current = 'Title Screen'

    def start_game(self):
        # This part is possibly buggy.
        if self.has_screen('Battle Screen'):
            self.remove_widget(self.get_screen('Battle Screen'))
        self.add_widget(BattleScreen(name='Battle Screen'))
        self.current = 'Battle Screen'

    def game_over(self):
        if self.has_screen('Death Screen'):
            self.remove_widget(self.get_screen('Death Screen'))
        self.add_widget(DeathScreen(name='Death Screen'))
        self.current = 'Death Screen'

    def victory(self):
        if self.has_screen('Victory Screen'):
            self.remove_widget(self.get_screen('Victory Screen'))
        self.add_widget(VictoryScreen(name='Victory Screen'))
        self.current = 'Victory Screen'

    def shop(self):
        if self.has_screen('Shop Screen'):
            self.remove_widget(self.get_screen('Shop Screen'))
        self.add_widget(ShopScreen(name='Shop Screen'))
        self.current = 'Shop Screen'

class TitleScreen(Screen):
    
    def __init__(self, **kw):
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

        INPUT_HANDLER.keyboard.bind(on_key_down=self._on_key_down)

    def on_pre_enter(self): # These two make the key events on this widget on accessible here.
        INPUT_HANDLER.keyboard.bind(on_key_down=self._on_key_down)

    def on_pre_leave(self):
        INPUT_HANDLER.keyboard.unbind(on_key_down=self._on_key_down)

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        code, key = keycode
        if key == 'enter':
            #self.parent.shop()
            self.parent.start_game()

class BattleScreen(Screen):
    
    def __init__(self, **kw):
        super(BattleScreen, self).__init__(**kw)
        #l = Label(text='Battle Screen', font_size=72)
        #self.add_widget(l)

    def on_enter(self):
        info = {key: val for key, val in PLAYER_INFO.items() if key in BATTLE_INFO} # Filters bad arguments.
        stage_size = random.randint(1200, 3200), random.randint(800, 2400)
        p = PlayerCharacter(pos=(100, stage_size[1]/4), **info)
        e = EnemyCharacter(pos=(stage_size[0]-100, stage_size[1]/4))
        self.world = BattleWorld(p, e, stage_size)
        self.interface = BattleInterface()
        self.add_widget(self.world)
        self.add_widget(self.interface)
        self.world.start_update()

    def game_over(self, *args):
        self.parent.game_over()

    def victory(self, *args):
        self.parent.victory()

# Children of Battle Screen
class BattleWorld(Widget):
    
    def __init__(self, player, enemy, stage_size, **kw):
        super(BattleWorld, self).__init__(**kw)
        global BATTLE_WORLD # Workaround access
        BATTLE_WORLD = self
        self.update_loop = None
        self.renderer = Renderer()
        self.entity_container = []
        self.terrain_container = []
        self.add_widget(self.renderer)

        self.ENDED = False

        # Constants
        self.GRAVITY = 50 # pixels/s2

        self.player = player
        self.p_dying = False # For animations
        self.enemy = enemy
        self.e_dying = False
        self.entity_container.append(self.player)
        self.entity_container.append(self.enemy)

        self.stage_size = stage_size

        tw = 64 # Tile width.
        tiles_x = stage_size[0] // tw + 1 # round up
        tiles_y = stage_size[1] // tw + 1 # round up
        one = partial(Terrain, source='assets/1x1.png', size=(tw, tw))
        two = partial(Terrain, source='assets/2x1.png', size=(tw*2, tw))
        """terrain = [Terrain(size=(457, 200), pos=(0, 0)), 
                    Terrain(size=(685,100), pos=(457, 0)), # Middle depression
                    Terrain(size=(457,25), pos=(571, 300)), # Middle float
                    Terrain(size=(457,200), pos=(1142, 0))]"""
        layout = [
        [0]*7 + [one]*6 + [0]*7 + [two, 0] * 2,
        [0]*4 + [one]*12 + [0]*4 + [two, 0] * 4,
        None,
        None,
        [one]*(tiles_x*4//20) + [0]*(tiles_x*8//20) + [one]*(tiles_x*4//20),
        [one]*(tiles_x*6//24) + [0]*(tiles_x*3//24) + [one]*(tiles_x*2//24) + [0]*(tiles_x*3//24) + [one]*(tiles_x*6//24) + [0]*(tiles_x*3//24) + [one]*(tiles_x*1//24),
        [two, 0] * (tiles_x // 2),
        ]
        for y, line in enumerate(layout[::-1]):
            if line:
                for x, tile in enumerate(line):
                    if tile:
                        self.terrain_container.append(tile(pos=(x*tw, y*tw)))
        """layout = []
        for y in range(tiles_y):
            layout.append([])
            for x in range(tiles_x):
                pos = (x*tw, y*tw)
                if y == 0: # Bottom layer is full.
                    if x % 2 == 0:
                        layout[y].append(two(pos=pos))

                elif y < 5:
                    print(layout[y])
                    if x >= 1:
                        #if layout[y][x-1].width == 128: #and (pos[0] - layout[y][x-1].x <= 64):
                        #    continue
                        if pos[0] - layout[y][x-1].x <= 128:
                            roll = random.randint(1, 5)
                            if roll > 1:
                                layout[y].append(random.choice([one, two])(pos=pos))
                    else:
                        layout[y].append(random.choice([one, two])(pos=pos))
        for line in layout:
            for i in line:
                if i:
                    self.terrain_container.append(i)"""

        #self.terrain_container.extend(terrain)

        #self.add_widget(FloatingHealthBar(2, player))
        #self.add_widget(FloatingHealthBar(2, enemy))

    def death_animation(self, character, size=(1024, 1024)):
        def on_complete(character):
            character.hp = 0
        duration = 0.6
        size = Animation(size=size, duration=duration)
        opacity = Animation(opacity=0.15, duration=duration)
        death_anim = size & opacity
        death_anim.on_complete = on_complete
        death_anim.start(character)

    def start_update(self): # So the battle start time can be managed easily, e.g. start update after count down
        self.update_loop = Clock.schedule_interval(self.update, 1/FPS)

    def stop_update(self, *args):
        self.update_loop.cancel()

    def update(self, dt):
        self.end_battle()
        if not self.p_dying and self.player.y < -500:
            self.death_animation(self.player)
            self.p_dying = True
        if not self.e_dying and self.enemy.y < -500:
            self.death_animation(self.enemy)
            self.e_dying = True


        for e in self.entity_container:
            e.update_input()
        for e in self.entity_container:
            e.update_physics()
        for a, b in combinations(self.entity_container, 2):
            if a.collide_widget(b):
                a.collide(b)
                b.collide(a)
                bad_normal = Vector(b.center) - a.center
                MULTIPLER = 5
                # fraction of total speed a's speed is.
                #a_ratio = a.velocity.length() / (a.velocity.length() + b.velocity.length())
                #b_ratio = 1 - a_ratio
                #delta_a = a_ratio * MULTIPLER
                #delta_b = b_ratio * MULTIPLER
                if all(isinstance(i, Character) for i in (a, b)):
                    # Transfer of momentum??
                    a.velocity -= bad_normal / FPS * MULTIPLER
                    b.velocity += bad_normal / FPS * MULTIPLER
        for e, t in product(self.entity_container, self.terrain_container):
            e.terrain_collision(t)
        for e in self.entity_container:
            e.update_graphics()
        """for e in self.entity_container:
            e.update_input()
            e.update_physics()
            e.update_graphics()"""
        for t in self.terrain_container:
            t.update_graphics()
        self.renderer.update()


    def end_battle(self):
        if self.enemy.hp > 0 and self.player.hp > 0:
            return None

        if self.ENDED:
            return None
        #self.stop_update()
        #self.renderer.clear() # Wipes image

        DELAY = 0.5
        end = False
        if self.enemy.hp <= 0:
            PLAYER_INFO['battle_num'] += 1 # Plus Score
            self.death_animation(self.enemy, size=(256, 256))
            Clock.schedule_once(self.parent.victory, DELAY)
            end = True
        elif self.player.hp <= 0:
            self.death_animation(self.player, size=(256, 256))
            Clock.schedule_once(self.parent.game_over, DELAY)
            end = True

        if end:
            self.ENDED = end
            PLAYER_INFO['hp'] = self.player.hp # Update hp to end of battle state.
            Clock.schedule_once(self.stop_update, DELAY)
            
    def get_terrain(self): # Temporary stage getter.
        terrain = []
        for t in terrain:
            self.terrain_container.append(t)

# Children of Battle World
class Renderer(Widget): # Camera + graphical engine

    def __init__(self, **kw):
        super(Renderer, self).__init__(**kw)
        global RENDERER # Workaround access
        RENDERER = self
        self.instructions = []
        self.background = 'assets/background1.png'
        self.camera_pos = [0, 0]
        self.camera_size = [0, 0] # In game area to be displayed.
        self.camera_zoom = 1
        self.camera_translate = None # TODO
        self.scale_origin = None

    def update(self):
        self.center_at_midpoint()
        self.render()

    def center_at_midpoint(self): # Camera func to center between the two players
        player = BATTLE_WORLD.player
        enemy = BATTLE_WORLD.enemy
        diff = Vector(player.center).distance(enemy.center)
        mid_point = (Vector(player.center) + enemy.center) / 2

        MIN_SIZE = (800, 300) # minimum size to prevent insane zooms.

        #zof = 1.5 # zoomout factor, How much area the camera covers.
        # SHOULD ALWAYS be Window size, zoom is not affected by translation.
        self.camera_size = Window.size#Vector(1, 0.75) * (diff) * 10 # Gives camera a size based on distance of chicken.
        #if sum(self.camera_size) < sum(MIN_SIZE):
            #self.camera_size = MIN_SIZE

        stage_center = (800, 200)
        #self.camera_pos = (Vector(mid_point)+stage_center) / 2 - Vector(self.camera_size) / 2
        self.camera_pos = Vector(mid_point)- Vector(self.camera_size) / 2

        # This function needs to be refined.
        self.camera_zoom = 1 / ((0.008 * diff + 3) * 0.2) # Ratio of how much to zoom.

        # Adjust this for changing camera position.
        self.camera_translate = Vector(0, 0) - Vector(self.camera_pos) # Camera offset for world coordinates.
        self.camera_translate += Vector(0, 600*0.1) # Offset UI for true center.
        self.scale_origin = Window.center # AFTER TRANSLATION, EVERYTHING SHOULD BE SCALED FROM WINDOW CENTER.

    def render(self): # Update graphical screen.
        self.canvas.clear()
        #self.canvas.add(Rectangle(size=(800, 600), pos=(0,0), source=self.background))
        #self.canvas.add(PushMatrix())
        
        # ORIGIN is based off center, so it being in the center of the screen always is corerct.
        #scale_origin = Vector(self.camera_size) / 2 # The origin is so the picture doesn't center at lower left.
        #scale_origin = Vector() / 2 # Keep it here.
        self.canvas.add(PushMatrix())
        self.canvas.add(Scale(self.camera_zoom+1, origin=self.scale_origin)) # Attempt at parallax bg.
        self.canvas.add(Rectangle(size=(800, 600), pos=(0,0), source=self.background))
        self.canvas.add(PopMatrix())

        self.canvas.add(PushMatrix())
        self.canvas.add(Scale(self.camera_zoom, origin=self.scale_origin))
        self.canvas.add(Translate(*self.camera_translate))

        for b in BATTLE_INTERFACE.healthbars: # Glitchless healthbars / 10m required global variable tho.
            self.instructions.extend(b.instructions)

        for ins in self.instructions:
            self.canvas.add(ins)
        self.canvas.add(PopMatrix())
        self.instructions.clear()

    def clear(self): # Called when battle scene ends, to remove visual glitches.
        self.canvas.clear()
        self.canvas.ask_update()

class BattleInterface(BoxLayout):
    
    def __init__(self, **kw):
        super(BattleInterface, self).__init__(**kw)
        global BATTLE_INTERFACE # Workaround access
        BATTLE_INTERFACE = self
        player = BATTLE_WORLD.player
        enemy = BATTLE_WORLD.enemy
        self.idisplays = []
        for key, item in player.keymapping.items():
            self.idisplays.append(IDisplay(key=key.upper(), item=item, bgcolor=[0,80/255,0.8, 1]))
        for item in enemy.equips:
            self.idisplays.append(IDisplay(key='', item=item, bgcolor=[1,102/255,0,1]))

        for i in self.idisplays:
            self.items.add_widget(i)

        self.healthbars = [FloatingHealthBar(1, player, color=[0,102/255,1]), FloatingHealthBar(1, enemy, color=[1,102/255,0])] 

# Other screens.

class ShopScreen(Screen):

    selected_box = ObjectProperty()
    money = NumericProperty()
    battle_num = NumericProperty()
    health_cost = NumericProperty(1)
    stat_1_cost = NumericProperty(3)
    stat_2_cost = NumericProperty(5)
    stat_3_cost = NumericProperty(2)

    def __init__(self, **kw):
        super(ShopScreen, self).__init__(**kw)
        self.bind(selected_box=self.selection_box)
        self.selected_box = self.one # The current selection, default is one.
        INPUT_HANDLER.keyboard.bind(on_key_down=self._on_key_down)

        self.money = PLAYER_INFO['money']
        self.battle_num = PLAYER_INFO['battle_num']
        self.update_elements() # To initialize properly

    def update_elements(self, *args):
        p = PLAYER_INFO
        self.stat_1.text = str(p['speed'])
        self.stat_2.text = str(p['jump'])
        self.stat_3.text = str(p['max_hp'])
        self.update_health_bar()

    def update_health_bar(self, *args):
        hp = PLAYER_INFO['hp']
        max_hp = PLAYER_INFO['max_hp']
        #print(self.health_bar.width)
        size = self.health_bar.width * (hp / max_hp), self.health_bar.height
        self.health_bar.canvas.before.clear()
        with self.health_bar.canvas.before:
            Color(rgba=(0.5,0.5,0.3,1))
            Rectangle(pos=self.health_bar.pos, size=self.health_bar.size)
            Color(rgba=(0.3,0.6,0.3,1))
            Rectangle(pos=self.health_bar.pos, size=size)
        self.health_bar.text = '[color=#e60000]{}[/color] / [color=#00e600]{}[/color]'.format(hp, max_hp)
        
    def selection_box(self, *args):
        self.selection.pos = self.selected_box.pos
        self.selection.size = self.selected_box.size

    def spend(self, amount): # Simple balance check
        if self.money - amount >= 0:
            return True
        return False

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        code, key = keycode
        s = self.selected_box
        # Not sphagetti, just unelegantti
        if s is self.one:
            if key == 'enter':
                print('One is done')
            elif key == 'd':
                self.selected_box = self.two
            elif key == 's':
                self.selected_box = self.three
            elif key == 'a':
                self.selected_box = self.exit
        elif s is self.two:
            if key == 'enter':
                print('Two is done')
            elif key == 'a':
                self.selected_box = self.one
            elif key == 's':
                self.selected_box = self.four
        elif s is self.three:
            if key == 'enter':
                print('Three is done')
            elif key == 'w':
                self.selected_box = self.one
            elif key == 's':
                self.selected_box = self.five
            elif key == 'd':
                self.selected_box = self.four
            elif key == 'a':
                self.selected_box = self.exit
        elif s is self.four:
            if key == 'enter':
                print('Four is done')
            elif key == 'w':
                self.selected_box = self.two
            elif key == 's':
                self.selected_box = self.five
            elif key == 'a':
                self.selected_box = self.three
        elif s is self.five:
            if key == 'enter':
                print('Five is done')
                if PLAYER_INFO['hp'] < PLAYER_INFO['max_hp']:
                    if self.spend(self.health_cost):
                        self.money -= self.health_cost
                        PLAYER_INFO['hp'] += 1

            elif key == 'w':
                self.selected_box = self.three
            elif key == 's':
                self.selected_box = self.six
            elif key == 'a':
                self.selected_box = self.exit
        elif s is self.six:
            if key == 'enter':
                print('Six is done')
                if self.spend(self.stat_1_cost):
                    self.money -= self.stat_1_cost
                    PLAYER_INFO['speed'] += 1
            elif key == 'w':
                self.selected_box = self.five
            elif key == 's':
                self.selected_box = self.seven
            elif key == 'a':
                self.selected_box = self.exit
        elif s is self.seven:
            if key == 'enter':
                print('Seven is done')
                if self.spend(self.stat_2_cost):
                    self.money -= self.stat_2_cost
                    PLAYER_INFO['jump'] += 1
            elif key == 'w':
                self.selected_box = self.six
            elif key == 's':
                self.selected_box = self.eight
            elif key == 'a':
                self.selected_box = self.exit
        elif s is self.eight:
            if key == 'enter':
                print('Eight is done')
                if self.spend(self.stat_3_cost):
                    self.money -= self.stat_3_cost
                    PLAYER_INFO['max_hp'] += 1
            elif key == 'w':
                self.selected_box = self.seven
            elif key == 'a':
                self.selected_box = self.exit
        elif s is self.exit:
            if key == 'enter':
                self.leave_shop()
            elif key == 'w':
                self.selected_box = self.one
            elif key == 'd':
                self.selected_box = self.eight
        self.update_elements() # Update for things that aren't bound.

    def on_leave(self):
        INPUT_HANDLER.keyboard.unbind(on_key_down=self._on_key_down)
        PLAYER_INFO['money'] = self.money # Updates

    def leave_shop(self):
        self.parent.start_game()

class DeathScreen(Screen):

    def __init__(self, **kw):
        super(DeathScreen, self).__init__(**kw)
        INPUT_HANDLER.keyboard.bind(on_key_down=self._on_key_down)
        press_enter = FlashingText(interval=1.25, text='~Press ENTER to restart~', font_size='36sp', y=-100)

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        code, key = keycode
        if key == 'enter':
            OCaTTApp.parse_savefile(None) # Resets game state.
            self.parent.title_screen()

    def on_leave(self):
        INPUT_HANDLER.keyboard.unbind(on_key_down=self._on_key_down)

class VictoryScreen(Screen):
    
    gained_money = NumericProperty()
    display_text = StringProperty('~Victorious~')

    def __init__(self, **kw):
        super(VictoryScreen, self).__init__(**kw)
        INPUT_HANDLER.keyboard.bind(on_key_down=self._on_key_down)

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        code, key = keycode
        if key == 'enter':
            self.manager.shop()

    def on_leave(self):
        INPUT_HANDLER.keyboard.unbind(on_key_down=self._on_key_down)

    def on_pre_enter(self):
        if PLAYER_INFO['battle_num'] != 11:
            self.get_money()
        else:
            self.display_text = '~You are now top chicken, there is no room for two~'
            self.gained_money = 100000

    def get_money(self):
        m = PLAYER_INFO['battle_num'] * 30
        new = int(random.gauss(m, 10))
        PLAYER_INFO['money'] += new # Add the moneys
        inc = Animation(gained_money=new, duration=1)
        inc.start(self)

class SoundEngine(Widget):
    
    def __init__(self, **kw):
        super(SoundEngine, self).__init__(**kw)
        self.screen_to_song = {
            'Title Screen': SoundLoader.load('assets/music/Twisted.mp3'),
            'Battle Screen': SoundLoader.load('assets/music/Blown Away.mp3'),
            'Death Screen': SoundLoader.load('assets/music/Suave Standpipe.mp3'),
            'Victory Screen': SoundLoader.load('assets/music/Open Those Bright Eyes.mp3'),
            'Shop Screen': SoundLoader.load('assets/music/Lobby Time.mp3')
            }
        self.transition_duration = 3 # graph of one going down other going up.
        source = self.screen_to_song[SCREEN_MANAGEMENT.current]
        self.current = source
        if self.current:
            self.current.loop = True
            self.current.play()

        Clock.schedule_interval(self.update, 1/2)

        #SCREEN_MANAGEMENT.bind(current=self._on_change_screen)
        #print('sound init')

    def update(self, *args):
        new = SCREEN_MANAGEMENT.current
        source = self.screen_to_song[new]
        if source == self.current:
            return None
        else:
            try:
                self.current.stop()
                self.current.seek(0) # Return to start of song.
            except AttributeError:
                pass
            self.current = source
            self.current.loop = True
            self.current.play()


class OCaTTApp(App): # One room at the top

    savefile = 'savefile.txt'

    def __init__(self, **kw): # Pending: Initialize window parameters
        super(OCaTTApp, self).__init__(**kw)
        self.sound_engine = None

    def parse_savefile(*args): # looks for save file, checks if exists, returns relevant data.
        with open(OCaTTApp.savefile, 'r') as f:
            data = f.read().split('\n')
        data = [i.split(',') for i in data]
        # this dict can be used as kwargs for battle player.
        player_info = {
        'max_speed': int(data[0][1]), # Unused
        'max_hp': int(data[1][1]),
        'size': [int(i) for i in data[2][1:]],
        'battle_num': int(data[3][1]),
        'equips': [ITEM_CONVERSION_TABLE[i] for i in data[4][1:]],
        'money': int(data[5][1]),
        'hp': int(data[6][1]),
        'speed': int(data[7][1]),
        'jump': int(data[8][1])
        }
        global PLAYER_INFO
        PLAYER_INFO = player_info

        global BATTLE_INFO # The keys used for initializing battle version.
        #BATTLE_INFO = ('max_speed', 'max_hp', 'size', 'equips', 'hp', 'speed', 'jump')
        BATTLE_INFO = ('max_hp', 'size', 'equips', 'hp', 'speed', 'jump')


    def build(self):
        self.parse_savefile() # get player info.
        sm = ScreenManagement()
        self.sound_engine = SoundEngine()
        return sm
        
if __name__ == '__main__':
    OCaTTApp().run()