import json, os, random, time, webbrowser
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget


class PowerGraph(Widget):

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.max_limit, self.max_scale, self.data = 50.0, 70.0, []
    self.bind(pos=self.draw, size=self.draw)

  def set_data(self, data, lim):
    self.data, self.max_limit = list(data), float(lim)
    self.max_scale = max(self.max_limit * 1.4, 35.0)
    self.draw()

  def draw(self, *args):
    self.canvas.clear()
    if self.width <= 10 or self.height <= 10:
      return
    with self.canvas:
      Color(0.08, 0.1, 0.14, 1)
      Rectangle(pos=self.pos, size=self.size)
      Color(0.3, 0.35, 0.45, 1)
      Line(rectangle=(self.x, self.y, self.width, self.height), width=1.2)
      ly = self.y + (self.max_limit / self.max_scale) * self.height
      Color(0.95, 0.2, 0.2, 0.85)
      Line(points=[self.x, ly, self.x + self.width, ly], width=1.6)
      sx = self.width / 19.0
      if len(self.data) > 1:
        pts = []
        for i, v in enumerate(self.data):
          pts.extend([self.x + i * sx, self.y + (v / self.max_scale) * self.height])
        Color(0.1, 0.75, 1, 1)
        Line(points=pts, width=2.2)
      for i, v in enumerate(self.data):
        px, py = self.x + i * sx, self.y + (v / self.max_scale) * self.height
        Color(1, 0.15, 0.15, 1) if v > self.max_limit else Color(
            0.15, 0.95, 0.4, 1
        )
        Ellipse(pos=(px - 3.5, py - 3.5), size=(7, 7))


class AuthScreen(Screen):

  def __init__(self, app_ref, **kwargs):
    super().__init__(**kwargs)
    self.app = app_ref
    self.is_reg = False

    root = BoxLayout(orientation="vertical", padding=25, spacing=12)
    root.add_widget(
        Label(
            text="ODTI ENERGIYA PRO (SCADA)",
            font_size="19sp",
            bold=True,
            color=(0.3, 0.85, 1, 1),
            size_hint=(1, 0.16),
        )
    )
    self.m_lbl = Label(
        text="Tizimga kirish", font_size="16sp", bold=True, size_hint=(1, 0.08)
    )
    root.add_widget(self.m_lbl)

    self.name_in = TextInput(
        hint_text="Ism-familiya",
        multiline=False,
        size_hint=(1, 0.1),
        opacity=0,
        disabled=True,
    )
    root.add_widget(self.name_in)

    self.lg_in = TextInput(
        hint_text="Login (admin)", multiline=False, size_hint=(1, 0.1)
    )
    root.add_widget(self.lg_in)

    self.pw_in = TextInput(
        hint_text="Parol (1234)",
        password=True,
        multiline=False,
        size_hint=(1, 0.1),
    )
    root.add_widget(self.pw_in)

    self.msg = Label(
        text="", font_size="13sp", color=(1, 0.3, 0.3, 1), size_hint=(1, 0.08)
    )
    root.add_widget(self.msg)

    self.act_btn = Button(
        text="KIRISH",
        font_size="16sp",
        bold=True,
        background_color=(0.15, 0.6, 0.85, 1),
        size_hint=(1, 0.11),
    )
    self.act_btn.bind(on_press=self.submit)
    root.add_widget(self.act_btn)

    self.sw_btn = Button(
        text="Royxatdan otish (Kuzatuvchi)",
        font_size="14sp",
        background_color=(0.25, 0.3, 0.4, 1),
        size_hint=(1, 0.1),
    )
    self.sw_btn.bind(on_press=self.toggle)
    root.add_widget(self.sw_btn)
    root.add_widget(Widget(size_hint=(1, 0.17)))
    self.add_widget(root)

  def toggle(self, inst):
    self.is_reg = not self.is_reg
    self.msg.text = ""
    if self.is_reg:
      self.m_lbl.text = "Yangi kuzatuvchi yaratish"
      self.name_in.opacity, self.name_in.disabled = 1, False
      self.act_btn.text, self.act_btn.background_color = (
          "ROYXATDAN OTISH",
          (0.2, 0.7, 0.35, 1),
      )
      self.sw_btn.text = "Kirish oynasiga qaytish"
    else:
      self.m_lbl.text = "Tizimga kirish"
      self.name_in.opacity, self.name_in.disabled = 0, True
      self.act_btn.text, self.act_btn.background_color = (
          "KIRISH",
          (0.15, 0.6, 0.85, 1),
      )
      self.sw_btn.text = "Royxatdan otish (Kuzatuvchi)"

  def submit(self, inst):
    lg, pw = self.lg_in.text.strip(), self.pw_in.text.strip()
    if not lg or not pw:
      self.msg.text = "Login va parolni kiriting!"
      return
    if self.is_reg:
      if lg in self.app.data["users"]:
        self.msg.text = "Bu login band!"
        return
      nm = self.name_in.text.strip() or lg
      self.app.data["users"][lg] = {"parol": pw, "ism": nm, "rol": "user"}
      self.app.save_db()
      self.app.login_ok(nm, "user")
    else:
      u = self.app.data["users"].get(lg)
      if u and u["parol"] == pw:
        self.app.login_ok(u["ism"], u.get("rol", "user"))
      else:
        self.msg.text = "Login yoki parol xato!"


