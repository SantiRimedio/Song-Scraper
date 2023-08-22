import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import lyricsgenius

class songScraper:
    """
    A class for scraping songs off spotify API and getting their lyrics from Genius API


    """

    def __init__(self, cid, secret, genius_api_key):
        """
        Initializes the SongScraper class.

        :param cid: Spotify API client ID.
        :param secret: Spotify API client secret.
        :param genius_api_key: Genius API access token.
        """
        self.spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=cid, client_secret=secret))
        self.genius = lyricsgenius.Genius(genius_api_key)

    def get_artists(self, genre="Rock Nacional", artist_n=5, song_n=5, market="AR",artist_popularity=15):
        """
        Retrieves songs for a specific genre.

        :param genre: music genre to search. Default "Rock Nacional".
        :param artist_n: number of artists to return. Default 5.
        :param song_n: number of songs to return for each artist. Default 5.
        :param popularity: lower threshold of popularity for artists. Default 15.
        :param market: market for the artists. Default "AR".

        :return: DataFrame containing column witt audio features.
        """
        offset=1
        size = artist_n
        # Request de search endpoint query=genre, tipo playlist.
        response = self.spotify.search(q=genre, type='playlist', market=market, limit=None, offset=offset)

        #Extraigo el id de las playlists que devuelve response
        playlists = [playlist['id'] for playlist in response['playlists']['items']]

        #Creo una lista vacia que se convertirá en el df final y un set de artistas para comprobar repeticiones
        artists_data = []
        seen_artist_ids = set()

        # While loop para obtener la cantidad de artistas especificada en size

        while size is None or len(artists_data) < size:
            #itero sobre cada playlist ID
            for playlist_id in playlists:
                results = self.spotify.playlist_tracks(playlist_id)
                tracks = results['items']

                # Itero sobre todos los tracks de la playlist
                for track in tracks:
                    track_info = track['track']

                    # Itero sobre los artistas de cada track
                    for artist in track_info['artists']:
                        artist_id = artist['id']

                        # Compruebo repeticiones
                        if artist_id not in seen_artist_ids:
                            seen_artist_ids.add(artist_id)


                            # Intento obtener más información del artista
                            try:
                                artist_data = self.spotify.artist(artist_id)
                            except:
                                artist_data = None

                            # Compruebo si el artista produce rock nacional
                            if artist_data is not None and ("argentine rock" in artist_data["genres"] or "rock nacional" in artist_data["genres"]):

                                #Filtro los artistas por un umbral de popularidad
                                if artist_data['popularity'] > artist_popularity:

                                    # Extraigo el nombre, id, genre y popularidad del artista.
                                    artist_info = {
                                        'Artist': artist['name'],
                                        'Artist_ID': artist_id,
                                        "Artist_genres": artist_data['genres'],
                                        "Artist_popularity": artist_data['popularity']
                                    }
                                    artists_data.append(artist_info)

                        if size is not None and len(artists_data) >= size:
                            break

                    if size is not None and len(artists_data) >= size:
                        break

                if size is not None and len(artists_data) >= size:
                    break

        df = pd.DataFrame(artists_data)
        songs = []
        song_id = []
        songs_release = []
        songs_popularity = []
        for i in df["Artist"]:
            #Obtengo n tracks para artista
            results = self.spotify.search(q=f"artist:{i}",  type='track', offset=0, limit=song_n)

            #Extraigo canción, id de canción, release y popularidad.
            songs.append([result["name"] for result in results["tracks"]["items"]])
            song_id.append([result["id"] for result in results["tracks"]["items"]])
            songs_release.append([result["album"]["release_date"] for result in results["tracks"]["items"]])
            songs_popularity.append([result["popularity"] for result in results["tracks"]["items"]])
        df["Track"] = songs
        df["Track_ID"] = song_id
        df["Track_release_date"] = songs_release
        df["Track_popularity"] = songs_popularity
        df = df.explode(["Track","Track_ID","Track_release_date","Track_popularity"])

        return df

    def get_songs(self, n=50, genre="", market="AR"):
        """
       Fetches song data, including track information, artist details, and audio features.

       :param n: Number of songs to fetch. Limit: 1000. See get_artists method for a bigger number of songs.
       :param genre: Music genre to fetch.
       :param market: Market on which to fetch songs. Defaults to AR.
       :return: DataFrame containing song data.
       """
        offset = 0  # You can adjust the offset as needed
        songs_data = []

        while len(songs_data) < n:
            results = self.spotify.search(q=f'genre:"{genre}"', type='track', limit=50, offset=offset, market=market)
            for track in results['tracks']['items']:
                track_name = track['name']
                track_id = track["id"]
                track_release_date = track['album']['release_date']
                track_popularity = track['popularity']
                artist_data = track['artists'][0]  # Assuming a single artist for simplicity
                artist_id = artist_data['id']
                artist_name = artist_data['name']
                artist_popularity = self.get_artist_popularity(artist_id)
                artist_genres = self.get_artist_genres(artist_id)
                album_name = track['album']['name']
                songs_data.append({'Track': track_name,"Track_ID": track_id ,"Track_release_date": track_release_date,"Track_popularity": track_popularity,'Artist': artist_name, 'Artist_ID': artist_id, 'Artist_Popularity': artist_popularity, 'Artist_Genres': artist_genres, 'Album': album_name})

                if len(songs_data) >= n:
                    break

            offset += 50

        return pd.DataFrame(songs_data)

    def get_artist_popularity(self, artist_id):
        artist_data = self.spotify.artist(artist_id)
        return artist_data['popularity']

    def get_artist_genres(self, artist_id):
        artist_data = self.spotify.artist(artist_id)
        return artist_data['genres']

    def get_audio_features(self, df):
        """
        Retrieves audio features for a song using its Spotify track ID.

        :param df: dataframe with column with "Track_ID".
        :return: DataFrame containing column witt audio features.
        """
    # Extraigo los audio features para cada canción
        features = []
        for i in df["Track_ID"]:
            try:
                feature = self.spotify.audio_features(i)
                if feature:
                    feature = {k: feature[0][k] for k in list(feature[0])[:11]}
                else:
                    feature = "nan"
            except:
                feature = "nan"
            features.append(feature)
        df["features_dict"] = features
        return df

    def get_lyrics(self, df):
        """
        Fetches lyrics for songs in a DataFrame using the Genius API.

        :param df: DataFrame containing song data.
        :return: DataFrame with added "Lyrics" column.
        """
        lyrics = []

        total_rows = len(df)
        for idx, row in df.iterrows():
            progress = f"Fetching Lyrics: {idx+1}/{total_rows}"
            print(progress, end="\r")  # Print with carriage return to overwrite previous line

            try:
                song = self.genius.search_song(row["Track"], row["Artist"])
                if song:
                    lyrics.append(song.lyrics)
                else:
                    lyrics.append("nan")
            except Exception as e:
                print(f"Error occurred: {e}")
                lyrics.append("nan")

        print()  # Print a newline after all iterations are done
        df["Lyrics"] = lyrics
        return df
