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
                
            # 1. Nettoyage et normalisation de l'en-tête (Conserve n'importe quel chiffre après NZ, ex: NZ1, NZ2...)
            if "SNR" in ligne_prop or "NZ" in ligne_prop:
                ligne_prop = ligne_prop.upper()
                # Remplace les erreurs d'OCR courantes au début (ex: W2I, N2I -> NZ)
                ligne_prop = re.sub(r'^[A-Z0-9]{1,3}I?S?SNR', 'NZ1SNR', ligne_prop)
                ligne_prop = re.sub(r'([A-Z]{2})([0-9])SNR', r'\1\2SNR', ligne_prop)

            # 2. Logique Universelle pour les lignes SSVT
            if "SSV" in ligne_prop:
                ligne_prop = ligne_prop.upper()
                # Uniformise le début en SSVT propre
                ligne_prop = re.sub(r'^SSV[T1I]', 'SSVT', ligne_prop)
                
                # Expression universelle pour structurer : SSVT + [Vol] + M + [Date (Chiffres + 3 Lettres)] + [Reste]
                # Elle nettoie automatiquement les confusions d'OCR (lettres lues à la place de chiffres dans le vol)
                match = re.match(r'(SSVT)([A-Z0-9]+)M([0-9A-Z]+)', ligne_prop)
                if match:
                    prefixe, vol_brut, suite_brute = match.groups()
                    
                    # Correction universelle du numéro de vol (convertit les lettres courantes mal lues en chiffres si nécessaire)
                    vol_propre = vol_brut.replace('S', '5').replace('T', '7').replace('Z', '2').replace('O', '0').replace('I', '1')
                    
                    # Extraction universelle de la date (ex: 02SEPPPT -> 02SEP ou 31AUG)
                    # On cherche les chiffres du jour au début de la suite, suivis des 3 lettres du mois
                    match_date = re.match(r'([0-9]{1,2})([A-Z]{3})(.*)', suite_brute)
                    if match_date:
                        jour, mois, fin_ligne = match_date.groups()
                        ligne_prop = f"{prefixe}{vol_propre}M{jour}{mois}{fin_ligne}"
                    else:
                        # Fallback si la date est collée d'une autre manière
                        ligne_prop = f"{prefixe}{vol_propre}M{suite_brute}"

            # 3. Correction de la ligne OS / 0S
            if "OS" in ligne_prop or "0S" in ligne_prop:
                ligne_prop = re.sub(r'^[0oO]S\s*V[I1l]', 'OS VT', ligne_prop.upper())

            # S'assurer que chaque ligne se termine par un point-virgule
            if not ligne_prop.endswith(';'):
                ligne_prop += ';'

            lignes_corrigees.append(ligne_prop)
            
        texte_final = "\n".join(lignes_corrigees)

        st.subheader("Résultat corrigé :")
        st.code(texte_final)
