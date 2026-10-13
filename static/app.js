/**
 * CREDIRISK AI - LOGIQUE APPLICATION FRONTEND
 * Interaction interactive, API REST, Jauge SVG et Batch Processing
 */

document.addEventListener('DOMContentLoaded', () => {
    // Initialiser les icônes Lucide
    if (window.lucide) {
        lucide.createIcons();
    }

    // =========================================================================
    // 1. GESTION DES ONGLETS DE NAVIGATION
    // =========================================================================
    const navTabs = document.querySelectorAll('.nav-tab');
    const tabPanels = document.querySelectorAll('.tab-panel');

    navTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetId = `panel-${tab.dataset.tab}`;
            navTabs.forEach(t => t.classList.remove('active'));
            tabPanels.forEach(p => p.classList.remove('active'));

            tab.classList.add('active');
            const targetPanel = document.getElementById(targetId);
            if (targetPanel) {
                targetPanel.classList.add('active');
            }
            if (window.lucide) lucide.createIcons();
        });
    });

    // =========================================================================
    // 2. PROFILS TYPES DE DÉMONSTRATION (PRESETS RAPIDES)
    // =========================================================================
    const presets = {
        excellent: {
            age: 42,
            nb_credit_ant: 6,
            nb_dossiers_membre: 3,
            agence: 'CEC_B',
            secteur_activite: 'COMMERCE',
            montant_debourse: 3000000,
            solde_credit: 250000,
            duree_credit: 'COURT_TERME',
            usage_credit: 'FEMME',
            annee_ouverture: 2026,
            mois_ouverture: 4
        },
        moderate: {
            age: 29,
            nb_credit_ant: 2,
            nb_dossiers_membre: 1,
            agence: 'MECYD',
            secteur_activite: 'CONSTRUCTION',
            montant_debourse: 1500000,
            solde_credit: 850000,
            duree_credit: 'MOYEN_TERME',
            usage_credit: 'TRESORERIE',
            annee_ouverture: 2025,
            mois_ouverture: 6
        },
        risky: {
            age: 23,
            nb_credit_ant: 0,
            nb_dossiers_membre: 1,
            agence: 'MECREST',
            secteur_activite: 'CONSOMMATION',
            montant_debourse: 2500000,
            solde_credit: 2400000,
            duree_credit: 'LONG_TERME',
            usage_credit: 'PERSONNEL',
            annee_ouverture: 2023,
            mois_ouverture: 2
        },
        primo: {
            age: 34,
            nb_credit_ant: 0,
            nb_dossiers_membre: 1,
            agence: 'CEC/PLATEAU',
            secteur_activite: 'COMMERCE',
            montant_debourse: 800000,
            solde_credit: 120000,
            duree_credit: 'COURT_TERME',
            usage_credit: 'MICRO_ENTREPRENEUR',
            annee_ouverture: 2026,
            mois_ouverture: 5
        }
    };

    const presetChips = document.querySelectorAll('.preset-chip');
    presetChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const key = chip.dataset.preset;
            const data = presets[key];
            if (data) {
                applyFormData(data);
                submitCreditForm();
            }
        });
    });

    function applyFormData(data) {
        Object.keys(data).forEach(field => {
            const el = document.getElementById(field);
            if (el) {
                el.value = data[field];
            }
        });
        updateLiveRatio();
    }

    // =========================================================================
    // 3. CALCUL DYNAMIQUE DU RATIO EN TEMPS RÉEL
    // =========================================================================
    const montantInput = document.getElementById('montant_debourse');
    const soldeInput = document.getElementById('solde_credit');
    const liveRatioEl = document.getElementById('liveRatio');

    function updateLiveRatio() {
        const montant = parseFloat(montantInput.value) || 1;
        const solde = parseFloat(soldeInput.value) || 0;
        const ratio = (solde / (montant + 1)) * 100;
        if (liveRatioEl) {
            liveRatioEl.textContent = `Ratio d'encours : ${ratio.toFixed(1)}% (Amorti : ${(100 - ratio).toFixed(1)}%)`;
        }
    }

    if (montantInput && soldeInput) {
        montantInput.addEventListener('input', updateLiveRatio);
        soldeInput.addEventListener('input', updateLiveRatio);
        updateLiveRatio();
    }

    // Bouton de réinitialisation
    const btnReset = document.getElementById('btnResetForm');
    if (btnReset) {
        btnReset.addEventListener('click', () => {
            applyFormData(presets.excellent);
        });
    }

    // =========================================================================
    // 4. SOUMISSION DU FORMULAIRE DE CRÉDIT & PRÉDICTION IA
    // =========================================================================
    const creditForm = document.getElementById('creditForm');
    const emptyState = document.getElementById('emptyState');
    const loaderWrapper = document.getElementById('loaderWrapper');
    const resultContent = document.getElementById('resultContent');
    const btnSubmit = document.getElementById('btnSubmit');

    if (creditForm) {
        creditForm.addEventListener('submit', (e) => {
            e.preventDefault();
            submitCreditForm();
        });
    }

    async function submitCreditForm() {
        const formData = {
            age: parseInt(document.getElementById('age').value),
            nb_credit_ant: parseInt(document.getElementById('nb_credit_ant').value),
            nb_dossiers_membre: parseInt(document.getElementById('nb_dossiers_membre').value),
            montant_debourse: parseFloat(document.getElementById('montant_debourse').value),
            solde_credit: parseFloat(document.getElementById('solde_credit').value),
            annee_ouverture: parseInt(document.getElementById('annee_ouverture').value),
            mois_ouverture: parseInt(document.getElementById('mois_ouverture').value),
            agence: document.getElementById('agence').value,
            secteur_activite: document.getElementById('secteur_activite').value,
            duree_credit: document.getElementById('duree_credit').value,
            usage_credit: document.getElementById('usage_credit').value
        };

        // UI : Affichage du loader
        if (emptyState) emptyState.style.display = 'none';
        if (resultContent) resultContent.style.display = 'none';
        if (loaderWrapper) loaderWrapper.style.display = 'block';
        if (btnSubmit) btnSubmit.disabled = true;

        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || 'Erreur lors du calcul');
            }

            const data = await response.json();
            renderPredictionResults(data);
        } catch (error) {
            alert(`Erreur : ${error.message}`);
            if (emptyState) emptyState.style.display = 'block';
        } finally {
            if (loaderWrapper) loaderWrapper.style.display = 'none';
            if (btnSubmit) btnSubmit.disabled = false;
        }
    }

    // =========================================================================
    // 5. AFFICHAGE DES RÉSULTATS & ANIMATION DE LA JAUGE SVG
    // =========================================================================
    function renderPredictionResults(data) {
        if (!resultContent) return;
        resultContent.style.display = 'block';

        // 1. Bandeau de décision
        const banner = document.getElementById('decisionBanner');
        const decisionVal = document.getElementById('decisionValue');
        const riskBadge = document.getElementById('riskBadge');

        banner.className = 'decision-banner';
        if (data.decision_code === 'APPROVED') {
            banner.classList.add('approved');
            decisionVal.textContent = 'ACCORDÉ';
        } else if (data.decision_code === 'REVIEW') {
            banner.classList.add('review');
            decisionVal.textContent = 'ÉTUDE EN COMITÉ';
        } else {
            banner.classList.add('rejected');
            decisionVal.textContent = 'REFUSÉ';
        }
        riskBadge.textContent = data.classe_risque;

        // 2. Score FICO & Animation Jauge SVG
        const scoreVal = document.getElementById('scoreValue');
        animateCount(scoreVal, data.score_credit, 1000);

        const gaugeProgress = document.getElementById('gaugeProgress');
        if (gaugeProgress) {
            // Arc semi-circulaire de longueur totale = 251.3
            const TOTAL_LENGTH = 251.3;
            // Échelle de 300 à 850 (amplitude = 550)
            const normalized = Math.max(0, Math.min(1, (data.score_credit - 300) / 550));
            // Offset inversé (0 = plein, 251.3 = vide)
            const targetOffset = TOTAL_LENGTH * (1 - normalized);
            gaugeProgress.style.strokeDashoffset = targetOffset;

            // Couleur de l'arc
            if (data.score_credit >= 700) {
                gaugeProgress.style.stroke = '#10b981'; // Vert
            } else if (data.score_credit >= 550) {
                gaugeProgress.style.stroke = '#f59e0b'; // Ambre
            } else {
                gaugeProgress.style.stroke = '#ef4444'; // Rouge
            }
        }

        // 3. KPIs
        const probDefautVal = document.getElementById('probDefautVal');
        const probBar = document.getElementById('probBar');
        probDefautVal.textContent = `${(data.probabilite_defaut * 100).toFixed(1)}%`;
        probBar.style.width = `${Math.min(100, data.probabilite_defaut * 100)}%`;
        probBar.style.background = data.probabilite_defaut > 0.5 ? '#ef4444' : (data.probabilite_defaut > 0.25 ? '#f59e0b' : '#10b981');

        const tauxRembVal = document.getElementById('tauxRembVal');
        const rembBar = document.getElementById('rembBar');
        tauxRembVal.textContent = `${(data.taux_remboursement * 100).toFixed(1)}%`;
        rembBar.style.width = `${Math.min(100, data.taux_remboursement * 100)}%`;

        const ratioSoldeVal = document.getElementById('ratioSoldeVal');
        const ratioBar = document.getElementById('ratioBar');
        ratioSoldeVal.textContent = `${(data.ratio_solde_debourse * 100).toFixed(1)}%`;
        ratioBar.style.width = `${Math.min(100, data.ratio_solde_debourse * 100)}%`;

        // 4. Diagnostic
        document.getElementById('diagnosticText').textContent = data.diagnostic;

        // 5. Audit Points Forts & Vigilance
        const listForts = document.getElementById('listPointsForts');
        listForts.innerHTML = '';
        if (data.points_forts.length > 0) {
            data.points_forts.forEach(pt => {
                const li = document.createElement('li');
                li.textContent = pt;
                listForts.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.textContent = 'Aucun facteur exceptionnel relevé.';
            listForts.appendChild(li);
        }

        const listVigilance = document.getElementById('listPointsVigilance');
        listVigilance.innerHTML = '';
        if (data.points_vigilance.length > 0) {
            data.points_vigilance.forEach(pt => {
                const li = document.createElement('li');
                li.textContent = pt;
                listVigilance.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.textContent = 'Aucun facteur critique de vigilance.';
            listVigilance.appendChild(li);
        }

        // 6. Recommandations
        const listRecs = document.getElementById('listRecommendations');
        listRecs.innerHTML = '';
        data.recommandations.forEach(rec => {
            const li = document.createElement('li');
            li.textContent = rec;
            listRecs.appendChild(li);
        });

        if (window.lucide) lucide.createIcons();
    }

    // Animation numérique fluide pour le score
    function animateCount(el, target, duration = 800) {
        let start = parseInt(el.textContent) || 300;
        if (isNaN(start)) start = 300;
        const diff = target - start;
        const startTime = performance.now();

        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            // Ease out cubic
            const ease = 1 - Math.pow(1 - progress, 3);
            const current = Math.round(start + (diff * ease));
            el.textContent = current;

            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                el.textContent = target;
            }
        }
        requestAnimationFrame(update);
    }

    // =========================================================================
    // 6. GESTION DU SCORING PAR LOT (BATCH EXCEL / CSV)
    // =========================================================================
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('batchFileInput');
    const selectedFileName = document.getElementById('selectedFileName');
    const btnRunBatch = document.getElementById('btnRunBatch');
    const batchResultsWrapper = document.getElementById('batchResultsWrapper');
    let selectedFile = null;

    if (dropZone && fileInput) {
        dropZone.addEventListener('click', () => fileInput.click());

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            if (e.dataTransfer.files.length > 0) {
                handleFileSelect(e.dataTransfer.files[0]);
            }
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileSelect(e.target.files[0]);
            }
        });
    }

    function handleFileSelect(file) {
        selectedFile = file;
        if (selectedFileName) {
            selectedFileName.textContent = `Fichier sélectionné : ${file.name} (${(file.size / 1024).toFixed(1)} Ko)`;
        }
        if (btnRunBatch) {
            btnRunBatch.disabled = false;
        }
    }

    if (btnRunBatch) {
        btnRunBatch.addEventListener('click', async () => {
            if (!selectedFile) return;

            btnRunBatch.disabled = true;
            btnRunBatch.innerHTML = '<div class="spinner" style="width:16px;height:16px;border-width:2px;margin:0;display:inline-block;"></div> Traitement en cours...';

            const formData = new FormData();
            formData.append('file', selectedFile);

            try {
                const response = await fetch('/api/batch-predict', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    const err = await response.json();
                    throw new Error(err.detail || 'Erreur lors du batch');
                }

                const data = await response.json();
                renderBatchResults(data);
            } catch (error) {
                alert(`Erreur de traitement par lot : ${error.message}`);
            } finally {
                btnRunBatch.disabled = false;
                btnRunBatch.innerHTML = '<i data-lucide="play"></i> Lancer le Traitement en Masse';
                if (window.lucide) lucide.createIcons();
            }
        });
    }

    function renderBatchResults(data) {
        if (!batchResultsWrapper) return;
        batchResultsWrapper.style.display = 'block';

        document.getElementById('batchTotal').textContent = data.total;
        document.getElementById('batchAccordes').textContent = `${data.accordes} (${data.taux_approbation}%)`;
        document.getElementById('batchComite').textContent = data.comite;
        document.getElementById('batchRefuses').textContent = data.refuses;

        const tableBody = document.getElementById('batchTableBody');
        tableBody.innerHTML = '';

        data.preview.forEach(row => {
            const tr = document.createElement('tr');
            
            let badgeClass = 'badge-accorde';
            if (row.DECISION_IA === 'ÉTUDE EN COMITÉ') badgeClass = 'badge-comite';
            if (row.DECISION_IA === 'REFUSÉ') badgeClass = 'badge-refuse';

            tr.innerHTML = `
                <td><strong>#${row.NUMERO_CREDIT || row.NUMERO_MEMBRE || '-'}</strong></td>
                <td>${row.AGENCE || '-'}</td>
                <td>${row.SECTEUR_ACTIVITE || '-'}</td>
                <td>${(row.MONTANT_DEBOURSE || 0).toLocaleString()} FCFA</td>
                <td>${(row.SOLDE_CREDIT || 0).toLocaleString()} FCFA</td>
                <td>${((row.PROBABILITE_DEFAUT || 0) * 100).toFixed(1)}%</td>
                <td><strong>${row.SCORE_CREDIT || '-'}</strong></td>
                <td><span class="table-badge ${badgeClass}">${row.DECISION_IA}</span></td>
            `;
            tableBody.appendChild(tr);
        });

        // Défilement automatique vers les résultats
        batchResultsWrapper.scrollIntoView({ behavior: 'smooth' });
    }

    // Bouton Télécharger Scoré
    const btnDownloadScored = document.getElementById('btnDownloadScoredExcel');
    if (btnDownloadScored) {
        btnDownloadScored.addEventListener('click', () => {
            window.location.href = '/api/download-sample';
        });
    }
});
