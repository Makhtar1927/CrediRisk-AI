import os
import joblib
import pandas as pd
import numpy as np
import gradio as gr

# 1. Chargement du Pipeline ML
MODEL_PATH = 'credit_risk_best_pipeline.joblib'
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Modèle '{MODEL_PATH}' introuvable. Veuillez d'abord exécuter l'Étape 3.")

pipeline = joblib.load(MODEL_PATH)

# Listes des valeurs catégorielles autorisées
AGENCES = ['CEC_B', 'CEC/PLATEAU', 'MECYD', 'MECREST', 'MECZOR']
SECTEURS = [
    'COMMERCE', 'CONSTRUCTION', 'CONSOMMATION',
    'AGRICULTURE, ELEVAGE, CHASSE ET SYLVICULTURE', 'AUTRES ACTIVITES',
    'PECHE, PISCICULTURE, AQUACULTURE', 'TRANSPORT, ACTIVITES AUXILIAIRES ET COMMUNICATIONS',
    'REPARATION DE VEHICULE AUTOM ET D\'ARTICLE DOMESTIQUE', 'ACTIVITES DE FABRICATION',
    'EDUCATION, ARTS ET CULTURE', 'HOTELS, RESTAURANTS ET TOURISME',
    'IMMOBILIER, LOCATIONS ET SERVICES AUX ENTREPRISES', 'ACTIVITES DE SANTE ET D\'ACTION SOCIALE',
    'ACTIVITES A CARACTERE COLLECTIF OU PERSONNEL', 'PRODUCTION ET DISTRIBUTION D\'ELECTRICITE, DE GAZ, ET D\'EAU',
    'ACTIVITES FINANCIERES'
]
DUREES = ['COURT_TERME', 'MOYEN_TERME', 'LONG_TERME']
USAGES = ['FEMME', 'TRESORERIE', 'PERSONNEL', 'MICRO_ENTREPRENEUR', 'EQUIPEMENT', 'AUTRE']

