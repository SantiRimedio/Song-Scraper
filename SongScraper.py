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

    def get_songs(self, n=50, genre="", market="AR"):
        """
       Fetches song data, including track information, artist details, and audio features.

       :param n: Number of songs to fetch.
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
            feature = self.spotify.audio_features(i)
            try:
                feature = {k: feature[0][k] for k in list(feature[0])[:11]}
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
