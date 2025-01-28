import streamlit as st

def welcome_text():
    """Welcome text with user """
    st.header(f'Welcome *{st.session_state.get("name", "Guest_default_for_testing")}*') # Use get method to run tests
    st.write(f'Have you ever wondered what the state spends your taxes on? This project is \
             designed to give you an insight into the federal budget over the last 12 years.')

    return

def image_with_motivation():
    """Show images and motiavtion text"""
    with st.container(border=True):
        st.header("The state handles a lot of money. But what exactly does it spend it on?")
        col1, col2 = st.columns(2)
        with col1:
            st.image("application/data/images/Bundestag.jpg")
        with col2:
            st.image("application/data/images/Bundespräsidentin.jpg")
        st.write('"Beratung des Antrags des Bundeskanzlers gemäß Artikel 68 des Grundgesetzes Drucksache 20/14150" (Quelle: "Deutscher Bundestag/Thomas Köhler/photothek", https://bilddatenbank.bundestag.de/search/picture-result?query=&filterQuery%5Bort%5D%5B0%5D=Reichstagsgeb%C3%A4ude%2C+Plenarsaal&sortVal=3#group-55)')

    return
        
def main():
    """Main of the Welcome page: Calls up text and images."""
    welcome_text()
    image_with_motivation()

# call main directly because of st.navigation
main()