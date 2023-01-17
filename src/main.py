# INTERFACES PRINCIPALE DE MESSAGERIE

from flask import Blueprint, render_template, url_for, redirect, request
from flask_login import login_required, current_user
from sqlalchemy import or_
from sqlalchemy import and_, func
from .models import User, Message
from . import socket_server
from . import RsaCrypt as RSA

main = Blueprint('main', __name__)
response_message = {}


@main.route("/")
@main.route("/home")
@main.route("/home/<username>")
@login_required
def index(username=None):
    global response_message
    included_parts = Message.query.filter(Message.destination_id == current_user.get_id()).all()
    print(included_parts)
    contact = search_contact(patern=current_user.get_id())
    if username is not None:
        return render_template("detail.html", contacts=contact, messages=response_message)
    return render_template("home.html", contacts=contact)


@main.route("/search_discussion", methods=['POST'])
def search_discussion():
    global response_message
    response_message = {}
    select = request.form.get('choice')
    print(f'select = {select}')
    user_dest = User.query.filter(User.pseudo == str(select.strip())).first()
    messageDecrypted = []
    resultat = Message.query.filter(
        or_(
            and_(Message.destination_id == user_dest.id, Message.author_id == current_user.get_id()),
            and_(Message.destination_id == current_user.get_id(), Message.author_id == user_dest.id))) \
        .order_by(Message.createAt.desc()).all()
    for msg in resultat:
        messageDecrypted.append(decrypt_message(msg))

    response_message['user_dest'] = user_dest
    response_message['message'] = messageDecrypted
    print(resultat)
    return redirect(url_for('main.index', username=(str(select))))


@main.route("/search/<patern>")
def search(patern):
    resultat = User.query.filter(User.pseudo.ilike(f'%{patern}%'), User.id != current_user.get_id()).all()
    items = []
    for res in resultat:
        d = {}
        d['pseudo'] = res.pseudo
        items.append(d)
    response = {}
    response['total_count'] = len(items)
    response['incomplete_results'] = False
    response['items'] = items
    print(response)
    return response


@main.route("/search_contact/<patern>")
def search_contact(patern):
    response = []
    dictionary = {}
    resultat = Message.query.with_entities(Message.author_id, func.count(Message.author_id)) \
        .filter(Message.destination_id == patern, Message.isRead == False) \
        .group_by(Message.author_id) \
        .order_by(Message.createAt.asc()) \
        .all()

    for id, res in resultat:
        user = User.query.filter_by(id=id).first()
        last_message = Message.query \
            .filter(Message.destination_id == patern, Message.isRead == False, Message.author_id == id) \
            .order_by(Message.createAt.desc()) \
            .first()
        dictionary['name'] = user.pseudo
        dictionary['last_message'] = decrypt_message(last_message).content
        dictionary['date'] = last_message.createAt
        dictionary['count'] = res
        response.append(dictionary)
    return response


def decrypt_message(message: Message):
    destination = message.destination_id
    author = message.author_id
    DpubKey, DprivKey = RSA.load_keys(destination)
    plaintext = RSA.decrypt(message.content, DprivKey)
    message.content = plaintext
    return message