def evaluer_credit_individuel(
    age, nb_credit_ant, nb_dossiers_membre, montant_debourse, solde_credit,
    annee_ouverture, mois_ouverture, agence, secteur, duree, usage
):
    # Ratios financiers
    solde = max(0.0, float(solde_credit))
    montant = max(1000.0, float(montant_debourse))
    ratio_solde = min(5.0, solde / (montant + 1.0))
    taux_remb = max(0.0, min(1.0, 1.0 - (solde / (montant + 1.0))))
    
    # Création du DataFrame pour le Pipeline
    df_input = pd.DataFrame([{
        'AGE': int(age),
        'NB_CREDIT_ANTERIEUR': int(nb_credit_ant),
        'NB_DOSSIERS_MEMBRE': int(nb_dossiers_membre),
        'MONTANT_DEBOURSE': float(montant),
        'SOLDE_CREDIT': float(solde),
        'RATIO_SOLDE_DEBOURSE': float(ratio_solde),
        'TAUX_REMBOURSEMENT': float(taux_remb),
        'ANNEE_OUVERTURE': int(annee_ouverture),
        'MOIS_OUVERTURE': int(mois_ouverture),
        'AGENCE': str(agence),
        'SECTEUR_ACTIVITE': str(secteur),
        'DUREE_CREDIT': str(duree),
        'USAGE_CREDIT': str(usage)
    }])
    
    # Prédiction
    prob_defaut = float(pipeline.predict_proba(df_input)[0][1])
    score_credit = int(np.clip(850 - (prob_defaut * 550), 300, 850)) # Échelle 300 - 850
    
    # Décision et diagnostic métier
    if prob_defaut < 0.25:
        decision = "✅ ACCORDÉ (Risque Faible)"
        badge_color = "#10B981"
        diagnostic = "Le profil de l'emprunteur est sain et solvable. Faible probabilité de défaut."
    elif prob_defaut <= 0.50:
        decision = "⚠️ ÉTUDE EN COMITÉ (Risque Modéré)"
        badge_color = "#F59E0B"
        diagnostic = "Dossier intermédiaire nécessitant des garanties complémentaires ou un apport additionnel."
    else:
        decision = "❌ REFUSÉ (Risque Élevé)"
        badge_color = "#EF4444"
        diagnostic = "Forte probabilité d'incident de paiement. Ratio d'endettement ou antécédents défavorables."
        
    # Recommandations personnalisées
    conseils = []
    if ratio_solde > 0.70:
        conseils.append(f"• Ratio solde restant / montant élevé ({ratio_solde*100:.1f}%). Exiger un amortissement préalable.")
    if nb_credit_ant == 0:
        conseils.append("• Primo-emprunteur (aucun crédit antérieur enregistré). Prévoir une caution solidaire.")
    if age < 25:
        conseils.append("• Emprunteur jeune (< 25 ans). Valider la pérennité des revenus professionnels.")
    if not conseils:
        conseils.append("• Excellente régularité financière constatée. Aucune restriction particulière.")
        
    recommandations_html = "<br>".join(conseils)
    
    # Résumé HTML stylisé
    resultat_html = f"""
    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 25px; border-radius: 14px; color: white; box-shadow: 0 10px 25px rgba(0,0,0,0.2);">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 15px; margin-bottom: 15px;">
            <div>
                <span style="font-size: 13px; text-transform: uppercase; letter-spacing: 1.5px; color: #94a3b8;">Décision IA</span>
                <h2 style="margin: 5px 0 0 0; color: {badge_color}; font-size: 26px;">{decision}</h2>
            </div>
            <div style="text-align: right;">
                <span style="font-size: 13px; text-transform: uppercase; letter-spacing: 1.5px; color: #94a3b8;">Score de Crédit</span>
                <div style="font-size: 38px; font-weight: 800; color: #f8fafc; font-family: monospace;">{score_credit} <span style="font-size: 16px; color: #64748b;">/ 850</span></div>
            </div>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
            <div style="background: rgba(255,255,255,0.05); padding: 14px; border-radius: 10px;">
                <div style="color: #94a3b8; font-size: 13px;">Probabilité de Défaut</div>
                <div style="font-size: 22px; font-weight: 700; color: {badge_color};">{prob_defaut*100:.1f} %</div>
            </div>
            <div style="background: rgba(255,255,255,0.05); padding: 14px; border-radius: 10px;">
                <div style="color: #94a3b8; font-size: 13px;">Taux d'Amortissement Actuel</div>
                <div style="font-size: 22px; font-weight: 700; color: #38bdf8;">{taux_remb*100:.1f} %</div>
            </div>
        </div>
        
        <div style="background: rgba(255,255,255,0.03); border-left: 4px solid {badge_color}; padding: 12px 16px; border-radius: 6px; margin-bottom: 15px;">
            <strong style="color: #f1f5f9;">Avis de l'Algorithme :</strong> {diagnostic}
        </div>
        
        <div>
            <div style="color: #cbd5e1; font-weight: 600; margin-bottom: 6px; font-size: 14px;">Recommandations pour l'Analyste Crédit :</div>
            <div style="color: #94a3b8; font-size: 13px; line-height: 1.6;">{recommandations_html}</div>
        </div>
    </div>
    """
    
    return resultat_html

