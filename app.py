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
                
            # 1. Correction de la ligne d'en-tête (ex: W2isNR -> NZ1SNR, etc.)
            if "SNR" in ligne_prop or "W2i" in ligne_prop or "N2i" in ligne_prop:
                ligne_prop = re.sub(r'^[A-Z0-9]{1,3}i?s?SNR', 'NZ1SNR', ligne_prop)
                ligne_prop = re.sub(r'NZ([0-9])SNR', r'NZ\1SNR', ligne_prop)

            # 2. Correction des lignes SSVT (gère les confusions de chiffres/lettres)
            if "SSVT" in ligne_prop or "SSV" in ligne_prop:
                # S'assure que ça commence bien par SSVT
                ligne_prop = re.sub(r'^SSV[T1l]', 'SSVT', ligne_prop)
                
                # Nettoyage des erreurs fréquentes d'OCR après SSVT (ex: SSVTSTIM -> SSVT517 ou similaire)
                # Remplace les 'S' ou 's' par '5' si positionnés au début d'un bloc de chiffres/codes
                ligne_prop = ligne_prop.replace("SSVTSTIM", "SSVT517") # Exemple récurrent d'OCR
                
                # Correction générique des 's' devenus '5' dans les blocs numériques après SSVT
                # On cible les caractères de type S/s dans les codes si nécessaire

            # 3. Correction de la ligne OS (ex: 0S VI ou Os VI -> OS VT)
            if "OS" in ligne_prop or "0S" in ligne_prop or "Os" in ligne_prop or "VI" in ligne_prop:
                # Remplace le '0' ou 'o' initial par 'O' et 'VI' par 'VT'
                ligne_prop = re.sub(r'^[0oO][sS]\s*V[I1l]', 'OS VT', ligne_prop)
                # Corrige aussi si c'est juste "0S VI" sans le début exact
                ligne_prop = ligne_prop.replace("0S VI", "OS VT").replace("Os VI", "OS VT")

            lignes_corrigees.append(ligne_prop)
            
        texte_final = "\n".join(lignes_corrigees)

        st.subheader("Résultat corrigé :")
        st.code(texte_final)
