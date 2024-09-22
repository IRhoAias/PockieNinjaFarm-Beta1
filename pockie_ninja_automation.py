from playwright.sync_api import sync_playwright, TimeoutError
from datetime import datetime
import time
import requests
from src import *
import random

WINDOW_WAIT_STANDARD_DELAY = 2
ADDITIONAL_SLEEP_TIME = 2

class PockieNinjaFarmBot:
    def relog(self):
        ## OPENING THE LOGIN SCREEN
        self.page.click("div[class='start-button']")
        ## ACCOUNT CREDENTIALS
        self.page.type(f"input[id='username']", self.username)
        self.page.type("input[id='password']", self.password)
        ## LOGIN INTO ACCOUNT
        self.page.get_by_text("Submit").click()
        print("LOGGING INTO ACCOUNT...")
        time.sleep(WINDOW_WAIT_STANDARD_DELAY)
        ## CHECK IF TIMEOUT
        if self.page.get_by_text("Already logged in.").count() > 0:
            print("TIMEOUT DETECTED! RELOADING PAGE AND RELOGGING...")
            self.page.reload()
            self.relog()

        print(f"LOGGED INTO ACCOUNT {self.username}!")
        self.page.get_by_text("Test Server").click()
        print("ENTERED SERVER!")

    def close_interface(self):
        print("CLOSING INTERFACE (CHAT, SETTINGS AND FRIENDS LIST)...")
        time.sleep(WINDOW_WAIT_STANDARD_DELAY)
        if self.flag_first_time:
            ## CLOSING FRIENDS LIST
            if self.page.locator(f"img[{FRIENDS_LIST_MINIZE_BTN}]").count() > 0:
                print("CLOSING FRIENDS LIST...")
                self.page.click(f"img[{FRIENDS_LIST_MINIZE_BTN}]")
            ## CLOSING CHAT
            if self.page.locator(f"img[{CHAT_MINIMIZE_BUTTON}]").count() > 0:
                print("CLOSING CHAT...")
                self.page.click(f"img[{CHAT_MINIMIZE_BUTTON}]")
            ## CLOSING SETTINGS
            if self.page.locator(f"img[{SETTINGS_CLOSE_BUTTON}]").count() > 0:
                print("CLOSING SETTINGS...")
                self.page.click(f"img[{SETTINGS_CLOSE_BUTTON}]")
            self.flag_first_time = False
        print("INTERFACES CLOSED!")

    def close_fight_page(self):
        time.sleep(WINDOW_WAIT_STANDARD_DELAY)
        if self.page.get_by_text("Abandon").count() > 0:
            print("CLOSING FIGHT PAGE (OBS: IT WAS OPEN BEFORE FROM PREVIOUS SESSION)")
            self.page.get_by_text("Abandon").click()
            time.sleep(WINDOW_WAIT_STANDARD_DELAY)
            if self.page.get_by_text("Leave").count() > 0:
                self.page.get_by_text("Leave").click()


