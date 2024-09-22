import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sv_ttk
import threading
from ctypes import windll
from pockie_ninja_automation import *
from src import *

MAIN_MENU_WINDOW_SIZE="440x330"
STANDARD_AREA_FARM_WINDOW_SIZE="440x260"
SLOT_MACHINE_FARM_WINDOW_SIZE="440x220"
SCROLL_BOT_WINDOW_SIZE="440x230"
STANDARD_PADDING_X=15
STANDARD_PADDING_Y=3
VERSION="2.2"

try:
    with open("account.txt", "r") as file:
        ACCOUNT = file.read().splitlines()
except FileNotFoundError:
    messagebox.showerror("Error", "The file 'account.txt' does not exist.")
    ACCOUNT = []  # Assign an empty list or handle the flow as you prefer

def set_style():
    sv_ttk.set_theme("dark")

## CREATE MAIN MENU
class MainMenu(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master=master
        self.master.title(f"Pockie Ninja Bot Farm | v{VERSION}")
        self.master.resizable(False, False)
        self.create_widgets()
        center(self.master)

    def create_widgets(self):
        self.notebook=ttk.Notebook(self.master)
        self.notebook.pack(expand=True, fill='both')

        # Initialize frames
        self.valhalla_farm_frame=ValhallaFarm(master=self.master)
        self.regular_area_frame=RegularAreaFarm(master=self.master)
        self.slot_machine_farm_frame=SlotMachineFarm(master=self.master)
        self.scroll_opener_frame=ScrollOpenerBot(master=self.master)

        # Add frames to notebook
        self.notebook.add(self.valhalla_farm_frame, text="Valhalla")
        self.notebook.add(self.regular_area_frame, text="Regular Area")
        self.notebook.add(self.slot_machine_farm_frame, text="Slot Machine")
        self.notebook.add(self.scroll_opener_frame, text="Open Scrolls")

        # Bind the event to change the window size
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def on_tab_change(self, event):
        tab=event.widget.tab('current')['text']
        if tab == "Valhalla":
            self.master.geometry(MAIN_MENU_WINDOW_SIZE)
        elif tab == "Regular Area":
            self.master.geometry(STANDARD_AREA_FARM_WINDOW_SIZE)
        elif tab == "Slot Machine":
            self.master.geometry(SLOT_MACHINE_FARM_WINDOW_SIZE)
        elif tab == "Open Scrolls":
            self.master.geometry(SCROLL_BOT_WINDOW_SIZE)
        center(self.master)

## CREATE VALHALLA GUI
class ValhallaFarm(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.create_widgets()
        self.bots=[]
        self.threads=[]

    def update_difficulties(self, *args):
        # Reset var and delete all old options
        self.difficulty_str_var.set('')
        self.difficulty_option_menu['menu'].delete(0, 'end')

        if self.dungeon_lvl_option_menu.cget("text") == VALHALLA_LVL_11:
            difficulty_options=[SOLO_VALHALLA_DIFFICULTY]
        else:
            difficulty_options=[NORMAL_VALHALLA_DIFFICULTY, SOLO_VALHALLA_DIFFICULTY]

        # Insert list of new options (tk._setit hooks them up to var)
        for option in difficulty_options:
            self.difficulty_option_menu['menu'].add_command(label=option, command=tk._setit(self.difficulty_str_var, option))
        self.difficulty_str_var.set(difficulty_options[0])

    def create_widgets(self):
        self.username_label=ttk.Label(self, text="Username:")
        self.username_entry=ttk.Entry(self)
        self.password_label=ttk.Label(self, text="Password:")
        self.password_entry=ttk.Entry(self, show="*")
        ## SET DUNGEON LEVEL AS A OPTION MENU
        self.dungeon_level_options=[VALHALLA_LVL_11, VALHALLA_LVL_16]
        self.dungeon_lvl_label=ttk.Label(self, text="Dungeon Level:")
        self.dungeon_lvl_str_var=tk.StringVar()
        self.dungeon_lvl_str_var.set(self.dungeon_level_options[0])
        self.dungeon_lvl_option_menu=tk.OptionMenu(self, self.dungeon_lvl_str_var, *self.dungeon_level_options, command=self.update_difficulties)
        ## DIFFICULTY OPTION MENU
        self.difficulty_options=[SOLO_VALHALLA_DIFFICULTY]
        self.difficulty_option_label=ttk.Label(self, text="Choose difficulty:")
        self.difficulty_str_var=tk.StringVar()
        self.difficulty_str_var.set(self.difficulty_options[0])
        self.difficulty_option_menu=tk.OptionMenu(self, self.difficulty_str_var, *self.difficulty_options)
        ## ADD A CHECKBOX IF YOU WANT TO RUN THE BOT IN HEADLESS MODE
        self.headless_var=tk.IntVar()
        self.headless_label=ttk.Label(self, text="Headless (No Browser):")
        self.headless_checkbox=ttk.Checkbutton(self, variable=self.headless_var)
        self.legend_box_var=tk.IntVar()
        self.legend_box_label=ttk.Label(self, text="Legend Box:")
        self.legend_box_checkbox=ttk.Checkbutton(self, variable=self.legend_box_var)
        self.game_speed_var=tk.DoubleVar()
        self.game_speed_label=ttk.Label(self, text="Game Speed (1.0)")
        self.game_speed_slider=ttk.Scale(self, from_=1, to=2, variable=self.game_speed_var, command=self.slider_changed)
        self.start_button=ttk.Button(self, text="Start", command=self.on_start_button_click)

        self.username_label.grid(row=0, column=0, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.username_entry.grid(row=0, column=1, sticky="we", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.password_label.grid(row=1, column=0, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.password_entry.grid(row=1, column=1, sticky="we", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.dungeon_lvl_label.grid(row=2, column=0, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.dungeon_lvl_option_menu.grid(row=2, column=1, sticky="w", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.difficulty_option_label.grid(row=3, column=0, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.difficulty_option_menu.grid(row=3, column=1, sticky="w", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.legend_box_label.grid(row=4, column=0, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.legend_box_checkbox.grid(row=4, column=1, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.game_speed_label.grid(row=5, column=0, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.game_speed_slider.grid(row=5, column=1, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.headless_label.grid(row=6, column=0, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.headless_checkbox.grid(row=6, column=1, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.start_button.grid(row=7, column=1, columnspan=2, sticky="ew", pady=STANDARD_PADDING_Y)

        if len(ACCOUNT) == 2:
            self.username_entry.insert(0, ACCOUNT[0])
            self.password_entry.insert(0, ACCOUNT[1])

    def get_speedhack_value(self):
        return f"Game Speed ({'{: .1f}'.format(self.game_speed_var.get())})"

    def slider_changed(self, event):
        self.game_speed_label.configure(text=self.get_speedhack_value())

    def on_start_button_click(self):
        new_thread=threading.Thread(target=self.start_bot, daemon=True)
        self.threads.append(new_thread)
        new_thread.start()

    def start_bot(self):
        username=self.username_entry.get()
        password=self.password_entry.get()
        dungeon_lvl=self.dungeon_lvl_option_menu.cget("text")
        difficulty=self.difficulty_option_menu.cget("text")
        headless=self.headless_var.get()
        legend_box=self.legend_box_var.get()
        game_speed='{: .1f}'.format(self.game_speed_var.get())

        if headless == 1:
            headless=True
        else:
            headless=False
        
        if legend_box == 1:
            legend_box=True
        else:
            legend_box=False

        if username == "" or password == "" or dungeon_lvl == "":
            messagebox.showwarning("Warning", "Please fill all the fields")
        else:
            messagebox.showinfo("Info", "Checking Your Credentials...\nPlease wait for a moment!")
            check_credentials_bot=CheckLoginCredentials(username, password)
            is_invalid, case=check_credentials_bot.check_credentials()
            if is_invalid:
                if case == 'logedin':
                    messagebox.showwarning("Warning", "Invalid Credentials!\nThis account is already logged in!")
                if case == 'password':
                    messagebox.showwarning("Warning", "Invalid Credentials!\nUsername or Password is incorrect!")
                return
            
            messagebox.showinfo("Info", "Valid Credentials!\nStarting Bot!")
            check_exit_success=self.create_and_run_bot(username, password, dungeon_lvl, difficulty, legend_box, game_speed, headless)
            while not check_exit_success:
                check_exit_success=self.create_and_run_bot(username, password, dungeon_lvl, difficulty, legend_box, game_speed, headless)

    def create_and_run_bot(self, username, password, dungeon_lvl, difficulty, legend_box, game_speed, headless):
        bot=PockieNinjaValhallaBot(username, password, int(dungeon_lvl), difficulty, legend_box, game_speed, headless=headless)
        self.bots.append(bot)
        check_exit_success=bot.main_loop()
        return check_exit_success

## CREATE STANDARD FARM GUI
class RegularAreaFarm(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.create_widgets()
        self.bots=[]
        self.threads=[]

    def populate_area_names(self):
        area_names=[SMELTING_MOUNTAINS_AREA_NAME, EVENTIDE_BARRENS_AREA_NAME, CROSSROADS_AREA_NAME]
        return area_names

    def populate_mob_names(self):
        options=[SUNFLOWER_NAME, BEE_NAME, SUSHI_NAME, SCARLET_NAME, WARRIOR_OF_DARKNESS_NAME] # , DEMON_BRUTE_NAME
        return options
    
    def update_mob_names(self, *args):
        # Reset var and delete all old options
        self.mob_name_str_var.set('')
        self.mob_name_option_menu['menu'].delete(0, 'end')
        area_name=self.area_name_option_menu.cget("text")
        if area_name == SMELTING_MOUNTAINS_AREA_NAME:
            options=[SUNFLOWER_NAME, BEE_NAME, SUSHI_NAME, SCARLET_NAME, WARRIOR_OF_DARKNESS_NAME] # , DEMON_BRUTE_NAME
        elif area_name == EVENTIDE_BARRENS_AREA_NAME:
            options=[POTATO_NAME, MONKEY_NAME, MEAL_NAME, KAPPA_NAME, BULLHEAD_NAME] # , PLAGUE_DEMON_NAME
        elif area_name == CROSSROADS_AREA_NAME:
            options=[TREE_ENT_NAME, MAN_EATER_NAME, LONGFEATHER_DEMON_NAME, CHEVALIER_DEMON_NAME, SHADOW_BAT_NAME,] # SOULENDER_NAME
        # Insert list of new options (tk._setit hooks them up to var)
        for option in options:
            self.mob_name_option_menu['menu'].add_command(label=option, command=tk._setit(self.mob_name_str_var, option))
        self.mob_name_str_var.set(options[0])

    def create_widgets(self):

        # Username and password widgets
        self.username_label=ttk.Label(self, text="Username")
        self.username_entry=ttk.Entry(self)
        self.password_label=ttk.Label(self, text="Password")
        self.password_entry=ttk.Entry(self, show="*")

        # Area names dropdown menu
        area_options=self.populate_area_names()
        self.area_option_label=ttk.Label(self, text="Choose Area")
        self.area_name_str_var=tk.StringVar()
        self.area_name_str_var.set(area_options[0])
        self.area_name_option_menu=tk.OptionMenu(self, self.area_name_str_var, *area_options, command=self.update_mob_names)

        # Mob names dropdown menu
        mobs_options=self.populate_mob_names()
        self.mob_option_label=ttk.Label(self, text="Choose Mob")
        self.mob_name_str_var=tk.StringVar()
        self.mob_name_str_var.set(mobs_options[0])
        self.mob_name_option_menu=tk.OptionMenu(self, self.mob_name_str_var, *mobs_options)

        # Game speed settings
        self.game_speed_var=tk.DoubleVar(value=1.0)  # Default value
        self.game_speed_label=ttk.Label(self, text="Game Speed (1.0)")
        self.game_speed_slider=ttk.Scale(self, from_=1, to=3, orient='horizontal', variable=self.game_speed_var, command=self.slider_changed)

        # Headless mode checkbox
        self.headless_var=tk.IntVar()
        self.headless_label=ttk.Label(self, text="Headless (No Browser):")
        self.headless_checkbox=ttk.Checkbutton(self, variable=self.headless_var)

        # Control buttons
        self.start_button=ttk.Button(self, text="Start", command=self.on_start_button_click)

        # Grid placement
        self.username_label.grid(row=0, column=0, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.username_entry.grid(row=0, column=1, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.password_label.grid(row=1, column=0, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.password_entry.grid(row=1, column=1, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.area_option_label.grid(row=2, column=0, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.area_name_option_menu.grid(row=2, column=1, sticky="we", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.mob_option_label.grid(row=3, column=0, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.mob_name_option_menu.grid(row=3, column=1, sticky="we", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.headless_label.grid(row=5, column=0, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.headless_checkbox.grid(row=5, column=1, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.game_speed_label.grid(row=4, column=0, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.game_speed_slider.grid(row=4, column=1, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.start_button.grid(row=5, column=1, columnspan=2, sticky="ew", pady=STANDARD_PADDING_Y)

        if len(ACCOUNT) == 2:
            self.username_entry.insert(0, ACCOUNT[0])
            self.password_entry.insert(0, ACCOUNT[1])
    
    def get_speedhack_value(self):
        return f"Game Speed ({'{: .1f}'.format(self.game_speed_var.get())})"

    def slider_changed(self, event):
        self.game_speed_label.configure(text=self.get_speedhack_value())

    def on_start_button_click(self):
        new_thread=threading.Thread(target=self.start_bot, daemon=True)
        self.threads.append(new_thread)
        new_thread.start()

    def start_bot(self):
        username=self.username_entry.get()
        password=self.password_entry.get()
        area_name=self.area_name_option_menu.cget("text")
        mob_name=self.mob_name_option_menu.cget("text")
        headless=self.headless_var.get()
        game_speed='{: .1f}'.format(self.game_speed_var.get())
        if headless == 1:
            headless=True
        else:
            headless=False
        if username == "" or password == "" or mob_name == "":
            messagebox.showwarning("Warning", "Please fill all the fields")
        else:
            messagebox.showinfo("Info", "Checking Your Credentials...\nPlease wait for a moment!")
            check_credentials_bot=CheckLoginCredentials(username, password)
            is_invalid, case=check_credentials_bot.check_credentials()
            if is_invalid:
                if case == 'logedin':
                    messagebox.showwarning("Warning", "Invalid Credentials!\nThis account is already logged in!")
                if case == 'username':
                    messagebox.showwarning("Warning", "Invalid Credentials!\nUsername is incorrect!")
                if case == 'password':
                    messagebox.showwarning("Warning", "Invalid Credentials!\nPassword is incorrect!")
                return
            messagebox.showinfo("Info", "Valid Credentials!\nStarting Bot!")
            check_exit_success=self.create_and_run_bot(username, password, area_name, mob_name, game_speed, headless)
            while not check_exit_success:
                check_exit_success=self.create_and_run_bot(username, password, area_name, mob_name, game_speed, headless)

    def create_and_run_bot(self, username, password, area_name, mob_name, game_speed, headless):
        bot=PockieNinjaStandardAreaFarm(username, password, area_name, mob_name, game_speed, headless=headless)
        self.bots.append(bot)
        check_exit_success=bot.main_loop()
        return check_exit_success

## CREATE SLOT MACHINE GUI
class SlotMachineFarm(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.create_widgets()
        self.bots=[]
        self.threads=[]

    def create_widgets(self):
        self.username_label=ttk.Label(self, text="Username")
        self.username_entry=ttk.Entry(self)
        self.password_label=ttk.Label(self, text="Password")
        self.password_entry=ttk.Entry(self, show="*")
        ## ADD A CHECKBOX IF YOU WANT TO RUN THE BOT IN HEADLESS MODE
        self.game_speed_var=tk.DoubleVar()
        self.game_speed_label=ttk.Label(self, text="Game Speed ( 1.0)")
        self.game_speed_slider=ttk.Scale(self, from_=1, to=3, variable=self.game_speed_var, command=self.slider_changed)
        self.headless_var=tk.IntVar()
        self.headless_label=ttk.Label(self, text="Headless (No Browser):")
        self.headless_checkbox=ttk.Checkbutton(self, variable=self.headless_var)
        self.start_button=ttk.Button(self, text="Start", command=self.on_start_button_click)

        self.username_label.grid(row=0, column=0, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.username_entry.grid(row=0, column=1, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.password_label.grid(row=1, column=0, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.password_entry.grid(row=1, column=1, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.game_speed_label.grid(row=4, column=0, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.game_speed_slider.grid(row=4, column=1, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.headless_label.grid(row=5, column=0, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.headless_checkbox.grid(row=5, column=1, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.start_button.grid(row=6, column=1, columnspan=2, sticky="ew", pady=STANDARD_PADDING_Y)

        if len(ACCOUNT) == 2:
            self.username_entry.insert(0, ACCOUNT[0])
            self.password_entry.insert(0, ACCOUNT[1])
    
    def get_speedhack_value(self):
        return f"Game Speed ({'{: .1f}'.format(self.game_speed_var.get())})"

    def slider_changed(self, event):
        self.game_speed_label.configure(text=self.get_speedhack_value())
        
    def on_start_button_click(self):
        new_thread=threading.Thread(target=self.start_bot, daemon=True)
        self.threads.append(new_thread)
        new_thread.start()

    def start_bot(self):
        username=self.username_entry.get()
        password=self.password_entry.get()
        headless=self.headless_var.get()
        game_speed='{: .1f}'.format(self.game_speed_var.get())

        if headless == 1:
            headless=True
        else:
            headless=False

        if username == "" or password == "":
            messagebox.showwarning("Warning", "Please fill all the fields")
        else:
            messagebox.showinfo("Info", "Checking Your Credentials...\nPlease wait for a moment!")
            check_credentials_bot=CheckLoginCredentials(username, password)
            is_invalid, case=check_credentials_bot.check_credentials()
            if is_invalid:
                if case == 'logedin':
                    messagebox.showwarning("Warning", "Invalid Credentials!\nThis account is already logged in!")
                if case == 'password':
                    messagebox.showwarning("Warning", "Invalid Credentials!\nUsername or Password is incorrect!")
                return
            
            messagebox.showinfo("Info", "Valid Credentials!\nStarting Bot!")
            check_exit_success=self.create_and_run_bot(username, password, game_speed, headless)
            while not check_exit_success:
                check_exit_success=self.create_and_run_bot(username, password, game_speed, headless)

    def create_and_run_bot(self, username, password, game_speed, headless):
        bot=PockieNinjaSlotMachineFarm(username, password, game_speed, headless=headless)
        self.bots.append(bot)
        check_exit_success=bot.main_loop()
        return check_exit_success

## CREATE SCROLL OPENER GUI
class ScrollOpenerBot(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.create_widgets()
        self.bots=[]
        self.threads=[]

    def create_widgets(self):
        self.username_label=ttk.Label(self, text="Username:")
        self.username_entry=ttk.Entry(self)
        self.password_label=ttk.Label(self, text="Password:")
        self.password_entry=ttk.Entry(self, show="*")
        ## SET DUNGEON LEVEL AS A OPTION MENU
        self.scroll_rank_options=["S-Rank Secret Scroll", "A-Rank Secret Scroll", "B-Rank Secret Scroll", "C-Rank Secret Scroll", "Special Treasure Jar"]
        self.scroll_rank_label=ttk.Label(self, text="Scroll Rank:")
        self.scroll_rank_str_var=tk.StringVar()
        self.scroll_rank_str_var.set(self.scroll_rank_options[0])
        self.scroll_rank_option_menu=tk.OptionMenu(self, self.scroll_rank_str_var , *self.scroll_rank_options)
        ## ADD A CHECKBOX IF YOU WANT TO RUN THE BOT IN HEADLESS MODE
        self.headless_var=tk.IntVar()
        self.headless_label=ttk.Label(self, text="Headless (No Browser):")
        self.headless_checkbox=ttk.Checkbutton(self, variable=self.headless_var)
        self.start_button=ttk.Button(self, text="Start", command=self.on_start_button_click)

        self.username_label.grid(row=0, column=0, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.username_entry.grid(row=0, column=1, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.password_label.grid(row=1, column=0, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.password_entry.grid(row=1, column=1, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.scroll_rank_label.grid(row=2, column=0, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.scroll_rank_option_menu.grid(row=2, column=1, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.headless_label.grid(row=4, column=0, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.headless_checkbox.grid(row=4, column=1, sticky="ew", padx=STANDARD_PADDING_X, pady=STANDARD_PADDING_Y)
        self.start_button.grid(row=5, column=1, columnspan=2, sticky="ew", pady=STANDARD_PADDING_Y)

        if len(ACCOUNT) == 2:
            self.username_entry.insert(0, ACCOUNT[0])
            self.password_entry.insert(0, ACCOUNT[1])

    def on_start_button_click(self):
        new_thread=threading.Thread(target=self.start_bot, daemon=True)
        self.threads.append(new_thread)
        new_thread.start()

    def start_bot(self):
        username=self.username_entry.get()
        password=self.password_entry.get()
        scroll_rank=self.scroll_rank_option_menu.cget("text")
        headless=self.headless_var.get()

        if headless == 1:
            headless=True
        else:
            headless=False

        if username == "" or password == "":
            messagebox.showwarning("Warning", "Please fill all the fields")
        else:
            messagebox.showinfo("Info", "Checking Your Credentials...\nPlease wait for a moment!")
            check_credentials_bot=CheckLoginCredentials(username, password)
            is_invalid, case=check_credentials_bot.check_credentials()
            if is_invalid:
                if case == 'logedin':
                    messagebox.showwarning("Warning", "Invalid Credentials!\nThis account is already logged in!")
                if case == 'password':
                    messagebox.showwarning("Warning", "Invalid Credentials!\nUsername or Password is incorrect!")
                return
            
            messagebox.showinfo("Info", "Valid Credentials!\nStarting Bot!")
            check_exit_success=self.create_and_run_bot(username, password, scroll_rank, headless)
            while not check_exit_success:
                check_exit_success=self.create_and_run_bot(username, password, scroll_rank, headless)
    
    def create_and_run_bot(self, username, password, scroll_rank, headless):
        bot=PockieNinjaScrollOpener(username, password, scroll_rank, headless)
        self.bots.append(bot)
        check_exit_success=bot.main_loop()
        return check_exit_success

def center(toplevel):
    toplevel.update_idletasks()
    # Tkinter way to find the screen resolution
    screen_width=toplevel.winfo_screenwidth()
    screen_height=toplevel.winfo_screenheight()
    size=tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
    x=screen_width/2 - size[0]/2
    y=screen_height/2 - size[1]/2
    toplevel.geometry("+%d+%d" % (x, y))

def rebuild():
    root=tk.Tk()
    app=MainMenu(master=root)
    set_style()
    app.mainloop()

if __name__ == "__main__":
    rebuild()
