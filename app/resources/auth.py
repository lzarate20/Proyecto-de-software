from flask import redirect, render_template, request, url_for, abort, session, flash
from app.models.user import User, Rol
from app.models.configuration import Configuration
from sqlalchemy import and_
from app.helpers.auth import authenticated as auth
from app.helpers.auth import get_pending_state as pend
from app.helpers.permission import has_permission as perm
from app.resources import rol
from oauthlib.oauth2 import WebApplicationClient
import requests
from os import environ
import json

GOOGLE_CLIENT_ID = environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

client = WebApplicationClient(GOOGLE_CLIENT_ID)

def login():
    return render_template("auth/login.html")

def google_login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri="https://127.0.0.1:5000/login/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))
    
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    if userinfo_response.json().get("email_verified"):
        users_email = userinfo_response.json()["email"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400
        
    # Create a user in your db with the information provided
    # by Google
    user = User(
        username=users_name, email=users_email, pending=True
    )

    # Doesn't exist? Add it to the database.
    print (userinfo_response.json())
    if not User.get_user_by_email(users_email):
        user.add_user()

    # Begin user session by logging the user in
    # login_user(user)
    #authenticate()
    # Send user back to homepage
    session["user"] = users_email
    session["username"] = users_name
    session["config"] = Configuration.get_configuration()
    session["permissions"] = User.get_permissions(user_id=user.id)
    session["pending"] = user.pending
    return redirect(url_for("home"))    

def authenticate():
    params = request.form
    user = User.login(params=params)
    if not user:
        flash("Usuario o clave incorrecto.")
        return redirect(url_for("auth_login"))
    session["user"] = user.email
    session["username"] = user.username
    session["config"] = Configuration.get_configuration()
    session["permissions"] = User.get_permissions(user_id=user.id)
    session["pending"] = user.pending
    flash("La sesión se inició correctamente.")

    return render_template("home.html")

def is_pending():
    return pend(session)

def authenticated():
    return auth(session)


def has_permission(permission):
    return perm(permission, session)


def logout():
    del session["user"]
    session.clear()
    flash("La sesión se cerró correctamente.")

    return redirect(url_for("auth_login"))
