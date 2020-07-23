from app import app
from flask import Flask, request, jsonify
import numpy as np
import emoji, json
from torchmoji.global_variables import PRETRAINED_PATH, VOCAB_PATH
from torchmoji.sentence_tokenizer import SentenceTokenizer
from torchmoji.model_def import torchmoji_emojis
from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import lyricsgenius


APP_ROOT = os.path.join(os.path.dirname(__file__), '.')   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')

# SPOTIPY_CLIENT_ID = 'e65ce781a807440ca1eb3ef4335e4bbe'
# SPOTIPY_CLIENT_SECRET = '51a43938818f461893a8ebf835057bdd'

genius = lyricsgenius.Genius("8-GuMWci6ko8MMhgWakb0tCkjD9DWw64whaphWqCVUrBR2FUlyK5y6UxXtWeb2cx")



client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager,requests_timeout=10)

  
EMOJIS = ":joy: :unamused: :weary: :sob: :heart_eyes: :pensive: :ok_hand: :blush: :heart: :smirk: :grin: :notes: :flushed: :100: :sleeping: :relieved: :relaxed: :raised_hands: :two_hearts: :expressionless: :sweat_smile: :pray: :confused: :kissing_heart: :heartbeat: :neutral_face: :information_desk_person: :disappointed: :see_no_evil: :tired_face: :v: :sunglasses: :rage: :thumbsup: :cry: :sleepy: :yum: :triumph: :hand: :mask: :clap: :eyes: :gun: :persevere: :smiling_imp: :sweat: :broken_heart: :yellow_heart: :musical_note: :speak_no_evil: :wink: :skull: :confounded: :smile: :stuck_out_tongue_winking_eye: :angry: :no_good: :muscle: :facepunch: :purple_heart: :sparkling_heart: :blue_heart: :grimacing: :sparkles:".split(' ')
model = torchmoji_emojis(PRETRAINED_PATH)
with open(VOCAB_PATH, 'r') as f:
  vocabulary = json.load(f)
st = SentenceTokenizer(vocabulary, 30)


def deepmojify(sentence,top_n =5):
  def top_elements(array, k):
    ind = np.argpartition(array, -k)[-k:]
    return ind[np.argsort(array[ind])][::-1]

  tokenized, _, _ = st.tokenize_sentences([sentence])
  prob = model(tokenized)[0]
  emoji_ids = top_elements(prob, top_n)
  emojis = map(lambda x: EMOJIS[x], emoji_ids)
  return emoji.emojize(f"{sentence} {' '.join(emojis)}", use_aliases=True)


def lyricmojify(song_name):
    song = genius.search_song(song_name)
    lyrics = song.lyrics
    sentences = lyrics.split("\n")

    emojified_lyrics = []

    for sentence in sentences:
        emojified_lyrics.append(sentence)
        if len(sentence) > 3 and '[' not in sentence:
            emo = deepmojify(sentence, top_n = 5)[-10:]
            emojified_lyrics.append(emo)
    
    emo_lyrics_obj = {
        'Mojified': emojified_lyrics
    }
    return emo_lyrics_obj





@app.route("/") 
def home_view(): 
	return "<h1>Welcome to EmojiFire 💯 🙌 👏</h1>"


@app.route("/songid/<songid>")
def getemojis(songid):
    track_deets = sp.track(songid)
    song_search = track_deets['name']+" by "+track_deets['artists'][0]['name']
    emo = lyricmojify(song_search)
    return str(emo)