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
from contextlib import suppress

from nx.utils import AnsiMenu as Menu
from nx.utils import clear_terminal as clr

print = functools.partial(print, flush=True)

"""
=================================================================================
ONLY EDIT THIS PORTION (End Users)
=================================================================================
"""
ROMFS_STYLE = 0  # 0 - Folder/dir, 1 = RomFs.bin, 2 = RomFs.romfs
GAMES_PATH = '/switch/games/'  # Root directory for game storage
DONOR_PATH = '/atmosphere/titles/'  # Root directory for donors
CONFIG_PATH = '/switch/games/config.ini'  # Where the config.ini is saved
ERROR_PATH = '/switch/games/error.txt'  # Where the error.txt is saved
DONOR_TITLES = ['Blazblue', 'Fallout Shelter', 'Fortnite', 'Hulu', 'Kitten Squad', 'Octopath Demo', 'PaccMan VS',
                'Pic-a-Pix Deluxe Demo', 'Pinball FX3', 'PixelJunk Monsters 2 Demo', 'Pokémon Quest',
                'Stern Pinball Arcade', 'The Pinball Arcade']  # Donor Titles
DONOR_TIDS = ['0100C6E00AF2C000', '010043500A17A000', '010025400AECE000', '0100A66003384000', '01000C900A136000',
              '010096000B3EA000', '0100BA3003B70000', '01006E30099B8000', '0100DB7003828000', '01004AF00A772000',
              '01005D100807A000', '0100AE0006474000', '0100cd300880E000']  # Donor TitleIDs
"""
=================================================================================
DONT EDIT BELOW THIS UNLESS YOU KNOW WHAT YOU ARE DOING
=================================================================================
"""

MENU_SEP = '============================'  # Menu seperator
MAIN_OPTIONS = ['Select Donor Title', 'Select Game Folder', 'Put Game In Donor', 'Put Game In Donor [Edit NPDM]',
                'Put Donor Game Back', 'Put All Games Back', MENU_SEP, 'Show Config', 'Reset Config', MENU_SEP, 'Exit']

MENU_SIGN = """  
____   _   _   _ ___   ____ ___ ___  ___  ____ ___ ________ ____ ____  
).-._( )_\ ) \_/ ) __( /  _ ) __\   \)_ _(/  _ ) __/ _)__ __/ __ /  _ \ 
|( ,-./( )\|  _  | _)  )  ' | _)| ) (_| |_)  ' | _)))_  | | ))__()  ' / 
)_`__)_/ \_)_( )_)___( |_()_)___/___)_____|_()_)___\__( )_( \____|_()_\ 

"""
ROMFS_PATH = ['/RomFs/', '/RomFs.bin', '/RomFs.romfs']
EXEFS_PATH = '/ExeFs/'
NPDM_PATH = '/ExeFs/main.npdm'


def clear():
    """
    Clears out the terminal screen and prints the menu sign at the top
    :return:
    """
    clr()
    sys.stdout.buffer.write(b'Hello')
    sys.stdout.flush()
    print(MENU_SIGN)


def countdown():
    """
    Simple countdown because if not we would never read whats on the screen..
    :return:
    """
    print("Returning to main menu in 5 seconds.")
    for i in range(5):
        print("{}...".format(5 - i))
        time.sleep(1)
    clear()


class DonorTitle(object):
    """
    Object to hold the donor information
    """

    def __init__(self, title_id):
        self.title_id = title_id
        self.current_used = None

    def get_title_id(self):
        """
        Returns the Title ID as a string
        :return:
        """
        return "{}".format(self.title_id)

    def set_currently_used(self, game_name):
        """
        Sets the currently used game
        :param game_name:
        :return:
        """
        if game_name is not None and os.path.isdir(GAMES_PATH + game_name):
            self.current_used = game_name
            return True
        self.current_used = None
        return False

    def get_currently_used(self):
        """
        Returns the currently used game as a string
        :return:
        """
        if self.current_used is not None:
            return "()".format(self.current_used)
        return "None"


