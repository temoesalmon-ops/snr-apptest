import streamlit as st
from PIL import Image
import pytesseract
from streamlit_paste_button import paste_image_button

st.title("Transcripteur de Texte (OCR)")

# Option de collage direct depuis le presse-papier
paste_result = paste_image_button(label="📋 Coller une image (Ctrl+V ici)")

# Option classique de fichier / glisser-déposer
uploaded_file = st.file_uploader("Ou glissez/uploadez un fichier...", type=["png", "jpg", "jpeg"])

img = None

if paste_result.image_data is not None:
    img = paste_result.image_data
elif uploaded_file is not None:
    img = Image.open(uploaded_file)

if img is not None:
    st.image(img, caption="Image chargée", use_container_width=True)
    
    with st.spinner("Transcription en cours..."):
        texte = pytesseract.image_to_string(img, config='--oem 3 --psm 6')
        st.subheader("Résultat :")
        st.code(texte.strip())
