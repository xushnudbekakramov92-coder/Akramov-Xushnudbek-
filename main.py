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

# HET yorqin oq-kulrang fon
Window.clearcolor = (0.95, 0.97, 0.99, 1)

TEAL = (0.04, 0.68, 0.85, 1)
DARK = (0.12, 0.16, 0.22, 1)
GRAY = (0.48, 0.54, 0.62, 1)
WHITE = (1, 1, 1, 1)


class WhiteCard(BoxLayout):

  def __init__(self, bg=WHITE, r=16, **kw):
    super().__init__(**kw)
    self.bg, self.r = bg, r
    self.bind(pos=self.upd, size=self.upd)

  def upd(self, *a):
    self.canvas.before.clear()
    with self.canvas.before:
      Color(0.86, 0.90, 0.94, 1)
      RoundedRectangle(
          pos=(self.x - 1, self.y - 2),
          size=(self.width + 2, self.height + 2),
          radius=[self.r],
      )
      Color(*self.bg)
      RoundedRectangle(pos=self.pos, size=self.size, radius=[self.r])


class TealBtn(Button):

  def __init__(self, bg=TEAL, fg=WHITE, r=14, **kw):
    super().__init__(**kw)
    self.background_normal, self.background_color, self.bg, self.r = (
        "",
        (0, 0, 0, 0),
        bg,
        r,
    )
    self.color = fg
    self.bind(pos=self.upd, size=self.upd, state=self.upd)

  def upd(self, *a):
    self.canvas.before.clear()
    c = (
        [max(0, x - 0.08) for x in self.bg[:3]] + [1]
        if self.state == "down"
        else self.bg
    )
    with self.canvas.before:
      Color(*c)
      RoundedRectangle(pos=self.pos, size=self.size, radius=[self.r])


class BalanceArc(Widget):

  def __init__(self, **kw):
    super().__init__(**kw)
    self.progress = 0.72
    self.bind(pos=self.draw, size=self.draw)

  def draw(self, *a):
    self.canvas.clear()
    if self.width <= 10:
      return
    cx, cy = self.center_x, self.center_y
    rad = min(self.width, self.height) * 0.43
    with self.canvas:
      Color(0.88, 0.92, 0.95, 1)
      Line(circle=(cx, cy, rad, -135, 135), width=6)
      Color(*TEAL)
      end_ang = -135 + 270 * self.progress
      Line(circle=(cx, cy, rad, -135, end_ang), width=6)


class MonthlyBarChart(Widget):

  def __init__(self, **kw):
    super().__init__(**kw)
    self.vals = [547, 2010, 185, 685, 4650, 2120]
    self.months = ["Yan", "Fev", "Mar", "Apr", "May", "Iyun"]
    self.is_solar = False
    self.is_sum = False
    self.bind(pos=self.draw, size=self.draw)

  def update_chart(self, solar=False, is_sum=False):
    self.is_solar, self.is_sum = solar, is_sum
    base = (
        [180, 320, 410, 520, 690, 740]
        if solar
        else [547, 2010, 185, 685, 4650, 2120]
    )
    self.vals = [v * 900 if is_sum else v for v in base]
    self.draw()

  def draw(self, *a):
    self.canvas.clear()
    if self.width <= 20:
      return
    max_v = max(self.vals) * 1.15
    n = len(self.vals)
    bw = (self.width - 40) / (n * 1.8)
    gap = bw * 0.8
    with self.canvas:
      Color(0.90, 0.93, 0.96, 1)
      for i in range(1, 4):
        gy = self.y + (self.height / 4.0) * i
        Line(points=[self.x + 10, gy, self.x + self.width - 10, gy], width=1)
      for i, v in enumerate(self.vals):
        bx = self.x + 20 + i * (bw + gap)
        bh = (v / max_v) * (self.height - 25)
        raw = v / 900 if self.is_sum else v
        if self.is_solar:
          Color(0.15, 0.78, 0.45, 1)
        elif raw > 1500:
          Color(0.95, 0.25, 0.25, 1)
        elif raw > 500:
          Color(0.98, 0.72, 0.15, 1)
        else:
          Color(0.15, 0.80, 0.45, 1)
        RoundedRectangle(
            pos=(bx, self.y + 18), size=(bw, max(bh, 8)), radius=[6, 6, 0, 0]
        )


class LoginScr(Screen):

  def __init__(self, app, **kw):
    super().__init__(**kw)
    self.app = app
    root = BoxLayout(orientation="vertical", padding=24, spacing=14)
    root.add_widget(Widget(size_hint=(1, 0.08)))

    card = WhiteCard(
        orientation="vertical", padding=22, spacing=12, size_hint=(1, 0.78)
    )
    card.add_widget(
        Label(
            text="ODTI ELEKTR TARMOQLARI",
            font_size="19sp",
            bold=True,
            color=TEAL,
            size_hint=(1, 0.16),
        )
    )
    card.add_widget(
        Label(
            text="Xush kelibsiz! Kabinetga kiring",
            font_size="14sp",
            color=GRAY,
            size_hint=(1, 0.1),
        )
    )

    self.acc_in = TextInput(
        text="3323310231747",
        hint_text="Shaxsiy hisob raqami",
        multiline=False,
        font_size="16sp",
        padding=[12, 12],
        background_normal="",
        background_color=(0.94, 0.96, 0.98, 1),
        foreground_color=DARK,
        size_hint=(1, 0.15),
    )
    self.pw_in = TextInput(
        text="1234",
        hint_text="Parol",
        password=True,
        multiline=False,
        font_size="16sp",
        padding=[12, 12],
        background_normal="",
        background_color=(0.94, 0.96, 0.98, 1),
        foreground_color=DARK,
        size_hint=(1, 0.15),
    )
    self.err = Label(
        text="", color=(0.9, 0.2, 0.2, 1), font_size="13sp", size_hint=(1, 0.08)
    )

    btn = TealBtn(
        text="Davom etish", font_size="16sp", bold=True, size_hint=(1, 0.16)
    )
    btn.bind(on_press=self.login)

    for w in (self.acc_in, self.pw_in, self.err, btn):
      card.add_widget(w)
    root.add_widget(card)
    root.add_widget(Widget(size_hint=(1, 0.14)))
    self.add_widget(root)

  def login(self, inst):
    if self.acc_in.text.strip() and self.pw_in.text.strip():
      self.app.open_app(self.acc_in.text.strip())
    else:
      self.err.text = "Hisob raqami va parolni kiriting!"