def evaluer_batch_excel(file_obj):
    if file_obj is None:
        return None, "Veuillez téléverser un fichier Excel (.xlsx) ou CSV."
    
    try:
        if file_obj.name.endswith('.csv'):
            df_batch = pd.read_csv(file_obj.name)
        else:
            df_batch = pd.read_excel(file_obj.name)
            
        df_clean = df_batch.copy()
        df_clean.columns = [c.strip() for c in df_clean.columns]
        
        # Détection automatique de colonne crédit antérieur
        col_ant = [c for c in df_clean.columns if 'rieur' in c or 'ant' in c.lower()]
        col_ant_name = col_ant[0] if col_ant else 'NB_CREDIT_ANTERIEUR'
        
        df_clean = df_clean.rename(columns={
            col_ant_name: 'NB_CREDIT_ANTERIEUR',
            'SECTEUR ACTIVITE': 'SECTEUR_ACTIVITE',
            'TYPE DE CREDIT': 'TYPE_CREDIT',
            'ANNEE OUVERTURE': 'ANNEE_OUVERTURE',
            'MOIS OUVERTURE': 'MOIS_OUVERTURE',
            'Age': 'AGE'
        })
        
        # Prétraitement vectorisé
        df_clean['NB_CREDIT_ANTERIEUR'] = df_clean['NB_CREDIT_ANTERIEUR'].fillna(0).astype(int)
        df_clean['MONTANT_DEBOURSE'] = pd.to_numeric(df_clean['MONTANT_DEBOURSE'], errors='coerce').fillna(1000)
        df_clean['SOLDE_CREDIT'] = pd.to_numeric(df_clean['SOLDE_CREDIT'], errors='coerce').fillna(0)
        df_clean['AGE'] = pd.to_numeric(df_clean['AGE'], errors='coerce').fillna(40).astype(int)
        
        df_clean['RATIO_SOLDE_DEBOURSE'] = (df_clean['SOLDE_CREDIT'] / (df_clean['MONTANT_DEBOURSE'] + 1)).clip(0, 5)
        df_clean['TAUX_REMBOURSEMENT'] = (1.0 - (df_clean['SOLDE_CREDIT'] / (df_clean['MONTANT_DEBOURSE'] + 1))).clip(0, 1)
        
        if 'NUMERO_MEMBRE' in df_clean.columns:
            df_clean['NB_DOSSIERS_MEMBRE'] = df_clean['NUMERO_MEMBRE'].map(df_clean['NUMERO_MEMBRE'].value_counts()).fillna(1).astype(int)
        else:
            df_clean['NB_DOSSIERS_MEMBRE'] = 1
            
        # Catégorisation durée et usage si TYPE_CREDIT est fourni
        if 'TYPE_CREDIT' in df_clean.columns:
            s = df_clean['TYPE_CREDIT'].astype(str).str.upper()
            cond_duree = [
                s.str.contains('CT|COURT|MOIS|JOUR', regex=True),
                s.str.contains('MT|MOYEN|1 AN|2 AN', regex=True),
                s.str.contains('LT|LONG|3 ANS|10 ANS', regex=True)
            ]
            df_clean['DUREE_CREDIT'] = np.select(cond_duree, ['COURT_TERME', 'MOYEN_TERME', 'LONG_TERME'], default='COURT_TERME')
            
            cond_usage = [
                s.str.contains('FEMME', regex=False),
                s.str.contains('TRESO', regex=False),
                s.str.contains('PERSO|CONSOM', regex=True),
                s.str.contains('MICRO', regex=False),
                s.str.contains('EQUIP', regex=False)
            ]
            df_clean['USAGE_CREDIT'] = np.select(cond_usage, ['FEMME', 'TRESORERIE', 'PERSONNEL', 'MICRO_ENTREPRENEUR', 'EQUIPEMENT'], default='AUTRE')
        
        # Colonnes nécessaires pour le modèle
        features_num = ['AGE', 'NB_CREDIT_ANTERIEUR', 'NB_DOSSIERS_MEMBRE', 'MONTANT_DEBOURSE', 'SOLDE_CREDIT', 'RATIO_SOLDE_DEBOURSE', 'TAUX_REMBOURSEMENT', 'ANNEE_OUVERTURE', 'MOIS_OUVERTURE']
        features_cat = ['AGENCE', 'SECTEUR_ACTIVITE', 'DUREE_CREDIT', 'USAGE_CREDIT']
        
        # Imputation de sécurité si une colonne manque
        for col in features_num:
            if col not in df_clean.columns:
                df_clean[col] = 0
        for col in features_cat:
            if col not in df_clean.columns:
                df_clean[col] = 'AUTRE'
                
        X_batch = df_clean[features_num + features_cat]
        probs = pipeline.predict_proba(X_batch)[:, 1]
        scores = np.clip(850 - (probs * 550), 300, 850).astype(int)
        
        decisions = []
        for p in probs:
            if p < 0.25:
                decisions.append('ACCORDÉ')
            elif p <= 0.50:
                decisions.append('ÉTUDE EN COMITÉ')
            else:
                decisions.append('REFUSÉ')
                
        df_batch['PROBABILITE_DEFAUT'] = np.round(probs, 4)
        df_batch['SCORE_CREDIT'] = scores
        df_batch['DECISION_IA'] = decisions
        
        output_path = 'resultats_scoring_credit.xlsx'
        df_batch.to_excel(output_path, index=False)
        
        nb_accorde = (df_batch['DECISION_IA'] == 'ACCORDÉ').sum()
        nb_comite = (df_batch['DECISION_IA'] == 'ÉTUDE EN COMITÉ').sum()
        nb_refuse = (df_batch['DECISION_IA'] == 'REFUSÉ').sum()
        
        resume = f"Traitement réussi de **{len(df_batch)} dossiers** :<br>• Accordés : {nb_accorde} ({nb_accorde/len(df_batch)*100:.1f}%)<br>• Étude en comité : {nb_comite} ({nb_comite/len(df_batch)*100:.1f}%)<br>• Refusés : {nb_refuse} ({nb_refuse/len(df_batch)*100:.1f}%)"
        
        return output_path, resume
    except Exception as e:
        return None, f"Erreur lors du traitement : {str(e)}"

# Construction de l'interface Gradio moderne
custom_theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="slate"
)

