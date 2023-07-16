from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.utils import get_color_from_hex
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout

class TrainSpotter(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(Log1(name='station'))
        sm.add_widget(Log2(name='type'))
        sm.add_widget(Log3(name='exact'))
        sm.add_widget(Log4(name='confirm'))
        sm.add_widget(Home(name='home'))
        sm.add_widget(Search(name='search'))
        sm.add_widget(Achievements(name='achievements'))
        sm.add_widget(Statistics(name='statistics'))
        sm.current = 'home'
        return sm


class Home(Screen):
    def __init__(self, **kwargs):
        super(Home, self).__init__(**kwargs)
        self.window = GridLayout()
        self.window.cols = 1
        self.window.size_hint = (0.6, 0.9)
        self.window.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        self.window.spacing = [1, 10]

        # Add widgets to window
        self.logo = Image(
            source="assets/Logo.png",
            size_hint=(0.75, 0.75)
        )
        self.window.add_widget(self.logo)

        self.menutext = Label(
            text="Train Spotter",
            font_size=30
        )
        self.window.add_widget(self.menutext)

        self.logbtn = Button(
            text="Log New Trip",
            font_size=30,
            size_hint=(0.75, 0.5),
            background_color=get_color_from_hex('#ff5aa4'),
            background_normal=""
        )
        self.logbtn.bind(on_press=self.goto_log)
        self.window.add_widget(self.logbtn)

        self.searchbtn = Button(
            text="Search / Filter Logs",
            font_size=30,
            size_hint=(0.75, 0.5),
            background_color=get_color_from_hex('#ffa500'),
            background_normal=""
        )
        self.searchbtn.bind(on_press=self.goto_search)
        self.window.add_widget(self.searchbtn)

        self.achbtn = Button(
            text="Your Achievements",
            font_size=30,
            size_hint=(0.75, 0.5),
            background_color=get_color_from_hex('#8cc63e'),
            background_normal=""
        )
        self.achbtn.bind(on_press=self.goto_achievements)
        self.window.add_widget(self.achbtn)

        self.stsbtn = Button(
            text="Your Statistics",
            font_size=30,
            size_hint=(0.75, 0.5),
            background_color=get_color_from_hex('#010385'),
            background_normal=""
        )
        self.stsbtn.bind(on_press=self.goto_statistics)
        self.window.add_widget(self.stsbtn)

        self.add_widget(self.window)

        # Initialize attributes to store entered values
        self.station_text = ''
        self.type_text = ''
        self.exact_text = ''
        self.sl = "No"
        self.rare = "No"
        self.di = "No"

    def goto_log(self, instance):
        self.manager.current = 'station'

    def goto_log2(self, instance):
        self.manager.current = 'type'

    def goto_log3(self, instance):
        log4_screen = self.manager.get_screen('confirm')
        log4_screen.update_labels(
        self.station_text,
        self.type_text,
        self.exact_text,
        self.sl,
        self.rare,
        self.di
    )
        self.manager.current = 'confirm'

    def goto_search(self, instance):
        self.manager.current = 'search'

    def goto_achievements(self, instance):
        self.manager.current = 'achievements'

    def goto_statistics(self, instance):
        self.manager.current = 'statistics'


class Log1(Screen):
    def __init__(self, **kwargs):
        super(Log1, self).__init__(**kwargs)
        self.window = GridLayout()
        self.window.cols = 1
        self.window.size_hint = (0.6, 0.9)
        self.window.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        self.window.spacing = [1, 10]

        self.sctsts = Label(
            text="Enter station",
            font_size=60
        )
        self.window.add_widget(self.sctsts)

        self.station = TextInput(
            text="Station Name",
            multiline=False,
            size_hint=(1, 0.15),
            font_size=30,
        )
        self.window.add_widget(self.station)

        button_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.2))

        self.stbtn = Button(
            text="Log Station",
            font_size=40,
            size_hint=(1, 1),
            background_color=get_color_from_hex('#66a3ff'),
            background_normal = ""
        )
        self.stbtn.bind(on_press=self.save_station)

        button_layout.add_widget(self.stbtn)

        self.window.add_widget(button_layout)

        self.add_widget(self.window)

    def save_station(self, instance):
        home_screen = self.manager.get_screen('home')
        home_screen.station_text = self.station.text
        print(home_screen.station_text)
        print("Station saved:", home_screen.station_text)
        self.manager.current = "type"


class Log2(Screen):
    def __init__(self, **kwargs):
        super(Log2, self).__init__(**kwargs)
        self.window = GridLayout()
        self.window.cols = 1
        self.window.size_hint = (0.6, 0.9)
        self.window.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        self.window.spacing = [1, 10]

        self.typetxt = Label(
            text="Train Class",
            font_size=30
        )
        self.window.add_widget(self.typetxt)
        self.type = TextInput(
            text="Enter Train Class",
            multiline=False,
            size_hint=(1, 0.1),
            font_size=30,
            input_type=("number"),
        )
        self.window.add_widget(self.type)

        button_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.2))

        self.tybtn = Button(
            text="Log Type",
            font_size=40,
            size_hint=(1, 1),
        )
        self.tybtn.bind(on_press=self.save_type)

        button_layout.add_widget(self.tybtn)

        self.window.add_widget(button_layout)

        self.add_widget(self.window)

    def save_type(self, instance):
        home_screen = self.manager.get_screen('home')
        home_screen.type_text = self.type.text
        print(home_screen.type_text)
        print("Type saved:", home_screen.type_text)
        self.manager.current = "exact"


