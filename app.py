import streamlit as st
from PIL import Image
import pytesseract

st.title("Transcripteur de Texte (OCR)")

# Uploader une image
uploaded_file = st.file_uploader("Choisissez une image...", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    st.image(img, caption="Image téléchargée", use_container_width=True)
    
    if st.button("Lancer la transcription"):
        with st.spinner("Transcription en cours..."):
            texte = pytesseract.image_to_string(img, config='--oem 3 --psm 6')
            st.subheader("Résultat :")
            st.code(texte.strip())