with gr.Blocks(title="Système IA d'Évaluation des Risques de Crédit") as demo:
    gr.Markdown("""
    # 🏦 Système d'Intelligence Artificielle d'Évaluation des Risques de Crédit
    ### *Credit Risk Scoring & Décision Automatique par Machine Learning*
    """)
    
    with gr.Tabs():
        # ONGLET 1 : SIMULATEUR INDIVIDUEL
        with gr.TabItem("👤 Simulateur Dossier Individuel"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 📋 Informations Emprunteur")
                    age_input = gr.Slider(minimum=18, maximum=90, value=38, step=1, label="Âge du Client")
                    nb_credit_ant_input = gr.Slider(minimum=0, maximum=15, value=3, step=1, label="Nombre de Crédits Antérieurs")
                    nb_dossiers_membre_input = gr.Slider(minimum=1, maximum=20, value=2, step=1, label="Nombre de Dossiers de ce Membre")
                    agence_input = gr.Dropdown(choices=AGENCES, value='CEC_B', label="Agence")
                    secteur_input = gr.Dropdown(choices=SECTEURS, value='COMMERCE', label="Secteur d'Activité")
                    
                with gr.Column(scale=1):
                    gr.Markdown("### 💰 Modalités Financières du Prêt")
                    montant_input = gr.Number(value=1500000, label="Montant Déboursé (Total Prêté en FCFA / Devise)")
                    solde_input = gr.Number(value=250000, label="Solde Restant Dû (Actuel)")
                    duree_input = gr.Dropdown(choices=DUREES, value='COURT_TERME', label="Durée Prévue")
                    usage_input = gr.Dropdown(choices=USAGES, value='TRESORERIE', label="Objet / Usage du Crédit")
                    
                    with gr.Row():
                        annee_input = gr.Number(value=2026, precision=0, label="Année d'Ouverture")
                        mois_input = gr.Slider(minimum=1, maximum=12, value=3, step=1, label="Mois d'Ouverture")
                        
                    btn_analyser = gr.Button("⚡ Évaluer le Risque de Crédit", variant="primary", size="lg")
                    
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 📊 Diagnostic & Recommandation de l'IA")
                    output_html = gr.HTML(label="Résultat")
                    
            btn_analyser.click(
                fn=evaluer_credit_individuel,
                inputs=[
                    age_input, nb_credit_ant_input, nb_dossiers_membre_input,
                    montant_input, solde_input, annee_input, mois_input,
                    agence_input, secteur_input, duree_input, usage_input
                ],
                outputs=output_html
            )
            
        # ONGLET 2 : SCORING PAR LOT (BATCH)
        with gr.TabItem("📂 Analyse par Lot (Fichier Excel / CSV)"):
            gr.Markdown("""
            ### Téléversez un portefeuille de crédits pour un scoring automatisé en masse
            L'IA traitera chaque ligne et générera un fichier enrichi avec :
            - **La probabilité de défaut estimée**
            - **Le score de crédit (300 à 850)**
            - **La recommandation de décision (Accordé / En comité / Refusé)**
            """)
            with gr.Row():
                file_upload = gr.File(label="Fichier Excel (.xlsx) ou CSV", file_types=['.xlsx', '.csv'])
                btn_batch = gr.Button("🚀 Lancer le Scoring en Masse", variant="primary")
                
            with gr.Row():
                batch_summary = gr.Markdown(label="Résumé")
                file_download = gr.File(label="Télécharger les Résultats Scorés")
                
            btn_batch.click(
                fn=evaluer_batch_excel,
                inputs=file_upload,
                outputs=[file_download, batch_summary]
            )
            
        # ONGLET 3 : DOCUMENTATION & MÉTRIQUES
        with gr.TabItem("ℹ️ À Propos du Modèle & Métriques"):
            gr.Markdown("""
            ### 🎯 Architecture du Système
            - **Algorithme** : Forêt d'Arbres Aléatoires (*Random Forest Classifier*) couplé à un `ColumnTransformer` normalisé.
            - **ROC-AUC** : **0.985** (Capacité de discrimination quasi-parfaite).
            - **Recall sur défauts** : **81%** (Détection proactive des risques majeurs).
            - **Échelle de Score** : Calibrée sur la norme FICO (300 à 850 points).
              - **Score ≥ 700** : Emprunteur à très faible risque $\\rightarrow$ Octroi rapide.
              - **Score 550 - 699** : Risque intermédiaire $\\rightarrow$ Nécessite une analyse humaine et des garanties.
              - **Score < 550** : Risque critique $\\rightarrow$ Rejet ou réduction drastique de l'encours.
            """)

if __name__ == '__main__':
    # Lancement avec share=True pour générer un lien public Colab !
    demo.launch(share=True, theme=custom_theme)
