import random, time, webbrowser
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

Window.clearcolor = (0.94, 0.96, 0.98, 1)

TEAL = (0.04, 0.68, 0.85, 1)
TEAL_LIGHT = (0.88, 0.96, 0.98, 1)
DARK = (0.11, 0.15, 0.21, 1)
GRAY = (0.48, 0.54, 0.62, 1)
WHITE = (1, 1, 1, 1)
SHADOW = (0.85, 0.89, 0.93, 1)


class Card(BoxLayout):

  def __init__(self, bg=WHITE, r=18, **kw):
    super().__init__(**kw)
    self.bg, self.r = bg, r
    self.bind(pos=self.upd, size=self.upd)

  def upd(self, *a):
    self.canvas.before.clear()
    with self.canvas.before:
      Color(*SHADOW)
      RoundedRectangle(
          pos=(self.x, self.y - 3),
          size=(self.width, self.height),
          radius=[self.r],
      )
      Color(*self.bg)
      RoundedRectangle(pos=self.pos, size=self.size, radius=[self.r])


class PillBtn(Button):

  def __init__(self, bg=TEAL, fg=WHITE, r=16, **kw):
    super().__init__(**kw)
    self.background_normal = ""
    self.background_down = ""
    self.background_color = (0, 0, 0, 0)
    self.bg, self.r, self.color = bg, r, fg
    self.bind(pos=self.upd, size=self.upd, state=self.upd)

  def upd(self, *a):
    self.canvas.before.clear()
    if self.state == "down":
      c = (
          max(0.0, self.bg[0] - 0.08),
          max(0.0, self.bg[1] - 0.08),
          max(0.0, self.bg[2] - 0.08),
          1,
      )
    else:
      c = self.bg
    with self.canvas.before:
      Color(*c)
      RoundedRectangle(pos=self.pos, size=self.size, radius=[self.r])


class BalanceGauge(Widget):

  def __init__(self, **kw):
    super().__init__(**kw)
    self.ratio = 0.74
    self.bind(pos=self.draw, size=self.draw)

  def draw(self, *a):
    self.canvas.clear()
    if self.width <= 10 or self.height <= 10:
      return
    cx = self.center_x
    cy = self.y + self.height * 0.28
    rad = min(self.width * 0.36, self.height * 0.62)
    with self.canvas:
      Color(0.88, 0.92, 0.96, 1)
      Line(circle=(cx, cy, rad, -110, 110), width=7, cap="round")
      Color(*TEAL)
      end_a = -110 + (220 * self.ratio)
      Line(circle=(cx, cy, rad, -110, end_a), width=7, cap="round")


class BarDiagram(Widget):

  def __init__(self, **kw):
    super().__init__(**kw)
    self.vals = [547, 2010, 185, 685, 4650, 2120]
    self.is_solar = False
    self.is_sum = False
    self.bind(pos=self.draw, size=self.draw)

  def set_mode(self, solar=False, is_sum=False):
    self.is_solar, self.is_sum = solar, is_sum
    base = (
        [320, 480, 590, 740, 890, 950]
        if solar
        else [547, 2010, 185, 685, 4650, 2120]
    )
    self.vals = [v * 900 if is_sum else v for v in base]
    self.draw()

  def draw(self, *a):
    self.canvas.clear()
    if self.width <= 20 or self.height <= 20:
      return
    max_v = max(self.vals) * 1.15
    n = len(self.vals)
    bw = (self.width - 36) / (n * 1.8)
    gap = bw * 0.8
    with self.canvas:
      Color(0.91, 0.94, 0.97, 1)
      for i in range(1, 5):
        gy = self.y + (self.height / 5.0) * i
        Line(points=[self.x + 8, gy, self.x + self.width - 8, gy], width=1)
      for i, v in enumerate(self.vals):
        bx = self.x + 18 + i * (bw + gap)
        bh = (v / max_v) * (self.height - 16)
        raw = v / 900 if self.is_sum else v
        if self.is_solar:
          Color(0.14, 0.78, 0.45, 1)
        elif raw > 1500:
          Color(0.95, 0.25, 0.28, 1)
        elif raw > 500:
          Color(0.98, 0.72, 0.15, 1)
        else:
          Color(0.15, 0.80, 0.45, 1)
        RoundedRectangle(
            pos=(bx, self.y + 8), size=(bw, max(bh, 10)), radius=[6, 6, 0, 0]
        )


