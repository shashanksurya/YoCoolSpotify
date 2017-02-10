
from app import app
from flask import Flask, render_template, request, redirect
import spotipy as spy

app.config['DEBUG'] = True

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=6969)
