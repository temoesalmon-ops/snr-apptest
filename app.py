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
            ligne_prop = ligne.strip().upper()
            if not ligne_prop:
                continue
                
            # 1. En-tête (isole le chiffre avant SNR)
            if "SNR" in ligne_prop:
                match = re.search(r'([0-9])', ligne_prop)
                chiffre = match.group(1) if match else "1"
                ligne_prop = f"NZ{chiffre}SNR"

            # 2. Lignes SSVT
            elif "SSV" in ligne_prop:
                ligne_prop = re.sub(r'^.*?SSV[T1I]?', 'SSVT', ligne_prop)
                
                if 'M' in ligne_prop:
                    parts = ligne_prop.split('M', 1)
                    # Vol : force la conversion des lettres confondues en chiffres
                    vol = parts[0].replace('SSVT', '').translate(str.maketrans("SOZTLI", "502711"))
                    vol = re.sub(r'[^0-9]', '', vol)
                    
                    # Date : force les 2 premiers caractères après M en chiffres
                    reste = parts[1]
                    if len(reste) >= 2:
                        jour = reste[:2].translate(str.maketrans("SOZTLI", "502711"))
                        jour = re.sub(r'[^0-9]', '0', jour) # Sécurité
                        ligne_prop = f"SSVT{vol}M{jour}{reste[2:]}"
                        
                # Suffixe : corrige N22 ou NZ2 mal lu à la fin
                ligne_prop = re.sub(r'N[2Z]([0-9]);?$', r'NZ\1', ligne_prop)

            # 3. Lignes OS
            elif "OS" in ligne_prop or "0S" in ligne_prop:
                ligne_prop = re.sub(r'^.*?[0O]S\s*V[T1IL]', 'OS VT', ligne_prop)

            # S'assurer du point-virgule final
            ligne_prop = ligne_prop.replace(';', '') + ';'
            lignes_corrigees.append(ligne_prop)
            
        st.subheader("Résultat corrigé :")
        st.code("\n".join(lignes_corrigees))