class LoginScreen(Screen):

  def __init__(self, app, **kw):
    super().__init__(**kw)
    self.app = app
    root = BoxLayout(orientation="vertical", padding=22, spacing=14)

    # Tepa firuza banner
    banner = Card(
        orientation="vertical", bg=TEAL, r=22, padding=18, size_hint=(1, 0.28)
    )
    banner.add_widget(
        Label(
            text="HUDUDIY ELEKTR\nTARMOQLARI",
            font_size="22sp",
            bold=True,
            halign="center",
            color=WHITE,
        )
    )
    banner.add_widget(
        Label(
            text="ODTI Smart Energiya Nazorati",
            font_size="13sp",
            color=TEAL_LIGHT,
        )
    )
    root.add_widget(banner)

    # Oq kirish kartasi
    card = Card(
        orientation="vertical", padding=22, spacing=12, size_hint=(1, 0.62)
    )
    l1 = Label(
        text="Xush kelibsiz!",
        font_size="20sp",
        bold=True,
        color=DARK,
        halign="left",
        size_hint=(1, 0.15),
    )
    l2 = Label(
        text="Kabinetga kirish uchun ma'lumotlarni kiriting",
        font_size="12sp",
        color=GRAY,
        halign="left",
        size_hint=(1, 0.10),
    )
    for w in (l1, l2):
      w.bind(size=w.setter("text_size"))
      card.add_widget(w)

    self.acc_in = TextInput(
        text="3323310231747",
        hint_text="Shaxsiy hisob raqami",
        multiline=False,
        font_size="16sp",
        padding=[14, 12],
        background_normal="",
        background_color=(0.94, 0.96, 0.98, 1),
        foreground_color=DARK,
        size_hint=(1, 0.18),
    )
    self.pw_in = TextInput(
        text="1234",
        hint_text="Parol",
        password=True,
        multiline=False,
        font_size="16sp",
        padding=[14, 12],
        background_normal="",
        background_color=(0.94, 0.96, 0.98, 1),
        foreground_color=DARK,
        size_hint=(1, 0.18),
    )
    self.err = Label(
        text="", color=(0.9, 0.2, 0.2, 1), font_size="13sp", size_hint=(1, 0.08)
    )

    btn = PillBtn(
        text="Davom etish", font_size="16sp", bold=True, r=20, size_hint=(1, 0.20)
    )
    btn.bind(on_press=self.do_login)

    for w in (self.acc_in, self.pw_in, self.err, btn):
      card.add_widget(w)
    root.add_widget(card)
    root.add_widget(Widget(size_hint=(1, 0.10)))
    self.add_widget(root)

  def do_login(self, inst):
    if self.acc_in.text.strip() and self.pw_in.text.strip():
      self.app.enter_app(self.acc_in.text.strip())
    else:
      self.err.text = "Hisob raqami va parolni kiriting!"


class MainScreen(Screen):

  def __init__(self, app, **kw):
    super().__init__(**kw)
    self.app = app
    self.balans = 259394.00
    self.kwh = 7819.0
    self.kw_now = 0.0
    self.test_rejim = False
    self.ip = "192.168.4.1"
    self.solar_mode = False
    self.sum_mode = False

    root = BoxLayout(orientation="vertical")

    self.sm = ScreenManager(size_hint=(1, 0.90))
    self.p_home = Screen(name="home")
    self.p_stat = Screen(name="stat")
    self.p_map = Screen(name="map")
    self.p_help = Screen(name="help")

    self.init_home()
    self.init_stat()
    self.init_map()
    self.init_help()

    for p in (self.p_home, self.p_stat, self.p_map, self.p_help):
      self.sm.add_widget(p)
    root.add_widget(self.sm)

    # Pastki oq navigatsiya paneli
    nav = Card(padding=[10, 8], spacing=8, r=0, size_hint=(1, 0.10))
    self.tabs = {}
    items = [
        ("home", "Asosiy"),
        ("stat", "Statistika"),
        ("map", "Filiallar"),
        ("help", "Yordam"),
    ]
    for code, name in items:
      b = PillBtn(
          text=name,
          font_size="13sp",
          bold=True,
          bg=TEAL if code == "home" else (0.93, 0.96, 0.98, 1),
          fg=WHITE if code == "home" else DARK,
          r=14,
      )
      b.bind(on_press=lambda inst, c=code: self.go_tab(c))
      self.tabs[code] = b
      nav.add_widget(b)
    root.add_widget(nav)
    self.add_widget(root)

  def go_tab(self, code):
    self.sm.current = code
    for k, b in self.tabs.items():
      b.bg = TEAL if k == code else (0.93, 0.96, 0.98, 1)
      b.color = WHITE if k == code else DARK
      b.upd()

  def init_home(self):
    box = BoxLayout(orientation="vertical", padding=14, spacing=10)

    # 1. Yuqori sarlavha
    hdr = BoxLayout(spacing=6, size_hint=(1, 0.08))
    self.acc_lbl = Label(
        text="Shaxsiy hisob\n3323310231747",
        font_size="12sp",
        bold=True,
        color=DARK,
        halign="left",
        size_hint=(0.44, 1),
    )
    self.acc_lbl.bind(size=self.acc_lbl.setter("text_size"))

    self.mode_btn = PillBtn(
        text="Rejim: REAL", font_size="11sp", bold=True, r=12, size_hint=(0.32, 0.82)
    )
    self.mode_btn.bind(on_press=self.open_mode_popup)

    out_b = PillBtn(
        text="Chiqish",
        font_size="11sp",
        bold=True,
        bg=(0.96, 0.88, 0.88, 1),
        fg=(0.82, 0.2, 0.2, 1),
        r=12,
        size_hint=(0.24, 0.82),
    )
    out_b.bind(on_press=lambda x: setattr(self.app.sm, "current", "login"))

    hdr.add_widget(self.acc_lbl)
    hdr.add_widget(self.mode_btn)
    hdr.add_widget(out_b)
    box.add_widget(hdr)

    # 2. Markaziy Balans Kartasi (Aylana yoy bilan)
    b_card = Card(orientation="vertical", padding=14, size_hint=(1, 0.43))
    self.gauge = BalanceGauge(size_hint=(1, 0.46))
    b_card.add_widget(self.gauge)
    b_card.add_widget(
        Label(
            text="Sizning oldindan to'lovingiz",
            font_size="12sp",
            color=GRAY,
            size_hint=(1, 0.11),
        )
    )
    self.bal_lbl = Label(
        text="259 394.00 so'm",
        font_size="22sp",
        bold=True,
        color=DARK,
        size_hint=(1, 0.20),
    )
    b_card.add_widget(self.bal_lbl)

    pay_btn = PillBtn(
        text="Balansni to'ldirish (+50 000)",
        font_size="14sp",
        bold=True,
        r=18,
        size_hint=(1, 0.23),
