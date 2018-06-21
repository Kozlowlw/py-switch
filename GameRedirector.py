"""
Script for swapping games between a storage location and the donor title location.
Basic LayeredFS stuff.

If you are not a dev, keep to editing stuff in the comments below. Or you will probably break something.
I'll keep an eye on pull requests if anyone is updating functionality.
"""
import functools
import os
import shutil
import sys
import time

from nx.utils import AnsiMenu as Menu
from nx.utils import clear_terminal as clr

# PyNX FIX YOUR ****, I shouldn't need to append a path to sys to get the library >.>
sys.path.append(os.path.abspath('/switch/PyNX/lib/python3.5/'))
import configparser

print = functools.partial(print, flush=True)  # Just a macro, we always need to flush... so do it?

MENU_SEP = '============================'  # Menu seperator
MAIN_OPTIONS = ['Select Donor Title', 'Select Game Folder', 'Put Game In Donor', 'Put Game In Donor [Edit NPDM]',
                'Put Donor Game Back', 'Put All Games Back', MENU_SEP, 'Show Config', MENU_SEP, 'Exit']

MENU_SIGN = """  
____   _   _   _ ___   ____ ___ ___  ___  ____ ___ ________ ____ ____  
).-._( )_\ ) \_/ ) __( /  _ ) __\   \)_ _(/  _ ) __/ _)__ __/ __ /  _ \ 
|( ,-./( )\|  _  | _)  )  ' | _)| ) (_| |_)  ' | _)))_  | | ))__()  ' / 
)_`__)_/ \_)_( )_)___( |_()_)___/___)_____|_()_)___\__( )_( \____|_()_\ 

"""


def clear():
    """
    Clears out the terminal screen and prints the menu sign at the top
    """
    clr()
    sys.stdout.buffer.write(b'Hello')  # We just need to write to the buffer, doesn't matter what for it to clear.
    sys.stdout.flush()
    print(MENU_SIGN)


def countdown():
    """
    Simple countdown because if not we would never read whats on the screen..
    """
    print("Returning to main menu in 5 seconds.")
    for i in range(5):
        print("{}...".format(5 - i))
        time.sleep(1)
    clear()


def move(src, dst):
    """
    Macro move, so I don't need to encapsulate so much in try:excepts
    """
    try:
        shutil.move(src, dst)
    except OSError:
        pass


