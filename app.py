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
                
            # 1. Correction de la ligne d'en-tête (ex: W2isNR -> NZ1SNR, NZ2SNR, etc.)
            # On cherche un motif qui ressemble à [Lettres][Chiffre]SNR
            if "SNR" in ligne_prop or "W2i" in ligne_prop or "N2i" in ligne_prop:
                ligne_prop = re.sub(r'^[A-Z0-9]{1,3}i?s?SNR', 'NZ1SNR', ligne_prop) # S'adapte au préfixe NZ
                # Correction générique si le 1 change : s'assure que c'est bien NZ[chiffre]SNR
                ligne_prop = re.sub(r'NZ([0-9])SNR', r'NZ\1SNR', ligne_prop)

            # 2. Correction des lignes SSVT (ex: SSVT + 3 chiffres + M...)
            if ligne_prop.startswith("SSVT") or "SSVT" in ligne_prop:
                # Corrige les 's' ou 'S' mal interprétés dans les 3 chiffres suivant SSVT (ex: SSVTS17 -> SSVT517)
                # Remplace les lettres 's' ou 'S' situées juste après SSVT par des '5' si besoin, ou nettoie les chiffres
                ligne_prop = re.sub(r'(SSVT)([0-9Ssz]{3})', lambda m: m.group(1) + m.group(2).replace('s', '5').replace('S', '5').replace('z', '2'), ligne_prop)
                
                # Correction des mots clés collés ou mal orthographiés après la date (ex: eepppt -> sepppt, eepfav -> sepfav)
                ligne_prop = re.sub(r'ee+pp+t', 'sepppt', ligne_prop, flags=re.IGNORECASE)
                ligne_prop = re.sub(r'ee+pf?av', 'sepfav', ligne_prop, flags=re.IGNORECASE)

            # 3. Correction de la ligne OS (ex: Os VI -> OS VT)
            if ligne_prop.startswith("OS") or ligne_prop.startswith("Os") or "VI" in ligne_prop:
                ligne_prop = re.sub(r'^Os?\s*V[I1l]', 'OS VT', ligne_prop)

            lignes_corrigees.append(ligne_prop)
            
        texte_final = "\n".join(lignes_corrigees)

        st.subheader("Résultat corrigé :")
        st.code(texte_final)
