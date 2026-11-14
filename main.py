import random, time, webbrowser
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
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
      Color(0.1, 0.12, 0.16, 1)
      Rectangle(pos=self.pos, size=self.size)
      Color(0.35, 0.4, 0.5, 1)
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


class ElektrNazoratApp(App):

  def build(self):
    self.hududlar = {
        "ODTI - Asosiy bino": [50.0, "Olmaliq, A.Temur 56 (1-qavat)", 40.8447, 69.5983],
        "ODTI - Laboratoriya": [35.0, "Olmaliq, ODTI B-korpus", 40.8455, 69.5995],
        "ODTI - Yotoqxona": [25.0, "Talabalar shaharchasi", 40.8430, 69.5960],
        "Olmaliq tarmogi": [60.0, "Markaziy TP-14 nimstansiya", 40.8480, 69.6020],
    }
    self.baza = {
        k: {"t": [], "kwh": 0.0, "pik": 0.0, "v": 220.0, "a": 0.0, "vq": "00:00:00"}
        for k in self.hududlar
    }
    self.joriy = "ODTI - Asosiy bino"
    self.limit = 50.0
    self.avto, self.ip, self.ul = True, "192.168.4.1", False

    root = BoxLayout(orientation="vertical", padding=12, spacing=8)

    hdr = BoxLayout(spacing=8, size_hint=(1, 0.07))
    hdr.add_widget(
        Label(
            text="SCHYOTCHIK MONITORING",
            font_size="15sp",
            bold=True,
            color=(0.3, 0.8, 1, 1),
            size_hint=(0.62, 1),
        )
    )
    self.m_btn = Button(
        text="Schyotchik IP",
        font_size="12sp",
        bold=True,
        background_color=(0.3, 0.4, 0.7, 1),
        size_hint=(0.38, 1),
    )
    self.m_btn.bind(on_press=self.ip_oyna)
    hdr.add_widget(self.m_btn)
    root.add_widget(hdr)

    top = BoxLayout(spacing=8, size_hint=(1, 0.08))
    self.spn = Spinner(
        text=self.joriy,
        values=list(self.hududlar.keys()),
        font_size="13sp",
        background_color=(0.15, 0.35, 0.55, 1),
        size_hint=(0.74, 1),
    )
    self.spn.bind(text=self.h_ozg)
    top.add_widget(self.spn)
    add_b = Button(
        text="+ Hudud",
        font_size="13sp",
        bold=True,
        background_color=(0.2, 0.6, 0.3, 1),
        size_hint=(0.26, 1),
    )
    add_b.bind(on_press=self.h_oyna)
    top.add_widget(add_b)
    root.add_widget(top)

    loc = BoxLayout(spacing=8, size_hint=(1, 0.09))
    self.l_lbl = Label(
        text="Manzil: " + self.hududlar[self.joriy][1],
        font_size="12sp",
        color=(0.95, 0.85, 0.4, 1),
        halign="left",
        valign="middle",
        size_hint=(0.70, 1),
    )
    self.l_lbl.bind(size=self.l_lbl.setter("text_size"))
    loc.add_widget(self.l_lbl)
    map_b = Button(
        text="Xaritada\nkorish",
        font_size="12sp",
        bold=True,
        halign="center",
        background_color=(0.1, 0.55, 0.5, 1),
        size_hint=(0.30, 1),
    )
    map_b.bind(on_press=self.xarita)
    loc.add_widget(map_b)
    root.add_widget(loc)

    self.graph = PowerGraph(size_hint=(1, 0.29))
    root.add_widget(self.graph)

    self.info = Label(
        text="Yuklanmoqda...", font_size="14sp", halign="center", size_hint=(1, 0.19)
    )
    root.add_widget(self.info)

    self.stat = Label(
        text="Jami: 0.00 kWh | Xarajat: 0 som",
        font_size="13sp",
        color=(0.8, 0.85, 0.9, 1),
        halign="center",
        size_hint=(1, 0.10),
    )
    root.add_widget(self.stat)

    self.holat = Label(
        text="[AVTO] Tizim faol",
        font_size="14sp",
        bold=True,
        color=(0.2, 0.9, 0.2, 1),
        size_hint=(1, 0.08),
    )
    root.add_widget(self.holat)

    btns = BoxLayout(spacing=10, size_hint=(1, 0.10))
    self.t_btn = Button(
        text="Pauza",
        font_size="15sp",
        bold=True,
        background_color=(0.85, 0.5, 0.1, 1),
    )
    self.t_btn.bind(on_press=self.pauza)
    btns.add_widget(self.t_btn)
    r_btn = Button(
        text="Nolga tushirish",
        font_size="15sp",
        bold=True,
        background_color=(0.7, 0.2, 0.2, 1),
    )
    r_btn.bind(on_press=self.toza)
    btns.add_widget(r_btn)
    root.add_widget(btns)

    self.ev = Clock.schedule_interval(self.yangila, 2.0)
    return root

  def xarita(self, inst):
    h = self.hududlar[self.joriy]
    webbrowser.open(f"https://google.com{h[2]},{h[3]}")

  def ip_oyna(self, inst):
    box = BoxLayout(orientation="vertical", padding=15, spacing=10)
    inp = TextInput(text=self.ip, multiline=False)
    btn = Button(
        text="Saqlash", background_color=(0.2, 0.7, 0.3, 1), size_hint=(1, 0.4)
    )
    box.add_widget(Label(text="Schyotchik (ESP32) IP:"))
    box.add_widget(inp)
    box.add_widget(btn)
    pop = Popup(title="Ulanish", content=box, size_hint=(0.85, 0.42))

    def ok(b):
      self.ip, self.ul = inp.text.strip(), True
      self.m_btn.text, self.m_btn.background_color = "IP: " + self.ip, (0.2, 0.65, 0.3, 1)
      pop.dismiss()

    btn.bind(on_press=ok)
    pop.open()

  def pauza(self, inst):
    if self.avto:
      self.ev.cancel()
      self.avto = False
      self.t_btn.text, self.t_btn.background_color = "Davom ettirish", (0.2, 0.7, 0.3, 1)
      self.holat.text, self.holat.color = "[PAUZA] Toxtatildi", (1, 0.8, 0.2, 1)
    else:
      self.ev = Clock.schedule_interval(self.yangila, 2.0)
      self.avto = True
      self.t_btn.text, self.t_btn.background_color = "Pauza", (0.85, 0.5, 0.1, 1)

  def toza(self, inst):
    m = self.baza[self.joriy]
    m["t"], m["kwh"], m["pik"] = [], 0.0, 0.0
    self.graph.set_data([], self.limit)
    self.holat.text, self.holat.color = "[TOZALANDI] Nolga tushirildi", (0.3, 0.8, 1, 1)

  def h_ozg(self, spn, txt):
    self.joriy = txt
    self.limit = self.hududlar[txt][0]
    self.l_lbl.text = "Manzil: " + self.hududlar[txt][1]
    self.ekran()

  def yangila(self, dt):
    for nom, info in self.hududlar.items():
      lim = info[0]
      p = round(random.uniform(lim * 0.25, lim * 1.15), 2)
      v = round(random.uniform(216.0, 234.0), 1)
      m = self.baza[nom]
      m["kwh"] += (p * 2) / 3600.0
      if p > m["pik"]:
        m["pik"] = p
      m["v"], m["a"], m["vq"] = v, round(p * 1000 / v, 2), time.strftime("%H:%M:%S")
      m["t"].append(p)
      if len(m["t"]) > 20:
        m["t"].pop(0)
    self.ekran()

  def ekran(self):
    m = self.baza[self.joriy]
    self.graph.set_data(m["t"], self.limit)
    if not m["t"]:
      return
    p = m["t"][-1]
    mb = f"IP: {self.ip}" if self.ul else "Simulyatsiya"
    self.info.text = f"Vaqt: {m['vq']} | {mb}\nQuvvat: {p} kW (Limit: {self.limit} kW)\nKuchlanish: {m['v']} V | Tok: {m['a']} A"
    kwh = round(m["kwh"], 4)
    self.stat.text = f"Jami: {kwh} kWh | Xarajat: {int(kwh * 900)} som\nMaksimal pik: {m['pik']} kW"
    if p > self.limit:
      self.holat.text, self.holat.color = "[!] DIQQAT: Limit oshib ketdi!", (1, 0.2, 0.2, 1)
    else:
      self.holat.text, self.holat.color = "[OK] Tarmoq barqaror", (0.2, 0.9, 0.2, 1)

  def h_oyna(self, inst):
    box = BoxLayout(orientation="vertical", padding=15, spacing=8)
    n_in = TextInput(hint_text="Hudud nomi", multiline=False)
    j_in = TextInput(hint_text="Manzil / Joyi", multiline=False)
    l_in = TextInput(hint_text="Limit kW", input_filter="float", multiline=False)
    btn = Button(
        text="Qoshish", background_color=(0.2, 0.7, 0.3, 1), size_hint=(1, 0.45)
    )
    box.add_widget(Label(text="Yangi schyotchik:"))
    box.add_widget(n_in)
    box.add_widget(j_in)
    box.add_widget(l_in)
    box.add_widget(btn)
    pop = Popup(title="Yangi obyekt", content=box, size_hint=(0.88, 0.55))

    def qosh(b):
      if n_in.text.strip() and l_in.text.strip():
        try:
          nom, lim = n_in.text.strip(), float(l_in.text.strip())
          self.hududlar[nom] = [lim, j_in.text.strip() or "Olmaliq", 40.845, 69.599]
          self.baza[nom] = {
              "t": [],
              "kwh": 0.0,
              "pik": 0.0,
              "v": 220.0,
              "a": 0.0,
              "vq": "00:00:00",
          }
          self.spn.values = list(self.hududlar.keys())
          self.spn.text = nom
          pop.dismiss()
        except ValueError:
          pass

    btn.bind(on_press=qosh)
    pop.open()


if __name__ == "__main__":
  ElektrNazoratApp().run()
