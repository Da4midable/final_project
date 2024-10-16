import streamlit as st

st.write("Hello World")
x = st.text_input('Favourite movie?')
st.write(f'Your favourite movie is {x.upper()}')