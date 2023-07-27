from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.utils import get_color_from_hex
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
import sqlite3


class TrainSpotter(App):
    def build(self):
        self.create_tables()  # Create the required tables in the SQLite database
        sm = ScreenManager()
        sm.add_widget(Log1(name='station'))
        sm.add_widget(Log2(name='type'))
        sm.add_widget(Log3(name='exact'))
        sm.add_widget(Log4(name='confirm'))
        sm.add_widget(Home(name='home'))
        sm.add_widget(Search(name='search'))
        sm.add_widget(SearchResults(name='search_results'))
        sm.add_widget(Achievements(name='achievements'))
        sm.add_widget(Statistics(name='statistics'))
        sm.current = 'home'
        return sm

    
    def create_tables(self):
        conn = sqlite3.connect("tp.db")
        cursor = conn.cursor()

        # Create the FullLog table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS FullLog (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                DateTime TEXT,
                Station TEXT,
                Class TEXT,
                Number TEXT,
                SpecialLivery TEXT,
                Rare TEXT,
                DriverInteraction TEXT
            )
        """)

        # Create the Basic table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Basic (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Class TEXT,
                Number TEXT,
                Quantity INTEGER
            )
        """)

        # Create the Total table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Total (
                ID INTEGER PRIMARY KEY,
                SpecialLivery INTEGER,
                Rare INTEGER,
                DriverInteraction INTEGER
            )
        """)

        # Insert an initial row into the Total table
        cursor.execute("""
            INSERT OR IGNORE INTO Total (ID, SpecialLivery, Rare, DriverInteraction)
            VALUES (1, 0, 0, 0)
        """)

        conn.commit()
        conn.close()

    def insert_log(self, station, train_class, train_number, special_livery, rare, driver_interaction):
        conn = sqlite3.connect("tp.db")
        cursor = conn.cursor()

        # Insert into FullLog table
        cursor.execute("""
            INSERT INTO FullLog ( Station, Class, Number, SpecialLivery, Rare, DriverInteraction)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (station, train_class, train_number, special_livery, rare, driver_interaction))

        # Check if there is a matching entry in the Basic table
        cursor.execute("""
            SELECT Quantity FROM Basic
            WHERE Class = ? AND Number = ?
        """, (train_class, train_number))
        result = cursor.fetchone()

        if result is None:
            # No matching entry found, insert a new row with quantity 1
            cursor.execute("""
                INSERT INTO Basic (Class, Number, Quantity)
                VALUES (?, ?, 1)
            """, (train_class, train_number))
        else:
            # Matching entry found, update the quantity by incrementing it by 1
            quantity = result[0] + 1
            cursor.execute("""
                UPDATE Basic SET Quantity = ?
                WHERE Class = ? AND Number = ?
            """, (quantity, train_class, train_number))

        # Update the Total table
        cursor.execute("""
            UPDATE Total SET
            SpecialLivery = (SELECT COUNT(*) FROM FullLog WHERE SpecialLivery = 'Yes'),
            Rare = (SELECT COUNT(*) FROM FullLog WHERE Rare = 'Yes'),
            DriverInteraction = (SELECT COUNT(*) FROM FullLog WHERE DriverInteraction = 'Yes')
            WHERE ID = 1
        """)

        conn.commit()
        conn.close()


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
            source="assets/logo.png",
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

    def insert_log(self, station, train_class, train_number, special_livery, rare, driver_interaction):
        # Insert the log into the database or perform any other required operations
        conn = sqlite3.connect("tp.db")
        cursor = conn.cursor()

        # Insert into FullLog table
        cursor.execute("""
            INSERT INTO FullLog (Station, Class, Number, SpecialLivery, Rare, DriverInteraction)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (station, train_class, train_number, special_livery, rare, driver_interaction))

        # Check if there is a matching entry in the Basic table
        cursor.execute("""
            SELECT Quantity FROM Basic
            WHERE Class = ? AND Number = ?
        """, (train_class, train_number))
        result = cursor.fetchone()

        if result is None:
            # No matching entry found, insert a new row with quantity 1
            cursor.execute("""
                INSERT INTO Basic (Class, Number, Quantity)
                VALUES (?, ?, 1)
            """, (train_class, train_number))
        else:
            # Matching entry found, update the quantity by incrementing it by 1
            quantity = result[0] + 1
            cursor.execute("""
                UPDATE Basic SET Quantity = ?
                WHERE Class = ? AND Number = ?
            """, (quantity, train_class, train_number))

        # Update the Total table
        cursor.execute("""
            UPDATE Total SET
            SpecialLivery = (SELECT COUNT(*) FROM FullLog WHERE SpecialLivery = 'Yes'),
            Rare = (SELECT COUNT(*) FROM FullLog WHERE Rare = 'Yes'),
            DriverInteraction = (SELECT COUNT(*) FROM FullLog WHERE DriverInteraction = 'Yes')
            WHERE ID = 1
        """)

        conn.commit()
        conn.close()

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
            background_normal=""
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
            input_type=("text"),
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
        self.confirm_button.bind(on_press=self.confirm)

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

    def confirm(self, instance):
        # Get the logged information
        home_screen = self.manager.get_screen('home')
        station = home_screen.station_text
        train_class = home_screen.type_text
        train_number = home_screen.exact_text
        special_livery = home_screen.sl
        rare = home_screen.rare
        driver_interaction = home_screen.di

        # Insert the log into the database
        app = App.get_running_app()
        app.insert_log(station, train_class, train_number, special_livery, rare, driver_interaction)

        self.manager.current = "home"


class Search(Screen):
    def __init__(self, **kwargs):
        super(Search, self).__init__(**kwargs)
        self.window = GridLayout()
        self.window.cols = 1
        self.window.size_hint = (0.6, 0.9)
        self.window.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        self.window.spacing = 1

        self.search_label = Label(text="Search by Train Class:", font_size=30)
        self.train_class_input = TextInput(multiline=False, font_size=30)

        self.search_livery_checkbox = CheckBox(active=False)
        self.search_livery_checkbox.bind(active=self.set_search_livery)
        self.search_livery_label = Label(text="Has Special Livery", font_size=30)

        self.search_rare_checkbox = CheckBox(active=False)
        self.search_rare_checkbox.bind(active=self.set_search_rare)
        self.search_rare_label = Label(text="Is Rare", font_size=30)

        self.search_interaction_checkbox = CheckBox(active=False)
        self.search_interaction_checkbox.bind(active=self.set_search_interaction)
        self.search_interaction_label = Label(text="Has Driver Interaction", font_size=30)

        self.search_button = Button(text="Search", font_size=30, background_color=get_color_from_hex('#ffa500'))
        self.search_button.bind(on_press=self.search_logs)

        self.back_button = Button(text="Back", font_size=30, background_color=get_color_from_hex('#ff0000'))
        self.back_button.bind(on_press=self.go_back)

        self.window.add_widget(self.search_label)
        self.window.add_widget(self.train_class_input)
        self.window.add_widget(self.search_livery_label)
        self.window.add_widget(self.search_livery_checkbox)
        self.window.add_widget(self.search_rare_label)
        self.window.add_widget(self.search_rare_checkbox)
        self.window.add_widget(self.search_interaction_label)
        self.window.add_widget(self.search_interaction_checkbox)
        self.window.add_widget(self.search_button)
        self.window.add_widget(self.back_button)

        self.add_widget(self.window)

    def set_search_livery(self, instance, value):
        self.search_livery = value

    def set_search_rare(self, instance, value):
        self.search_rare = value

    def set_search_interaction(self, instance, value):
        self.search_interaction = value

    def search_logs(self, instance):
        train_class = self.train_class_input.text
        has_livery = self.search_livery_checkbox.active
        is_rare = self.search_rare_checkbox.active
        has_interaction = self.search_interaction_checkbox.active

        # Perform the search using the provided filters
        conn = sqlite3.connect("tp.db")
        cursor = conn.cursor()

        # Construct the SQL query with dynamic conditions based on the checkbox status
        query_conditions = []
        params = []

        query_conditions.append("(Class = ? AND DriverInteraction = ?)")
        params.extend([train_class, "Yes" if has_interaction else "No"])

        if has_livery and is_rare:
            query_conditions.append("(Class = ? AND SpecialLivery = ? AND Rare = ?)")
            params.extend([train_class, "Yes", "Yes"])
        elif has_livery:
            query_conditions.append("(Class = ? AND SpecialLivery = ?)")
            params.extend([train_class, "Yes"])
        elif is_rare:
            query_conditions.append("(Class = ? AND Rare = ?)")
            params.extend([train_class, "Yes"])

        # Combine the conditions using AND operator to create the final query
        query = """
            SELECT Station, Class, Number, SpecialLivery, Rare, DriverInteraction
            FROM FullLog
        """

        if query_conditions:
            query += " WHERE " + " AND ".join(query_conditions)

        cursor.execute(query, tuple(params))
        results = cursor.fetchall()
        conn.close()

        # Display the search results
        search_results_screen = self.manager.get_screen('search_results')
        search_results_screen.on_results_text(results)
        self.manager.current = 'search_results'


    def go_back(self, instance):
        self.manager.current = 'home'




class SearchResults(Screen):
    def __init__(self, **kwargs):
        super(SearchResults, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')

        # Create the ScrollView and GridLayout
        self.scrollview = ScrollView()
        self.grid_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)

        # Set the height of the GridLayout to be determined by its content
        self.grid_layout.bind(minimum_height=self.grid_layout.setter('height'))

        # Add the GridLayout to the ScrollView
        self.scrollview.add_widget(self.grid_layout)

        # Add the ScrollView to the main layout
        self.layout.add_widget(self.scrollview)

        # Back button
        self.back_button = Button(text='Back', size_hint=(None, None), size=(100, 50))
        self.back_button.bind(on_release=self.go_back)
        self.layout.add_widget(self.back_button)

        self.add_widget(self.layout)

    def on_results_text(self, results):
        # Clear any previous search results
        self.grid_layout.clear_widgets()

        # Add each attribute name in front of its corresponding value and format them
        for result in results:
            result_layout = BoxLayout(orientation='vertical', spacing=30, size_hint_y=None, padding=(0, 40))
            result_layout.bind(minimum_height=result_layout.setter('height'))

            labels = [
                f"Class: {result[1]}",
                f"Number: {result[2]}",
                f"Special Livery: {result[3]}",
                f"Rare: {result[4]}",
                f"Driver Interaction: {result[5]}"
            ]
            for label in labels:
                result_label = Label(text=label, font_size=20, halign='left', valign='middle')
                result_layout.add_widget(result_label)

            self.grid_layout.add_widget(result_layout)


    def go_back(self, instance):
        self.manager.current = 'search'

class Achievements(Screen):
    def __init__(self, **kwargs):
        super(Achievements, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.add_widget(self.layout)

        self.label = Label(text='Achievements', font_size=30, size_hint=(1, 0.1))
        self.layout.add_widget(self.label)

        # Create the ScrollView and GridLayout for achievements
        self.scrollview = ScrollView()
        self.achievements_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.achievements_layout.bind(minimum_height=self.achievements_layout.setter('height'))

        # Add the GridLayout to the ScrollView
        self.scrollview.add_widget(self.achievements_layout)

        # Add the ScrollView to the main layout
        self.layout.add_widget(self.scrollview)

        self.backbtn = Button(text='Back', font_size=30, size_hint=(1, 0.2))
        self.backbtn.bind(on_press=self.back_to_home)
        self.layout.add_widget(self.backbtn)

    def on_enter(self):
        # Fetch and display achievements every time the screen is shown
        unlocked_achievements = self.check_achievements()

        # Clear any previous achievements from the GridLayout
        self.achievements_layout.clear_widgets()

        # Add each achievement to the GridLayout
        for achievement in unlocked_achievements:
            achievement_label = Label(text=achievement, font_size=20, halign='left', valign='middle', size_hint_y=None, padding=(0, 40))
            achievement_label.bind(texture_size=achievement_label.setter('size'))
            self.achievements_layout.add_widget(achievement_label)

    def back_to_home(self, instance):
        self.manager.current = 'home'

    def fetch_total_data(self):
        conn = sqlite3.connect('tp.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Total')
        total_data = cursor.fetchone()
        conn.close()
        return total_data

    def fetch_train_count(self):
        conn = sqlite3.connect('tp.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM FullLog')
        train_count = cursor.fetchone()[0]
        conn.close()
        return train_count

    def check_train_count_achievements(self, train_count):
        achievements = {
            1: "1st Train Logged",
            10: "10th Train Logged",
            25: "25th Train Logged",
            100: "100th Train Logged",
            250: "250th Train Logged",
            1000: "1000th Train Logged",
            1500: "1500th Train Logged",
            2000: "2000th Train Logged",
            5000: "5000th Train Logged",
            10000: "10000th Train Logged",
            20000: "20000th Train Logged",
            30000: "30000th Train Logged",
            40000: "40000th Train Logged",
            50000: "50000th Train Logged",
            60000: "60000th Train Logged",
            70000: "70000th Train Logged",
            80000: "80000th Train Logged",
            90000: "90000th Train Logged",
            100000: "100000th Train Logged",
            1000000: "1000000th Train Logged"
        }

        unlocked_achievements = []
        for count, achievement in achievements.items():
            if train_count >= count:
                unlocked_achievements.append(achievement)

        return unlocked_achievements

    def check_other_achievements(self, total_data):
        unlocked_achievements = []

        # Check and add special livery achievements
        special_livery_count = total_data[1]
        if special_livery_count >= 1:
            unlocked_achievements.append("1st Special Livery")
        if special_livery_count >= 5:
            unlocked_achievements.append("5th Special Livery")
        if special_livery_count >= 10:
            unlocked_achievements.append("10th Special Livery")
        if special_livery_count >= 25:
            unlocked_achievements.append("25th Special Livery")
        if special_livery_count >= 50:
            unlocked_achievements.append("50th Special Livery")
        if special_livery_count >= 75:
            unlocked_achievements.append("75th Special Livery")
        if special_livery_count >= 100:
            unlocked_achievements.append("100th Special Livery")
        if special_livery_count >= 150:
            unlocked_achievements.append("150th Special Livery")
        if special_livery_count >= 250:
            unlocked_achievements.append("250th Special Livery")
        if special_livery_count >= 500:
            unlocked_achievements.append("500th Special Livery")
        if special_livery_count >= 1000:
            unlocked_achievements.append("1000th Special Livery")
        if special_livery_count >= 2500:
            unlocked_achievements.append("2500th Special Livery")
        if special_livery_count >= 5000:
            unlocked_achievements.append("5000th Special Livery")
        if special_livery_count >= 10000:
            unlocked_achievements.append("10000th Special Livery")
        if special_livery_count >= 25000:
            unlocked_achievements.append("25000th Special Livery")
        if special_livery_count >= 50000:
            unlocked_achievements.append("50000th Special Livery")
        if special_livery_count >= 100000:
            unlocked_achievements.append("100000th Special Livery")
        if special_livery_count >= 250000:
            unlocked_achievements.append("250000th Special Livery")
        if special_livery_count >= 500000:
            unlocked_achievements.append("500000th Special Livery")
        if special_livery_count >= 1000000:
            unlocked_achievements.append("1000000th Special Livery")
        # Add more special livery achievements here for different counts

        # Check and add rare achievements
        rare_count = total_data[2]
        if rare_count >= 1:
            unlocked_achievements.append("1st Rare Train")
        if rare_count >= 5:
            unlocked_achievements.append("5th Rare Train")
        if rare_count >= 10:
            unlocked_achievements.append("10th Rare Train")
        if rare_count >= 25:
            unlocked_achievements.append("25th Rare Train")
        if rare_count >= 50:
            unlocked_achievements.append("50th Rare Train")
        if rare_count >= 75:
            unlocked_achievements.append("75th Rare Train")
        if rare_count >= 100:
            unlocked_achievements.append("100th Rare Train")
        if rare_count >= 150:
            unlocked_achievements.append("150th Rare Train")
        if rare_count >= 250:
            unlocked_achievements.append("250th Rare Train")
        if rare_count >= 500:
            unlocked_achievements.append("500th Rare Train")
        if rare_count >= 1000:
            unlocked_achievements.append("1000th Rare Train")
        if rare_count >= 2500:
            unlocked_achievements.append("2500th Rare Train")
        if rare_count >= 5000:
            unlocked_achievements.append("5000th Rare Train")
        if rare_count >= 10000:
            unlocked_achievements.append("10000th Rare Train")
        if rare_count >= 25000:
            unlocked_achievements.append("25000th Rare Train")
        if rare_count >= 50000:
            unlocked_achievements.append("50000th Rare Train")
        if rare_count >= 100000:
            unlocked_achievements.append("100000th Rare Train")
        if rare_count >= 250000:
            unlocked_achievements.append("250000th Rare Train")
        if rare_count >= 500000:
            unlocked_achievements.append("500000th Rare Train")
        if rare_count >= 1000000:
            unlocked_achievements.append("1000000th Rare Train")
        # Add more rare achievements here for different counts

        # Check and add driver interaction achievements
        driver_interaction_count = total_data[3]
        if driver_interaction_count >= 1:
            unlocked_achievements.append("1st Driver Interaction")
        if driver_interaction_count >= 5:
            unlocked_achievements.append("5th Driver Interaction")
        if driver_interaction_count >= 10:
            unlocked_achievements.append("10th Driver Interaction")
        if driver_interaction_count >= 25:
            unlocked_achievements.append("25th Driver Interaction")
        if driver_interaction_count >= 50:
            unlocked_achievements.append("50th Driver Interaction")
        if driver_interaction_count >= 75:
            unlocked_achievements.append("75th Driver Interaction")
        if driver_interaction_count >= 100:
            unlocked_achievements.append("100th Driver Interaction")
        if driver_interaction_count >= 150:
            unlocked_achievements.append("150th Driver Interaction")
        if driver_interaction_count >= 250:
            unlocked_achievements.append("250th Driver Interaction")
        if driver_interaction_count >= 500:
            unlocked_achievements.append("500th Driver Interaction")
        if driver_interaction_count >= 1000:
            unlocked_achievements.append("1000th Driver Interaction")
        if driver_interaction_count >= 2500:
            unlocked_achievements.append("2500th Driver Interaction")
        if driver_interaction_count >= 5000:
            unlocked_achievements.append("5000th Driver Interaction")
        if driver_interaction_count >= 10000:
            unlocked_achievements.append("10000th Driver Interaction")
        if driver_interaction_count >= 25000:
            unlocked_achievements.append("25000th Driver Interaction")
        if driver_interaction_count >= 50000:
            unlocked_achievements.append("50000th Driver Interaction")
        if driver_interaction_count >= 100000:
            unlocked_achievements.append("100000th Driver Interaction")
        if driver_interaction_count >= 250000:
            unlocked_achievements.append("250000th Driver Interaction")
        if driver_interaction_count >= 500000:
            unlocked_achievements.append("500000th Driver Interaction")
        if driver_interaction_count >= 1000000:
            unlocked_achievements.append("1000000th Driver Interaction")

        # Add more driver interaction achievements here for different counts

        # Check and add quantity of the same train achievements
        conn = sqlite3.connect('tp.db')
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(Quantity) FROM Basic')
        max_quantity = cursor.fetchone()[0]
        conn.close()

        
        if max_quantity >= 2:
            unlocked_achievements.append("1st of the same train")
        if max_quantity >= 5:
            unlocked_achievements.append("5th of the same train")
        if max_quantity >= 10:
            unlocked_achievements.append("10th of the same train")
        if max_quantity >= 15:
            unlocked_achievements.append("15th of the same train")
        if max_quantity >= 20:
            unlocked_achievements.append("20th of the same train")
        if max_quantity >= 30:
            unlocked_achievements.append("30th of the same train")
        if max_quantity >= 50:
            unlocked_achievements.append("50th of the same train")
        if max_quantity >= 75:
            unlocked_achievements.append("75th of the same train")
        if max_quantity >= 100:
            unlocked_achievements.append("100th of the same train")
        if max_quantity >= 250:
            unlocked_achievements.append("250th of the same train")
        if max_quantity >= 500:
            unlocked_achievements.append("500th of the same train")
        if max_quantity >= 1000:
            unlocked_achievements.append("1000th of the same train")

        return unlocked_achievements

    def check_achievements(self):
        # Fetch the train count
        train_count = self.fetch_train_count()

        # Check train count-based achievements
        unlocked_achievements = self.check_train_count_achievements(train_count)

        # Fetch the total data
        total_data = self.fetch_total_data()

        # Check other achievements based on total data
        unlocked_achievements.extend(self.check_other_achievements(total_data))

        return unlocked_achievements


class Statistics(Screen):
    def __init__(self, **kwargs):
        super(Statistics, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.add_widget(self.layout)
        self.label = Label(text='Statistics', font_size=30, size_hint=(1, 0.1))
        self.layout.add_widget(self.label)

        # Add statistics labels
        self.total_trains_label = Label(text='Total Trains Logged: 0', font_size=20,size_hint_y=None, padding=(0, 20))
        self.layout.add_widget(self.total_trains_label)

        self.special_livery_label = Label(text='Special Livery Trains: 0', font_size=20, size_hint_y=None, padding=(0, 20))
        self.layout.add_widget(self.special_livery_label)

        self.rare_trains_label = Label(text='Rare Trains: 0', font_size=20)
        self.layout.add_widget(self.rare_trains_label)

        self.driver_interaction_label = Label(text='Trains with Driver Interaction: 0', font_size=20, size_hint_y=None, padding=(0, 20))
        self.layout.add_widget(self.driver_interaction_label)

        self.most_common_train_label = Label(text='Most Common Train: None', font_size=20,size_hint_y=None, padding=(0, 20))
        self.layout.add_widget(self.most_common_train_label)

        self.backbtn = Button(text='Back', font_size=30, size_hint=(1, 0.2))
        self.backbtn.bind(on_press=self.back_to_home)
        self.layout.add_widget(self.backbtn)

    def on_enter(self):
        # Fetch and display statistics every time the screen is shown
        statistics = self.fetch_statistics()

        # Update statistics labels
        self.total_trains_label.text = f'Total Trains Logged: {statistics["total_trains"]}'
        self.special_livery_label.text = f'Special Livery Trains: {statistics["special_livery"]}'
        self.rare_trains_label.text = f'Rare Trains: {statistics["rare_trains"]}'
        self.driver_interaction_label.text = f'Trains with Driver Interaction: {statistics["driver_interaction"]}'
        self.most_common_train_label.text = f'Most Common Train: {statistics["most_common_train"]}'

    def back_to_home(self, instance):
        self.manager.current = 'home'

    def fetch_statistics(self):
        conn = sqlite3.connect('tp.db')
        cursor = conn.cursor()

        # Get the total number of trains logged
        cursor.execute('SELECT COUNT(*) FROM FullLog')
        total_trains = cursor.fetchone()[0]

        # Get the count of special livery trains
        cursor.execute('SELECT COUNT(*) FROM FullLog WHERE SpecialLivery = "Yes"')
        special_livery = cursor.fetchone()[0]

        # Get the count of rare trains
        cursor.execute('SELECT COUNT(*) FROM FullLog WHERE Rare = "Yes"')
        rare_trains = cursor.fetchone()[0]

        # Get the count of trains with driver interaction
        cursor.execute('SELECT COUNT(*) FROM FullLog WHERE DriverInteraction = "Yes"')
        driver_interaction = cursor.fetchone()[0]

        # Get the most common train
        cursor.execute('SELECT Class, Number, MAX(Quantity) FROM Basic')
        most_common_train = cursor.fetchone()
        most_common_train_text = f'{most_common_train[0]} {most_common_train[1]} ({most_common_train[2]} times)' if most_common_train else 'None'

        conn.close()

        return {
            "total_trains": total_trains,
            "special_livery": special_livery,
            "rare_trains": rare_trains,
            "driver_interaction": driver_interaction,
            "most_common_train": most_common_train_text,
        }


if __name__ == '__main__':
    TrainSpotter().run()
