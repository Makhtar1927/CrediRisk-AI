# 🏦 CrediRisk AI - Système d'Évaluation de Risque de Crédit

Système d'Intelligence Artificielle décisionnel pour l'évaluation et l'octroi de crédits bancaires et microfinance, basé sur des modèles de Machine Learning entraînés sur plus de 15 000 dossiers réels.

---

## 🚀 Fonctionnalités Clés

- **Mode Clair First (Light Theme)** : Design épuré inspiré des meilleures plateformes Fintech internationales (Stripe, Qonto, Mercury).
- **Simulateur Individuel en Temps Réel** :
  - Calcul de la **Probabilité de Défaut** (%).
  - Calcul du **Score de Crédit FICO** (échelle standardisée de 300 à 850 points).
  - **Décision d'Octroi Automatique** : *ACCORDÉ*, *ÉTUDE EN COMITÉ*, *REFUSÉ*.
  - Jauge SVG animée et ratios financiers interactifs (Taux d'amortissement, Ratio Solde/Dette).
  - Profils types de démonstration en 1 clic (*Client Solvable*, *Dossier Intermédiaire*, *Profil Risqué*, *Primo-Emprunteur*).
  - Recommandations d'atténuation du risque pour le comité de crédit.
- **Scoring en Masse (Batch Processing)** :
  - Téléversement direct de fichiers Excel (`.xlsx`) ou `.csv`.
  - Calcul instantané pour des centaines de dossiers.
  - Téléchargement du rapport complet scoré.
- **Performances du Modèle** :
  - **ROC-AUC : 0.9851**
  - **Recall sur défauts : 81.2%**
  - **Précision globale : 96.1%**

---

## 🛠️ Structure du Projet

```text
├── main.py                          # Serveur API FastAPI & routage statique
├── credit_risk_best_pipeline.joblib # Modèle ML complet entraîné (Random Forest + Preprocessing)
├── DataSet_Credit.xlsx              # Dataset original pour entraînement et batch
├── requirements.txt                 # Dépendances pour Render / Cloud
├── Procfile                         # Commande de démarrage Render / Heroku
├── render.yaml                      # Configuration blueprint Render
├── static/
│   ├── index.html                   # Interface Web responsive (Light Mode First)
│   ├── style.css                    # Design System CSS moderne
│   └── app.js                       # Logique frontend interactive & appels API
└── README.md                        # Documentation
```

---

## 💻 Exécution en Local

1. Installez les dépendances :
```bash
pip install -r requirements.txt
```

2. Lancez le serveur :
```bash
python main.py
```
ou :
```bash
uvicorn main:app --reload --port 8000
```

3. Ouvrez votre navigateur sur : **`http://localhost:8000`**

---

## ☁️ Guide de Déploiement : Render vs Vercel

### Pourquoi Render est le MEILLEUR choix pour ce projet ML ?
- **Render** supporte les environnements Python natifs avec des packages volumineux de Machine Learning (`scikit-learn`, `numpy`, `pandas`, `scipy`).
- **Vercel** est optimisé pour le frontend (Next.js/React) et limite les fonctions serverless Python à 250 Mo décompressés, ce qui entraîne souvent des erreurs de taille mémoire (`Task timed out` ou dépassement de quota) lors du chargement des modèles ML.

---

### 🌐 Déploiement Gratuit sur Render (Étape par Étape)

1. **Poussez votre code sur GitHub** :
   ```bash
   git init
   git add .
   git commit -m "Initial commit - CrediRisk AI"
   git branch -M main
   git remote add origin https://github.com/VOTRE_UTILISATEUR/credirisk-ai.git
   git push -u origin main
   ```

2. **Créez votre service sur Render** :
   - Rendez-vous sur [dashboard.render.com](https://dashboard.render.com).
   - Cliquez sur **New +** ➔ **Web Service**.
   - Sélectionnez votre dépôt GitHub `credirisk-ai`.
   - Renseignez les paramètres suivants :
     - **Name** : `credirisk-ai`
     - **Region** : *Frankfurt (EU)* ou la plus proche de chez vous.
     - **Runtime** : `Python 3`
     - **Build Command** : `pip install -r requirements.txt`
     - **Start Command** : `uvicorn main:app --host 0.0.0.0 --port $PORT`
     - **Instance Type** : `Free`
   - Cliquez sur **Create Web Service**.

3. **Votre application est en ligne !**
   Render vous fournira une URL HTTPS gratuite (ex: `https://credirisk-ai.onrender.com`).

---

## ⏰ Empêcher la Mise en Veille sur Render (Cronjob Keep-Alive)

Sur le forfait gratuit Render, les services web se mettent en veille après 15 minutes d'inactivité (*spindown*), ce qui provoque un délai de 30 à 50 secondes au prochain chargement.

Pour maintenir votre application **active 24h/24 et 7j/7 sans temps de veille** :

### 1. Endpoint de Santé Dédié
L'API intègre un point de terminaison ultraléger :
- **URL** : `https://credirisk-ai.onrender.com/health` (ou `/api/health`)
- **Réponse HTTP 200** :
  ```json
  {
    "status": "healthy",
    "service": "CrediRisk AI",
    "model_loaded": true,
    "uptime_seconds": 3600,
    "timestamp": 1791928532
  }
  ```

### 2. Configuration d'un Cronjob Gratuit (En 2 minutes)
1. Rendez-vous sur **[cron-job.org](https://cron-job.org)** (ou [UptimeRobot.com](https://uptimerobot.com)).
2. Créez un compte gratuit.
3. Cliquez sur **Create Cronjob** :
   - **Title** : `CrediRisk AI Keep-Alive`
   - **URL** : `https://VOTRE-APP.onrender.com/health`
   - **Schedule** : Toutes les **10 minutes** (`Every 10 minutes`).
   - **Method** : `GET`
4. Enregistrez : le cronjob enverra un ping toutes les 10 minutes, empêchant Render d'endormir le serveur !

---

## 📱 Responsivité & Expérience Mobile

L'interface s'adapte automatiquement à toutes les résolutions d'écran :
- **Mobiles (iOS / Android)** : Formulaire à 1 colonne, contrôles tactiles agrandis (44px), défilement horizontal fluide des onglets et presets sans débordement, défilement automatique vers la fiche d'audit dès le clic.
- **Tablettes & Ordinateurs portables** : Disposition réorganisée et lisibilité optimale des matrices et graphiques.
- **Écrans larges** : Affichage côte à côte (formulaire et résultat fixe) pour un confort de saisie type poste de travail bancaire.