class Manager(object):
    """
    The meat and potatos. This does pretty much everything.
    """

    def __init__(self, config_file, error_file):
        self.config_file = config_file
        self.error_file = error_file
        self.donor_titles = None
        self.selected_donor = None
        self.selected_game = None

    def set_donor(self, title_id):
        """
        Sets the donor title to use
        :param title_id:
        :return:
        """
        if title_id is not None:
            for donor in self.donor_titles:
                if donor.get_title_id() == title_id:
                    self.selected_donor = donor
                    return True
            return False
        self.selected_donor = None
        return True

    def get_donor(self):
        """
        Returns the donor as a string
        :return:
        """
        if self.selected_donor is not None:
            return "{}".format(self.selected_donor)
        return "None"

    def set_game(self, game_name):
        """
        Sets the selected game
        :param game_name:
        :return:
        """
        if game_name is not None:
            if os.path.exists(GAMES_PATH + game_name):
                self.selected_game = game_name
                return True
            return False
        self.selected_game = None
        return True

    def get_game(self):
        """
        Returns a string for the selected game
        :return:
        """
        if self.selected_game is not None:
            return "{}".format(self.selected_game)
        return "None"

    def write_config(self):
        """
        Write the donor titles to the config.ini
        :return:
        """
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        with open(self.config_file, 'w') as conf:
            for dt in self.donor_titles:
                conf.write('{0}={1}\n'.format(dt.get_title_id(), dt.get_currently_used()))
        return True

    def read_config(self):
        """
        Read in the config.ini and setup the donor titles
        :return:
        """
        if self.donor_titles is not None:
            if os.path.exists(self.config_file):
                dt = []
                with open(self.config_file, 'r') as conf:
                    for index, line in enumerate(conf.readlines()):
                        line = line.strip()
                        line_split = line.split("=")
                        dtt = DonorTitle(line_split[0])
                        if line_split[1] is not 'None':
                            dtt.set_currently_used(line_split[1])
                        dt.append(dtt)
                self.donor_titles = dt
        else:
            self.reset_config()

    def reset_config(self):
        """
        Deletes and resets the config.ini file
        :return:
        """
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        dt = []
        for i in range(len(DONOR_TIDS)):
            dtt = DonorTitle(DONOR_TIDS[i])
            dtt.set_currently_used(None)
            dt.append(dtt)
        self.donor_titles = dt
        self.write_config()

    def move_to_donor(self):
        """
        Moves the selected game to the selected donor
        :return:
        """
        if not os.path.exists(DONOR_PATH + self.selected_donor.get_title_id()):
            if self.selected_donor.set_currently_used(self.selected_game):
                with suppress(OSError):
                    print("Moving game to donor...")
                    shutil.move(GAMES_PATH + self.selected_game + ROMFS_PATH[ROMFS_STYLE],
                                DONOR_PATH + self.selected_donor.get_title_id() + ROMFS_PATH[ROMFS_STYLE])
                    shutil.move(GAMES_PATH + self.selected_game + EXEFS_PATH,
                                DONOR_PATH + self.selected_donor.get_title_id() + EXEFS_PATH)
                    print("Success!")
                    print("Removing extras")
                    if os.path.exists(GAMES_PATH + self.selected_game + ROMFS_PATH[ROMFS_STYLE]):
                        shutil.rmtree(GAMES_PATH + self.selected_game + ROMFS_PATH[ROMFS_STYLE])
                    if os.path.exists(GAMES_PATH + self.selected_game + EXEFS_PATH):
                        shutil.rmtree(GAMES_PATH + self.selected_game + EXEFS_PATH)
                    print("Success!")
                return True
        return False

    def move_to_games(self):
        """
        Moves the selected donor game to the games folder
        :return:
        """
        if os.path.exists(DONOR_PATH + self.selected_donor.get_title_id()):
            if self.selected_donor.set_currently_used(None):
                with suppress(OSError):
                    print("Moving game from donor to /switch/games...")
                    shutil.move(DONOR_PATH + self.selected_donor.get_title_id() + ROMFS_PATH[ROMFS_STYLE],
                                GAMES_PATH + self.selected_donor.get_currently_used() + ROMFS_PATH[ROMFS_STYLE])
                    shutil.move(DONOR_PATH + self.selected_donor.get_title_id() + EXEFS_PATH,
                                GAMES_PATH + self.selected_donor.get_currently_used() + EXEFS_PATH)
                    print("Success!")
                    print("Removing extras...")
                    if os.path.exists(DONOR_PATH + self.selected_donor.get_title_id()):
                        shutil.rmtree(DONOR_PATH + self.selected_donor.get_title_id())
                    print("Success!")

    def move_all_to_games(self):
        """
        Moves all currently used games back to the games folder
        :return:
        """
        for donor in self.donor_titles:
            if os.path.exists(DONOR_PATH + donor.get_title_id()):
                if donor.set_currently_used(None):
                    with suppress(OSError):
                        print("Moving game from {} to /switch/games/".format(donor.get_title_id()))
                        shutil.move(DONOR_PATH + donor.get_title_id() + ROMFS_PATH[ROMFS_STYLE],
                                    GAMES_PATH + donor.get_currently_used() + ROMFS_PATH[ROMFS_STYLE])
                        shutil.move(DONOR_PATH + donor.get_title_id() + EXEFS_PATH,
                                    GAMES_PATH + donor.get_currently_used() + EXEFS_PATH)
                        print("Success!")
                        print("Removing extras...")
                        if os.path.exists(DONOR_PATH + donor.get_title_id()):
                            shutil.rmtree(DONOR_PATH + donor.get_title_id())
                        print("Success!")

    def edit_npdm(self):
        """
        Edit the npdm for the selected game to match the selected donor
        :return:
        """
        if not os.path.exists(GAMES_PATH + self.selected_game + NPDM_PATH + '.bak'):
            print("Backing up NPDM")
            with suppress(OSError):
                shutil.copy2(GAMES_PATH + self.selected_game + NPDM_PATH,
                             GAMES_PATH + self.selected_game + NPDM_PATH + '.bak')
            print("Finished")
        with open(GAMES_PATH + self.selected_game + NPDM_PATH, 'r+b') as npdm:
            donor_id = self.selected_donor.get_title_id()
            donor_id_flipped = "".join(reversed([donor_id[i:i + 2] for i in range(0, len(donor_id), 2)]))
            donor_id = bytearray.fromhex(donor_id_flipped)
            content = bytearray(npdm.read())
            tid_offset = content.find(b'ACI0') + 0x10
            tid_length = 0x8
            content[tid_offset:tid_offset + tid_length] = donor_id
            npdm.seek(0)
            npdm.write(content)
        return True

    def to_strings(self):
        """
        Returns an array of strings to be used with AnsiMenu
        :return:
        """
        lines = ["-> Press any option to return to the main menu"]
        for index, dt in enumerate(self.donor_titles):
            if dt.get_currently_used() is None:
                tmp = 'None'
            else:
                tmp = dt.get_currently_used()
            lines.append("{0} is currently being used by {1}".format(DONOR_TITLES[index], tmp))
        return lines


