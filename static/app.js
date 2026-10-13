/**
 * CREDIRISK AI — FRONTEND ENGINE v2
 * Dark Mode Toggle · Toast Notifications · Responsive Interactions
 */

document.addEventListener('DOMContentLoaded', () => {
    // Init Lucide icons
    if (window.lucide) lucide.createIcons();

    // =========================================================================
    // 0. DARK MODE TOGGLE
    // =========================================================================
    const btnTheme  = document.getElementById('btnToggleTheme');
    const themeIcon = document.getElementById('themeIcon');
    const html      = document.documentElement;

    const savedTheme = localStorage.getItem('crediRiskTheme') || 'light';
    applyTheme(savedTheme);

    function applyTheme(theme) {
        html.setAttribute('data-theme', theme);
        localStorage.setItem('crediRiskTheme', theme);
        if (themeIcon) {
            themeIcon.setAttribute('data-lucide', theme === 'dark' ? 'sun' : 'moon');
            if (window.lucide) lucide.createIcons();
        }
    }

    if (btnTheme) {
        btnTheme.addEventListener('click', () => {
            const current = html.getAttribute('data-theme');
            applyTheme(current === 'dark' ? 'light' : 'dark');
        });
    }

    // =========================================================================
    // 1. TOAST NOTIFICATIONS
    // =========================================================================
    const toastContainer = document.getElementById('toast-container');

    function showToast(message, type = 'info', duration = 4000) {
        if (!toastContainer) return;
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        const icon = type === 'error' ? 'x-circle' : type === 'success' ? 'check-circle' : 'info';
        toast.innerHTML = `<i data-lucide="${icon}" style="width:18px;height:18px;flex-shrink:0;"></i> ${message}`;
        toastContainer.appendChild(toast);
        if (window.lucide) lucide.createIcons();
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(20px)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 320);
        }, duration);
    }

    // =========================================================================
    // 2. NAVIGATION TABS
    // =========================================================================
    const navTabs   = document.querySelectorAll('.nav-tab');
    const tabPanels = document.querySelectorAll('.tab-panel');

    navTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetId = `panel-${tab.dataset.tab}`;
            navTabs.forEach(t => { t.classList.remove('active'); t.setAttribute('aria-selected', 'false'); });
            tabPanels.forEach(p => p.classList.remove('active'));
            tab.classList.add('active');
            tab.setAttribute('aria-selected', 'true');
            const panel = document.getElementById(targetId);
            if (panel) panel.classList.add('active');
            if (window.lucide) lucide.createIcons();
        });
    });

    // =========================================================================
    // 3. PROFILS TYPES (PRESETS RAPIDES)
    // =========================================================================
    const presets = {
        excellent: {
            age: 44, nb_credit_ant: 7, nb_dossiers_membre: 4,
            agence: 'CEC_B', secteur_activite: 'COMMERCE',
            montant_debourse: 3500000, solde_credit: 200000,
            duree_credit: 'COURT_TERME', usage_credit: 'FEMME',
            annee_ouverture: 2026, mois_ouverture: 3
        },
        moderate: {
            age: 30, nb_credit_ant: 2, nb_dossiers_membre: 1,
            agence: 'MECYD', secteur_activite: 'CONSTRUCTION',
            montant_debourse: 1500000, solde_credit: 900000,
            duree_credit: 'MOYEN_TERME', usage_credit: 'TRESORERIE',
            annee_ouverture: 2025, mois_ouverture: 6
        },
        risky: {
            age: 23, nb_credit_ant: 0, nb_dossiers_membre: 1,
            agence: 'MECREST', secteur_activite: 'CONSOMMATION',
            montant_debourse: 2500000, solde_credit: 2400000,
            duree_credit: 'LONG_TERME', usage_credit: 'PERSONNEL',
            annee_ouverture: 2023, mois_ouverture: 2
        },
        primo: {
            age: 34, nb_credit_ant: 0, nb_dossiers_membre: 1,
            agence: 'CEC/PLATEAU', secteur_activite: 'COMMERCE',
            montant_debourse: 800000, solde_credit: 120000,
            duree_credit: 'COURT_TERME', usage_credit: 'MICRO_ENTREPRENEUR',
            annee_ouverture: 2026, mois_ouverture: 5
        }
    };

    document.querySelectorAll('.preset-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            const data = presets[chip.dataset.preset];
            if (data) { applyFormData(data); submitCreditForm(); }
        });
    });

    function applyFormData(data) {
        Object.keys(data).forEach(field => {
            const el = document.getElementById(field);
            if (el) el.value = data[field];
        });
        updateLiveRatio();
    }

    // =========================================================================
    // 4. RATIO LIVE EN TEMPS RÉEL
    // =========================================================================
    const montantInput = document.getElementById('montant_debourse');
    const soldeInput   = document.getElementById('solde_credit');
    const liveRatioEl  = document.getElementById('liveRatio');

    function updateLiveRatio() {
        const montant = parseFloat(montantInput?.value) || 1;
        const solde   = parseFloat(soldeInput?.value)   || 0;
        const ratio   = Math.min(100, (solde / (montant + 1)) * 100);
        const amorti  = Math.max(0, 100 - ratio);
        if (liveRatioEl) {
            liveRatioEl.textContent = `Ratio d'encours : ${ratio.toFixed(1)}% — Amorti : ${amorti.toFixed(1)}%`;
            liveRatioEl.style.color = ratio > 80 ? 'var(--danger)' : ratio > 50 ? 'var(--warning)' : 'var(--text-muted)';
        }
    }

    if (montantInput && soldeInput) {
        montantInput.addEventListener('input', updateLiveRatio);
        soldeInput.addEventListener('input', updateLiveRatio);
        updateLiveRatio();
    }

    // Reset button
    const btnReset = document.getElementById('btnResetForm');
    if (btnReset) {
        btnReset.addEventListener('click', () => applyFormData(presets.excellent));
    }

    // =========================================================================
    // 5. SOUMISSION FORMULAIRE & PRÉDICTION IA
    // =========================================================================
    const creditForm   = document.getElementById('creditForm');
    const emptyState   = document.getElementById('emptyState');
    const loaderWrapper= document.getElementById('loaderWrapper');
    const resultContent= document.getElementById('resultContent');
    const btnSubmit    = document.getElementById('btnSubmit');

    if (creditForm) {
        creditForm.addEventListener('submit', e => { e.preventDefault(); submitCreditForm(); });
    }

    async function submitCreditForm() {
        const age     = parseInt(document.getElementById('age')?.value);
        const montant = parseFloat(document.getElementById('montant_debourse')?.value);
        const solde   = parseFloat(document.getElementById('solde_credit')?.value);

        if (!age || !montant) {
            showToast('Veuillez renseigner tous les champs obligatoires.', 'error');
            return;
        }
        if (solde > montant) {
            showToast('Le solde restant ne peut pas dépasser le montant déboursé.', 'error');
            return;
        }

        const formData = {
            age,
            nb_credit_ant:     parseInt(document.getElementById('nb_credit_ant')?.value) || 0,
            nb_dossiers_membre:parseInt(document.getElementById('nb_dossiers_membre')?.value) || 1,
            montant_debourse:  montant,
            solde_credit:      solde,
            annee_ouverture:   parseInt(document.getElementById('annee_ouverture')?.value) || 2026,
            mois_ouverture:    parseInt(document.getElementById('mois_ouverture')?.value) || 1,
            agence:            document.getElementById('agence')?.value || 'CEC_B',
            secteur_activite:  document.getElementById('secteur_activite')?.value || 'COMMERCE',
            duree_credit:      document.getElementById('duree_credit')?.value || 'COURT_TERME',
            usage_credit:      document.getElementById('usage_credit')?.value || 'TRESORERIE'
        };

        // UI loader
        if (emptyState)    emptyState.style.display = 'none';
        if (resultContent) resultContent.style.display = 'none';
        if (loaderWrapper) loaderWrapper.style.display = 'flex';
        if (btnSubmit)     { btnSubmit.disabled = true; }

        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                const err = await response.json().catch(() => ({ detail: `Erreur HTTP ${response.status}` }));
                throw new Error(err.detail || `Erreur serveur (${response.status})`);
            }

            const data = await response.json();
            renderPredictionResults(data);
        } catch (error) {
            showToast(`Erreur : ${error.message}`, 'error');
            if (emptyState) emptyState.style.display = 'flex';
        } finally {
            if (loaderWrapper) loaderWrapper.style.display = 'none';
            if (btnSubmit)     { btnSubmit.disabled = false; }
        }
    }

    // =========================================================================
    // 6. AFFICHAGE DES RÉSULTATS & JAUGE SVG ANIMÉE
    // =========================================================================
    function renderPredictionResults(data) {
        if (!resultContent) return;
        resultContent.style.display = 'block';

        // — Bandeau de décision —
        const banner      = document.getElementById('decisionBanner');
        const decisionVal = document.getElementById('decisionValue');
        const riskBadge   = document.getElementById('riskBadge');

        banner.className = 'decision-banner';
        if (data.decision_code === 'APPROVED') {
            banner.classList.add('approved');
            decisionVal.textContent = '✓ ACCORDÉ';
        } else if (data.decision_code === 'REVIEW') {
            banner.classList.add('review');
            decisionVal.textContent = '⚠ ÉTUDE EN COMITÉ';
        } else {
            banner.classList.add('rejected');
            decisionVal.textContent = '✗ REFUSÉ';
        }
        riskBadge.textContent = data.classe_risque;

        // — Score & Jauge SVG —
        const scoreVal = document.getElementById('scoreValue');
        animateCount(scoreVal, data.score_credit, 1200);

        const gaugeProgress = document.getElementById('gaugeProgress');
        if (gaugeProgress) {
            const TOTAL = 251.3;
            const norm  = Math.max(0, Math.min(1, (data.score_credit - 300) / 550));
            gaugeProgress.style.strokeDashoffset = TOTAL * (1 - norm);
            gaugeProgress.style.stroke =
                data.score_credit >= 700 ? '#059669' :
                data.score_credit >= 550 ? '#d97706' : '#dc2626';
        }

        // — KPIs —
        const probPct  = (data.probabilite_defaut * 100).toFixed(1);
        const rembPct  = (data.taux_remboursement * 100).toFixed(1);
        const ratioPct = (data.ratio_solde_debourse * 100).toFixed(1);

        safeText('probDefautVal', `${probPct}%`);
        safeWidth('probBar', Math.min(100, data.probabilite_defaut * 100));
        const probBar = document.getElementById('probBar');
        if (probBar) probBar.style.background =
            data.probabilite_defaut > 0.5 ? '#dc2626' :
            data.probabilite_defaut > 0.25 ? '#d97706' : '#059669';

        safeText('tauxRembVal', `${rembPct}%`);
        safeWidth('rembBar', Math.min(100, data.taux_remboursement * 100));

        safeText('ratioSoldeVal', `${ratioPct}%`);
        safeWidth('ratioBar', Math.min(100, data.ratio_solde_debourse * 100));

        // — Diagnostic —
        safeText('diagnosticText', data.diagnostic);

        // — Audit —
        renderList('listPointsForts', data.points_forts, 'Aucun facteur exceptionnel relevé.');
        renderList('listPointsVigilance', data.points_vigilance, 'Aucun facteur critique de vigilance.');
        renderList('listRecommendations', data.recommandations, '');

        if (window.lucide) lucide.createIcons();

        // Scroll sur mobile
        if (window.innerWidth <= 1100) {
            document.getElementById('resultCard')?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }

    function safeText(id, text) {
        const el = document.getElementById(id);
        if (el) el.textContent = text;
    }
    function safeWidth(id, pct) {
        const el = document.getElementById(id);
        if (el) el.style.width = `${pct}%`;
    }
    function renderList(id, items, emptyMsg) {
        const ul = document.getElementById(id);
        if (!ul) return;
        ul.innerHTML = '';
        const list = items && items.length > 0 ? items : (emptyMsg ? [emptyMsg] : []);
        list.forEach(txt => {
            const li = document.createElement('li');
            li.textContent = txt;
            ul.appendChild(li);
        });
    }

    // Animation numérique fluide (ease-out cubic)
    function animateCount(el, target, duration = 1000) {
        let start = parseInt(el?.textContent) || 300;
        if (isNaN(start)) start = 300;
        const diff      = target - start;
        const startTime = performance.now();
        function tick(now) {
            const progress = Math.min((now - startTime) / duration, 1);
            const ease     = 1 - Math.pow(1 - progress, 3);
            if (el) el.textContent = Math.round(start + diff * ease);
            if (progress < 1) requestAnimationFrame(tick);
            else if (el) el.textContent = target;
        }
        requestAnimationFrame(tick);
    }

    // =========================================================================
    // 7. SCORING PAR LOT (BATCH EXCEL / CSV)
    // =========================================================================
    const dropZone           = document.getElementById('dropZone');
    const fileInput          = document.getElementById('batchFileInput');
    const selectedFileName   = document.getElementById('selectedFileName');
    const btnRunBatch        = document.getElementById('btnRunBatch');
    const batchResultsWrapper= document.getElementById('batchResultsWrapper');
    let   selectedFile       = null;

    if (dropZone && fileInput) {
        // Click on zone
        dropZone.addEventListener('click', e => {
            if (e.target !== fileInput) fileInput.click();
        });

        // Drag & drop
        dropZone.addEventListener('dragover',  e => { e.preventDefault(); dropZone.classList.add('dragover'); });
        dropZone.addEventListener('dragleave', ()  => dropZone.classList.remove('dragover'));
        dropZone.addEventListener('dragenter', e   => e.preventDefault());
        dropZone.addEventListener('drop', e => {
            e.preventDefault(); dropZone.classList.remove('dragover');
            if (e.dataTransfer.files.length > 0) handleFileSelect(e.dataTransfer.files[0]);
        });
        fileInput.addEventListener('change', e => {
            if (e.target.files.length > 0) handleFileSelect(e.target.files[0]);
        });
    }

    function handleFileSelect(file) {
        const allowed = ['.xlsx', '.csv', '.xls'];
        const ext = '.' + file.name.split('.').pop().toLowerCase();
        if (!allowed.includes(ext)) {
            showToast('Format non supporté. Utilisez .xlsx ou .csv', 'error');
            return;
        }
        selectedFile = file;
        if (selectedFileName) {
            selectedFileName.textContent = `📄 ${file.name} — ${(file.size / 1024).toFixed(1)} Ko`;
        }
        if (btnRunBatch) btnRunBatch.disabled = false;
        dropZone.classList.add('dragover');
    }

    if (btnRunBatch) {
        btnRunBatch.addEventListener('click', async () => {
            if (!selectedFile) return;
            btnRunBatch.disabled = true;
            btnRunBatch.innerHTML = '<div class="spinner" style="width:16px;height:16px;border-width:2px;margin:0;display:inline-block;"></div>&nbsp; Traitement en cours...';

            const fd = new FormData();
            fd.append('file', selectedFile);

            try {
                const res = await fetch('/api/batch-predict', { method: 'POST', body: fd });
                if (!res.ok) {
                    const err = await res.json().catch(() => ({ detail: `Erreur HTTP ${res.status}` }));
                    throw new Error(err.detail || `Erreur serveur (${res.status})`);
                }
                const data = await res.json();
                renderBatchResults(data);
                showToast(`✓ ${data.total} dossiers traités avec succès !`, 'success');
            } catch (err) {
                showToast(`Erreur de traitement : ${err.message}`, 'error');
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

        safeText('batchTotal',    data.total.toLocaleString());
        safeText('batchAccordes', `${data.accordes.toLocaleString()} (${data.taux_approbation}%)`);
        safeText('batchComite',   data.comite.toLocaleString());
        safeText('batchRefuses',  data.refuses.toLocaleString());

        const body = document.getElementById('batchTableBody');
        if (!body) return;
        body.innerHTML = '';

        (data.preview || []).forEach(row => {
            const tr  = document.createElement('tr');
            const dec = row.DECISION_IA || '';
            const badge =
                dec === 'ACCORDÉ'         ? 'badge-accorde' :
                dec === 'ÉTUDE EN COMITÉ' ? 'badge-comite'  : 'badge-refuse';

            const montant = (row.MONTANT_DEBOURSE || 0).toLocaleString('fr-FR');
            const solde   = (row.SOLDE_CREDIT     || 0).toLocaleString('fr-FR');
            const prob    = ((row.PROBABILITE_DEFAUT || 0) * 100).toFixed(1);

            const probColor = parseFloat(prob) > 50 ? 'var(--danger)' : parseFloat(prob) > 25 ? 'var(--warning)' : 'var(--success)';
            const secteur   = (row['SECTEUR ACTIVITE'] || row.SECTEUR_ACTIVITE || '—');
            const secteurShort = secteur.length > 20 ? secteur.substring(0, 18) + '…' : secteur;

            tr.innerHTML = `
                <td><strong>#${row.NUMERO_CREDIT || row.NUMERO_MEMBRE || '—'}</strong></td>
                <td>${row.AGENCE || '—'}</td>
                <td title="${secteur}">${secteurShort}</td>
                <td>${montant} FCFA</td>
                <td>${solde} FCFA</td>
                <td><strong style="color:${probColor}">${prob}%</strong></td>
                <td><strong>${row.SCORE_CREDIT || '—'}</strong></td>
                <td><span class="table-badge ${badge}">${dec}</span></td>
            `;
            body.appendChild(tr);
        });
        batchResultsWrapper.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    // Télécharger fichier scoré (on utilise le sample pour la démo)
    const btnDownloadScored = document.getElementById('btnDownloadScoredExcel');
    if (btnDownloadScored) {
        btnDownloadScored.addEventListener('click', () => {
            window.location.href = '/api/download-sample';
        });
    }

    // =========================================================================
    // 8. HEALTH CHECK AU DÉMARRAGE
    // =========================================================================
    (async () => {
        try {
            const res  = await fetch('/health');
            const data = await res.json();
            if (!data.model_loaded) {
                showToast('⚠ Modèle ML non chargé sur le serveur. Certaines fonctions sont indisponibles.', 'error', 8000);
            }
        } catch {
            // Silencieux si le serveur est inaccessible en local
        }
    })();
});
