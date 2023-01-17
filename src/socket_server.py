import random
import functools
from flask import session, request, flash
from flask_socketio import emit, join_room, leave_room, rooms
from flask_login import current_user
from flask_socketio import disconnect
from . import socketio
from . import RsaCrypt as RSA

from .models import User, Message
from . import db

client_count = 0
a_count = 0
b_count = 0


def get_all_room():
    rooms = User.query.with_entities(User.pseudo).all()
    return rooms


def get_destination_user(userId):
    user = User.query.filter_by(id=userId).first()
    return user


def cb(data):
    print(data)


def task(sid):
    socketio.sleep(5)
    # socketio.emit('mult', {'numbers': [5, 3]}, callback=cb)
    result = socketio.call('mult', {'numbers': [5, 3]}, to=sid)
    print(result)


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped
    pass


@authenticated_only
@socketio.on('connect')
def onConnect():
    global client_count
    global a_count
    global b_count
    client_count += 1
    sid = request.sid
    print(f'sid= {sid}')
    room = session.get('global_room')
    join_room(room)
    join_room(current_user.pseudo)
    socketio.emit('status', {'msg': str(session.get('pseudo')) + ' est nous a rejoins.'}, room=room)
    socketio.start_background_task(task, sid)
    socketio.emit('client_count', client_count)
    room = 'a'
    room2 = 'b'
    my_rooms = get_all_room()
    for item in my_rooms:
        join_room(str(item))
    if random.random() > 0.5:
        room
        join_room('a')
        a_count += 1
        socketio.emit('room_count', a_count, to='a')
    else:
        join_room('b')
        b_count += 1
        socketio.emit('room_count', b_count, to='b')


@socketio.on('disconnect')
def ondisconnect():
    global client_count
    global a_count
    global b_count
    client_count -= 1
    room = session.get('global_room')
    socketio.emit('client_count', client_count)
    leave_room(room)
    #leave_room(current_user.pseudo)
    socketio.emit('status', {'msg': str(session.get('pseudo')) + ' est parti.'}, room=room)
    my_rooms = get_all_room()
    for item in my_rooms:
        leave_room(str(item))
    if 'a' in rooms():
        a_count -= 1
        socketio.emit('room_count', a_count, to='a')
    else:
        b_count -= 1
        socketio.emit('room_count', b_count, to='b')
    socketio.emit('user_left')


@socketio.event()
def sum(data):
    result = data['numbers'][0] + data['numbers'][1]
    socketio.emit('sum_result', {'result': result}, to=data['sid'])


@socketio.event()
def text(data):
    result = data
    destination = get_destination_user(data['dest'])
    print(f'destination = {destination.id}')
    pubKey, privKey = RSA.load_keys(current_user.id)
    DpubKey, DprivKey = RSA.load_keys(destination.id)
    msg = data['msg']
    ciphertext = RSA.encrypt(msg, DpubKey)
    signature = RSA.sign_sha1(msg, privKey)
    new_message = Message(content=ciphertext, signature=signature, author_id=data['from'], destination_id=data['dest'])
    socketio.emit('receive', {'msg_content': new_message.content,
                              'msg_status': new_message.isRead,
                              'signature': signature,
                              'author_id': data['from'],
                              'destination_id': data['dest'],
                              'msg_date': new_message.createAt.isoformat()}, room=data['room'])

    socketio.emit('i_send_message', {'msg_content': msg,
                                     'msg_status': new_message.isRead,
                                     'signature': signature,
                                     'msg_date': new_message.createAt.isoformat()}, room=current_user.pseudo)


@socketio.event()
def decrypt(data):
    print('data is')
    print(data)
    destination = get_destination_user(data['datas'][3])
    author = get_destination_user(data['datas'][2])
    DpubKey, DprivKey = RSA.load_keys(destination.id)
    pubKey, privKey = RSA.load_keys(author.id)
    msg = data['datas'][1]
    plaintext = RSA.decrypt(msg, DprivKey)

    if plaintext:
        if RSA.verify_sha1(plaintext, data['datas'][0], pubKey):
            msg = Message(content=msg, signature=data['datas'][0], author_id=data['datas'][2], destination_id=data['datas'][3])
            db.session.add(msg)
            db.session.commit()
            return plaintext

    return False
