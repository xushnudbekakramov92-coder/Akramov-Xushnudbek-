import random, time, webbrowser
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Line, RoundedRectangle
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
DARK = (0.11, 0.15, 0.21, 1)
GRAY = (0.48, 0.54, 0.62, 1)
WHITE = (1, 1, 1, 1)


class Card(BoxLayout):

  def __init__(self, bg=WHITE, r=18, **kw):
    super().__init__(**kw)
    self.bg, self.r = bg, r
    self.bind(pos=self.upd, size=self.upd)

  def upd(self, *a):
    self.canvas.before.clear()
    with self.canvas.before:
      Color(0.85, 0.89, 0.93, 1)
      RoundedRectangle(pos=(self.x, self.y - 3), size=self.size, radius=[self.r])
      Color(*self.bg)
      RoundedRectangle(pos=self.pos, size=self.size, radius=[self.r])


class PillBtn(Button):

  def __init__(self, bg=TEAL, fg=WHITE, r=16, **kw):
    super().__init__(**kw)
    self.background_normal, self.background_color = "", (0, 0, 0, 0)
    self.bg, self.r, self.color = bg, r, fg
    self.bind(pos=self.upd, size=self.upd, state=self.upd)

  def upd(self, *a):
    self.canvas.before.clear()
    c = (
        (max(0, self.bg[0] - 0.08), max(0, self.bg[1] - 0.08), max(0, self.bg[2] - 0.08), 1)
        if self.state == "down"
        else self.bg
    )
    with self.canvas.before:
      Color(*c)
      RoundedRectangle(pos=self.pos, size=self.size, radius=[self.r])


class Gauge(Widget):

  def __init__(self, **kw):
    super().__init__(**kw)
    self.bind(pos=self.draw, size=self.draw)

  def draw(self, *a):
    self.canvas.clear()
    if self.width <= 10:
      return
    cx, cy = self.center_x, self.y + self.height * 0.28
    rad = min(self.width * 0.36, self.height * 0.62)
    with self.canvas:
      Color(0.88, 0.92, 0.96, 1)
      Line(circle=(cx, cy, rad, -110, 110), width=7, cap="round")
      Color(*TEAL)
      Line(circle=(cx, cy, rad, -110, 52), width=7, cap="round")


class BarChart(Widget):

  def __init__(self, **kw):
    super().__init__(**kw)
    self.vals = [420, 680, 1150, 490, 1650, 890]
    self.solar, self.is_sum = False, False
    self.bind(pos=self.draw, size=self.draw)

  def set_mode(self, solar=False, is_sum=False):
    self.solar, self.is_sum = solar, is_sum
    base = [180, 240, 310, 390, 460, 520] if solar else [420, 680, 1150, 490, 1650, 890]
    self.vals = [v * 900 if is_sum else v for v in base]
    self.draw()

  def draw(self, *a):
    self.canvas.clear()
    if self.width <= 20:
      return
    mv = max(self.vals) * 1.15
    bw = (self.width - 36) / (len(self.vals) * 1.8)
    gap = bw * 0.8
    with self.canvas:
      Color(0.91, 0.94, 0.97, 1)
      for i in range(1, 5):
        gy = self.y + (self.height / 5.0) * i
        Line(points=[self.x + 8, gy, self.x + self.width - 8, gy], width=1)
      for i, v in enumerate(self.vals):
        bx = self.x + 18 + i * (bw + gap)
        bh = (v / mv) * (self.height - 16)
        raw = v / 900 if self.is_sum else v
        if self.solar:
          Color(0.14, 0.78, 0.45, 1)
        elif raw > 1500:
          Color(0.95, 0.25, 0.28, 1)
        elif raw > 500:
          Color(0.98, 0.72, 0.15, 1)
        else:
          Color(0.15, 0.80, 0.45, 1)
        RoundedRectangle(pos=(bx, self.y + 8), size=(bw, max(bh, 10)), radius=[6])
