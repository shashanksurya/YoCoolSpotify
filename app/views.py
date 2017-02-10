'''Views for YoCoolSpotify'''

from app import app

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