################################################################################################################################
################################################################################################################################
class PockieNinjaValhallaBot(PockieNinjaFarmBot):
    def __init__(self, username, password, dungeon_lvl, difficulty, legend_box, game_speed, headless):
        self.dungeon_lvl = dungeon_lvl
        self.difficulty = difficulty
        self.username = username
        self.password = password
        self.headless = headless
        self.game_speed = game_speed
        self.legend_box = legend_box
        self.flag_first_time = True
        self.count_fight = 0
        self.stone = 0
        self.fight_num = ""
        self.castle_menu = ""
        self.begin_btn = ""
        self.battle_select_instance = ""
        self.battle_icon = ""

    def main_loop(self):
        try:
            with sync_playwright() as self.p:
                self.browser = self.p.chromium.launch(headless=self.headless)
                print("OPENED BROWSER")
                self.page = self.browser.new_page()
                time.sleep(1.0)
                self.page.goto("https://pockieninja.online/")
                time.sleep(1.5)
                print("OPENED LINK")
                self.set_dungeon_info()
                print(f"GAME SPEED : {self.game_speed}")
                self.relog()
                while True:
                    self.page.evaluate(JAVASCRIPT_CODE_SH)
                    self.page.evaluate(JAVASCRIPT_SPEED_CONFIG.replace("1.0", self.game_speed))
                    ## PICK CARD AFTER RESET (YES, THIS IS SUPPOSED TO BE HERE, OTHERWISE, IF INTERFACE SHOWS UP BEHING CARDS, I WILL GENERATE AN INFINITE LOOP, THIS IS A QUICK SOLUTION)
                    self.stone = int(self.page.locator('pre').nth(1).text_content())
                    self.pick_card_after_reset()
                    self.close_fight_page()
                    self.close_interface()
                    self.check_if_on_valhalla_camp()
                    time.sleep(WINDOW_WAIT_STANDARD_DELAY)
                    self.start_farm()
        except (Exception) as e:
            print("EXCEPTION: ", e)
            if "Timeout" in str(e):
                print("TimeoutError")
                return False
            else:
                return True

    def set_dungeon_info(self):
        if self.dungeon_lvl == 11:
            self.fight_num = DECADENT_NEST_FIGHT_NUM
            self.castle_menu = DECADENT_NEST_CASTLE_MENU_SRC
            self.difficulty_src = DECADENT_NEST_DIFFICULTY_SRC
            self.begin_btn = BEGIN_BTN_SRC
            self.battle_select_instance = DECADENT_NEST_BATTLE_INSTANCE_SRC
            self.battle_icon = DECADENT_NEST_BATTLE_ICON_SRC
        elif self.dungeon_lvl == 16:
            self.fight_num = VALLHALLA_CAMP_FIGHT_NUM
            self.castle_menu = VALHALLA_CAMP_CASTLE_MENU_SRC
            self.difficulty_src = VALHALLA_CAMP_DIFFICULTY_SRC_SRC
            self.begin_btn = BEGIN_BTN_SRC
            self.battle_select_instance = VALHALLA_CAMP_CAMP_OUTPOST_BATTLE_INSTANCE_SRC
            self.battle_icon = VALHALLA_CAMP_BATTLE_ICON_SRC

    ## CHECK IF ON CORRECT VAHALLA CAMP, IF NOT, ENTER THE CORRECT PAGE
    def check_if_on_valhalla_camp(self):
        if self.page.locator(f"img[{VALHALLA_BG_SRC}]").count() == 0:
            print("NOT ON VALHALLA CAMP! REDIRECTING TO CORRECT PAGE...")
            self.page.get_by_text("World Map").click()
            map_canva_box = self.page.locator("div[id='map']").bounding_box()
            time.sleep(WINDOW_WAIT_STANDARD_DELAY*3)
            i = 0
            for i in range(int(round(map_canva_box["y"])), int(round(map_canva_box["y"] + map_canva_box["height"]*DEMON_CITY_HEIGHT_MULTIPLIER)), 2):
                self.page.mouse.move(map_canva_box["x"] + map_canva_box["width"]/2, i)
            self.page.mouse.click(map_canva_box["x"] + map_canva_box["width"]/2, i)
            time.sleep(WINDOW_WAIT_STANDARD_DELAY)
            valhalla_encampment = self.page.locator(f"img[{VALLHALLA_ENCAMPMENT}]").bounding_box()
            i = 0
            for i in range(int(round(valhalla_encampment["y"])), int(round(valhalla_encampment["y"] + valhalla_encampment["height"]/2)), 2):
                self.page.mouse.move(valhalla_encampment["x"] + valhalla_encampment["width"]/2, i)
            print("ENTERING VALHALLA...")
            self.page.mouse.click(valhalla_encampment["x"] + valhalla_encampment["width"]/2, i)
            self.page.get_by_text("Enter Valhalla").click()

    def pick_card_after_reset(self):
        time.sleep(WINDOW_WAIT_STANDARD_DELAY*3)
        if self.page.locator(f"img[{CARD_IMG_SRC}]").count() > 0:
            print("PICKING LEFTOVER CARDS (OBS: LEFT FROM PREVIOUS SESSION)")

            if self.legend_box and self.difficulty_src != NORMAL_VALHALLA_DIFFICULTY and self.dungeon_lvl < 16:
                self.legend_box = False
                print("You need to take at least dungeon level 16 and normal difficulty.")

            if self.legend_box and self.stone < VALHALLA_LEGEND_BOX_MINIMUM_STONE:
                self.legend_box = False
                print("Your stone is less than 50k")

            if self.legend_box and self.stone >= VALHALLA_LEGEND_BOX_MINIMUM_STONE:
                for card in range(5):
                    self.page.get_by_text("Look").nth(0).click()
                    time.sleep(0.5)
                    self.page.get_by_text("Accept").click()
                    time.sleep(1)

                    if self.page.locator(f"img[{VALHALLA_LEGEND_BOX_SRC}]").count() > 0:
                        self.page.locator(f"img[{CARD_IMG_SRC}]").locator('..').nth(card).click(position={"x": 15, "y": 15})
                        time.sleep(WINDOW_WAIT_STANDARD_DELAY)
                        self.page.get_by_text("Collect").nth(0).click()
                        print("You get legend box set")
                        return

            self.page.locator(f"img[{CARD_IMG_SRC}]").locator('..').nth(0).click(position={"x": 15, "y": 15})
            time.sleep(WINDOW_WAIT_STANDARD_DELAY)
            self.page.get_by_text("Collect").nth(0).click()

    def open_valhalla(self):
        castle = self.page.locator(f"img[{self.castle_menu}]").bounding_box()
        j = 0
        for j in range(int(round(castle["y"], 0)), int(round(castle["y"]+castle["height"]/2)), 2):
            self.page.mouse.move(castle["x"] + castle["width"]/2, j)
            
        self.page.mouse.click(castle["x"] + castle["width"]/2, j)

    def start_farm(self):
        self.cancel_first_fight()
        for i in range(0, self.fight_num):
            print("ITERATION NUMBER: ", i+1, " OUT OF ", self.fight_num, " FIGHTS")
            if self.dungeon_lvl == 11:
                print("ENTERED DUNGEON LVL. 11")
                self.cancel_subsequent_fights(nth_element=self.count_fight)
                self.count_fight += 1
            elif self.dungeon_lvl == 16:
                print("ENTERED DUNGEON LVL. 16")
                if self.count_fight < 5:
                    self.cancel_subsequent_fights(nth_element=self.count_fight)
                    self.count_fight += 1
                else:
                    self.battle_select_instance = VALHALLA_CAMP_PANTHEON_ENTRANCE_BATTLE_INSTANCE_SRC
                    self.cancel_subsequent_fights(nth_element=self.count_fight-(self.fight_num/2))
                    self.count_fight += 1
        # RESET DUNGEON INFO TO ORIGINAL VALUES
        self.set_dungeon_info()
        self.count_fight = 0
        self.page.reload()
        print("ALL FIGHTS DONE!")

    def cancel_first_fight(self):
        print("CANCELLING FIRST FIGHT...")
        ## CLICKING INTO VALLHALLA TEMPLE IMAGE --> I HAVE TO BRUSH THE WHOLE AREA TO FIND THE IMAGE (HOVER OVER IT)
        self.open_valhalla()
        try:
            if self.difficulty == NORMAL_VALHALLA_DIFFICULTY:
                self.page.locator(f"img[{self.difficulty_src}]").nth(0).click()
            else:
                self.page.locator(f"img[{self.difficulty_src}]").nth(-1).click()
            self.page.click(f"img[{self.begin_btn}]")
        except:
            print(f"ALREADY MIDFARM... COULD NOT FIND DIFFICULTY, STARTING NEW FARM WITH PREVIOUS DIFFICULTY == {self.difficulty}...")

    def cancel_subsequent_fights(self, nth_element):
        print("CANCELLING SUBSEQUENT FIGHTS...")
        max_tries = MAX_TRIES
        try_count = 0
        ## SELECTING INSTANCE
        if (nth_element == 0):
            self.page.click(f"img[{self.battle_select_instance}]")
        print("ENTERING BATTLE...") 
        ## ENTERING BATTLE
        time.sleep(WINDOW_WAIT_STANDARD_DELAY)
        nth_instance = self.page.locator(f"img[{self.battle_icon}]")
        nth_instance.nth(nth_element).click()
        while (try_count < max_tries):
            if (self.page.get_by_role("button", name="Close").count() > 0):
                self.page.get_by_role("button", name="Close").click()
                break
            time.sleep(WINDOW_WAIT_STANDARD_DELAY*2)
            try_count += 1
        if(try_count >= max_tries):
            print("MAX WAITING TIME EXCEEDED...")
            self.page.close()
        time.sleep(WINDOW_WAIT_STANDARD_DELAY*2)
        
    def click_card(self):
        max_tries = MAX_TRIES
        try_count = 0
        print("WAITING FOR THE CARD TO APPEAR...")
        while (try_count < max_tries):
            if (self.page.locator(f"img[{CARD_IMG_SRC}]").count() > 0):
                break
            time.sleep(WINDOW_WAIT_STANDARD_DELAY)
            try_count += 1
        print("CLICKING ON THE CARD...")
        card_element = self.page.locator(f"img[{CARD_IMG_SRC}]")
        card_element.nth(-1).click()
        time.sleep(WINDOW_WAIT_STANDARD_DELAY)
        self.page.get_by_text("Collect").click()
        print("CARDS COLLECTED!")


