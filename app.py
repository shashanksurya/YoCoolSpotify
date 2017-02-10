
from flask import Flask, render_template, request, redirect
import spotipy as spy

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/')
def main():
  return redirect('/index')

@app.route('/index/<song>')
def index(song):
  sp = spy.Spotify()
  results = sp.search(q=song,limit=20)
  res = []
  for i,t in enumerate(results['tracks']['items']):
  	res.append(' '+t['name'])
  return 'HEllo '+'\n'.join(res)

if __name__ == '__main__':
  app.run(host='0.0.0.0',port=6969)
