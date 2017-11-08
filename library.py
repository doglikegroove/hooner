import os
import mutagen


def __validate_track(full_path):
    """Validates whether a file path is a valid piece of media for the library"""
    valid_extensions = ['flac', 'mp3']
    return os.path.splitext(full_path)[1].lower().lstrip('.') in valid_extensions


def __find_tracks(path):
    """Find valid music files under a directory path"""
    valid_tracks = []
    raw_library = os.walk(path)
    for subdir in raw_library:
        if not subdir[2]:
            continue
        else:
            for file in subdir[2]:
                full_path = os.path.join(subdir[0], file)
                file_type = __validate_track(full_path)
                if file_type:
                    t = Track(full_path)
                    if t.valid:
                        valid_tracks.append(t)

    return valid_tracks


def add_tracks_to_library(path):
    """Parses information from found tracks and builds databases"""
    tracks = __find_tracks(path)
    track_db = TrackDatabase()
    album_db = AlbumDatabase()
    track_artist_db = ArtistDatabase()
    album_artist_db = ArtistDatabase()

    def _produce(artist_name):
        if artist_name in track_artist_db:
            return track_artist_db[artist_name]
        elif artist_name in album_artist_db:
            return album_artist_db[artist_name]
        else:
            return Artist(artist_name)

    for t in tracks:
        track_db[t.filename] = t
        try:
            album = album_db[t.album]
        except KeyError:
            album = Album(t.album)
            album_db[t.album] = album
        album.track_list.append(t.filename)
        track_artist = _produce(t.artist)
        track_artist_db[t.artist] = track_artist
        track_artist.album_list.add(album)
        album_artist = _produce(t.album_artist)
        album_artist_db[t.album_artist] = album_artist
        album_artist.album_list.add(album)

    return {'album_artists': album_artist_db, 'artists': track_artist_db, 'albums': album_db, 'tracks': track_db}


