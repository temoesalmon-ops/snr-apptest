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
        
        lignes = texte_brut.split('\n')
        lignes_corrigees = []
        
        for ligne in lignes:
            ligne_prop = ligne.strip()
            if not ligne_prop:
                continue
                
            # 1. Correction de l'en-tête (Garde le chiffre après NZ, ex: NZ2SNR, NZ1SNR)
            if "SNR" in ligne_prop or "NZ" in ligne_prop:
                ligne_prop = ligne_prop.upper()
                ligne_prop = re.sub(r'^[A-Z0-9]{1,3}I?S?SNR', 'NZ1SNR', ligne_prop)
                ligne_prop = re.sub(r'([A-Z]{2})([0-9])SNR', r'\1\2SNR', ligne_prop)

            # 2. Correction des lignes SSVT
            if "SSV" in ligne_prop:
                ligne_prop = ligne_prop.upper()
                ligne_prop = re.sub(r'^SSV[T1I]', 'SSVT', ligne_prop)
                
                # Corrections spécifiques des erreurs d'OCR fréquentes sur les vols 571
                ligne_prop = ligne_prop.replace("SSVTSTIMOZ", "SSVT571M02")
                ligne_prop = ligne_prop.replace("SSVTSTIMIS", "SSVT571M15")
                
                # Correction générale si des lettres 'T' se glissent à la place de chiffres dans le vol (ex: SSVTSTIM -> SSVT571)
                ligne_prop = re.sub(r'SSVTSTIM', 'SSVT571', ligne_prop)

            # 3. Correction de la ligne OS
            if "OS" in ligne_prop or "0S" in ligne_prop or "OS" in ligne_prop:
                ligne_prop = re.sub(r'^[0oO]S\s*V[I1l]', 'OS VT', ligne_prop.upper())

            # S'assurer que chaque ligne se termine par un point-virgule
            if not ligne_prop.endswith(';'):
                ligne_prop += ';'

            lignes_corrigees.append(ligne_prop)
            
        texte_final = "\n".join(lignes_corrigees)

        st.subheader("Résultat corrigé :")
        st.code(texte_final)