class Log3(Screen):
    def __init__(self, **kwargs):
        super(Log3, self).__init__(**kwargs)
        self.window = GridLayout()
        self.window.cols = 1
        self.window.size_hint = (0.6, 0.9)
        self.window.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        self.window.spacing = 1

        self.typetxt = Label(
            text="Train Number",
            font_size=40
        )
        self.window.add_widget(self.typetxt)
        self.exact = TextInput(
            text="Enter Train number",
            multiline=False,
            size_hint=(1, .5),
            font_size=30,
            input_type=("number"),
        )
        self.window.add_widget(self.exact)
        layout = BoxLayout(orientation='horizontal')

        self.special_livery_checkbox = CheckBox(active=False)
        self.special_livery_checkbox.bind(active=self.set_special_livery)
        layout.add_widget(Label(text="Special Livery"))
        layout.add_widget(self.special_livery_checkbox)

        self.rare_checkbox = CheckBox(active=False)
        self.rare_checkbox.bind(active=self.set_rare)
        layout.add_widget(Label(text="Rare"))
        layout.add_widget(self.rare_checkbox)

        self.driver_interaction_checkbox = CheckBox(active=False)
        self.driver_interaction_checkbox.bind(active=self.set_driver_interaction)
        layout.add_widget(Label(text="Driver Interaction"))
        layout.add_widget(self.driver_interaction_checkbox)

        self.window.add_widget(layout)

        button_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.2))
        self.tybtn = Button(
            text="Log Train Number",
            font_size=40,
            size_hint=(1, 2),

        )
        self.tybtn.bind(on_press=self.save_exact)
        button_layout.add_widget(self.tybtn)

        self.window.add_widget(button_layout)
        self.add_widget(self.window)

    def save_exact(self, instance):
        home_screen = self.manager.get_screen('home')
        home_screen.exact_text = self.exact.text
        print(home_screen.exact_text)
        print("Exact saved:", home_screen.exact_text)
        home_screen.goto_log3(None)
        self.manager.current = "confirm"

    def set_special_livery(self, instance, value):
        home_screen = self.manager.get_screen('home')
        home_screen.sl = "Yes" if value else "No"

    def set_rare(self, instance, value):
        home_screen = self.manager.get_screen('home')
        home_screen.rare = "Yes" if value else "No"

    def set_driver_interaction(self, instance, value):
        home_screen = self.manager.get_screen('home')
        home_screen.di = "Yes" if value else "No"


class Log4(Screen):
    def __init__(self, **kwargs):
        super(Log4, self).__init__(**kwargs)
        self.window = GridLayout()
        self.window.cols = 1
        self.window.size_hint = (0.6, 0.9)
        self.window.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        self.window.spacing = [1, 10]

        self.station_label = Label(text="Station:", font_size=30)
        self.type_label = Label(text="Type:", font_size=30)
        self.exact_label = Label(text="Exact:", font_size=30)
        self.sl_label = Label(text="Special Livery:", font_size=30)
        self.rare_label = Label(text="Rare:", font_size=30)
        self.di_label = Label(text="Driver Interaction:", font_size=30)
        self.confirm_button = Button(
            text="Confirm",
            font_size=30,
            background_color=get_color_from_hex('#009105'),
            background_normal=""
        )
        self.deny_button = Button(
            text="Deny",
            font_size=30,
            background_color=get_color_from_hex('#910000'),
            background_normal=""
        )
        self.deny_button.bind(on_press=self.deny)

        self.window.add_widget(self.station_label)
        self.window.add_widget(self.type_label)
        self.window.add_widget(self.exact_label)
        self.window.add_widget(self.sl_label)
        self.window.add_widget(self.rare_label)
        self.window.add_widget(self.di_label)
        self.window.add_widget(self.confirm_button)
        self.window.add_widget(self.deny_button)

        self.add_widget(self.window)

    def update_labels(self, station_text, type_text, exact_text, sl_text, rare_text, di_text):
        self.station_label.text = f"Station: {station_text}"
        self.type_label.text = f"Type: {type_text}"
        self.exact_label.text = f"Exact: {exact_text}"
        self.sl_label.text = f"Special Livery: {sl_text}"
        self.rare_label.text = f"Rare: {rare_text}"
        self.di_label.text = f"Driver Interaction: {di_text}"

    def deny(self, instance):
        self.manager.current = "station"

    def accept():
        pass


class Search(Screen):
    pass


class Achievements(Screen):
    pass


class Statistics(Screen):
    pass


if __name__ == "__main__":
    TrainSpotter().run()
