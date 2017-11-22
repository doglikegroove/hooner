from library import *
from display import initiate_display
import os
import pickle


def write_preferences(preferences_file, preferences):
    try:
        with open(preferences_file, 'wb') as f:
            pickle.dump(preferences, f)
    except Exception as e:
        raise e
        exit(1)
    return preferences


def get_preferences(preferences_file):
    try:
        with open(preferences_file, 'rb') as f:
            preferences = pickle.load(f)
    except FileNotFoundError:
        return False
    except Exception as e:
        raise e
        exit(1)
    return preferences


def get_search_path(initial_dir):
    from tkinter.filedialog import askdirectory
    from tkinter import Tk
    root = Tk()
    root.withdraw()
    music_path = askdirectory(parent=root, initialdir=initial_dir, title='Select a directory tree to scan for music')
    return music_path


def initialize_first_library(preferences_file):
    preferences = get_preferences(preferences_file)
    home_dir = os.path.expanduser('~')
    music_path = get_search_path(home_dir)
    my_library = add_tracks_to_library(music_path)
    library_store = home_dir + '/.hooner_library.pickle'
    with open(library_store, 'wb') as f:
        pickle.dump(my_library, f)
    preferences['library'] = library_store
    write_preferences(preferences_file, preferences)
    return my_library


def open_library(library_store):
    try:
        with open(library_store, 'rb') as f:
            my_library = pickle.load(f)
    except Exception as e:
        raise e
        exit(1)
    return my_library


def main():
    preferences_file = os.path.expanduser('~') + '/.hooner_prefs'
    preferences = get_preferences(preferences_file) or write_preferences(preferences_file, {})
    try:
        current_library = open_library(preferences['library'])
    except KeyError:
        current_library = initialize_first_library(preferences_file)
    root_window = initiate_display(current_library)
    root_window.mainloop()


if __name__ == "__main__":
    main()
