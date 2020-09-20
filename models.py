
class Artist(object):
    def __init__(self, spotify_artist=None):
        if spotify_artist is None:
            return
        self._id = spotify_artist['id']
        self._name = spotify_artist['name']
        self._uri = spotify_artist['uri']
        self._href = spotify_artist['href']

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    @staticmethod
    def from_json(artist_json):
        a = Artist()
        setattr(a, '_id', artist_json['id'])
        setattr(a, '_name', artist_json['name'])
        setattr(a, '_uri', artist_json['uri'])
        setattr(a, '_href', artist_json['href'])
        return a

    def to_map(self):
        return {
            'id': self._id,
            'name': self._name,
            'uri': self._uri,
            'href': self._href
        }


class Track(object):
    def __init__(self, spotify_track=None):
        if spotify_track is None:
            return
        self._id = spotify_track['id']
        self._name = spotify_track['name']
        self._uri = spotify_track['uri']
        self._href = spotify_track['href']

    @property
    def id(self):
        return self._id

    @staticmethod
    def from_json(track_json):
        t = Track()
        setattr(t, '_id', track_json['id'])
        setattr(t, '_name', track_json['name'])
        setattr(t, '_uri', track_json['uri'])
        setattr(t, '_href', track_json['href'])
        return t

    def to_map(self):
        return {
            'id': self._id,
            'name': self._name,
            'uri': self._uri,
            'href': self._href
        }


class Playlist(object):
    def __init__(self, user_id=None, spotify_playlist=None):
        if spotify_playlist is None:
            return
        self._id = spotify_playlist['id']
        self._name = spotify_playlist['name']
        self._owned = spotify_playlist['owner']['id'] == user_id
        self._uri = spotify_playlist['uri']
        self._public = spotify_playlist['public']
        self._collaborative = spotify_playlist['collaborative']
        self._description = spotify_playlist['description']
        self._tracks = []

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def owned(self):
        return self._owned

    @property
    def public(self):
        return self._public

    @property
    def description(self):
        return self._description

    @property
    def collaborative(self):
        return self._collaborative

    @property
    def tracks(self):
        return self._tracks

    @staticmethod
    def from_json(playlist_json):
        p = Playlist()
        setattr(p, '_id', playlist_json['id'])
        setattr(p, '_name', playlist_json['name'])
        setattr(p, '_owned', playlist_json['owned'])
        setattr(p, '_uri', playlist_json['uri'])
        setattr(p, '_public', playlist_json['public'])
        setattr(p, '_collaborative', playlist_json['collaborative'])
        setattr(p, '_description', playlist_json['description'])
        setattr(p, '_tracks', [Track.from_json(t) for t in playlist_json['tracks']])
        return p

    def add_track(self, spotify_track):
        self._tracks.append(Track(spotify_track))

    def to_map(self):
        return {
            'id': self._id,
            'name': self._name,
            'owned': self._owned,
            'uri': self._uri,
            'public': self._public,
            'collaborative': self._collaborative,
            'description': self._description,
            'tracks': [t.to_map() for t in self._tracks]
        }
