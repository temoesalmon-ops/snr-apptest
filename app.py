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
                
            # 1. Correction de l'en-tête
            if "SNR" in ligne_prop or "W2I" in ligne_prop or "N2I" in ligne_prop or "NZ" in ligne_prop:
                ligne_prop = re.sub(r'^[A-Z0-9]{1,3}I?S?SNR', 'NZ1SNR', ligne_prop.upper())
                ligne_prop = re.sub(r'NZ([0-9])SNR', r'NZ\1SNR', ligne_prop)

            # 2. Correction des lignes SSVT (Format: SSVT + Vol + M + Date + Origine/Dest + Suffixe)
            if "SSVT" in ligne_prop or "SSV" in ligne_prop:
                ligne_prop = ligne_prop.upper()
                ligne_prop = re.sub(r'^SSV[T1I]', 'SSVT', ligne_prop)
                
                # Correction du numéro de vol après SSVT (ex: S20 -> 520)
                match = re.match(r'(SSVT)([0-9SszO0]+)(M.*)', ligne_prop)
                if match:
                    prefix, vol, reste = match.groups()
                    vol = vol.replace('S', '5').replace('Z', '2').replace('O', '0')
                    
                    # Recherche et correction propre du format de date (ex: 31AUG, 15FEB) précédé par 'M'
                    # On s'assure que le format de la date est bien [1-31][3 lettres du mois]
                    reste_corrige = re.sub(r'M([0-9]{1,2})([A-Z]{3})', r'M\1\2', reste)
                    
                    ligne_prop = prefix + vol + reste_corrige

            # 3. Correction de la ligne OS
            if "OS" in ligne_prop or "0S" in ligne_prop:
                ligne_prop = re.sub(r'^[0oO]S\s*V[I1l]', 'OS VT', ligne_prop.upper())

            # S'assurer que chaque ligne se termine par un point-virgule
            if not ligne_prop.endswith(';'):
                ligne_prop += ';'

            lignes_corrigees.append(ligne_prop)
            
        texte_final = "\n".join(lignes_corrigees)

        st.subheader("Résultat corrigé :")
        st.code(texte_final)