class MainScreen(Screen):

  def __init__(self, app_ref, **kwargs):
    super().__init__(**kwargs)
    self.app = app_ref
    self.baza = {}
    self.jurnal = []
    self.joriy = "ODTI - Asosiy bino"
    self.avto, self.ip, self.ul = True, "192.168.4.1", False
    self.tg_chat = ""

    root = BoxLayout(orientation="vertical", padding=10, spacing=6)

    # 1. Xodim, Rol va Chiqish
    u_bar = BoxLayout(spacing=6, size_hint=(1, 0.06))
    self.u_lbl = Label(
        text="Xodim: Admin",
        font_size="12sp",
        bold=True,
        color=(0.4, 0.95, 0.5, 1),
        halign="left",
        size_hint=(0.74, 1),
    )
    self.u_lbl.bind(size=self.u_lbl.setter("text_size"))
    u_bar.add_widget(self.u_lbl)
    out_b = Button(
        text="Chiqish",
        font_size="12sp",
        bold=True,
        background_color=(0.75, 0.25, 0.25, 1),
        size_hint=(0.26, 1),
    )
    out_b.bind(on_press=self.logout)
    u_bar.add_widget(out_b)
    root.add_widget(u_bar)

    # 2. Tezkor tugmalar (IP, QR, Jurnal, Telegram)
    tools = BoxLayout(spacing=5, size_hint=(1, 0.07))
    self.ip_b = Button(
        text="IP: Test",
        font_size="11sp",
        bold=True,
        background_color=(0.3, 0.4, 0.7, 1),
    )
    self.ip_b.bind(on_press=self.ip_oyna)
    qr_b = Button(
        text="QR Kod",
        font_size="11sp",
        bold=True,
        background_color=(0.2, 0.5, 0.6, 1),
    )
    qr_b.bind(on_press=self.qr_oyna)
    log_b = Button(
        text="Jurnal (0)",
        font_size="11sp",
        bold=True,
        background_color=(0.6, 0.35, 0.2, 1),
    )
    log_b.bind(on_press=self.jurnal_oyna)
    self.log_b = log_b
    tg_b = Button(
        text="Telegram",
        font_size="11sp",
        bold=True,
        background_color=(0.15, 0.55, 0.85, 1),
    )
    tg_b.bind(on_press=self.tg_oyna)
    tools.add_widget(self.ip_b)
    tools.add_widget(qr_b)
    tools.add_widget(log_b)
    tools.add_widget(tg_b)
    root.add_widget(tools)

    # 3. Hudud tanlash va + Hudud (faqat Admin uchun)
    top = BoxLayout(spacing=6, size_hint=(1, 0.07))
    self.spn = Spinner(
        text=self.joriy,
        font_size="12sp",
        background_color=(0.15, 0.35, 0.55, 1),
        size_hint=(0.74, 1),
    )
    self.spn.bind(text=self.h_ozg)
    top.add_widget(self.spn)
    self.add_b = Button(
        text="+ Hudud",
        font_size="12sp",
        bold=True,
        background_color=(0.2, 0.6, 0.3, 1),
        size_hint=(0.26, 1),
    )
    self.add_b.bind(on_press=self.h_oyna)
    top.add_widget(self.add_b)
    root.add_widget(top)

    # 4. Manzil va Xarita
    loc = BoxLayout(spacing=6, size_hint=(1, 0.07))
    self.l_lbl = Label(
        text="Manzil: ...",
        font_size="11sp",
        color=(0.95, 0.85, 0.4, 1),
        halign="left",
        valign="middle",
        size_hint=(0.72, 1),
    )
    self.l_lbl.bind(size=self.l_lbl.setter("text_size"))
    loc.add_widget(self.l_lbl)
    map_b = Button(
        text="Xarita",
        font_size="12sp",
        bold=True,
        background_color=(0.1, 0.55, 0.5, 1),
        size_hint=(0.28, 1),
    )
    map_b.bind(on_press=self.xarita)
    loc.add_widget(map_b)
    root.add_widget(loc)

    # 5. Jonli Grafik
    self.graph = PowerGraph(size_hint=(1, 0.25))
    root.add_widget(self.graph)

    # 6. 3 Faza (L1, L2, L3) va Quyosh paneli malumotlari
    self.info = Label(
        text="Yuklanmoqda...", font_size="13sp", halign="center", size_hint=(1, 0.23)
    )
    root.add_widget(self.info)

    # 7. Statistika (Jami kWh va Xarajat)
    self.stat = Label(
        text="Jami: 0.00 kWh | Xarajat: 0 som",
        font_size="12sp",
        color=(0.8, 0.85, 0.9, 1),
        halign="center",
        size_hint=(1, 0.09),
    )
    root.add_widget(self.stat)

    # 8. Ogohlantirish statusi
    self.holat = Label(
        text="[AVTO] Tizim faol",
        font_size="13sp",
        bold=True,
        color=(0.2, 0.9, 0.2, 1),
        size_hint=(1, 0.07),
    )
    root.add_widget(self.holat)

    # 9. Boshqaruv tugmalari
    btns = BoxLayout(spacing=8, size_hint=(1, 0.09))
    self.t_btn = Button(
        text="Pauza",
        font_size="14sp",
        bold=True,
        background_color=(0.85, 0.5, 0.1, 1),
    )
    self.t_btn.bind(on_press=self.pauza)
    btns.add_widget(self.t_btn)
    self.r_btn = Button(
        text="Nolga tushirish",
        font_size="14sp",
        bold=True,
        background_color=(0.7, 0.2, 0.2, 1),
    )
    self.r_btn.bind(on_press=self.toza)
    btns.add_widget(self.r_btn)
    root.add_widget(btns)

    self.add_widget(root)
    self.ev = None

  def init_session(self, user_name, rol):
    hududlar = self.app.data["hududlar"]
    for k, v in hududlar.items():
      if k not in self.baza:
        self.baza[k] = {}
            "t": [],
            "kwh": v[4],
            "pik": 0.0,
