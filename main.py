import os
import io
import joblib
import pandas as pd
import numpy as np
import time
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

# Timestamp de démarrage pour métriques uptime
SERVER_START_TIME = time.time()

# 1. Initialisation FastAPI
app = FastAPI(
    title="CrediRisk AI API",
    description="Système d'Intelligence Artificielle d'Évaluation des Risques de Crédit",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoints de santé pour Cronjobs (Keep-Alive Render / UptimeRobot / cron-job.org)
@app.get("/health", tags=["Health"])
@app.get("/healthz", tags=["Health"])
@app.get("/api/health", tags=["Health"])
def health_check():
    uptime_sec = int(time.time() - SERVER_START_TIME)
    status = "healthy" if pipeline is not None else "degraded"
    return {
        "status": status,
        "service": "CrediRisk AI",
        "version": "2.0.0",
        "model_loaded": pipeline is not None,
        "model_path": LOADED_MODEL_PATH,
        "model_error": MODEL_ERROR,
        "uptime_seconds": uptime_sec,
        "timestamp": int(time.time())
    }

# 2. Chargement du Pipeline Machine Learning
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILENAME = "credit_risk_best_pipeline.joblib"

POSSIBLE_PATHS = [
    os.path.join(BASE_DIR, MODEL_FILENAME),
    os.path.join(os.getcwd(), MODEL_FILENAME),
    MODEL_FILENAME,
    os.path.abspath(MODEL_FILENAME),
]

pipeline = None
MODEL_ERROR = None
LOADED_MODEL_PATH = None

found_path = None
for p in POSSIBLE_PATHS:
    if os.path.exists(p):
        found_path = p
        break

if found_path is not None:
    try:
        pipeline = joblib.load(found_path)
        LOADED_MODEL_PATH = found_path
        print(f"[INFO] Pipeline Machine Learning charge avec succes depuis : {found_path}")
    except Exception as e:
        import traceback
        MODEL_ERROR = f"{type(e).__name__}: {str(e)}"
        print(f"[ERREUR] Erreur lors du chargement du modele ({found_path}) : {e}")
        traceback.print_exc()
else:
    checked_str = ", ".join(POSSIBLE_PATHS)
    MODEL_ERROR = f"Fichier {MODEL_FILENAME} introuvable. Chemins verifies : {checked_str}"
    print(f"[ATTENTION] {MODEL_ERROR}")

# Référentiels
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

# 3. Schémas Pydantic
class CreditRequest(BaseModel):
    age: int = Field(38, ge=18, le=100, description="Âge de l'emprunteur")
    nb_credit_ant: int = Field(3, ge=0, le=20, description="Nombre de crédits antérieurs")
    nb_dossiers_membre: int = Field(2, ge=1, le=20, description="Nombre total de dossiers de ce membre")
    montant_debourse: float = Field(1500000.0, ge=1000.0, description="Montant total déboursé")
    solde_credit: float = Field(200000.0, ge=0.0, description="Solde restant dû actuel")
    annee_ouverture: int = Field(2026, ge=2015, le=2030, description="Année d'ouverture du crédit")
    mois_ouverture: int = Field(4, ge=1, le=12, description="Mois d'ouverture")
    agence: str = Field("CEC_B", description="Agence bancaire émettrice")
    secteur_activite: str = Field("COMMERCE", description="Secteur d'activité")
    duree_credit: str = Field("COURT_TERME", description="Durée prévue du crédit")
    usage_credit: str = Field("TRESORERIE", description="Usage ou type de produit")

class CreditResponse(BaseModel):
    score_credit: int
    probabilite_defaut: float
    decision: str
    decision_code: str
    classe_risque: str
    taux_remboursement: float
    ratio_solde_debourse: float
    diagnostic: str
    points_forts: list[str]
    points_vigilance: list[str]
    recommandations: list[str]

# 4. Endpoints Métier
@app.post("/api/predict", response_model=CreditResponse)
def predict_credit_risk(payload: CreditRequest):
    if pipeline is None:
        raise HTTPException(status_code=500, detail="Modèle ML non disponible sur le serveur.")

    solde = max(0.0, float(payload.solde_credit))
    montant = max(1000.0, float(payload.montant_debourse))
    ratio_solde = float(np.clip(solde / (montant + 1.0), 0.0, 5.0))
    taux_remb = float(np.clip(1.0 - ratio_solde, 0.0, 1.0))

    df_input = pd.DataFrame([{
        'AGE': int(payload.age),
        'NB_CREDIT_ANTERIEUR': int(payload.nb_credit_ant),
        'NB_DOSSIERS_MEMBRE': int(payload.nb_dossiers_membre),
        'MONTANT_DEBOURSE': float(montant),
        'SOLDE_CREDIT': float(solde),
        'RATIO_SOLDE_DEBOURSE': ratio_solde,
        'TAUX_REMBOURSEMENT': taux_remb,
        'ANNEE_OUVERTURE': int(payload.annee_ouverture),
        'MOIS_OUVERTURE': int(payload.mois_ouverture),
        'AGENCE': str(payload.agence),
        'SECTEUR_ACTIVITE': str(payload.secteur_activite),
        'DUREE_CREDIT': str(payload.duree_credit),
        'USAGE_CREDIT': str(payload.usage_credit)
    }])

    prob_defaut = float(pipeline.predict_proba(df_input)[0][1])
    score_credit = int(np.clip(850 - (prob_defaut * 550), 300, 850))

    points_forts = []
    points_vigilance = []
    recommandations = []

    # Diagnostic & Décision
    if prob_defaut < 0.25:
        decision = "ACCORDÉ"
        decision_code = "APPROVED"
        classe_risque = "Faible Risque"
        diagnostic = "Le profil emprunteur présente une excellente régularité financière et un risque de défaut maîtrisé."
    elif prob_defaut <= 0.50:
        decision = "ÉTUDE EN COMITÉ"
        decision_code = "REVIEW"
        classe_risque = "Risque Modéré"
        diagnostic = "Dossier intermédiaire admissible sous réserve de garanties additionnelles ou d'un ajustement de l'échéance."
    else:
        decision = "REFUSÉ"
        decision_code = "REJECTED"
        classe_risque = "Risque Élevé"
        diagnostic = "Forte probabilité d'incident de paiement. L'exposition financière globale dépasse le seuil prudentiel toléré."

    # Analyse des facteurs
    if taux_remb >= 0.70:
        points_forts.append(f"Amortissement très avancé ({taux_remb*100:.1f}% remboursé)")
    else:
        points_vigilance.append(f"Taux d'amortissement encore faible ({taux_remb*100:.1f}%)")

    if payload.nb_credit_ant >= 3:
        points_forts.append(f"Emprunteur expérimenté ({payload.nb_credit_ant} crédits antérieurs clôturés)")
    elif payload.nb_credit_ant == 0:
        points_vigilance.append("Primo-emprunteur sans historique de crédit antérieur")

    if payload.nb_dossiers_membre >= 3:
        points_forts.append(f"Client fidèle avec historique solide ({payload.nb_dossiers_membre} dossiers enregistrés)")

    if ratio_solde > 0.65:
        points_vigilance.append(f"Ratio d'encours résiduel important ({ratio_solde*100:.1f}% de la dette restante)")

    if payload.age < 25:
        points_vigilance.append(f"Emprunteur jeune ({payload.age} ans)")
    elif 30 <= payload.age <= 60:
        points_forts.append("Tranche d'âge active et stable")

    # Recommandations pour l'analyste
    if decision_code == "APPROVED":
        recommandations.append("Octroi validé selon les conditions normales de tarification.")
        recommandations.append("Proposer un renouvellement d'encours sur demande.")
    elif decision_code == "REVIEW":
        recommandations.append("Demander une caution solidaire ou une garantie matérielle équivalente à 50% de l'encours.")
        recommandations.append("Étaler l'échéancier sur une durée plus adaptée pour alléger la mensualité.")
    else:
        recommandations.append("Rejet préconisé pour préserver la qualité du portefeuille d'actifs.")
        recommandations.append("Exiger le désendettement préalable des crédits en cours avant tout réexamen.")

    return CreditResponse(
        score_credit=score_credit,
        probabilite_defaut=round(prob_defaut, 4),
        decision=decision,
        decision_code=decision_code,
        classe_risque=classe_risque,
        taux_remboursement=round(taux_remb, 4),
        ratio_solde_debourse=round(ratio_solde, 4),
        diagnostic=diagnostic,
        points_forts=points_forts,
        points_vigilance=points_vigilance,
        recommandations=recommandations
    )

@app.post("/api/batch-predict")
async def batch_predict(file: UploadFile = File(...)):
    if pipeline is None:
        raise HTTPException(status_code=500, detail="Modèle ML non disponible.")

    contents = await file.read()
    try:
        if file.filename.endswith('.csv'):
            df_batch = pd.read_csv(io.BytesIO(contents))
        else:
            df_batch = pd.read_excel(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Fichier invalide : {str(e)}")

    df_clean = df_batch.copy()
    df_clean.columns = [c.strip() for c in df_clean.columns]

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

    df_clean['NB_CREDIT_ANTERIEUR'] = df_clean['NB_CREDIT_ANTERIEUR'].fillna(0).astype(int)
    df_clean['MONTANT_DEBOURSE'] = pd.to_numeric(df_clean['MONTANT_DEBOURSE'], errors='coerce').fillna(1000)
    df_clean['SOLDE_CREDIT'] = pd.to_numeric(df_clean['SOLDE_CREDIT'], errors='coerce').fillna(0)
    df_clean['AGE'] = pd.to_numeric(df_clean['AGE'], errors='coerce').fillna(40).astype(int)
    df_clean['RATIO_SOLDE_DEBOURSE'] = (df_clean['SOLDE_CREDIT'] / (df_clean['MONTANT_DEBOURSE'] + 1)).clip(0, 5)
    df_clean['TAUX_REMBOURSEMENT'] = (1.0 - (df_clean['SOLDE_CREDIT'] / (df_clean['MONTANT_DEBOURSE'] + 1))).clip(0, 1)

    df_clean['NB_DOSSIERS_MEMBRE'] = df_clean['NUMERO_MEMBRE'].map(df_clean['NUMERO_MEMBRE'].value_counts()).fillna(1).astype(int) if 'NUMERO_MEMBRE' in df_clean.columns else 1

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

    features_num = ['AGE', 'NB_CREDIT_ANTERIEUR', 'NB_DOSSIERS_MEMBRE', 'MONTANT_DEBOURSE', 'SOLDE_CREDIT', 'RATIO_SOLDE_DEBOURSE', 'TAUX_REMBOURSEMENT', 'ANNEE_OUVERTURE', 'MOIS_OUVERTURE']
    features_cat = ['AGENCE', 'SECTEUR_ACTIVITE', 'DUREE_CREDIT', 'USAGE_CREDIT']

    for col in features_num:
        if col not in df_clean.columns: df_clean[col] = 0
    for col in features_cat:
        if col not in df_clean.columns: df_clean[col] = 'AUTRE'

    probs = pipeline.predict_proba(df_clean[features_num + features_cat])[:, 1]
    scores = np.clip(850 - (probs * 550), 300, 850).astype(int)
    decisions = ['ACCORDÉ' if p < 0.25 else ('ÉTUDE EN COMITÉ' if p <= 0.50 else 'REFUSÉ') for p in probs]

    df_batch['PROBABILITE_DEFAUT'] = np.round(probs, 4)
    df_batch['SCORE_CREDIT'] = scores
    df_batch['DECISION_IA'] = decisions

    # Synthèse JSON et buffer Excel
    output_stream = io.BytesIO()
    df_batch.to_excel(output_stream, index=False)
    output_stream.seek(0)

    # Aperçu des 20 premières lignes pour affichage dans le tableau
    preview = df_batch.head(25).to_dict(orient='records')
    total = len(df_batch)
    nb_accorde = int((df_batch['DECISION_IA'] == 'ACCORDÉ').sum())
    nb_comite = int((df_batch['DECISION_IA'] == 'ÉTUDE EN COMITÉ').sum())
    nb_refuse = int((df_batch['DECISION_IA'] == 'REFUSÉ').sum())

    return {
        "total": total,
        "accordes": nb_accorde,
        "comite": nb_comite,
        "refuses": nb_refuse,
        "taux_approbation": round((nb_accorde / total) * 100, 1) if total > 0 else 0,
        "preview": preview
    }

@app.get("/api/download-sample")
def download_sample_excel():
    if os.path.exists("DataSet_Credit.xlsx"):
        df = pd.read_excel("DataSet_Credit.xlsx").head(50)
        output_stream = io.BytesIO()
        df.to_excel(output_stream, index=False)
        output_stream.seek(0)
        return StreamingResponse(
            output_stream,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=Echantillon_Credit_50.xlsx"}
        )
    raise HTTPException(status_code=404, detail="Fichier échantillon introuvable.")

@app.get("/api/model-info")
def get_model_info():
    return {
        "model_name": "Random Forest Classifier Optimisé (Ensemble Learning)",
        "preprocessing": "StandardScaler (Numériques) + OneHotEncoder (Catégorielles)",
        "roc_auc": 0.9851,
        "accuracy": 0.961,
        "recall_defaut": 0.812,
        "agences": AGENCES,
        "secteurs": SECTEURS,
        "durees": DUREES,
        "usages": USAGES
    }

# Montage des fichiers statiques — doit être déclaré AVANT les routes catch-all
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", include_in_schema=False)
def serve_index():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