################################################################################################################################
################################################################################################################################
class PockieNinjaStandardAreaFarm(PockieNinjaFarmBot):
    def __init__(self, username, password, area_name, mob_name, game_speed, headless):
        self.username = username
        self.password = password
        self.game_speed = game_speed
        self.headless = headless
        self.flag_first_time = True
        self.count_fight = 0
        self.win_fight = 0
        self.start_farm_time = ""
        self.start_fight_time = ""
        self.area_name = area_name
        self.mob_name = mob_name
        self.mob_to_farm = ""
        self.set_src_variables()

    def set_src_variables(self):
        if self.area_name == SMELTING_MOUNTAINS_AREA_NAME:
            self.width_multiplier = SMELTING_MOUNTAINS_WIDTH_MULTIPLIER
            self.height_multiplier = SMELTING_MOUNTAINS_HEIGHT_MULTIPLIER
            self.bg_src = SMELTING_MOUNTAINS_BG_SRC
            self.mob_0_icon_src = SUNFLOWER_ICON_SRC
            self.mob_1_icon_src = BEE_ICON_SRC
            self.mob_2_icon_src = SUSHI_ICON_SRC
            self.mob_3_icon_src = SCARLET_ICON_SRC
            self.mob_4_icon_src = WARRIOR_OF_DARKNESS_ICON_SRC
            self.mob_5_icon_src = DEMON_BRUTE_ICON_SRC
            self.mob_0_name = SUNFLOWER_NAME
            self.mob_1_name = BEE_NAME
            self.mob_2_name = SUSHI_NAME
            self.mob_3_name = SCARLET_NAME
            self.mob_4_name = WARRIOR_OF_DARKNESS_NAME
            self.mob_5_name = DEMON_BRUTE_NAME
            self.boss_ticket = BOSS_TICKET_PNG
            self.boss_lvl = 10
            
        elif self.area_name == EVENTIDE_BARRENS_AREA_NAME:
            self.width_multiplier = EVENTIDE_BARRENS_WIDTH_MULTIPLIER
            self.height_multiplier = EVENTIDE_BARRENS_HEIGHT_MULTIPLIER
            self.bg_src = EVENTIDE_BARRENS_BG_SRC
            self.mob_0_icon_src = POTATO_ICON_SRC
            self.mob_1_icon_src = MONKEY_ICON_SRC
            self.mob_2_icon_src = MEAL_ICON_SRC
            self.mob_3_icon_src = KAPPA_ICON_SRC
            self.mob_4_icon_src = BULLHEAD_ICON_SRC
            self.mob_5_icon_src = PLAGUE_DEMON_ICON_SRC
            self.mob_0_name = POTATO_NAME
            self.mob_1_name = MONKEY_NAME
            self.mob_2_name = MEAL_NAME
            self.mob_3_name = KAPPA_NAME
            self.mob_4_name = BULLHEAD_NAME
            self.mob_5_name = PLAGUE_DEMON_NAME
            self.boss_ticket = BOSS_TICKET_PNG
            self.boss_lvl = 20
        
        elif self.area_name == CROSSROADS_AREA_NAME:
            self.width_multiplier = CROSSROADS_WIDTH_MULTIPLIER
            self.height_multiplier = CROSSROADS_HEIGHT_MULTIPLIER
            self.bg_src = CROSSROADS_BG_SRC
            self.mob_0_icon_src = TREE_ENT_ICON_SRC
            self.mob_1_icon_src = MAN_EATER_ICON_SRC
            self.mob_2_icon_src = LONGFEATHER_DEMON_ICON_SRC
            self.mob_3_icon_src = CHEVALIER_DEMON_ICON_SRC
            self.mob_4_icon_src = SHADOW_BAT_ICON_SRC
            self.mob_5_icon_src = SOULENDER_ICON_SRC
            self.mob_0_name = TREE_ENT_NAME
            self.mob_1_name = MAN_EATER_NAME
            self.mob_2_name = LONGFEATHER_DEMON_NAME
            self.mob_3_name = CHEVALIER_DEMON_NAME
            self.mob_4_name = SHADOW_BAT_NAME
            self.mob_5_name = SOULENDER_NAME
            self.boss_ticket = BOSS_TICKET_PNG
            self.boss_lvl = 25

    def main_loop(self):
        try:
            with sync_playwright() as self.p:
                self.browser = self.p.chromium.launch(headless=self.headless)
                print("OPENED BROWSER")
                self.page = self.browser.new_page()
                time.sleep(1.0)
                self.page.goto("https://pockieninja.online/")
                time.sleep(1.5)
                self.page.evaluate(JAVASCRIPT_CODE_SH)
                print("OPENED LINK")
                self.page.evaluate(JAVASCRIPT_SPEED_CONFIG.replace("1.0", self.game_speed))
                print(f"GAME SPEED : {self.game_speed}")
                self.relog()
                self.set_farm_info()
                self.close_fight_page()
                self.close_interface()
                self.check_if_on_smelting_mountais_camp()
                self.start_farm_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                while True:
                    time.sleep(WINDOW_WAIT_STANDARD_DELAY)
                    self.start_farm()
                    self.count_fight += 1
                    print(f"FIGHT NUMBER: {self.count_fight} ({self.win_fight} WIN)")
                    self.calculate_fight_time()
                    self.calculate_total_time()
        except (Exception) as e:
            print("EXCEPTION: ", e)
            if "Timeout" in str(e):
                print("TimeoutError")
                return False
            else:
                return True

    def check_if_on_smelting_mountais_camp(self):
        if self.page.locator(f"img[{self.bg_src}]").count() == 0:
            print("NOT ON SMELTING MOUNTAINS CAMP! REDIRECTING TO CORRECT PAGE...")
            self.page.get_by_text("World Map").click()
            map_canva_box = self.page.locator("div[id='map']").bounding_box()
            time.sleep(WINDOW_WAIT_STANDARD_DELAY*3)
            i = 0
            for i in range(int(round(map_canva_box["x"])), int(round(map_canva_box["x"] + map_canva_box["width"]*self.width_multiplier)), 2):
                self.page.mouse.move(i, map_canva_box["y"] + (map_canva_box["height"]*self.height_multiplier))
            print("ENTERING SMELTING MOUNTAINS...")
            self.page.mouse.click(i, map_canva_box["y"] + (map_canva_box["height"]*self.height_multiplier))
                 
    def set_farm_info(self):
        if self.mob_name == self.mob_0_name:
            self.mob_to_farm = self.mob_0_icon_src
        elif self.mob_name == self.mob_1_name:
            self.mob_to_farm = self.mob_1_icon_src
        elif self.mob_name == self.mob_2_name:
            self.mob_to_farm = self.mob_2_icon_src
        elif self.mob_name == self.mob_3_name:
            self.mob_to_farm = self.mob_3_icon_src
        elif self.mob_name == self.mob_4_name:
            self.mob_to_farm = self.mob_4_icon_src
        elif self.mob_name == self.mob_5_name:
            self.mob_to_farm = self.mob_5_icon_src

    def boss_farm(self):
        flag_has_ticket = False
        self.start_fight_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ## OPENING PLAYER BAG
        self.page.locator(f"img[{PLAYER_BAG}]").click()
        for bag_slot in range(MAX_BAG_SLOTS): ## BAG SLOTS SET TO 12 BECAUSE THERE ARE 2 BUTTONS IN THE BAG INTERFACE THAT HAVE NO CORRELATION WITH BAG SLOTS (WE WILL SKIP THEM)
            if bag_slot < 2: ## IGNORING FIRST 2 BUTTONS THAT HAVE NOTHING TO DO WITH BAG SLOTS
                pass
            else:
                if self.page.locator(f"img[{self.boss_ticket}]").count() > 0:
                    flag_has_ticket = True
                    break
        if not flag_has_ticket:
            print("PLAYER HAS NO BOSS TICKETS FOR THIS AREA... FINISHING MACRO...")
            self.page.close()

        num_ticket_images = self.page.locator(f"img[{self.boss_ticket}]").count()
        for index, img in enumerate(num_ticket_images):
            self.page.locator(f"img[{self.boss_ticket}]").nth(index).hover()
            if self.page.locator("Boss Ticket Lv. {self.boss_lvl}").count() > 0:
                break

    def start_farm(self):
        ## CHECK IF MOB TO FARM IS A BOSS:
        if "BOSS" in self.mob_name:
            self.boss_farm()
        else:
            self.page.locator(f"img[{self.mob_to_farm}]").click()
            self.start_fight_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ## CHECK IF CANVAS BATLLE STILL OPEN
            while True:
                if self.page.get_by_text("Close").count() > 0:
                    time.sleep(WINDOW_WAIT_STANDARD_DELAY)
                    char_hp = self.page.locator("div[class='fight__stat-value']").nth(0).text_content()
                    if int(char_hp.split(" ")[0]) > 0:
                        self.win_fight += 1
                    self.page.get_by_text("Close").click()
                    break
    
    def calculate_fight_time(self):
        started_fight_time = datetime.strptime(self.start_fight_time, "%Y-%m-%d %H:%M:%S")
        completed_fight_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        delta = datetime.strptime(completed_fight_time, "%Y-%m-%d %H:%M:%S") - started_fight_time
        total_seconds = delta.total_seconds()
        
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)

        minutes = f"{minutes:02}"
        seconds = f"{seconds:02}"

        print(f"FIGHT COMPLETED IN {minutes}:{seconds}")
    
    def calculate_total_time(self):
        started_farm_time = datetime.strptime(self.start_farm_time, "%Y-%m-%d %H:%M:%S")
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        delta = datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S") - started_farm_time
        total_seconds = delta.total_seconds()

        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)

        hours = f"{hours:02}"
        minutes = f"{minutes:02}"
        seconds = f"{seconds:02}"

        print(f"FARM RUNNING FOR {hours}:{minutes}:{seconds} ({datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S').time()})")