class Manager(object):
    def __init__(self):
        self.CONFIG_PATH = '/switch/games/config.ini'
        self.DEFAULT_DONOR_DICT = {
            'hulu': '0100A66003384000',
            'paccman vs': '0100BA3003B70000',
            'blazblue': '0100C6E00AF2C000',
            'pokémon quest': '01005D100807A000',
            'pinball fx3': '0100DB7003828000',
            'pic-a-pix deluxe demo': '01006E30099B8000',
            'octopath demo': '010096000B3EA000',
            'fortnite': '010025400AECE000',
            'the pinball arcade': '0100CD300880E000',
            'kitten squad': '01000C900A136000',
            'stern pinball arcade': '0100AE0006474000',
            'pixeljunk monsters 2 demo': '01004AF00A772000',
            'fallout shelter': '010043500A17A000'
        }
        # Oi. Pycharm yells if I don't declare them. Blame the IDE.
        self.games_path = None
        self.donor_path = None
        self.npdm_file = None
        self.romfs = None
        self.exefs = None
        self.donor_titles = None
        self.selected_donor = None
        self.selected_game = None

    def set_game(self, game_name):
        """
        Sets the selected game
        :param game_name:
        :return:
        """
        if game_name is not None:
            if os.path.exists(self.games_path + game_name):
                self.selected_game = game_name
                return True
            return False
        self.selected_game = None

    def set_donor(self, title):
        """
        Sets the selected donor
        :param title:
        :return:
        """
        if title is not None:
            for donor in self.donor_titles:
                if donor == title:
                    self.selected_donor = donor
                    return True
            return False
        self.selected_donor = None
        return True

    def get_donor_title_id(self, title):
        """
        Returns the title id for a given title in config.ini
        :param title:
        :return:
        """
        for option in config.options('DONOR TITLES'):
            if option == title:
                return config.get('DONOR TITLES', option)

    def get_donor_used_by(self, title):
        """
        Returns the game currently being used by a donor in config.ini
        :param title:
        :return:
        """
        for option in config.options('DONORS USED'):
            if option == title:
                return config.get('DONORS USED', option)

    def set_donor_used_by(self, title, game_name):
        """
        Updateds the donor in config.ini to be the selected game
        :param title:
        :param game_name:
        :return:
        """
        for option in config.options('DONORS USED'):
            if option == title:
                if game_name is None:
                    config.set('DONORS USED', option, 'None')
                else:
                    config.set('DONORS USED', option, game_name)
                self.write_config()

    def generate_config(self):
        """
        Generates a new config
        :return:
        """
        config.add_section('COMMON')
        config.set('COMMON', 'romfs', '/RomFs/')
        config.set('COMMON', 'exefs', '/ExeFs/')
        config.set('COMMON', 'games path', '/switch/games/')
        config.set('COMMON', 'donor path', '/atmosphere/titles/')
        config.set('COMMON', 'npdm file', 'main.npdm')
        config.add_section('DONOR TITLES')
        config.add_section('DONORS USED')
        for key, val in self.DEFAULT_DONOR_DICT.items():
            config.set('DONOR TITLES', key, val)
            config.set('DONORS USED', key, 'None')
        self.write_config()

    def read_config(self):
        """
        Reads in the current config
        :return:
        """
        config.read(self.CONFIG_PATH)
        self.games_path = config.get('COMMON', 'games path')
        self.donor_path = config.get('COMMON', 'donor path')
        self.romfs = config.get('COMMON', 'romfs')
        self.exefs = config.get('COMMON', 'exefs')
        self.npdm_file = config.get('COMMON', 'npdm file')
        # We can get the rest of the information if we know the titles, no need to pull them
        self.donor_titles = config.options('DONOR TITLES')

    def write_config(self):
        """
        Writes to the config file
        :return:
        """
        with open(self.CONFIG_PATH, 'w') as conf_file:
            config.write(conf_file)

    def move_to_donor(self):
        """
        Moves the selected game to the selected donor
        :return:
        """
        donor_id = self.get_donor_title_id(self.selected_donor)
        if not os.path.exists(self.donor_path + donor_id):
            src = self.games_path + self.selected_game
            dst = self.donor_path + donor_id
            print("Moving {0} to {1}...".format(self.selected_game, self.selected_donor))
            print("Moving romfs...")
            move(src + self.romfs, dst + self.romfs)
            print("Moving exefs...")
            move(src + self.exefs, dst + self.exefs)
            print("Success!")
            print("Removing extras...")
            if os.path.exists(src + self.romfs):
                shutil.rmtree(src + self.romfs)
            if os.path.exists(src + self.exefs):
                shutil.rmtree(src + self.exefs)
            print("Success!")
            print("Updating config.ini...")
            self.set_donor_used_by(self.selected_donor, self.selected_game)
            self.write_config()
            print("Success!")
            return True
        return False

    def move_to_games(self, specific_donor=None):
        """
        Moves the current game being used by the donor to the games storage location
        :param specific_donor:
        :return:
        """
        if specific_donor is None:
            donor_id = self.get_donor_title_id(self.selected_donor)
            game_using = self.get_donor_used_by(self.selected_donor)
        else:
            donor_id = self.get_donor_title_id(specific_donor)
            game_using = self.get_donor_used_by(specific_donor)
        if os.path.exists(self.donor_path + donor_id):
            src = self.donor_path + donor_id
            dst = self.games_path + game_using
            print("Moving game from {0} to {1}".format(self.selected_donor, game_using))
            print("Moving romfs...")
            move(src + self.romfs, dst + self.romfs)
            print("Moving exefs...")
            move(src + self.exefs, dst + self.exefs)
            print("Success!")
            print("Removing extras...")
            if os.path.exists(src):
                shutil.rmtree(src)
            print("Success!")
            print("Updating config.ini...")
            if specific_donor is None:
                self.set_donor_used_by(self.selected_donor, None)
            else:
                self.set_donor_used_by(specific_donor, None)
            self.write_config()
            print("Success!")
            return True
        return False

    def swap_currently_selected(self):
        """
        Swap the selected game into the donor and moves out the currently used game if it is found
        :return:
        """
        self.read_config()
        if self.selected_donor is None:
            print("Select a donor first")
            countdown()
            return False
        if self.selected_game is None:
            print("Select a game first")
            countdown()
            return False
        if self.get_donor_used_by(self.selected_donor) != 'None':
            if self.move_to_games():
                pass
            else:
                print('move_to_games() Failed!')
                return False
        if self.move_to_donor():
            pass
        else:
            print('move_to_donor() Failed!')
            return False
        countdown()
        return True

    def move_all_to_games(self):
        """
        Iterates through the donors and moves all games back to the games directory
        :return:
        """
        for donor in self.donor_titles:
            print("Moving files from {0} to {1}".format(donor, self.get_donor_used_by(donor)))
            if self.move_to_games(specific_donor=donor):
                print("Success!")

    def edit_npdm(self):
        """
        Edits the NPDM of the selected game to match the selected donor
        :return:
        """
        if not os.path.exists(self.games_path + self.selected_game + self.exefs + self.npdm_file + '.bak'):
            print("Backing up NPDM...")
            try:
                shutil.copy2(self.games_path + self.selected_game + self.exefs + self.npdm_file,
                             self.games_path + self.selected_game + self.exefs + self.npdm_file + '.bak')
            except OSError:
                pass
            print("Success!")
        print("Editing {0}'s npdm for {1}".format(self.selected_game, self.selected_donor))
        with open(self.games_path + self.selected_game + self.exefs + self.npdm_file, 'r+b') as npdm:
            donor_id = self.get_donor_title_id(self.selected_donor)
            donor_id_flipped = "".join(reversed([donor_id[i:i + 2] for i in range(0, len(donor_id), 2)]))
            donor_id = bytearray.fromhex(donor_id_flipped)
            content = bytearray(npdm.read())
            tid_offset = content.find(b'ACI0') + 0x10
            tid_length = 0x8
            content[tid_offset:tid_offset + tid_length] = donor_id
            npdm.seek(0)
            npdm.write(content)
        print("Success!")
        return True

    def to_strings(self):
        """
        Creates the list of strings from the show config menu
        :return:
        """
        lines = ["-> Press any option to return to main menu"]
        lines.append(MENU_SEP)
        lines.append("[COMMON]")
        for option in config.options('COMMON'):
            lines.append("{0} = {1}".format(option, config.get('COMMON', option)))
        lines.append("")
        lines.append("[DONOR TITLES]")
        for option in config.options('DONOR TITLES'):
            lines.append("{0} = {1}".format(option, config.get('DONOR TITLES', option)))
        lines.append("")
        lines.append("[DONORS USED]")
        for option in config.options('DONORS USED'):
            lines.append("{0} is currently being used by {1}".format(option, config.get('DONORS USED', option)))
        lines.append("")
        lines.append(MENU_SEP)
        lines.append("-> Press any option to return to main menu")
        return lines


