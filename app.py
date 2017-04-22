
from app import app
from flask import Flask, render_template, request, redirect
import spotipy as spy

app.config['DEBUG'] = True
app.secret_key = 'aPaphieduub4phuechab8choo7aQu3'

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080)
