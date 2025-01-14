import os
import streamlit as st


def init_sidebar(
        base_directory_key: str,
        glob_raw_pictures_key: str,
        glob_processed_pictures_key,
):
    with st.sidebar:
        def callback_path():
            if base_directory_key in st.session_state:
                if not os.path.isdir(st.session_state[base_directory_key]):
                    st.sidebar.error(f'{st.session_state[base_directory_key]} does not exists', icon="🚨")

        st.title('Input parameters')

        st.text_input(
            label='Global directory',
            help='Global common directory in which all of your pictures will be',
            placeholder='C:\\Users\\you\\Pictures\\Photos',
            key=base_directory_key,
            on_change=callback_path,
        )

        st.text_input(
            label='Glob path of raw images, relative to Base Directory',
            help='Glob that will identify your RAW pictures (actual RAW files not supported for the moment, use jpg from camera)',
            placeholder='**\\**\\RAW\\*.JPG',
            key=glob_raw_pictures_key,
        )

        st.text_input(
            label='Glob path of processed images, relative to Base Directory',
            help='Glob that will identify your processed pictures',
            placeholder='**\\**\\Traité*\\*',
            key=glob_processed_pictures_key,
        )

        st.divider()
        st.markdown('# Getting started with glob path\n'
                    '- [Glob path Python Documentation](https://docs.python.org/3/library/glob.html)\n'
                    '- [Glob path beginner guide](https://www.malikbrowne.com/blog/a-beginners-guide-glob-patterns/)\n')
