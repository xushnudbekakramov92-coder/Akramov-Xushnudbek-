import json, os, random, time, webbrowser
from kivy.app import App
from kivy.clock import Clock
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


class CardBox(BoxLayout):

  def __init__(self, bg_color=(0.13, 0.16, 0.22, 1), **kwargs):
    super().__init__(**kwargs)
    self.bg_color = bg_color
    self.bind(pos=self.update_bg, size=self.update_bg)

  def update_bg(self, *args):
    self.canvas.before.clear()
    with self.canvas.before:
      Color(*self.bg_color)
      RoundedRectangle(pos=self.pos, size=self.size, radius=[12])


class PowerGraph(Widget):

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.limit, self.scale, self.data = 50.0, 70.0, []
    self.bind(pos=self.draw, size=self.draw)

  def update_data(self, data, lim):
    self.data, self.limit = list(data), float(lim)
    self.scale = max(self.limit * 1.35, 35.0)
    self.draw()

  def draw(self, *args):
    self.canvas.clear()
    if self.width <= 10 or self.height <= 10:
      return
    with self.canvas:
      Color(0.09, 0.11, 0.16, 1)
      RoundedRectangle(pos=self.pos, size=self.size, radius=[12])

      # To'r chiziqlar
      Color(0.2, 0.24, 0.32, 0.6)
      for i in range(1, 4):
        gy = self.y + (self.height / 4.0) * i
        Line(points=[self.x + 8, gy, self.x + self.width - 8, gy], width=1)

      # Limit chizig'i
      ly = self.y + (self.limit / self.scale) * self.height
      Color(0.95, 0.25, 0.25, 0.9)
      Line(points=[self.x + 5, ly, self.x + self.width - 5, ly], width=1.6)

      sx = (self.width - 20) / 14.0
      if len(self.data) > 1:
        pts = []
        for i, v in enumerate(self.data):
          pts.extend([
              self.x + 10 + i * sx,
              self.y + (v / self.scale) * self.height,
          ])
        Color(0.15, 0.8, 1, 1)
        Line(points=pts, width=2.4)

      for i, v in enumerate(self.data):
        px = self.x + 10 + i * sx
        py = self.y + (v / self.scale) * self.height
        Color(1, 0.2, 0.2, 1) if v > self.limit else Color(0.2, 0.95, 0.45, 1)
        Ellipse(pos=(px - 4, py - 4), size=(8, 8))


