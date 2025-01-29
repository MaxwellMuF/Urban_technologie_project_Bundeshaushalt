import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

def plot_df(df, title):
    fig = plt.figure(figsize=(12, 8))
    plt.style.use('ggplot')  # You can choose other styles like 'ggplot', 'fivethirtyeight', etc.

    # Plotting the DataFrame and set title and axes labels
    df.plot(ax=plt.gca())
    plt.title(label=title, fontsize=16, fontweight='bold')
    plt.xlabel("Years", fontsize=14)
    plt.ylabel("Booking value [€]", fontsize=14)

    # Ticks and legend
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(fontsize=12, loc="best")

    # Show the plot
    st.pyplot(fig)
    return