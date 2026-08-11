import streamlit as st
from PIL import Image
import pytesseract
from streamlit_paste_button import paste_image_button

st.title("Code SNR en Image")

paste_result = paste_image_button(label="📋 Coller une image (Ctrl+V ici)")

if paste_result.image_data is not None:
    img = paste_result.image_data
    st.image(img, caption="Image chargée", use_container_width=True)
    
    with st.spinner("Transcription en cours..."):
        texte = pytesseract.image_to_string(img, config='--oem 3 --psm 6')
        st.subheader("Résultat :")
        st.code(texte.strip())
