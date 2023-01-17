# MODULE DAUTHENTIFICATION

from flask import Blueprint, render_template, url_for, redirect, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
from .models import User
from . import db
from . import serverLDAP
import subprocess
from . import CertReq as CertRequest
from . import CertReqMake as MakeCert
import re

auth = Blueprint('auth', __name__)
address_server_ldap = "192.168.1.32"


@auth.route('/login')
def login():
    return render_template("login.html", title="")


@auth.route('/login', methods=['POST'])
def login_post():
    # login code goes here
    pseudo = request.form.get('pseudo')
    password = request.form.get('password')
    user = User.query.filter_by(pseudo=pseudo).first()

    if not user or not check_password_hash(user.password, password):
        flash('veillez verifier vos information et recommencer encore !!!', 'danger')
        return redirect(url_for('auth.login'))

    ldapresponse = serverLDAP.user_authentication(address_server_ldap, pseudo, password)
    if ldapresponse != True:
        flash(ldapresponse, 'danger')
        return redirect(url_for('auth.login'))

    login_user(user)
    session['pseudo'] = user.pseudo
    session['room'] = user.pseudo
    session['global_room'] = 'salon'
    return redirect(url_for('main.index'))


@auth.route('/signup')
def signup():
    return render_template("signUp.html", title='inscription')


@auth.route('/signup', methods=['POST'])
def signup_post():
    # code to validate and add user to database goes here
    number = request.form.get('number')
    name = request.form.get('name')
    surname = request.form.get('surname')
    pseudo = request.form.get('pseudo')
    password = request.form.get('password')
    pattern = re.compile("^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$")
    if not bool(pattern.match(password)):
        flash(f'Le mot de passe doit contenir minimum 8 caracteres, minimum 1 caractere numerique, ', 'danger')
        flash(f'minimum 1 caractere alphabetique, minimum 1 caractere special', 'danger')
        return redirect(url_for('auth.signup'))

    user = User.query.filter_by(pseudo=pseudo).first()
    if user:
        flash(f' le pseudo {user.pseudo} existe deja', 'danger')
        return redirect(url_for('auth.signup'))

    new_user = User(id=number, surname=surname, name=name, pseudo=pseudo,
                    password=generate_password_hash(password, method='md5'))

    cmd = "slappasswd -s " + password + " -h {MD5} > passwd.txt"
    subprocess.call(cmd, shell=True)
    f = open("passwd.txt", "r")
    listes_line = f.readlines()
    f.close()

    ldapPass = listes_line[0].strip()
    print(f'pass ldap = {ldapPass}')
    ldap_response = serverLDAP.user_add(address_server_ldap, new_user.pseudo, new_user.surname, new_user.name, str(ldapPass))
    if ldap_response != True:
        flash(f' le pseudo {new_user.pseudo} existe deja', 'danger')
        return redirect(url_for('auth.signup'))

    db.session.add(new_user)
    db.session.commit()
    CertRequest.MakeReq(number, pseudo)
    MakeCert.MakeCert(number)
    flash(f' le pseudo {new_user.pseudo} est bien enregistré', 'success')
    return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session['name'] = ''
    session['room'] = ''
    flash(f' deconnection !!! ', 'success')
    return redirect(url_for('auth.login'))
