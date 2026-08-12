import streamlit as st
from PIL import Image
import pytesseract
from streamlit_paste_button import paste_image_button
import re

st.title("Transcripteur de Texte (OCR)")

paste_result = paste_image_button(label="📋 Coller une image (Ctrl+V ici)")

if paste_result.image_data is not None:
    img = paste_result.image_data
    st.image(img, caption="Image chargée", use_container_width=True)
    
    with st.spinner("Transcription en cours..."):
        texte_brut = pytesseract.image_to_string(img, config='--oem 3 --psm 6')
        
        # --- CORRECTIONS CIBLÉES DES ERREURS OCR ---
        texte_corrige = texte_brut
        texte_corrige = texte_corrige.replace("W2isNR", "NZ1SNR")
        texte_corrige = texte_corrige.replace("SSVTS", "SSVT5")
        texte_corrige = texte_corrige.replace("Os VI", "OS VT")
        texte_corrige = texte_corrige.replace("eepppt", "sepppt")
        texte_corrige = texte_corrige.replace("eepfav", "sepfav")
        texte_corrige = re.sub(r'OS\s+VI', 'OS VT', texte_corrige)

        st.subheader("Résultat corrigé :")
        st.code(texte_corrige.strip())
