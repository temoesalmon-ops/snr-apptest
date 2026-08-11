import streamlit as st
from PIL import Image
import pytesseract

st.title("Transcripteur de Texte (OCR)")

# Zone de glisser-déposer (Drag & Drop natif de Streamlit)
uploaded_file = st.file_uploader("Glissez ou déposez votre image ici...", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    st.image(img, caption="Image chargée", use_container_width=True)
    
    with st.spinner("Transcription en cours..."):
        texte = pytesseract.image_to_string(img, config='--oem 3 --psm 6')
        st.subheader("Résultat :")
        st.code(texte.strip())