class LoginScr(Screen):

  def __init__(self, app, **kw):
    super().__init__(**kw)
    self.app = app
    root = BoxLayout(orientation="vertical", padding=20, spacing=14)
    bn = Card(orientation="vertical", bg=TEAL, r=22, padding=16, size_hint=(1, 0.28))
    bn.add_widget(Label(text="HUDUDIY ELEKTR\nTARMOQLARI", font_size="22sp", bold=True, halign="center", color=WHITE))
    bn.add_widget(Label(text="ODTI Smart Energiya Nazorati", font_size="13sp", color=(0.88, 0.96, 0.98, 1)))
    root.add_widget(bn)

    c = Card(orientation="vertical", padding=20, spacing=12, size_hint=(1, 0.62))
    c.add_widget(Label(text="Kabinetga kirish", font_size="19sp", bold=True, color=DARK, size_hint=(1, 0.18)))
    self.acc = TextInput(text="3323310231747", hint_text="Hisob raqami", multiline=False, font_size="16sp", padding=, background_normal="", background_color=(0.94, 0.96, 0.98, 1), foreground_color=DARK, size_hint=(1, 0.19))
    self.pw = TextInput(text="1234", hint_text="Parol", password=True, multiline=False, font_size="16sp", padding=, background_normal="", background_color=(0.94, 0.96, 0.98, 1), foreground_color=DARK, size_hint=(1, 0.19))
    self.err = Label(text="", color=(0.9, 0.2, 0.2, 1), font_size="13sp", size_hint=(1, 0.10))
    btn = PillBtn(text="Davom etish", font_size="16sp", bold=True, r=20, size_hint=(1, 0.22))
    btn.bind(on_press=self.go)
    for w in (self.acc, self.pw, self.err, btn):
      c.add_widget(w)
    root.add_widget(c)
    root.add_widget(Widget(size_hint=(1, 0.10)))
    self.add_widget(root)

  def go(self, i):
    if self.acc.text.strip() and self.pw.text.strip():
      self.app.enter(self.acc.text.strip())
    else:
      self.err.text = "Hisob raqami va parolni kiriting!"