class LoginScreen(Screen):

  def __init__(self, app, **kwargs):
    super().__init__(**kwargs)
    self.app = app
    self.reg_mode = False

    box = BoxLayout(orientation="vertical", padding=28, spacing=14)
    box.add_widget(
        Label(
            text="ODTI ENERGIYA PRO\nSmart Monitoring Tizimi",
            font_size="21sp",
            bold=True,
            halign="center",
            color=(0.3, 0.85, 1, 1),
            size_hint=(1, 0.24),
        )
    )

    self.lg = TextInput(
        text="admin",
        hint_text="Login",
        multiline=False,
        font_size="16sp",
        size_hint=(1, 0.11),
    )
    self.pw = TextInput(
        text="1234",
        hint_text="Parol",
        password=True,
        multiline=False,
        font_size="16sp",
        size_hint=(1, 0.11),
    )
    self.err = Label(
        text="", color=(1, 0.3, 0.3, 1), font_size="14sp", size_hint=(1, 0.08)
    )

    self.btn_ok = Button(
        text="TIZIMGA KIRISH",
        font_size="17sp",
        bold=True,
        background_color=(0.12, 0.65, 0.4, 1),
        size_hint=(1, 0.13),
    )
    self.btn_ok.bind(on_press=self.kirish)

    self.btn_sw = Button(
        text="Yangi hisob yaratish",
        font_size="14sp",
        background_color=(0.22, 0.3, 0.45, 1),
        size_hint=(1, 0.1),
    )
    self.btn_sw.bind(on_press=self.rejim)

    box.add_widget(self.lg)
    box.add_widget(self.pw)
    box.add_widget(self.err)
    box.add_widget(self.btn_ok)
    box.add_widget(self.btn_sw)
    box.add_widget(Widget(size_hint=(1, 0.23)))
    self.add_widget(box)

  def rejim(self, inst):
    self.reg_mode = not self.reg_mode
    self.err.text = ""
    if self.reg_mode:
      self.lg.text, self.pw.text = "", ""
      self.btn_ok.text = "ROYXATDAN OTISH"
      self.btn_sw.text = "Kirish oynasiga qaytish"
    else:
      self.lg.text, self.pw.text = "admin", "1234"
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

    root = BoxLayout(orientation="vertical", padding=12, spacing=8)

    # 1. Yuqori panel: Xodim, Jurnal, Chiqish
    top_u = BoxLayout(spacing=6, size_hint=(1, 0.065))
    self.u_lbl = Label(
        text="Xodim: admin",
        font_size="13sp",
        bold=True,
        color=(0.4, 0.95, 0.55, 1),
        halign="left",
        size_hint=(0.46, 1),
    )
    self.u_lbl.bind(size=self.u_lbl.setter("text_size"))

    self.log_btn = Button(
        text="Jurnal (0)",
        font_size="12sp",
        bold=True,
        background_color=(0.65, 0.4, 0.15, 1),
        size_hint=(0.28, 1),
    )
    self.log_btn.bind(on_press=self.jurnal_oyna)

    btn_out = Button(
        text="Chiqish",
        font_size="12sp",
        bold=True,
        background_color=(0.75, 0.25, 0.25, 1),
        size_hint=(0.26, 1),
    )
    btn_out.bind(on_press=self.chiqish)
    top_u.add_widget(self.u_lbl)
    top_u.add_widget(self.log_btn)
    top_u.add_widget(btn_out)
    root.add_widget(top_u)

    # 2. Bino tanlash va + Bino
    h_bar = BoxLayout(spacing=8, size_hint=(1, 0.075))
    self.spn = Spinner(
        text=self.joriy,
        font_size="13sp",
        bold=True,
        background_color=(0.15, 0.4, 0.65, 1),
        size_hint=(0.72, 1),
    )
    self.spn.bind(text=self.hudud_ozgardi)
    btn_add = Button(
        text="+ Bino",
        font_size="13sp",
        bold=True,
        background_color=(0.18, 0.62, 0.35, 1),
        size_hint=(0.28, 1),
    )
    btn_add.bind(on_press=self.yangi_bino)
    h_bar.add_widget(self.spn)
    h_bar.add_widget(btn_add)
    root.add_widget(h_bar)

    # 3. Manzil va GPS Xarita kartasi
    m_card = CardBox(
        bg_color=(0.14, 0.18, 0.25, 1), padding=[10, 4], spacing=8, size_hint=(1, 0.085)
    )
    self.m_lbl = Label(
        text="Manzil: ...",
        font_size="12sp",
        color=(0.95, 0.85, 0.4, 1),
        halign="left",
        valign="middle",
        size_hint=(0.70, 1),
    )
    self.m_lbl.bind(size=self.m_lbl.setter("text_size"))
    btn_map = Button(
        text="Xaritada\nko'rish",
        font_size="12sp",
        bold=True,
        halign="center",
        background_color=(0.08, 0.58, 0.52, 1),
        size_hint=(0.30, 1),
    )
    btn_map.bind(on_press=self.xarita)
    m_card.add_widget(self.m_lbl)
    m_card.add_widget(btn_map)
    root.add_widget(m_card)

    # 4. Jonli Grafik
    self.graph = PowerGraph(size_hint=(1, 0.26))
    root.add_widget(self.graph)

    # 5. 3 ta Karta: Quvvat, Kuchlanish, Tok kuchi
    cards_row = BoxLayout(spacing=8, size_hint=(1, 0.14))

    c1 = CardBox(orientation="vertical", padding=6)
    c1.add_widget(Label(text="QUVVAT", font_size="11sp", color=(0.6, 0.7, 0.8, 1)))
    self.kw_lbl = Label(text="0.0 kW", font_size="17sp", bold=True, color=(0.2, 0.85, 1, 1))
    c1.add_widget(self.kw_lbl)

    c2 = CardBox(orientation="vertical", padding=6)
    c2.add_widget(Label(text="KUCHLANISH", font_size="11sp", color=(0.6, 0.7, 0.8, 1)))
    self.v_lbl = Label(text="220 V", font_size="17sp", bold=True, color=(0.3, 0.95, 0.5, 1))
    c2.add_widget(self.v_lbl)

    c3 = CardBox(orientation="vertical", padding=6)
    c3.add_widget(Label(text="TOK KUCHI", font_size="11sp", color=(0.6, 0.7, 0.8, 1)))
    self.a_lbl = Label(text="0.0 A", font_size="17sp", bold=True, color=(1, 0.75, 0.25, 1))
    c3.add_widget(self.a_lbl)

    cards_row.add_widget(c1)
    cards_row.add_widget(c2)
    cards_row.add_widget(c3)
    root.add_widget(cards_row)

    # 6. 3 Faza va Xarajatlar kartasi
    stat_card = CardBox(orientation="vertical", padding=[10, 6], size_hint=(1, 0.16))
    self.faza_lbl = Label(
        text="3 Faza: L1=220V | L2=221V | L3=219V",
        font_size="12sp",
        color=(0.75, 0.85, 0.95, 1),
    )
    self.stat_lbl = Label(
        text="Jami sarf: 0.00 kWh | Xarajat: 0 so'm",
        font_size="14sp",
        bold=True,
        color=(1, 1, 1, 1),
    )
    stat_card.add_widget(self.faza_lbl)
    stat_card.add_widget(self.stat_lbl)
    root.add_widget(stat_card)

    # 7. Holat (Ogohlantirish)
    self.holat = Label(
        text="[OK] Tarmoq barqaror ishlamoqda",
        font_size="14sp",
        bold=True,
        color=(0.2, 0.9, 0.2, 1),
        size_hint=(1, 0.07),
    )
    root.add_widget(self.holat)

    # 8. Pastki boshqaruv tugmalari
    b_bar = BoxLayout(spacing=10, size_hint=(1, 0.09))
    self.btn_p = Button(
        text="Pauza",
        font_size="15sp",
        bold=True,
        background_color=(0.85, 0.5, 0.1, 1),
    )
    self.btn_p.bind(on_press=self.pauza)
    btn_r = Button(
        text="Nolga tushirish",
        font_size="15sp",
        bold=True,
        background_color=(0.7, 0.2, 0.2, 1),
    )
    btn_r.bind(on_press=self.tozalash)