class MainAppScr(Screen):

  def __init__(self, app, **kw):
    super().__init__(**kw)
    self.app = app
    self.balans = 259394.00
    self.kwh = 7819.0
    self.kw_now = 18.4
    self.solar_mode = False
    self.sum_mode = False

    root = BoxLayout(orientation="vertical")

    # Ichki sahifalar menejeri
    self.inner_sm = ScreenManager(size_hint=(1, 0.90))
    self.s_home = Screen(name="home")
    self.s_stat = Screen(name="stat")
    self.s_map = Screen(name="map")
    self.s_chat = Screen(name="chat")

    self.build_home()
    self.build_stat()
    self.build_map()
    self.build_chat()

    for s in (self.s_home, self.s_stat, self.s_map, self.s_chat):
      self.inner_sm.add_widget(s)
    root.add_widget(self.inner_sm)

    # Pastki navigatsiya paneli (4 ta bo'lim)
    nav = WhiteCard(padding=[8, 6], spacing=6, r=0, size_hint=(1, 0.10))
    self.nav_btns = {}
    tabs = [
        ("home", "Asosiy"),
        ("stat", "Statistika"),
        ("map", "Filiallar"),
        ("chat", "Yordam"),
    ]
    for code, title in tabs:
      b = TealBtn(
          text=title,
          font_size="13sp",
          bold=True,
          bg=TEAL if code == "home" else (0.92, 0.95, 0.97, 1),
          fg=WHITE if code == "home" else DARK,
          r=10,
      )
      b.bind(on_press=lambda inst, c=code: self.switch_tab(c))
      self.nav_btns[code] = b
      nav.add_widget(b)
    root.add_widget(nav)
    self.add_widget(root)

  def switch_tab(self, code):
    self.inner_sm.current = code
    for k, b in self.nav_btns.items():
      b.bg = TEAL if k == code else (0.92, 0.95, 0.97, 1)
      b.color = WHITE if k == code else DARK
      b.upd()

  # 1-SAHIFA: ASOSIY (Balans, Schyotchik holati, Batafsil)
  def build_home(self):
    box = BoxLayout(orientation="vertical", padding=14, spacing=10)

    # Tepasi: Shaxsiy hisob va Chiqish
    hdr = BoxLayout(size_hint=(1, 0.08))
    self.acc_lbl = Label(
        text="Shaxsiy hisob:\n3323310231747",
        font_size="13sp",
        bold=True,
        color=DARK,
        halign="left",
    )
    self.acc_lbl.bind(size=self.acc_lbl.setter("text_size"))
    out_b = TealBtn(
        text="Chiqish",
        font_size="12sp",
        bg=(0.95, 0.88, 0.88, 1),
        fg=(0.8, 0.2, 0.2, 1),
        size_hint=(0.28, 0.8),
    )
    out_b.bind(on_press=lambda x: setattr(self.app.sm, "current", "login"))
    hdr.add_widget(self.acc_lbl)
    hdr.add_widget(out_b)
    box.add_widget(hdr)

    # Markaziy Aylana Balans Kartasi
    bal_card = WhiteCard(orientation="vertical", padding=12, size_hint=(1, 0.42))
    arc_box = BoxLayout(orientation="vertical")
    self.arc = BalanceArc(size_hint=(1, 0.55))
    arc_box.add_widget(self.arc)
    arc_box.add_widget(
        Label(
            text="Sizning oldindan to'lovingiz",
            font_size="12sp",
            color=GRAY,
            size_hint=(1, 0.12),
        )
    )
    self.bal_lbl = Label(
        text="259 394.00 so'm",
        font_size="22sp",
        bold=True,
        color=DARK,
        size_hint=(1, 0.20),
    )
    arc_box.add_widget(self.bal_lbl)
    bal_card.add_widget(arc_box)

    topup_b = TealBtn(
        text="Balansni to'ldirish (+50 000)",
        font_size="14sp",
        bold=True,
        size_hint=(1, 0.22),
    )
    topup_b.bind(on_press=self.add_balance)
    bal_card.add_widget(topup_b)
    box.add_widget(bal_card)

    # Schyotchik ko'rsatkichi va Holati kartasi
    info_card = WhiteCard(padding=14, spacing=10, size_hint=(1, 0.22))
    left_i = BoxLayout(orientation="vertical")
    left_i.add_widget(
        Label(
            text="Schyotchik ko'rsatkichi",
            font_size="12sp",
            color=GRAY,
            halign="left",
        )
    )
    self.kwh_lbl = Label(
        text="7 819 kWh",
        font_size="19sp",
        bold=True,
        color=DARK,
        halign="left",
    )
    self.kw_live = Label(
        text="Joriy quvvat: 18.4 kW",
        font_size="12sp",
        color=TEAL,
        bold=True,
        halign="left",
    )
