import streamlit as st
from streamlit_option_menu import option_menu


sel=option_menu(None, ["Upload & Extract","Modify"])
                       #icons=["house","cloud-upload","pencil-square"],
                       #default_index=0,
                       #styles={"nav-link": {"font-size": "35px", "text-align": "centre", "margin": "-2px", "--hover-color": "#6495ED"},
                               #"icon": {"font-size": "35px"},
                               #"container" : {"max-width": "6000px"},
                               #"nav-link-selected": {"background-color": "#6495ED"}})

if sel == "Upload & Extract":
    st.subheader("Upload a Business Card")
    uploaded_card = st.file_uploader("upload here", label_visibility="collapsed", type=["png", "jpeg", "jpg"])

if sel=='Modify':
    st.subheader('Alter or delete the extracted data')
    sel1=option_menu(None,['Alter','Delete'],orientation='horizontal')

    if sel1=='Alter':
        st.write('Alter table')
    
    if sel1=='Delete':
        st.write('Delete records')