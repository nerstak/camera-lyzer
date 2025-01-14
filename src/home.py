from constants import INPUT_BASE_DIRECTORY, INPUT_GLOB_RAW_PICTURES, INPUT_GLOB_PROCESSED_PICTURES
from elements.charts import charts
from elements.sidebar import init_sidebar

import polars as pl
import streamlit as st

from exif_loader.exif_loader import load_dataframe_pictures

st.set_page_config(
    layout='wide',
    page_icon=':camera:',
    page_title='Camera Lyzer',
    initial_sidebar_state='expanded',
)
init_sidebar(
    base_directory_key=INPUT_BASE_DIRECTORY,
    glob_raw_pictures_key=INPUT_GLOB_RAW_PICTURES,
    glob_processed_pictures_key=INPUT_GLOB_PROCESSED_PICTURES,
)

if INPUT_BASE_DIRECTORY in st.session_state:
    raw_df = pl.DataFrame()
    processed_df = pl.DataFrame()
    raw_errors = ''
    processed_errors = ''

    if INPUT_GLOB_RAW_PICTURES in st.session_state:
        raw_df, raw_errors = load_dataframe_pictures(
            st.session_state[INPUT_BASE_DIRECTORY], st.session_state[INPUT_GLOB_RAW_PICTURES], 'Raw'
        )

    if INPUT_GLOB_PROCESSED_PICTURES in st.session_state:
        processed_df, processed_errors = load_dataframe_pictures(
            st.session_state[INPUT_BASE_DIRECTORY], st.session_state[INPUT_GLOB_PROCESSED_PICTURES], 'Processed'
        )

    if 0 < len(raw_df.columns) == len(processed_df.columns) and len(processed_df.columns) > 0:
        charts(pl.concat([raw_df, processed_df]))
    elif len(raw_df.columns) != len(processed_df.columns):
        st.error('Could not load pictures' +
                 (f' "Raw": {raw_errors}' if raw_errors else '') +
                 (f' "Processed": {processed_errors}' if processed_errors else '')
                 )
    else:
        st.warning('Please fill the sidebar inputs')
