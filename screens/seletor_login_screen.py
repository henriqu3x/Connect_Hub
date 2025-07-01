from kivy.core.window import Window
from kivy.properties import ListProperty
from kivymd.uix.card import MDCard
from kivy.uix.screenmanager import Screen
from kivy.animation import Animation
from kivy.properties import BooleanProperty

class SeletorLoginScreen(Screen):
    pass

class HoverMDCard(MDCard):
    solid = BooleanProperty(True)
    normal_color = ListProperty([0.5, 0.3, 0.8, 1])
    hover_color = ListProperty([0.6, 0.4, 0.9, 0.2])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)
        self.is_hovered = False
        if self.solid:
            self.md_bg_color = self.normal_color
        else:
            self.md_bg_color = [0, 0, 0, 0]  
    
    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return
        pos = args[1]
        inside = self.collide_point(*self.to_widget(*pos))
        if inside and not self.is_hovered:
            Animation(md_bg_color=self.hover_color, d=0.2).start(self)
            Window.set_system_cursor("hand")
            self.is_hovered = True
        elif not inside and self.is_hovered:
            Animation(md_bg_color=self.normal_color, d=0.2).start(self)
            Window.set_system_cursor("arrow")
            self.is_hovered = False
    
    def reset_color(self):
        if self.solid:
            self.md_bg_color = self.normal_color
        else:
            self.md_bg_color = [0, 0, 0, 0]
        self.is_hovered = False
        Window.set_system_cursor("arrow")