class Track:
    """Base class for our song/track/what-have-you"""

    def __init__(self, filename=None):
        self.filename = filename
        self.artist = 'Unknown'
        self.album_artist = 'Unknown'
        self.album = 'Unknown'
        self.title = 'Unknown'
        self.genre = 'Unknown'
        self.tracknumber = '1'
        self.discnumber = '1'
        self.valid = False

        if filename:
            self.filetype = os.path.splitext(filename)[1].lower().lstrip('.')
            try:
                self.__attach_info()
            except InvalidInfoError:
                self.valid = False
                pass
            else:
                self.valid = True
        else:
            self.filetype = None

    def __repr__(self):
        text = ''
        track_attributes = []
        for item in dir(self):
            if item.startswith('_'):
                continue
            track_attributes.append(item)
        for attr in sorted(track_attributes):
            value = getattr(self, attr)
            if hasattr(value, '__call__'):
                continue
            text = text + '\t' + attr + ': ' + str(value) + ' (' + str(type(value)) + ')' + '\n'
        return text

    def __lt__(self, other):
        if self.artist.lower() < other.artist.lower():
            return True
        elif self.artist.lower() > other.artist.lower():
            return False
        else:
            if self.album.lower() < other.album.lower():
                return True
            elif self.album.lower() > other.album.lower():
                return False
            else:
                if int(self.discnumber) < int(other.discnumber):
                    return True
                elif int(self.discnumber) > int(other.discnumber):
                    return False
                else:
                    if int(self.tracknumber) <= int(other.tracknumber):
                        return True
                    elif int(self.tracknumber) > int(other.tracknumber):
                        return False

    def __attach_info_from_headers(self, mutagen_object):
        for key in mutagen_object:
            setattr(self, key, list(mutagen_object[key])[0])

    def __attach_info_from_stream_info(self, mutagen_object):
        for attr in dir(mutagen_object):
            if attr.startswith('__'):
                continue
            setattr(self, attr, getattr(mutagen_object, attr))

    def __ensure_artists(self):
        if self.album_artist == 'Unknown' and self.artist != 'Unknown':
            self.album_artist = self.artist
        elif self.artist == 'Unknown' and self.album_artist != 'Unknown':
            self.artist = self.album_artist
        else:
            self.artist = 'Unknown'
            self.album_artist = 'Unknown'

    def __split_number_pairs(self, number_attr):
        import re
        match_object = re.match(r'(\d+)\D(\d+)', getattr(self, number_attr))
        if match_object:
            setattr(self, number_attr, match_object.group(1))

    def __attach_mp3_info(self):
        try:
            mutagen_id3 = mutagen.File(self.filename, easy=True)
        except mutagen.mp3.HeaderNotFoundError:
            # We should do something here, like log an error. Raise for now
            raise InvalidInfoError()
        else:
            self.__attach_info_from_headers(mutagen_id3)
            self.__split_number_pairs('tracknumber')
            self.__split_number_pairs('discnumber')
            self.tracknumber = self.tracknumber.lstrip('0') or '0'
            self.discnumber = self.discnumber.lstrip('0') or '0'

        try:
            mp3 = mutagen.mp3.MP3(self.filename)
        except mutagen.mp3.HeaderNotFoundError:
            # We should do something here, like log an error. Raise for now
            raise InvalidInfoError()
        else:
            self.__attach_info_from_stream_info(mp3.info)

        return None

    def __attach_flac_info(self):
        try:
            mutagen_object = mutagen.flac.FLAC(self.filename)
        except:
            # We should do something here, like log an error. Raise for now
            raise InvalidInfoError()
        else:
            self.__attach_info_from_headers(mutagen_object)
            self.__attach_info_from_stream_info(mutagen_object.info)
            self.tracknumber = self.tracknumber.lstrip('0') or '0'
            self.discnumber = self.discnumber.lstrip('0') or '0'

    def __attach_info(self):
        """Fill out a track object given a filename"""
        info_funcs = {'mp3': self.__attach_mp3_info,
                      'flac': self.__attach_flac_info}
        info_funcs[self.filetype]()
        self.__ensure_artists()
        try:
            self.length
        except AttributeError:
            raise InvalidInfoError()
        else:
            m, s = divmod(int(self.length), 60)
            h, m = divmod(m, 60)
            if h:
                self.time_string = "%d:%02d:%02d" % (h, m, s)
            else:
                self.time_string = "%d:%02d" % (m, s)



class Album:
    """List of track filenames with other attributes"""
    def __init__(self, name):
        self.title = name
        self.track_list = []

    def __str__(self):
        text = 'Album: ' + self.title + '\n'
        try:
            for track in self.track_list:
                text = text + '\t' + track + '\n'
        except:
            text += '\tNo tracks\n'
        return text

    def __lt__(self, other):
        if self.title.lower() < other.title.lower():
            return True
    
    def add_track(self, track_filename):
        self.track_list.append(track_filename)

    def remove_track(self, track_filename):
        self.track_list.remove(track_filename)


class Artist:
    """List of Albums with other attributes"""
    def __init__(self, name):
        self.name = name
        self.album_list = set()

    def __str__(self):
        text = 'Artist ' + self.name + ' appears on albums:\n'
        try:
            for album in self.album_list:
                text = text + '\t' + album.name + '\n'
        except:
            text += '\tNo tracks\n'
        return text

    def __lt__(self, other):
        if self.name.lower() < other.name.lower():
            return True
    
    def add_album(self, album):
        self.album_list.add(album)

    def remove_album(self, album):
        self.album_list.remove(album)


class TrackDatabase(dict):
    """One-to-one filename to track object database dictionary."""
    def __init__(self):
        super().__init__()


class AlbumDatabase(dict):
    """One-to-one Album name to album object database dictionary."""
    def __init__(self):
        super().__init__()


class ArtistDatabase(dict):
    """One-to-one filename to track object database dictionary."""
    def __init__(self):
        super().__init__()


class InvalidInfoError(Exception): pass
