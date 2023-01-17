#!/bin/env python

# POINT DENTREE DU PROJET
# C'est le premier fichier qui fusionne tous les sous modules du projet
# En particulier le sous serveur socket.io et le serveur web flask

from src import create_app, socketio

app = create_app(debug=True)

if __name__ == '__main__':
    socketio.run(app)
