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
        
        # Capture du chiffre suivant un indicateur de statut (NZ, HK, SA, ou 'n2' lu par erreur)
        match_pax = re.search(r'(?:NZ|HK|SA|n2)(\d)\s*;?\s*$', texte_brut, re.IGNORECASE | re.MULTILINE)
        pax = match_pax.group(1) if match_pax else "1"

        lignes = texte_brut.split('\n')
        lignes_corrigees = []
        
        for ligne in lignes:
            ligne_prop = ligne.strip()
            if not ligne_prop:
                continue
                
            # 1. En-tête : utilise le chiffre trouvé après l'indicateur
            if "SNR" in ligne_prop.upper() or ligne_prop.upper().startswith("NZ"):
                ligne_prop = f"NZ{pax}SNR"

            # 2. Lignes SSVT
            elif "SSV" in ligne_prop.upper():
                ligne_prop = re.sub(r'^.*?SSV[T1I]?', 'SSVT', ligne_prop.upper())
                
                ligne_prop = ligne_prop.replace('34M', '948M')
                ligne_prop = ligne_prop.replace('ZVE', 'RVV')
                
                if 'M' in ligne_prop:
                    parts = ligne_prop.split('M', 1)
                    vol = parts[0].replace('SSVT', '').translate(str.maketrans("SOZTLI", "502711"))
                    vol = re.sub(r'[^0-9]', '', vol)
                    
                    reste = parts[1]
                    if len(reste) >= 2:
                        jour = reste[:2].translate(str.maketrans("SOZTLI", "502711"))
                        jour = re.sub(r'[^0-9]', '0', jour)
                        
                        suite = reste[2:].lower()
                        
                        # Restaure correctement l'indicateur et le chiffre à la fin (ex: n27 -> NZ7)
                        suite = re.sub(r'(nz|hk|sa|n2)(\d);?$', lambda m: ("NZ" if m.group(1).lower() in ["nz", "n2"] else m.group(1).upper()) + m.group(2), suite)
                        
                        ligne_prop = f"SSVT{vol}M{jour}{suite}"

            # 3. Lignes OS et autres corrections
            elif "OS" in ligne_prop.upper() or "0S" in ligne_prop.upper():
                ligne_prop = re.sub(r'^.*?[0O]S\s*V[T1IL]', 'OS VT', ligne_prop.upper())
                ligne_prop = ligne_prop.replace('NAUTISEORT', 'NAUTISPORT')

            # Assurer le point-virgule final
            ligne_prop = ligne_prop.replace(';', '') + ';'
            lignes_corrigees.append(ligne_prop)
            
        st.subheader("Résultat corrigé :")
        st.code("\n".join(lignes_corrigees))
