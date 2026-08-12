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
        # PSM 6 : Traite l'image comme un bloc de texte uniforme
        # On ajoute oem 3 (par défaut)
        texte_brut = pytesseract.image_to_string(img, config='--oem 3 --psm 6')
        
        # --- CORRECTION AUTOMATIQUE DES ERREURS COURANTES (OCR) ---
        # Exemple : Si un 's' ou 'S' se glisse entre deux chiffres (ex: 202s-11-11 -> 2025-11-11)
        texte_corrige = re.sub(r'(?<=\d)[sS](?=\d)', '5', texte_brut)
        
        # Vous pouvez ajouter d'autres règles si besoin (ex: O et 0)
        # texte_corrige = texte_corrige.replace('O', '0') 

        st.subheader("Résultat corrigé :")
        st.code(texte_corrige.strip())