def menu_creator(list_of_strings, action=None, break_after_action=True, break_if_selected_is=-1):
    """
    Creates an AnsiMenu with the given list_of_strings with some extra options
    :param list_of_strings:
    :param action:
    :param break_after_action:
    :param break_if_selected_is:
    :return:
    """
    clear()
    while True:
        selected = None
        menu_me = Menu(list_of_strings)
        selected = menu_me.query()
        if selected is not None:
            clear()
            if action is not None:
                action(selected)
            if break_after_action or break_if_selected_is == selected:
                break


def donor_menu():
    """
    Creates the 'Select Donor Title' menu
    :return:
    """
    menu_creator(manager.donor_titles, action=donor_menu_action)


def donor_menu_action(selected):
    """
    'Select Donor Title' action for use with the menu creator
    :param selected:
    :return:
    """
    manager.set_donor(manager.donor_titles[selected])
    print("selected {}".format(manager.donor_titles[selected]))
    time.sleep(0.5)
    clear()


def game_menu():
    """
    Creates the 'Select Game Folder' menu
    :return:
    """
    menu_creator(os.listdir(manager.games_path), action=game_menu_action)


def game_menu_action(selected):
    """
    'Select Game Folder' action for use with menu_creator
    :param selected:
    :return:
    """
    manager.set_game(os.listdir(manager.games_path)[selected])
    print("selected {}".format(os.listdir(manager.games_path)[selected]))
    time.sleep(0.5)
    clear()


def config_menu():
    """
    Creates the 'Show Config' menu
    :return:
    """
    menu_creator(manager.to_strings())


def main_menu_action(selected):
    """
    The main menu logic
    :param selected:
    :return:
    """
    clear()
    if selected == 0:
        donor_menu()
    elif selected == 1:
        game_menu()
    elif selected == 2:
        manager.swap_currently_selected()
        countdown()
    elif selected == 3:
        manager.edit_npdm()
        manager.swap_currently_selected()
        countdown()
    elif selected == 4:
        manager.move_to_games()
        countdown()
    elif selected == 5:
        manager.move_all_to_games()
        countdown()
    elif selected == 7:
        config_menu()


config = configparser.ConfigParser()
manager = Manager()


def main():
    if not os.path.exists(manager.CONFIG_PATH):
        manager.generate_config()
    manager.read_config()
    clear()
    menu_creator(MAIN_OPTIONS, action=main_menu_action, break_after_action=False, break_if_selected_is=9)


if __name__ == '__main__':
    main()
