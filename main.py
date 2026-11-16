import json
import os
import random
import time
import webbrowser

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

Window.clearcolor = (0.06, 0.08, 0.12, 1)


class ModernCard(BoxLayout):
    def __init__(self, bg=(0.11, 0.14, 0.20, 1), border=(0.2, 0.26, 0.36, 1), radius=14, **kwargs):
        super().__init__(**kwargs)
        self.bg = bg
        self.border = border
        self.rad = radius
        self.bind(pos=self.redraw, size=self.redraw)

    def redraw(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[self.rad])
            Color(*self.border)
            Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, self.rad),
                width=1.1,
            )


class NiceButton(Button):
    def __init__(self, bg=(0.15, 0.55, 0.85, 1), radius=12, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.bg = bg
        self.rad = radius
        self.bind(pos=self.redraw, size=self.redraw, state=self.redraw)

    def redraw(self, *args):
        self.canvas.before.clear()
        if self.state == "down":
            c = [max(0, x - 0.08) for x in self.bg[:3]] + [1]
        else:
            c = self.bg
        with self.canvas.before:
            Color(*c)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[self.rad])


class LoadBar(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.percent = 0.0
        self.bind(pos=self.draw, size=self.draw)

    def set_percent(self, pct):
        self.percent = max(0.0, min(100.0, pct))
        self.draw()

    def draw(self, *args):
        self.canvas.clear()
        if self.width <= 10:
            return
        with self.canvas:
            Color(0.16, 0.20, 0.28, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[6])
            w = (self.percent / 100.0) * self.width
            if self.percent > 90:
                Color(0.95, 0.22, 0.25, 1)
            elif self.percent > 70:
                Color(0.95, 0.65, 0.15, 1)
            else:
                Color(0.15, 0.85, 0.45, 1)
            if w > 4:
                RoundedRectangle(pos=self.pos, size=(w, self.height), radius=[6])


class NeonGraph(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.limit = 50.0
        self.scale = 70.0
        self.data = []
        self.bind(pos=self.draw, size=self.draw)

    def update_data(self, data, lim):
        self.data = list(data)
        self.limit = float(lim)
        self.scale = max(self.limit * 1.35, 35.0)
        self.draw()

    def draw(self, *args):
        self.canvas.clear()
        if self.width <= 10 or self.height <= 10:
            return
        with self.canvas:
            Color(0.10, 0.13, 0.19, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[14])

            Color(0.22, 0.27, 0.36, 0.45)
            for i in range(1, 4):
                gy = self.y + (self.height / 4.0) * i
                Line(points=[self.x + 12, gy, self.x + self.width - 12, gy], width=1)

            ly = self.y + (self.limit / self.scale) * self.height
            Color(0.95, 0.25, 0.3, 0.85)
            Line(points=[self.x + 8, ly, self.x + self.width - 8, ly], width=1.5)

            sx = (self.width - 24) / 14.0
            if len(self.data) > 1:
                pts = []
                for i, v in enumerate(self.data):
                    pts.extend([
                        self.x + 12 + i * sx,
                        self.y + (v / self.scale) * self.height,
                    ])
                Color(0.1, 0.7, 1, 0.25)
                Line(points=pts, width=6.0)
                Color(0.2, 0.85, 1, 1)
                Line(points=pts, width=2.4)

            for i, v in enumerate(self.data):
                px = self.x + 12 + i * sx
                py = self.y + (v / self.scale) * self.height
                col = (1, 0.2, 0.25, 1) if v > self.limit else (0.15, 0.95, 0.5, 1)
                Color(col[0], col[1], col[2], 0.3)
                Ellipse(pos=(px - 7, py - 7), size=(14, 14))
                Color(*col)
                Ellipse(pos=(px - 3.5, py - 3.5), size=(7, 7))


class LoginScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.reg_mode = False

        root = BoxLayout(orientation="vertical", padding=26, spacing=14)
        root.add_widget(Widget(size_hint=(1, 0.08)))

        card = ModernCard(
            orientation="vertical",
            padding=22,
            spacing=12,
            bg=(0.10, 0.13, 0.19, 1),
            radius=20,
            size_hint=(1, 0.76),
        )
        card.add_widget(
            Label(
                text="ODTI ENERGIYA PRO",
                font_size="22sp",
                bold=True,
                color=(0.25, 0.85, 1, 1),
                size_hint=(1, 0.16),
            )
        )

        self.sub_lbl = Label(
            text="Smart Elektr Monitoring Tizimi",
            font_size="13sp",
            color=(0.65, 0.72, 0.82, 1),
            size_hint=(1, 0.08),
        )
        card.add_widget(self.sub_lbl)

        self.lg = TextInput(
            text="admin",
            hint_text="Login",
            multiline=False,
            font_size="16sp",
            padding=[12, 12],
            background_color=(0.16, 0.20, 0.28, 1),
            foreground_color=(1, 1, 1, 1),
            size_hint=(1, 0.14),
        )
        self.pw = TextInput(
            text="1234",
            hint_text="Parol",
            password=True,
            multiline=False,
            font_size="16sp",
            padding=[12, 12],
            background_color=(0.16, 0.20, 0.28, 1),
            foreground_color=(1, 1, 1, 1),
            size_hint=(1, 0.14),
        )
        self.err = Label(
            text="",
            color=(1, 0.35, 0.35, 1),
            font_size="13sp",
            size_hint=(1, 0.08),
        )

        self.btn_ok = NiceButton(
            text="TIZIMGA KIRISH",
            font_size="16sp",
            bold=True,
            bg=(0.12, 0.65, 0.42, 1),
            size_hint=(1, 0.15),
        )
        self.btn_ok.bind(on_press=self.kirish)

        self.btn_sw = NiceButton(
            text="Yangi hisob yaratish",
            font_size="14sp",
            bg=(0.20, 0.26, 0.36, 1),
            size_hint=(1, 0.13),
        )
        self.btn_sw.bind(on_press=self.rejim)

        card.add_widget(self.lg)
        card.add_widget(self.pw)
        card.add_widget(self.err)
        card.add_widget(self.btn_ok)
        card.add_widget(self.btn_sw)

        root.add_widget(card)
        root.add_widget(Widget(size_hint=(1, 0.16)))
        self.add_widget(root)

    def rejim(self, inst):
        self.reg_mode = not self.reg_mode
        self.err.text = ""
        if self.reg_mode:
            self.lg.text, self.pw.text = "", ""
            self.sub_lbl.text = "Yangi xodim profilini ochish"
            self.btn_ok.text = "RO'YXATDAN O'TISH"
            self.btn_sw.text = "Kirish oynasiga qaytish"
        else:
            self.lg.text, self.pw.text = "admin", "1234"
            self.sub_lbl.text = "Smart Elektr Monitoring Tizimi"
            self.btn_ok.text = "TIZIMGA KIRISH"
            self.btn_sw.text = "Yangi hisob yaratish"

    def kirish(self, inst):
        u, p = self.lg.text.strip(), self.pw.text.strip()
        if not u or not p:
            self.err.text = "Login va parolni kiriting!"
            return

        users = self.app.db["users"]
        if self.reg_mode:
            if u in users:
                self.err.text = "Bu login band!"
                return
            users[u] = p
            self.app.save_db()
            self.app.ochish(u)
        else:
            if users.get(u) == p:
                self.app.ochish(u)
            else:
                self.err.text = "Login yoki parol noto'g'ri!"


class HomeScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.baza = {}
        self.jurnal = []
        self.joriy = "ODTI - Asosiy bino"
        self.avto = True
        self.test_rejim = False
        self.ip = "192.168.4.1"

        root = BoxLayout(orientation="vertical", padding=12, spacing=8)

        top_u = BoxLayout(spacing=5, size_hint=(1, 0.06))
        self.u_lbl = Label(
            text="● admin",
            font_size="12sp",
            bold=True,
            color=(0.3, 0.95, 0.55, 1),
            halign="left",
            size_hint=(0.28, 1),
        )
        self.u_lbl.bind(size=self.u_lbl.setter("text_size"))

        self.mode_btn = NiceButton(
            text="Rejim: REAL",
            font_size="11sp",
            bold=True,
            bg=(0.15, 0.55, 0.85, 1),
            radius=10,
            size_hint=(0.26, 1),
        )
        self.mode_btn.bind(on_press=self.rejim_oyna)

        self.log_btn = NiceButton(
            text="Jurnal (0)",
            font_size="11sp",
            bold=True,
            bg=(0.65, 0.42, 0.14, 1),
            radius=10,
            size_hint=(0.24, 1),
        )
        self.log_btn.bind(on_press=self.jurnal_oyna)

        btn_out = NiceButton(
            text="Chiqish",
            font_size="11sp",
            bold=True,
            bg=(0.75, 0.22, 0.25, 1),
            radius=10,
            size_hint=(0.22, 1),
        )
        btn_out.bind(on_press=self.chiqish)

        top_u.add_widget(self.u_lbl)
        top_u.add_widget(self.mode_btn)
        top_u.add_widget(self.log_btn)
        top_u.add_widget(btn_out)
        root.add_widget(top_u)

        h_bar = BoxLayout(spacing=8, size_hint=(1, 0.07))
        self.spn = Spinner(
            text=self.joriy,
            font_size="13sp",
            bold=True,
            background_normal="",
            background_color=(0.14, 0.34, 0.58, 1),
            size_hint=(0.72, 1),
        )
        self.spn.bind(text=self.hudud_ozgardi)

        btn_add = NiceButton(
            text="+ Bino",
            font_size="13sp",
            bold=True,
            bg=(0.15, 0.62, 0.38, 1),
            radius=10,
            size_hint=(0.28, 1),
        )
        btn_add.bind(on_press=self.yangi_bino)

        h_bar.add_widget(self.spn)
        h_bar.add_widget(btn_add)
        root.add_widget(h_bar)

        m_card = ModernCard(
            bg=(0.12, 0.16, 0.23, 1),
            padding=[10, 6],
            spacing=8,
            size_hint=(1, 0.085),
        )
        self.m_lbl = Label(
            text="Manzil: ...",
            font_size="12sp",
            color=(0.95, 0.85, 0.45, 1),
            halign="left",
            valign="middle",
            size_hint=(1, 1),
        )
        m_card.add_widget(self.m_lbl)
        root.add_widget(m_card)

        self.add_widget(root)

    def rejim_oyna(self, inst):
        pass

    def jurnal_oyna(self, inst):
        pass

    def chiqish(self, inst):
        self.manager.current = "login"

    def hudud_ozgardi(self, inst, value):
        self.m_lbl.text = f"Manzil: {value}"

    def yangi_bino(self, inst):
        pass


class ODTIApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = {"users": {"admin": "1234"}}
        self.login_screen = None
        self.home_screen = None

    def save_db(self):
        return True

    def ochish(self, user):
        if self.root is not None:
            self.root.current = "home"
            self.home_screen.u_lbl.text = f"● {user}"

    def build(self):
        sm = ScreenManager()

        self.login_screen = LoginScreen(self, name="login")
        self.home_screen = HomeScreen(self, name="home")

        sm.add_widget(self.login_screen)
        sm.add_widget(self.home_screen)
        sm.current = "login"
        return sm


if __name__ == "__main__":
    ODTIApp().run()


# End of fixed file.