class MainScr(Screen):

  def __init__(self, app, **kw):
    super().__init__(**kw)
    self.app = app
    self.bal, self.kwh, self.kw = 259394.0, 7819.0, 0.0
    self.test, self.ip = False, "192.168.4.1"
    self.sol_m, self.sum_m = False, False

    root = BoxLayout(orientation="vertical")
    self.sm = ScreenManager(size_hint=(1, 0.90))
    self.p1, self.p2, self.p3, self.p4 = Screen(name="home"), Screen(name="stat"), Screen(name="map"), Screen(name="help")
    self.build_home()
    self.build_stat()
    self.build_map()
    self.build_help()
    for p in (self.p1, self.p2, self.p3, self.p4):
      self.sm.add_widget(p)
    root.add_widget(self.sm)

    nav = Card(padding=, spacing=8, r=0, size_hint=(1, 0.10))
    self.tabs = {}
    for code, name in [("home", "Asosiy"), ("stat", "Statistika"), ("map", "Filiallar"), ("help", "Yordam")]:
      b = PillBtn(text=name, font_size="13sp", bold=True, bg=TEAL if code == "home" else (0.93, 0.96, 0.98, 1), fg=WHITE if code == "home" else DARK, r=14)
      b.bind(on_press=lambda i, c=code: self.tab(c))
      self.tabs[code] = b
      nav.add_widget(b)
    root.add_widget(nav)
    self.add_widget(root)

  def tab(self, code):
    self.sm.current = code
    for k, b in self.tabs.items():
      b.bg = TEAL if k == code else (0.93, 0.96, 0.98, 1)
      b.color = WHITE if k == code else DARK
      b.upd()

  def build_home(self):
    box = BoxLayout(orientation="vertical", padding=14, spacing=10)
    hdr = BoxLayout(spacing=6, size_hint=(1, 0.08))
    self.albl = Label(text="Hisob:\n3323310231747", font_size="12sp", bold=True, color=DARK, halign="left", size_hint=(0.44, 1))
    self.albl.bind(size=self.albl.setter("text_size"))
    self.mbtn = PillBtn(text="Rejim: REAL", font_size="11sp", bold=True, r=12, size_hint=(0.32, 0.82))
    self.mbtn.bind(on_press=self.mode_pop)
    ob = PillBtn(text="Chiqish", font_size="11sp", bold=True, bg=(0.96, 0.88, 0.88, 1), fg=(0.82, 0.2, 0.2, 1), r=12, size_hint=(0.24, 0.82))
    ob.bind(on_press=lambda x: setattr(self.app.sm, "current", "login"))
    for w in (self.albl, self.mbtn, ob):
      hdr.add_widget(w)
    box.add_widget(hdr)

    bc = Card(orientation="vertical", padding=14, size_hint=(1, 0.43))
    bc.add_widget(Gauge(size_hint=(1, 0.46)))
    bc.add_widget(Label(text="Sizning oldindan to'lovingiz", font_size="12sp", color=GRAY, size_hint=(1, 0.11)))
    self.blbl = Label(text="259 394.00 so'm", font_size="22sp", bold=True, color=DARK, size_hint=(1, 0.20))
    bc.add_widget(self.blbl)
    pb = PillBtn(text="Balansni to'ldirish (+50 000)", font_size="14sp", bold=True, r=18, size_hint=(1, 0.23))
    pb.bind(on_press=self.topup)
    bc.add_widget(pb)
    box.add_widget(bc)

    ic = Card(padding=14, spacing=10, size_hint=(1, 0.22))
    lf = BoxLayout(orientation="vertical")
    t1 = Label(text="Schyotchik ko'rsatkichi", font_size="12sp", color=GRAY, halign="left")
    self.khl = Label(text="7 819 kWh", font_size="20sp", bold=True, color=DARK, halign="left")
    self.kwl = Label(text="Joriy quvvat: 0.0 kW", font_size="12sp", bold=True, color=TEAL, halign="left")
    for w in (t1, self.khl, self.kwl):
      w.bind(size=w.setter("text_size"))
      lf.add_widget(w)
    rt = BoxLayout(orientation="vertical", spacing=4, size_hint=(0.44, 1))
    rt.add_widget(Label(text="Holati", font_size="12sp", color=GRAY))
    self.bdg = PillBtn(text="Kutilmoqda", font_size="12sp", bold=True, bg=(0.96, 0.65, 0.15, 1), r=14, size_hint=(1, 0.45))
    rt.add_widget(self.bdg)
    rt.add_widget(Label(text="ODTI - Asosiy bino", font_size="11sp", color=GRAY))
    ic.add_widget(lf)
    ic.add_widget(rt)
    box.add_widget(ic)

    pc = Card(padding=12, size_hint=(1, 0.14))
    pc.add_widget(Label(text="Oxirgi to'lov:\n150 000 so'm", font_size="13sp", bold=True, color=DARK))
    pc.add_widget(Label(text="Sana:\n16.11.2026", font_size="13sp", color=GRAY))
    box.add_widget(pc)

    db = PillBtn(text="Shaxsiy hisob holati (Batafsil)   >", font_size="14sp", bold=True, bg=WHITE, fg=DARK, r=16, size_hint=(1, 0.12))
    db.bind(on_press=self.det_pop)
    box.add_widget(db)
    self.p1.add_widget(box)

  def topup(self, i):
    self.bal += 50000
    self.blbl.text = f"{self.bal:,.2f} so'm".replace(",", " ")

  def mode_pop(self, i):
    box = BoxLayout(orientation="vertical", padding=15, spacing=10)
    inp = TextInput(text=self.ip, multiline=False)
    b1 = PillBtn(text="REAL REJIM (Schyotchik IP)")
    b2 = PillBtn(text="TEST REJIM (Simulyatsiya)", bg=(0.14, 0.74, 0.45, 1))
    for w in (Label(text="Schyotchik (ESP32) IP:"), inp, b1, b2):
      box.add_widget(w)
    pop = Popup(title="Tizim rejimi", content=box, size_hint=(0.88, 0.52))

    def sr(b):
      self.ip, self.test = inp.text.strip(), False
      self.mbtn.text, self.mbtn.bg = "Rejim: REAL", TEAL
      self.mbtn.upd()
      self.kwl.text = "Joriy quvvat: 0.0 kW"
      self.bdg.text, self.bdg.bg = "Kutilmoqda", (0.96, 0.65, 0.15, 1)
      self.bdg.upd()
      pop.dismiss()

    def st(b):
      self.test = True
      self.mbtn.text, self.mbtn.bg = "Rejim: TEST", (0.14, 0.74, 0.45, 1)
      self.mbtn.upd()
      self.bdg.text, self.bdg.bg = "Aktiv", (0.12, 0.78, 0.65, 1)
      self.bdg.upd()
      pop.dismiss()

    b1.bind(on_press=sr)
    b2.bind(on_press=st)
    pop.open()

  def det_pop(self, i):
    g = GridLayout(cols=2, padding=10, spacing=8)
    for k, v in [("Schyotchik:", "Ex-2865017"), ("Turi:", "3-fazali Smart"), ("Ko'rsatkich:", f"{int(self.kwh)} kWh"), ("Sana:", "10.06.2025"), ("Hudud:", "ODTI (Olmaliq)"), ("Limit:", "50.0 kW")]:
      c = Card(orientation="vertical", padding=10)
      c.add_widget(Label(text=k, font_size="11sp", color=GRAY))
      c.add_widget(Label(text=v, font_size="14sp", bold=True, color=DARK))
      g.add_widget(c)
    box = BoxLayout(orientation="vertical", padding=10, spacing=8)
    cb = PillBtn(text="Yopish", size_hint=(1, 0.15))
    box.add_widget(g)
    box.add_widget(cb)
    pop = Popup(title="Hisob holati", content=box, size_hint=(0.92, 0.72))
    cb.bind(on_press=pop.dismiss)
    pop.open()

  def build_stat(self):
    box = BoxLayout(orientation="vertical", padding=14, spacing=10)
    box.add_widget(Label(text="Iste'mol statistikasi", font_size="19sp", bold=True, color=DARK, size_hint=(1, 0.08)))
    r1, r2 = BoxLayout(spacing=8, size_hint=(1, 0.08)), BoxLayout(spacing=8, size_hint=(1, 0.08))
    self.bel = PillBtn(text="Elektr energiya", font_size="13sp", bold=True)
    self.bsol = PillBtn(text="Quyosh batareyasi", font_size="13sp", bold=True, bg=(0.88, 0.92, 0.96, 1), fg=DARK)
    self.bel.bind(on_press=lambda x: self.ust(False, self.sum_m))
    self.bsol.bind(on_press=lambda x: self.ust(True, self.sum_m))
    r1.add_widget(self.bel)
    r1.add_widget(self.bsol)

    self.bkw = PillBtn(text="kWh", font_size="13sp", bold=True)
    self.bsm = PillBtn(text="So'm", font_size="13sp", bold=True, bg=(0.88, 0.92, 0.96, 1), fg=DARK)
    self.bkw.bind(on_press=lambda x: self.ust(self.sol_m, False))
    self.bsm.bind(on_press=lambda x: self.ust(self.sol_m, True))
    r2.add_widget(self.bkw)
    r2.add_widget(self.bsm)
    box.add_widget(r1)
    box.add_widget(r2)

    cc = Card(orientation="vertical", padding=12, size_hint=(1, 0.54))
    cc.add_widget(Label(text="Oylik ko'rsatkichlar (Yan - Iyun)", font_size="13sp", bold=True, color=DARK, size_hint=(1, 0.12)))
    self.diag = BarChart(size_hint=(1, 0.76))
    mr = BoxLayout(size_hint=(1, 0.12))
    for m in ("Yan", "Fev", "Mar", "Apr", "May", "Iyun"):
      mr.add_widget(Label(text=m, font_size="11sp", color=GRAY))
    cc.add_widget(self.diag)
    cc.add_widget(mr)
    box.add_widget(cc)

    tr = BoxLayout(spacing=6, size_hint=(1, 0.16))
    for txt, col in [("200 kWh gacha\n450 so'm", (0.14, 0.75, 0.4, 1)), ("1000 kWh gacha\n900 so'm", (0.92, 0.65, 0.1, 1)), ("1000+ kWh\n1 350 so'm", (0.92, 0.25, 0.28, 1))]:
      tc = Card(padding=6)
      tc.add_widget(Label(text=txt, font_size="11sp", bold=True, color=col, halign="center"))
      tr.add_widget(tc)
    box.add_widget(tr)
    self.p2.add_widget(box)

  def ust(self, sol, is_s):
    self.sol_m, self.sum_m = sol, is_s
    self.bel.bg, self.bel.color = ((0.88, 0.92, 0.96, 1), DARK) if sol else (TEAL, WHITE)
