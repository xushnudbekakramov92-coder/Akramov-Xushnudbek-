from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen

KV = """
ScreenManager:
    MainScreen:
    EnergyScreen:
    SavingScreen:

<MainScreen>:
    name: "main"
    BoxLayout:
        orientation: "vertical"
        padding: 20
        spacing: 15

        canvas.before:
            Color:
                rgba: 0.04, 0.10, 0.20, 1
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: "ODTI ENERGIYA"
            font_size: "28sp"
            bold: True
            color: 0.2, 0.8, 1, 1

        Label:
            text: "Energiya — kelajak manbai"
            font_size: "17sp"

        Widget:

        Button:
            text: "Elektr energiyasi"
            font_size: "20sp"
            size_hint_y: None
            height: "60dp"
            background_normal: ""
            background_color: 0.05, 0.45, 0.8, 1
            on_release: app.root.current = "energy"

        Button:
            text: "Energiya tejash"
            font_size: "20sp"
            size_hint_y: None
            height: "60dp"
            background_normal: ""
            background_color: 0.05, 0.6, 0.4, 1
            on_release: app.root.current = "saving"

        Widget:

        Label:
            text: "ODTI | 2026"
            size_hint_y: None
            height: "35dp"
            color: 0.7, 0.7, 0.7, 1

<EnergyScreen>:
    name: "energy"
    BoxLayout:
        orientation: "vertical"
        padding: 20
        spacing: 15

        Label:
            text: "ELEKTR ENERGIYASI"
            font_size: "24sp"
            bold: True

        Label:
            text: "Elektr energiyasi — elektr zaryadlarining harakati natijasida hosil bo'ladigan energiya turidir."
            text_size: self.width, None
            halign: "center"
            valign: "middle"

        Label:
            text: "U sanoat, transport, aloqa va kundalik hayotda keng qo'llaniladi."
            text_size: self.width, None
            halign: "center"

        Button:
            text: "Bosh sahifaga qaytish"
            size_hint_y: None
            height: "55dp"
            on_release: app.root.current = "main"

<SavingScreen>:
    name: "saving"
    BoxLayout:
        orientation: "vertical"
        padding: 20
        spacing: 15

        Label:
            text: "ENERGIYANI TEJASH"
            font_size: "24sp"
            bold: True

        Label:
            text: "1. Keraksiz chiroqlarni o'chiring.\\n\\n2. Energiya tejamkor lampalardan foydalaning.\\n\\n3. Elektr jihozlarini ishlatmaganda o'chiring.\\n\\n4. Elektr energiyasidan oqilona foydalaning."
            text_size: self.width, None
            halign: "left"
            valign: "middle"

        Button:
            text: "Bosh sahifaga qaytish"
            size_hint_y: None
            height: "55dp"
            on_release: app.root.current = "main"
"""

class MainScreen(Screen):
    pass

class EnergyScreen(Screen):
    pass

class SavingScreen(Screen):
    pass

class ODTIEnergiyaApp(App):
    def build(self):
        self.title = "ODTI Energiya"
        return Builder.load_string(KV)

if __name__ == "__main__":
    ODTIEnergiyaApp().run()
