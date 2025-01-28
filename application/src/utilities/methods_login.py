import yaml
import json
import streamlit as st
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import (CredentialsError,
                                               ForgotError,
                                               Hasher,
                                               LoginError,
                                               RegisterError,
                                               ResetError,
                                               UpdateError)

# ----------------------------- Data and inits ------------------------------

def load_config(config_path="data/config.yaml"):
    """Loading config file"""
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.load(file, Loader=SafeLoader)

    return config

def save_config(config, config_path="data/config.yaml"):
    """Saving config file"""
    with open(config_path, 'w', encoding='utf-8') as file:
        yaml.dump(config, file, default_flow_style=False)

    return

def create_authenticator(config:yaml):
    """Creating the authenticator object"""
    global authenticator
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
        )
    
    return

# ----------------------------- Bevor login -----------------------------------

def login_widget():
    """Spawn a login widget"""
    try:
        authenticator.login()
    except LoginError as e:
        st.error(e)

    return

def logout_widget():
    """Logout user instant and clear user session_states"""
    st.title(f"Thank you for a visit *{st.session_state.name}*")
    authenticator.logout()
    
    if st.session_state.Logout:
        # delete user DB
        del st.session_state.df_stations_user_edit

    return

def register_new_user_widget():
    """Spawn a new user registration widget"""
    try:
        (email_of_registered_user,
            username_of_registered_user,
            name_of_registered_user) = authenticator.register_user()
        if email_of_registered_user:
            st.success('User registered successfully')
    except RegisterError as e:
        st.error(e)

    return

def forgot_password_widget():
    """Spawn a forgot password widget"""
    try:
        (username_of_forgotten_password,
            email_of_forgotten_password,
            new_random_password) = authenticator.forgot_password()
        if username_of_forgotten_password:
            st.success('New password sent securely')
            # Random password to be transferred to the user securely
        elif not username_of_forgotten_password:
            st.error('Username not found')
    except ForgotError as e:
        st.error(e)

    return

def forgot_username_widget():
    """Spawn a forgot password widget"""
    try:
        (username_of_forgotten_username,
            email_of_forgotten_username) = authenticator.forgot_username()
        if username_of_forgotten_username:
            st.success('Username sent securely')
            # Username to be transferred to the user securely
        elif not username_of_forgotten_username:
            st.error('Email not found')
    except ForgotError as e:
        st.error(e)

    return

# ----------------------------- After login -----------------------------------

def reset_password_widget():
    """Spawn a password reset widget"""
    if st.session_state['authentication_status']:
        try:
            if authenticator.reset_password(st.session_state['username']):
                st.success('Password modified successfully')
        except (CredentialsError, ResetError) as e:
            st.error(e)
    
    return

def update_user_details():
    """Spawn an update user details widget"""
    if st.session_state['authentication_status']:
        try:
            if authenticator.update_user_details(st.session_state['username']):
                st.success('Entry updated successfully')
        except UpdateError as e:
            st.error(e)
    
    return