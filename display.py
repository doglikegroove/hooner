from tkinter import *
from tkinter import ttk
from player import play_track


class SmartFrame(ttk.Frame):
    def __init__(self, *args, **kwargs):
        ttk.Frame.__init__(self, *args, **kwargs)
        self.is_refreshing = False
        self.library = {}

    def set_refreshing(self, state):
        self.is_refreshing = state

    def attach_library(self, library):
        self.library = library


def _play_track(event):
    play_track(event.widget.selection()[0])


def _refresh_artist_box(artist_box, valid_tracks):
    root_frame = artist_box.master
    previous_selections = artist_box.selection()
    refreshed_artists = set()
    for i in artist_box.get_children():
        artist_box.delete(i)
    for track in valid_tracks:
        refreshed_artists.add(root_frame.library['album_artists'][track.album_artist])
    for entry in sorted(refreshed_artists):
        artist_box.insert('', 'end', entry.name, text=entry.name)
    for selection in previous_selections:
        try:
            artist_box.selection_add(selection)
        except Exception as e:
            pass


def _refresh_album_box(album_box, valid_tracks):
    root_frame = album_box.master
    artist_box = root_frame.children['artist_box']
    artist_selections = artist_box.selection()
    previous_album_selections = album_box.selection()
    refreshed_albums = set()
    for i in album_box.get_children():
        album_box.delete(i)
    for track in valid_tracks:
        album = root_frame.library['albums'][track.album]
        if artist_selections:
            for artist in artist_selections:
                if album in root_frame.library['album_artists'][artist].album_list:
                    refreshed_albums.add(album)
        else:
            refreshed_albums.add(album)
    for entry in sorted(refreshed_albums):
        album_box.insert('', 'end', entry.title, text=entry.title)
    for selection in previous_album_selections:
        try:
            album_box.selection_add(selection)
        except Exception as e:
            pass


def _refresh_track_box(track_box, valid_tracks):
    root_frame = track_box.master
    artist_box = root_frame.children['artist_box']
    artist_selections = artist_box.selection() or artist_box.get_children()
    album_box = root_frame.children['album_box']
    album_selections = album_box.selection() or album_box.get_children()
    previous_track_selections = track_box.selection()
    refreshed_tracks = set()
    for i in track_box.get_children():
        track_box.delete(i)
    for possible_track in valid_tracks:
        if possible_track.album in album_selections and possible_track.album_artist in artist_selections:
            refreshed_tracks.add(possible_track)
    for new_track in sorted(refreshed_tracks):
        track_values = (new_track.tracknumber, new_track.title, new_track.artist,
                        new_track.album, new_track.genre, new_track.time_string)
        track_box.insert('', 'end', new_track.filename, values=track_values)
    for selection in previous_track_selections:
        try:
            track_box.selection_add(selection)
        except Exception as e:
            pass


def _refresh_display(event):
    if str(event.widget) == '.root_frame.search_frame.search_box':
        search_re = event.widget.get()
        root_frame = event.widget.master.master
    else:
        root_frame = event.widget.master
        search_re = root_frame.children['search_frame'].children['search_box'].get()
    search_re.strip()
    new_track_list = set()

    def _match_track(track_to_check):
        import re
        for attr in ('album', 'artist', 'album_artist', 'genre', 'title'):
            if re.search(search_re.lower(), getattr(track_to_check, attr).lower()):
                return True

    for track in root_frame.library['tracks'].values():
        if not search_re or _match_track(track):
            new_track_list.add(track)
    _refresh_artist_box(root_frame.children['artist_box'], new_track_list)
    _refresh_album_box(root_frame.children['album_box'], new_track_list)
    _refresh_track_box(root_frame.children['track_box'], new_track_list)


def _build_root_window():
    root_window = Tk()
    root_window.option_add('*tearOff', FALSE)
    root_window.title('Hooner')
    root_window.columnconfigure(0, weight=1)
    root_window.rowconfigure(0, weight=1)
    return root_window


def _build_root_frame(root_window, library):
    root_frame = SmartFrame(root_window, name='root_frame')
    root_frame.attach_library(library)
    root_frame.grid(column=0, row=0, sticky=(N, W, E, S))
    root_frame.columnconfigure(0, weight=3)
    root_frame.columnconfigure(1, weight=5)
    root_frame.rowconfigure(0, weight=0)
    root_frame.rowconfigure(1, weight=1)
    root_frame.rowconfigure(2, weight=5)
    return root_frame


def _build_menu_bar(root_window):
    menu_bar = Menu(root_window, name='menu_bar')
    root_window['menu'] = menu_bar
    return menu_bar


def _build_search_frame(root_frame):
    search_frame = ttk.Frame(root_frame, name='search_frame')
    search_frame.columnconfigure(0, weight=1)
    search_frame.columnconfigure(1, weight=2)
    search_frame.grid(column=1, row=0, sticky=(N, S, E))
    search_box = ttk.Entry(search_frame, name='search_box')
    search_box.grid(column=1, row=0, sticky=(N, S, E))
    search_label = ttk.Label(search_frame, text='Search: ', anchor='w')
    search_label.grid(column=0, row=0, sticky=(N, S, E))
    return search_frame


def _build_artist_box(root_frame):
    artist_box = ttk.Treeview(root_frame, name='artist_box', selectmode='extended')
    artist_box.heading('#0', text='Album Artist')
    artist_box.grid(column=0, row=1, sticky=(N, S, E, W))
    return artist_box


def _build_album_box(root_frame):
    album_box = ttk.Treeview(root_frame, name='album_box', selectmode='extended')
    album_box.heading('#0', text='Album')
    album_box.grid(column=1, row=1, sticky=(N, S, E, W))
    return album_box


def _build_track_box(root_frame):
    track_box_columns = ('N', 'Title', 'Artist', 'Album', 'Genre', 'Time')
    track_box = ttk.Treeview(root_frame, name='track_box', selectmode='extended', columns=track_box_columns)
    track_box.heading('#0', text='>')
    track_box.column('#0', width=25, anchor='center', stretch=False)
    track_box.heading('N', text='#')
    track_box.column('N', width=25, anchor='center', stretch=False)
    track_box.heading('Title', text='Title')
    track_box.heading('Artist', text='Album Artist')
    track_box.heading('Album', text='Album')
    track_box.heading('Genre', text='Genre')
    track_box.column('Genre', width=150)
    track_box.heading('Time', text='Time')
    track_box.column('Time', width=75, anchor='e', stretch=False)
    track_box.grid(column=0, row=2, columnspan=2, sticky=(N, S, E, W))
    return track_box


def _build_display(library):
    root_window = _build_root_window()
    root_frame = _build_root_frame(root_window, library)
    menu_bar = _build_menu_bar(root_window)
    search_frame = _build_search_frame(root_frame)
    artist_box = _build_artist_box(root_frame)
    album_box = _build_album_box(root_frame)
    track_box = _build_track_box(root_frame)
    search_frame.children['search_box'].bind('<KeyRelease>', _refresh_display)
    artist_box.bind('<ButtonRelease-1>', _refresh_display)
    album_box.bind('<ButtonRelease-1>', _refresh_display)
    artist_box.event_generate('<ButtonRelease-1>')
    track_box.bind('<Double-1>', _play_track)
    menu_File = Menu(menu_bar)
    menu_bar.add_cascade(menu=menu_File, label='File')
    menu_File.add_command(label='Quit', command=lambda: exit(0))

    return root_window


def initiate_display(passed_in_library):
    root_window = _build_display(passed_in_library)
    return root_window
