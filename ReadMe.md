# PROJET DE TCHAT PYTHON

## Video detaillée du projet

<https://www.loom.com/share/40a6574620e24ad98ae2678ad856e003>

## Installer les outils necessaire pour le projet

Après l'avoir cloné, entrer dans la racine du projet

    sudo apt install -y software-properties-common
    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt update
    sudo apt-get install -y build-essential python3-dev libldap2-dev libsasl2-dev slapd ldap-utils tox lcov valgrind python3.11
    sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1
    sudo apt install -y python3.11-dev python3.11-venv python3.11-distutils python3.11-gdbm python3.11-tk python3.11-lib2to3

## Créer un environnement virtuel

    python -m venv venv
    . venv/bin/activate

## Installer les bibliotheques nécessaire du projets

    pip install setuptools wheel twine rsa
    pip install -r requirements.txt

## Vous devez avoir un serveur LDAP deja parfaitement configuré, sinon l'authentification et la connexion ne marcheront pas

**Admin LDAP :** cn=admin,dc=tekup,dc=leo

**Unite d'organisation de l'annuaire :** ou=utilisateurs,dc=tekup,dc=leo

## Modifier l'adresse IP de votre serveur LDAP dans le fichier src/auth.py

## Lancer l'application dans le terminal

    python chat.py

Utiliser obligatoirement l'adresse IP 127.0.0.1 --> <https://127.0.0.1:5000> dans le navigateur, ou alors, modifier uniquement cette adresse IP dans le fichier src/static/js/choice.js. C'est cette adresse qui permet de faire la recherche d'un utilisateur dans la base de données.
