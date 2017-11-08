from library import *
from display import initiate_display
import pickle

music_path = '/home/sparky/Music'
library_store = music_path + '/.hooner_library.pickle'


def main():
    try:
        with open(library_store, 'rb') as f:
            my_library = pickle.load(f)
    except FileNotFoundError:
        my_library = add_tracks_to_library(music_path)
        with open(library_store, 'wb') as f:
            pickle.dump(my_library, f)
    except Exception as e:
        raise e
        exit(1)

    root_window = initiate_display(my_library)
    root_window.mainloop()


if __name__ == "__main__":
    main()
