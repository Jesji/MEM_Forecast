# App for generation project
import streamlit as st
import pandas as pd
from pathlib import Path
import glob 
import os 
import sqlite3
from ASDataBase import create_df_table, call_tables
from ASWebScraping import create_download_folder, selenium_download
from ASDash import get_df_plot
import time
import plotly.graph_objects as go


st.set_page_config(layout = "wide")
st.title("MEM Explore")
tab1, tab2, tab3 = st.tabs(["Download", "Visualization", "Forecast"])
if "data_downloaded" not in st.session_state:
    st.session_state.data_downloaded = False

with tab1:
    st.header("Donwload data from web")
    # create download folder
    download_folder = create_download_folder()
    with st.container():
        # ask for date range 
        date_range = st.slider(label="Choose range of years to download",min_value=2016,max_value=2025,value=(2023,2025))
        beginning_date, end_date = date_range
        if st.button("Donwload to DB"):
            with st.spinner("Connecting to web...", show_time=True):
                #time.sleep(5)
                selenium_download(beginning_date=beginning_date, end_date=end_date,download_folder=download_folder)
                create_df_table(download_folder=download_folder)
                st.session_state.data_downloaded = True
                st.success("Data Downloaded succesfully!")
with tab2:
    if st.session_state.data_downloaded == False:
        st.warning("Please download data first!")
    else:
        st.subheader("Energy generation by source")
        dfs = call_tables()
        options = ["Daily", "Monthly", "Yearly"]
        selection = st.segmented_control("Select frequency", options, selection_mode="single",default="Monthly")
        df_gen_res, columns_to_plot = get_df_plot(dfs, selection)
        fig = go.Figure()
        for col in columns_to_plot:
            fig.add_trace(
                go.Bar(x=df_gen_res.index, y=df_gen_res[col], name=f'{col}')
            )
        fig.update_layout(barmode='stack', title_text='Energy generation')
        st.plotly_chart(fig, use_container_width=True)



    