configuration = Manager(CONFIG_PATH, ERROR_PATH)


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
    menu_creator(DONOR_TITLES, action=donor_menu_action)


def donor_menu_action(selected):
    """
    'Select Donor Title' action for use with the menu creator
    :param selected:
    :return:
    """
    configuration.set_donor(DONOR_TIDS[selected])
    print("selected {}".format(DONOR_TIDS[selected]))
    time.sleep(0.5)
    clear()


def game_menu():
    """
    Creates the 'Select Game Folder' menu
    :return:
    """
    menu_creator(os.listdir(GAMES_PATH), action=game_menu_action)


def game_menu_action(selected):
    """
    'Select Game Folder' action for use with menu_creator
    :param selected:
    :return:
    """
    configuration.set_game(os.listdir(GAMES_PATH)[selected])
    print("selected {}".format(os.listdir(GAMES_PATH)[selected]))
    time.sleep(0.5)
    clear()


def config_menu():
    """
    Creates the 'Show Config' menu
    :return:
    """
    menu_creator(configuration.to_strings())


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
        configuration.move_to_donor()
        countdown()
    elif selected == 3:
        configuration.edit_npdm()
        configuration.move_to_donor()
        countdown()
    elif selected == 4:
        configuration.move_to_games()
        countdown()
    elif selected == 5:
        configuration.move_all_to_games()
        countdown()
    elif selected == 7:
        config_menu()
    elif selected == 8:
        configuration.reset_config()
        countdown()


def main():
    """
    Main Loop... Do you really need me to annotate this?
    We read the config... then make the menu...
    """
    configuration.read_config()
    clear()
    menu_creator(MAIN_OPTIONS, action=main_menu_action, break_after_action=False, break_if_selected_is=10)


if __name__ == '__main__':
    main()