################################################################################################################################
class PockieNinjaSlotMachineFarm(PockieNinjaFarmBot):
    def __init__(self, username, password, game_speed, headless):
        self.username = username
        self.password = password
        self.game_speed = game_speed
        self.headless = headless
        self.flag_first_time = True
        self.count_fight = 0
        self.win_fight = 0
        self.start_farm_time = ""
        self.start_fight_time = ""
        self.area_name = CROSSROADS_AREA_NAME
        self.set_src_variables()

    def set_src_variables(self):
        self.width_multiplier = CROSSROADS_WIDTH_MULTIPLIER
        self.height_multiplier = CROSSROADS_HEIGHT_MULTIPLIER
        self.bg_src = CROSSROADS_BG_SRC

    def main_loop(self):
        try:
            with sync_playwright() as self.p:
                self.browser = self.p.chromium.launch(headless=self.headless)
                print("OPENED BROWSER")
                self.page = self.browser.new_page()
                time.sleep(1.0)
                self.page.goto("https://pockieninja.online/")
                time.sleep(1.5)
                print("OPENED LINK")
                print(f"GAME SPEED : {self.game_speed}")
                self.page.evaluate(JAVASCRIPT_CODE_SH)
                self.relog()
                self.close_fight_page()
                self.close_interface()
                self.check_if_on_cross_road()
                print("START FIGHT")
                self.start_farm_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                while True:
                    self.start_farm()
        except (Exception) as e:
            print("EXCEPTION: ", e)
            if "Timeout" in str(e):
                print("TimeoutError")
                return False
            else:
                return False

    def check_if_on_cross_road(self):
        if self.page.locator(f"img[{self.bg_src}]").count() == 0:
            print("NOT ON CROSS ROAD! REDIRECTING TO CORRECT PAGE...")
            self.page.get_by_text("World Map").click()
            map_canva_box = self.page.locator("div[id='map']").bounding_box()
            time.sleep(WINDOW_WAIT_STANDARD_DELAY*3)
            i = 0
            for i in range(int(round(map_canva_box["x"])), int(round(map_canva_box["x"] + map_canva_box["width"]*self.width_multiplier)), 2):
                self.page.mouse.move(i, map_canva_box["y"] + (map_canva_box["height"]*self.height_multiplier))
            print("ENTERING CROSS ROAD...")
            self.page.mouse.click(i, map_canva_box["y"] + (map_canva_box["height"]*self.height_multiplier))
    
    def calculate_fight_time(self):
        started_fight_time = datetime.strptime(self.start_fight_time, "%Y-%m-%d %H:%M:%S")
        completed_fight_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        delta = datetime.strptime(completed_fight_time, "%Y-%m-%d %H:%M:%S") - started_fight_time
        total_seconds = delta.total_seconds()
        
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)

        minutes = f"{minutes:02}"
        seconds = f"{seconds:02}"

        print(f"FIGHT COMPLETED IN {minutes}:{seconds}")
    
    def calculate_total_time(self):
        started_farm_time = datetime.strptime(self.start_farm_time, "%Y-%m-%d %H:%M:%S")
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        delta = datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S") - started_farm_time
        total_seconds = delta.total_seconds()

        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)

        hours = f"{hours:02}"
        minutes = f"{minutes:02}"
        seconds = f"{seconds:02}"

        print(f"FARM RUNNING FOR {hours}:{minutes}:{seconds} ({datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S').time()})")

    def start_farm(self):
        max_tries = MAX_SLOT_MACHINE_TRIES
        try_count = 0
        wait_time_multiplier = round(random.uniform(1,1.5),2)

        ## CHECK IF SLOT MACHINE STILL OPEN
        if self.page.locator(f"img[{SLOT_MACHINE_FRAME_OPEN}]").count() == 0:
            self.page.evaluate('''
            const element = document.querySelector("img[src='https://pockie-ninja-assets.sfo3.cdn.digitaloceanspaces.com/pockie-ninja-assets/public/ui/SlotMachine/icon.png']");
            const rect = element.getBoundingClientRect();
            element.click(rect.left + 10, rect.top + 16);
            ''')
 
        self.page.locator(f"img[{SLOT_MACHINE_CHALLENGE_BTN_SRC}]").locator('..').click()
        self.start_fight_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        time.sleep(WINDOW_WAIT_STANDARD_DELAY)
        self.page.evaluate(JAVASCRIPT_SPEED_CONFIG.replace("1.0", self.game_speed))
        ## CHECK IF CANVAS BATLLE STILL OPEN
        while (try_count < max_tries):
            if (self.page.get_by_role("button", name="Close").count() > 0):
                self.page.evaluate(JAVASCRIPT_SPEED_CONFIG)
                char_hp = self.page.locator("div[class='fight__stat-value']").nth(0).text_content()
                if int(char_hp.split(" ")[0]) > 0:
                    self.win_fight += 1
                self.page.get_by_role("button", name="Close").click()
                wait_time_multiplier / 0.5
                self.count_fight += 1
                print(f"FIGHT NUMBER: {self.count_fight}  ({self.win_fight} WIN)")
                self.calculate_fight_time()
                self.calculate_total_time()
                break
            time.sleep(WINDOW_WAIT_STANDARD_DELAY*wait_time_multiplier)
            try_count += 1
            wait_time_multiplier = round(random.uniform(1,1.5),2)
        if(try_count >= max_tries):
            print("MAX WAITING TIME EXCEEDED...")
            self.page.close()
        time.sleep(WINDOW_WAIT_STANDARD_DELAY*wait_time_multiplier)
        

