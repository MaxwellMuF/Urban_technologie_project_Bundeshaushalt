import streamlit as st
# Own python files
from application.src.utilities import methods_login

# Initialize st.session_state (st.Class properties) at start or reload of app/page. 
def init_st_session_state():
    """Initialize all streamlit.session_states that are needed or required in the app."""

    if "submited_post" not in st.session_state:
        st.session_state.submited_post = False
    return

# ------------------------------- Pages --------------------------------------

def pages_bevor_login():
    """Pages of streamlit app bevor login defined by functions"""
    login = st.Page(methods_login.login_widget, title="Login", icon=":material/home:")
    register_new_user = st.Page(methods_login.register_new_user_widget, title="Sign Up", icon=":material/person_add:")
    forgot_password = st.Page(methods_login.forgot_password_widget, title="Forget Password", icon=":material/lock_reset:")
    forgot_username = st.Page(methods_login.forgot_username_widget, title="Forget Username", icon=":material/help_outline:")

    return [login, register_new_user, forgot_password, forgot_username]

def pages_after_login():
    """Pages of streamlit app after login defined by functions and python files"""
    welcome = st.Page("application/src/ui/streamlit_pages/page_1_welcome.py", title="Welcome", icon=":material/home:")
    raw_data = st.Page("application/src/ui/streamlit_pages/page_2_raw_data.py", title="Raw data", icon=":material/dataset:")
    haushalt = st.Page("application/src/ui/streamlit_pages/page_3_12years.py", title="12 years Bundeshaushalt", icon=":material/monitoring:")
    reset_password = st.Page(methods_login.reset_password_widget, title="Reset Password", icon=":material/lock_reset:")
    logout = st.Page(methods_login.logout_widget, title="Logout", icon=":material/home:")

    return [welcome, raw_data, haushalt, reset_password, logout]

def main():
    """
    Main function of the entire steamlit app. 
    This is where the navigator is defined that leads to all scripts and functions. 
    And the authenticator process is called.
    """
    init_st_session_state()
    # load authenticator config and create login st.authenticator
    config = methods_login.load_config(config_path="application/data/config.yaml")
    methods_login.create_authenticator(config)

    # Show pages before a user is logged in
    if not st.session_state.authentication_status:
        page_navigator = st.navigation(pages_bevor_login())
        page_navigator.run()
    
    # Show pages after a user is logged in (Note: st.authenticator uses browser cookies)
    elif st.session_state.authentication_status:
        page_navigator = st.navigation(pages_after_login())
        page_navigator.run()

    # Catches some unexpected login problems. Should not occur.
    else:
        print("We should never get here!")
    
    # save authenticator config
    methods_login.save_config(config, config_path="application/data/config.yaml")
    
    return

if __name__ == "__main__":
    main()