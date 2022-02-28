#/usr/bin/env python3

from contextlib import redirect_stderr
from crypt import methods
from urllib import request
from flask import Flask, redirect, render_template, request, make_response
from tinydb import TinyDB, Query
import uuid
import socket

app = Flask(__name__)
db = TinyDB('recipes.json')
HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = '127.0.0.1'
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    return client.recv(2048).decode(FORMAT)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = db.search(Query().username == request.form['usernameInput'])
        if len(user) > 0 and user[0]['password'] == request.form['passwordInput']:
            resp = make_response(redirect('/'))
            resp.set_cookie('username', request.form['usernameInput'])
            return resp
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        db.insert(
            {
                'username': request.form['usernameInput'],
                'password': request.form['passwordInput'],
                'recipes': [],
            }
        )
        resp = make_response(redirect('/'))
        resp.set_cookie('username', request.form['usernameInput'])
        return resp

    username = None
    password = None
    if request.args.get('generate'):
        username = send("1").strip() + send("1").strip()
        password = send("1").strip() + send("1").strip()
    return render_template('signup.html', username = username, password = password)

@app.route('/', methods=['GET'])
def home():
    if request.cookies.get('username'):
        data = db.search(Query().username == request.cookies.get('username'))
        return render_template('home.html', recipes = data[0]['recipes'])
    return redirect('/login')

@app.route('/details/<recipe_id>', methods=['GET'])
def details(recipe_id):
    if request.cookies.get('username'):

        data = db.search(Query().username == request.cookies.get('username'))
        for index, recipe in enumerate(data[0]['recipes']):
            if recipe['id'] == recipe_id:
                return render_template('details.html', recipe = recipe)

    return redirect('/login')

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.cookies.get('username'):
        if request.method == 'POST':

            if request.form.get('imageInputModal'):
                return render_template('create.html', image = request.form.get('imageInputModal'))

            data = db.search(Query().username == request.cookies.get('username'))
            recipe = {
                'id': str(uuid.uuid4()),
                'name': request.form['nameInput'],
                'description': request.form['descriptionInput'],
                'instructions': request.form['instructionInput'],
                'image': request.form['imageInput'],
            }
            data[0]['recipes'].append(recipe)
            db.update(data[0], Query().username == request.cookies.get('username'))
            return redirect('/')

        return render_template('create.html')
    return redirect('/login')

@app.route('/edit/<recipe_id>', methods=['GET', 'POST'])
def edit(recipe_id):
    if request.cookies.get('username'):

        data = db.search(Query().username == request.cookies.get('username'))
        for index, recipe in enumerate(data[0]['recipes']):
            if recipe['id'] == recipe_id:
                print(request.form)
                if request.method == 'POST':
                    recipe = {
                        'id': str(uuid.uuid4()),
                        'name': request.form['nameInput'],
                        'description': request.form['descriptionInput'],
                        'instructions': request.form['instructionInput'],
                        'image': request.form['imageInput'],
                    }
                    data[0]['recipes'][index] = recipe
                    db.update(data[0], Query().username == request.cookies.get('username'))
                    return redirect('/')

                return render_template('edit.html', recipe = recipe)
    return redirect('/login')

@app.route('/delete/<recipe_id>', methods=['GET'])
def delete(recipe_id):
    if request.cookies.get('username'):
        data = db.search(Query().username == request.cookies.get('username'))
        for index, recipe in enumerate(data[0]['recipes']):
            if recipe['id'] == recipe_id:
                data[0]['recipes'].remove(recipe)
                db.update(data[0], Query().username == request.cookies.get('username'))
                return redirect('/')
        return redirect('/')
    return redirect('/login')

@app.route('/imageedit/<recipe_id>', methods=['POST'])
def imageedit(recipe_id):
    if request.cookies.get('username'):
        data = db.search(Query().username == request.cookies.get('username'))
        for index, recipe in enumerate(data[0]['recipes']):
            if recipe['id'] == recipe_id:
                recipe['image'] = request.form['imageInput']
                return redirect('/edit/' + recipe_id)
        return redirect('/')
    return redirect('/login')

if __name__ == '__main__':
    app.run()