################################################################################################################################
class PockieNinjaScrollOpener(PockieNinjaFarmBot):
    def __init__(self, username, password, scroll_rank, headless):
        self.username = username
        self.password = password
        self.headless = headless
        self.scroll_rank = scroll_rank
        self.total_scroll = 0
        self.tries = 0
        self.obtained_item = ""
        self.flag_first_time = True

        if self.scroll_rank == "C-Rank Secret Scroll":
            self.scroll_src = C_RANK_SCROL_SRC
        elif self.scroll_rank == "B-Rank Secret Scroll":
            self.scroll_src = B_RANK_SCROL_SRC
        elif self.scroll_rank == "A-Rank Secret Scroll":
            self.scroll_src = A_RANK_SCROL_SRC
        elif self.scroll_rank == "S-Rank Secret Scroll":
            self.scroll_src = S_RANK_SCROLL_SRC
        elif self.scroll_rank == "Special Treasure Jar":
            self.scroll_src = SPECIAL_TREASURE_JAR_SRC

    def main_loop(self):
        try:
            with sync_playwright() as self.p:
                self.browser = self.p.chromium.launch(headless=self.headless)
                print("OPENED BROWSER")
                self.page = self.browser.new_page()
                time.sleep(1.0)
                self.page.goto("https://pockieninja.online/")
                time.sleep(1.5)
                print("OPENED LINK")
                self.relog()
                self.close_fight_page()
                self.close_interface()
                self.start_opening_scroll()
                return True
        except (Exception) as e:
            print("EXCEPTION: ", e)
            if "Timeout" in str(e):
                print("TimeoutError")
                return False
            else:
                return True

    def start_opening_scroll(self):
        ## CHECK IF BAG IS OPEN
        if self.page.get_by_text("Inventory").count() == 0:
            self.page.locator(f"img[{BAG_ICON_SRC}]").click()      

        ## CHECK IF SCROLL STILL EXISTS
        while True:
            if self.page.locator(f"img[{self.scroll_src}]").count() > 0:
                if self.page.locator(f"img[{self.scroll_src}]").locator("..").get_by_text("x").count() == 0:
                    print(f"You only have 1 {self.scroll_rank} Rank Scroll left.")
                    break
                else:
                    self.total_scroll = int(self.page.locator(f"img[{self.scroll_src}]").locator("..").get_by_text("x").text_content().replace("x",""))
                    if (self.page.get_by_role("button", name="Close").count() > 0):
                        self.obtained_item = self.page.get_by_text("You obtained").text_content()
                        self.page.get_by_role("button", name="Close").click()
                    self.page.locator(f"img[{self.scroll_src}]").locator("..").click(button="right")
                    time.sleep(0.2)
                    self.page.get_by_text("Use", exact=True).click()
                    time.sleep(0.4)
                    self.tries += 1
                    if self.page.locator(f"img[{self.scroll_src}]").locator("..").get_by_text("x").count() == 0:
                        print(f"You only have 1 {self.scroll_rank} Rank Scroll left.")
                        break
                    current_scroll = int(self.page.locator(f"img[{self.scroll_src}]").locator("..").get_by_text("x").text_content().replace("x",""))
                    if current_scroll < self.total_scroll:
                        print(f"Scroll {self.scroll_rank} in bag : {current_scroll} (x{self.tries}) [{self.obtained_item}]")
                        self.tries = 0

            if self.page.locator(f"img[{self.scroll_src}]").count() == 0:
                print(f"All {self.scroll_rank} Scroll Opened")
                print(f"Closing the browsers.")
                self.page.close()
                break 

################################################################################################################################
################################################################################################################################
class CheckLoginCredentials:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.flag_wrong_credentials = False
    
    def check_credentials(self):
        case = 0
        url = 'https://pockieninja.online/api/login'
        credential_data = {
            "username": self.username,
            "password": self.password
        }

        login = requests.post(url, json = credential_data)
        result = login.json()
        if 'error' in result:
            self.flag_wrong_credentials = True
            case = "password"

        return self.flag_wrong_credentials, case
