import streamlit as st
from page_model import display
import os
import warnings
warnings.filterwarnings('ignore')

path = os.getcwd()
path = '/'.join(path.split('\\')[:-1])
st.set_page_config(layout="wide")

with st.sidebar:
    add_radio = st.radio(
        "Self-Regulation Learning Report",
        ("Home", "Item 1", "Item 2", "Item 3", "Item 4", 'Model')
    )

# if add_radio == 'Model':
display(f'model.json')
