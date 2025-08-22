// ===== CONFIGURATION ET DONNÉES =====

// Table XP système serveur (extraite du CSV)
const XP_TABLE = {
    1: 1, 2: 2, 3: 2, 4: 3, 5: 3, 6: 4, 7: 4, 8: 4, 9: 4, 10: 4,
    11: 5, 12: 5, 13: 5, 14: 6, 15: 6, 16: 7, 17: 8, 18: 9, 19: 10, 20: 0
};

// PV moyens par classe (basé sur les dés de vie)
const HP_AVERAGES = {
    'Magicien': 4, 'Ensorceleur': 4,  // d6 → 4
    'Artificier': 5, 'Barde': 5, 'Clerc': 5, 'Druide': 5, 'Moine': 5, 'Occultiste': 5, 'Roublard': 5,  // d8 → 5
    'Guerrier': 6, 'Paladin': 6, 'Rôdeur': 6,  // d10 → 6
    'Barbare': 7  // d12 → 7
};

// Coûts d'apprentissage de sorts (Niveau × 50 PO)
const SPELL_LEARNING_COSTS = {
    1: 50, 2: 100, 3: 150, 4: 200, 5: 250, 6: 300, 7: 350, 8: 400, 9: 450
};

// Variables globales
let queteCounter = 0;
let recompenseCounters = {}; // Pour tracker les compteurs de récompenses par quête

// ===== GESTION DES ONGLETS =====

function showTab(tabName, event) {
    // Cacher tous les contenus d'onglets
    const contents = document.querySelectorAll('.tab-content');
    contents.forEach(content => content.classList.remove('active'));

    // Désactiver tous les boutons d'onglets
    const buttons = document.querySelectorAll('.tab-btn');
    buttons.forEach(btn => btn.classList.remove('active'));

    // Afficher le contenu sélectionné
    const targetTab = document.getElementById(`tab-${tabName}`);
    if (targetTab) {
        targetTab.classList.add('active');
    }

    // Activer le bouton sélectionné
    event.currentTarget.classList.add('active');
}

// ===== GESTION DES TRANSACTIONS =====

function addTransactionLine() {
    const container = document.getElementById('transactions-container');
    if (!container) return;

    const line = document.createElement('div');
    line.className = 'transaction-line';
    line.innerHTML = `
        <select>
            <option value="ACHAT">ACHAT</option>
            <option value="VENTE">VENTE</option>
        </select>
        <input type="text" placeholder="Description">
        <input type="number" class="quantity" min="1" step="1" value="1" placeholder="1">
        <input type="number" class="price" step="0.01" placeholder="0">
        <button type="button" class="delete-transaction">🗑️</button>
    `;
    container.appendChild(line);
    setupTransactionLine(line);
    regenerateIfNeeded();
}

function deleteTransactionLine(line) {
    if (line instanceof HTMLElement) {
        line.remove();
        regenerateIfNeeded();
    }
}

function setupTransactionLine(line) {
    if (!line) return;
    const inputs = line.querySelectorAll('select, input');
    inputs.forEach(inp => {
        if (!inp.getAttribute('data-listener-added')) {
            inp.addEventListener('input', regenerateIfNeeded);
            if (inp.tagName === 'SELECT') {
                inp.addEventListener('change', regenerateIfNeeded);
            }
            inp.setAttribute('data-listener-added', 'true');
        }
    });

    const delBtn = line.querySelector('.delete-transaction');
    if (delBtn && !delBtn.getAttribute('data-listener-added')) {
        delBtn.addEventListener('click', () => deleteTransactionLine(line));
        delBtn.setAttribute('data-listener-added', 'true');
    }
}

// ===== GESTION DES QUÊTES =====

function addQuete() {
    // S'assurer que le compteur reflète l'état actuel du DOM
    const domCount = document.querySelectorAll('.quete-bloc').length - 1;
    if (domCount !== queteCounter) {
        queteCounter = domCount;
    }

    queteCounter++;
    const container = document.getElementById('quetes-container');

    const queteHtml = createQueteHTML(queteCounter);
    container.insertAdjacentHTML('beforeend', queteHtml);

    // Re-numérote toutes les quêtes pour garder une numérotation séquentielle
    renumberQuetes();

    // Ajouter les event listeners pour la nouvelle quête
    setupQueteListeners(queteCounter);

    // Afficher le bouton de suppression de la quête nouvellement créée si ce n'est pas la première
    const newDeleteBtn = document.querySelector(`[data-quete="${queteCounter}"] .delete-quete`);
    if (newDeleteBtn && queteCounter > 0) {
        newDeleteBtn.style.display = 'block';
    }

    regenerateIfNeeded();
}

function deleteQuete(index) {
    const queteBloc = document.querySelector(`[data-quete="${index}"]`);
    if (queteBloc) {
        queteBloc.remove();

        // Recalculer le compteur en fonction du DOM
        queteCounter = document.querySelectorAll('.quete-bloc').length - 1;

        // Mettre à jour les indices des quêtes restantes
        renumberQuetes();

        // Masquer le bouton de suppression s'il ne reste qu'une quête
        const remainingQuetes = document.querySelectorAll('.quete-bloc');
        if (remainingQuetes.length === 1) {
            const deleteBtn = document.querySelector('[data-quete="0"] .delete-quete');
            if (deleteBtn) {
                deleteBtn.style.display = 'none';
            }
        }

        regenerateIfNeeded();
    }
}

function renumberQuetes() {
    const blocs = document.querySelectorAll('.quete-bloc');
    blocs.forEach((bloc, index) => {
        bloc.setAttribute('data-quete', index);

        const title = bloc.querySelector('h4');
        if (title) {
            title.textContent = `🎯 Quête ${index + 1}`;
        }

        bloc.querySelectorAll('[id]').forEach(el => {
            el.id = el.id.replace(/\d+$/, index);
        });

        bloc.querySelectorAll('label[for]').forEach(label => {
            const forValue = label.getAttribute('for');
            if (forValue) {
                label.setAttribute('for', forValue.replace(/\d+$/, index));
            }
        });

        const deleteBtn = bloc.querySelector('.delete-quete');
        if (deleteBtn) {
            deleteBtn.setAttribute('onclick', `deleteQuete(${index})`);
        }
    });
}

function addRecompense(index) {
    const container = document.getElementById(`recompenses-container-${index}`);
    if (!container) return;

    if (recompenseCounters[index] === undefined) {
        recompenseCounters[index] = container.querySelectorAll('.recompense-item').length;
    }

    const recompenseIndex = recompenseCounters[index]++;

    const html = `
        <div class="recompense-item" data-recompense="${recompenseIndex}">
            <select style="flex: 0 0 120px;">
                <option value="monnaie" selected>💰 Monnaie</option>
                <option value="item">🎒 Objet</option>
            </select>
            <div class="recompense-details" style="flex: 1; display: flex; gap: 5px;">
                <input type="number" placeholder="PC" style="flex: 1;">
                <input type="number" placeholder="PA" style="flex: 1;">
                <input type="number" placeholder="PO" style="flex: 1;">
                <input type="number" placeholder="PP" style="flex: 1;">
            </div>
            <button type="button" class="delete-recompense">🗑️</button>
        </div>
    `;

    container.insertAdjacentHTML('beforeend', html);

    setupRecompenseItem(index, recompenseIndex);
}

function deleteRecompense(queteIndex, recompenseIndex) {
    const item = document.querySelector(`#recompenses-container-${queteIndex} .recompense-item[data-recompense="${recompenseIndex}"]`);
    if (item) {
        item.remove();
        regenerateIfNeeded();
    }
}

function setupRecompenseItem(queteIndex, recompenseIndex) {
    const item = document.querySelector(`#recompenses-container-${queteIndex} .recompense-item[data-recompense="${recompenseIndex}"]`);
    if (!item) return;

    const select = item.querySelector('select');
    const updateFields = function() {
        const details = item.querySelector('.recompense-details');
        if (this.value === 'item') {
            details.innerHTML = `<input type="text" placeholder="Description" style="flex: 1;">`;
        } else {
            details.innerHTML = `
                <input type="number" placeholder="PC" style="flex: 1;">
                <input type="number" placeholder="PA" style="flex: 1;">
                <input type="number" placeholder="PO" style="flex: 1;">
                <input type="number" placeholder="PP" style="flex: 1;">
            `;
        }

        details.querySelectorAll('input').forEach(inp => {
            if (!inp.hasAttribute('data-listener-added')) {
                inp.addEventListener('input', regenerateIfNeeded);
                inp.setAttribute('data-listener-added', 'true');
            }
        });

        regenerateIfNeeded();
    };

    select.addEventListener('change', updateFields);
    updateFields.call(select);
}

function createQueteHTML(index) {
    return `
        <div class="quete-bloc" data-quete="${index}">
            <h4 style="color: #3498db; margin-bottom: 15px;">🎯 Quête ${index + 1}</h4>
            
            <div class="form-group">
                <label for="titre-quete-${index}">Titre de la Quête :</label>
                <input type="text" id="titre-quete-${index}" placeholder="Titre de la quête">
            </div>

            <div class="form-group">
                <label for="nom-mj-${index}">Nom du MJ :</label>
                <input type="text" id="nom-mj-${index}" placeholder="@NomDuMJ">
            </div>

            <div class="checkbox-group">
                <input type="checkbox" id="quete-multiple-${index}">
                <label for="quete-multiple-${index}">Quête avec plusieurs sessions</label>
            </div>

            <div id="quete-simple-${index}" class="form-group">
                <label for="lien-recompense-${index}">Lien vers les récompenses :</label>
                <input type="text" id="lien-recompense-${index}" placeholder="https://discord.com/channels/...">
            </div>

            <div id="quete-multiple-details-${index}" class="form-group" style="display: none;">
                <label for="sessions-quete-${index}">Sessions de la quête :</label>
                <textarea id="sessions-quete-${index}" rows="4" placeholder="- https://discord.com/channels/.../... + 1XP,&#10;- https://discord.com/channels/.../... + 1 XP"></textarea>
            </div>

            <div class="form-group">
                <label for="xp-quete-${index}">XP de cette quête :</label>
                <input type="number" id="xp-quete-${index}" placeholder="1" min="0" max="10" value="1">
            </div>

            <div class="checkbox-group">
                <input type="checkbox" id="refuse-xp-${index}">
                <label for="refuse-xp-${index}">Refuser l’XP de cette quête</label>
            </div>

        <div class="form-group">
            <h5 style="color: #2c3e50; margin-bottom: 10px;">🎁 Récompenses (optionnelles) :</h5>

            <div class="checkbox-group">
                <label for="include-monnaies-${index}">
                    <input type="checkbox" id="include-monnaies-${index}" style="width: auto; margin-right: 8px;">
                    Inclure monnaies
                </label>
            </div>
            <div id="monnaie-container-${index}" style="display: none;">
                <div class="monnaie-inputs" style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 5px;">
                    <input type="number" id="pc-quete-${index}" placeholder="PC">
                    <input type="number" id="pa-quete-${index}" placeholder="PA">
                    <input type="number" id="po-quete-${index}" placeholder="PO">
                    <input type="number" id="pp-quete-${index}" placeholder="PP">
                </div>
                <input type="text" id="total-quete-or-${index}" placeholder="Total en PO" disabled style="margin-top: 5px;">
            </div>

            <div class="checkbox-group">
                <label for="include-objets-${index}">
                    <input type="checkbox" id="include-objets-${index}" style="width: auto; margin-right: 8px;">
                    Inclure objets
                </label>
            </div>
            <div id="objets-container-${index}" style="display: none;">
                <textarea id="objets-quete-${index}" rows="2" placeholder="2 émeraudes d'une valeur de 200PO, un étrange engrenage en rotation perpétuelle"></textarea>
            </div>

            <div class="reward-type">
                <label>⭐ Autres récompenses :</label>
                <textarea id="autres-quete-${index}" rows="2" placeholder="Don du fruit blanc à Kornélius, Sort Interdiction dans le grimoire"></textarea>
            </div>
        </div>

            <button type="button" class="delete-quete" onclick="deleteQuete(${index})" style="display: none;">
                🗑️ Supprimer cette quête
            </button>
        </div>
    `;
}

function updateMonnaieTotal(index) {
    const pcEl = document.getElementById(`pc-quete-${index}`);
    const paEl = document.getElementById(`pa-quete-${index}`);
    const poEl = document.getElementById(`po-quete-${index}`);
    const ppEl = document.getElementById(`pp-quete-${index}`);
    const totalEl = document.getElementById(`total-quete-or-${index}`);
    if (!totalEl) return;

    const pc = pcEl ? parseInt(pcEl.value) || 0 : 0;
    const pa = paEl ? parseInt(paEl.value) || 0 : 0;
    const po = poEl ? parseInt(poEl.value) || 0 : 0;
    const pp = ppEl ? parseInt(ppEl.value) || 0 : 0;

    const totalPO = po + (pa / 10) + (pc / 100) + (pp * 10);
    totalEl.value = totalPO === 0 ? '' : `${totalPO.toFixed(2)} PO`;
}

function setupQueteListeners(index) {
    // Toggle multiple sessions
    const toggleMultiple = document.getElementById(`quete-multiple-${index}`);
    if (toggleMultiple) {
        toggleMultiple.addEventListener('change', function() {
            const queteSimple = document.getElementById(`quete-simple-${index}`);
            const queteMultiple = document.getElementById(`quete-multiple-details-${index}`);
            
            if (queteSimple && queteMultiple) {
                if (this.checked) {
                    queteSimple.style.display = 'none';
                    queteMultiple.style.display = 'block';
                } else {
                    queteSimple.style.display = 'block';
                    queteMultiple.style.display = 'none';
                }
            }
            
            regenerateIfNeeded();
        });
    }

    // Toggle monnaies section
    const includeMonnaies = document.getElementById(`include-monnaies-${index}`);
    if (includeMonnaies) {
        const updateMonnaies = function() {
            const container = document.getElementById(`monnaie-container-${index}`);
            if (container) {
                container.style.display = this.checked ? 'block' : 'none';
            }
            if (!this.checked) {
                const totalEl = document.getElementById(`total-quete-or-${index}`);
                if (totalEl) totalEl.value = '';
            }
            updateMonnaieTotal(index);
            regenerateIfNeeded();
        };
        includeMonnaies.addEventListener('change', updateMonnaies);
        updateMonnaies.call(includeMonnaies);
    }

    // Toggle objets section
    const includeObjets = document.getElementById(`include-objets-${index}`);
    if (includeObjets) {
        const updateObjets = function() {
            const container = document.getElementById(`objets-container-${index}`);
            if (container) {
                container.style.display = this.checked ? 'block' : 'none';
            }
            regenerateIfNeeded();
        };
        includeObjets.addEventListener('change', updateObjets);
        updateObjets.call(includeObjets);
    }
    
    // Event listeners pour tous les champs de cette quête
    const queteInputs = document.querySelectorAll(`[id*="-${index}"], [id*="-quete-${index}"]`);
    queteInputs.forEach(input => {
        if (!input.hasAttribute('data-listener-added')) {
            input.addEventListener('input', regenerateIfNeeded);
            input.setAttribute('data-listener-added', 'true');
        }
    });

    const xpInput = document.getElementById(`xp-quete-${index}`);
    const refuseXP = document.getElementById(`refuse-xp-${index}`);
    if (refuseXP && xpInput) {
        const toggleXP = function() {
            if (this.checked) {
                xpInput.value = 0;
                xpInput.disabled = true;
            } else {
                xpInput.disabled = false;
            }
            regenerateIfNeeded();
        };
        refuseXP.addEventListener('change', toggleXP);
        toggleXP.call(refuseXP);
    }

    const pcInput = document.getElementById(`pc-quete-${index}`);
    const paInput = document.getElementById(`pa-quete-${index}`);
    const poInput = document.getElementById(`po-quete-${index}`);
    const ppInput = document.getElementById(`pp-quete-${index}`);
    [pcInput, paInput, poInput, ppInput].forEach(inp => {
        if (inp && !inp.hasAttribute('data-total-listener')) {
            inp.addEventListener('input', () => updateMonnaieTotal(index));
            inp.setAttribute('data-total-listener', 'true');
        }
    });

    updateMonnaieTotal(index);

    const addBtn = document.querySelector(`[data-quete="${index}"] .add-recompense`);
    const recompenseContainer = document.getElementById(`recompenses-container-${index}`);

    if (recompenseContainer && recompenseCounters[index] === undefined) {
        recompenseCounters[index] = recompenseContainer.querySelectorAll('.recompense-item').length;
    }

    if (addBtn) {
        addBtn.addEventListener('click', () => addRecompense(index));
    }

    if (recompenseContainer) {
        const items = recompenseContainer.querySelectorAll('.recompense-item');
        items.forEach(item => {
            const rIndex = item.getAttribute('data-recompense');
            setupRecompenseItem(index, rIndex);
        });

        recompenseContainer.addEventListener('click', function(e) {
            if (e.target.classList.contains('delete-recompense')) {
                const item = e.target.closest('.recompense-item');
                const recompenseIndex = item.getAttribute('data-recompense');
                deleteRecompense(index, recompenseIndex);
            }
        });
    }
}

// ===== GÉNÉRATION DES QUÊTES =====

function generateQuestesSection() {
    const quetes = document.querySelectorAll('.quete-bloc');
    let totalXPQuetes = 0;
    let totalMonnaies = { PC: 0, PA: 0, PO: 0, PP: 0 };
    let objetsQuetes = [];
    let autresQuetes = [];
    let xpQuetes = [];
    let recompensesQuetes = [];
    let quetesList = [];
    let objetsList = [];
    let poList = [];

    quetes.forEach((quete, index) => {
        const dataIndex = quete.getAttribute('data-quete');
        const titreEl = document.getElementById(`titre-quete-${dataIndex}`);
        const mjEl = document.getElementById(`nom-mj-${dataIndex}`);
        const xpEl = document.getElementById(`xp-quete-${dataIndex}`);
        const refuseXP = document.getElementById(`refuse-xp-${dataIndex}`);
        const multipleEl = document.getElementById(`quete-multiple-${dataIndex}`);

        const titre = titreEl ? titreEl.value || `[TITRE_QUETE_${index + 1}]` : `[TITRE_QUETE_${index + 1}]`;
        const mj = mjEl ? mjEl.value || `[MJ_${index + 1}]` : `[MJ_${index + 1}]`;
        const xpQuete = xpEl && !refuseXP?.checked ? parseInt(xpEl.value) || 0 : 0;
        const isMultiple = multipleEl ? multipleEl.checked : false;

        if (!refuseXP?.checked) {
            totalXPQuetes += xpQuete;
        }
        xpQuetes.push(xpQuete);

        // Récupérer les récompenses
        let recompensesText = '';

        // Monnaies
        const includeMonnaies = document.getElementById(`include-monnaies-${dataIndex}`);
        let questPO = 0;
        if (includeMonnaies && includeMonnaies.checked) {
            const pcEl = document.getElementById(`pc-quete-${dataIndex}`);
            const paEl = document.getElementById(`pa-quete-${dataIndex}`);
            const poEl = document.getElementById(`po-quete-${dataIndex}`);
            const ppEl = document.getElementById(`pp-quete-${dataIndex}`);

            const pc = pcEl ? parseInt(pcEl.value) || 0 : 0;
            const pa = paEl ? parseInt(paEl.value) || 0 : 0;
            const po = poEl ? parseInt(poEl.value) || 0 : 0;
            const pp = ppEl ? parseInt(ppEl.value) || 0 : 0;

            // Ajouter aux totaux
            totalMonnaies.PC += pc;
            totalMonnaies.PA += pa;
            totalMonnaies.PO += po;
            totalMonnaies.PP += pp;

            // Construire le texte des monnaies
            let monnaieText = [];
            if (pc !== 0) monnaieText.push(`${pc > 0 ? '+' : ''}${pc} PC`);
            if (pa !== 0) monnaieText.push(`${pa > 0 ? '+' : ''}${pa} PA`);
            if (po !== 0) monnaieText.push(`${po > 0 ? '+' : ''}${po} PO`);
            if (pp !== 0) monnaieText.push(`${pp > 0 ? '+' : ''}${pp} PP`);

            if (monnaieText.length > 0) {
                recompensesText += ', ' + monnaieText.join(' ');
            }

            questPO = po + pa / 10 + pc / 100 + pp * 10;
        }

        // Objets
        let objetsText = '';
        const includeObjets = document.getElementById(`include-objets-${dataIndex}`);
        if (includeObjets && includeObjets.checked) {
            const objetsEl = document.getElementById(`objets-quete-${dataIndex}`);
            if (objetsEl && objetsEl.value.trim()) {
                objetsText = objetsEl.value.trim();
                recompensesText += ', ' + objetsText;
                objetsQuetes.push(objetsText);
            }
        }

        // Autres
        const autresEl = document.getElementById(`autres-quete-${dataIndex}`);
        if (autresEl && autresEl.value.trim()) {
            recompensesText += ', ' + autresEl.value.trim();
            autresQuetes.push(autresEl.value.trim());
        }

        recompensesQuetes.push(recompensesText.replace(/^,\s*/, ''));

        // Construire les différentes listes
        let questLine;
        if (isMultiple) {
            const sessionsEl = document.getElementById(`sessions-quete-${dataIndex}`);
            const sessions = sessionsEl ? sessionsEl.value || `[SESSIONS_QUETE_${index + 1}]` : `[SESSIONS_QUETE_${index + 1}]`;
            questLine = `${titre} + ${mj} ⁠- [${sessions}]`;
        } else {
            const lienEl = document.getElementById(`lien-recompense-${dataIndex}`);
            const lien = lienEl ? lienEl.value || `[LIEN_RECOMPENSE_${index + 1}]` : `[LIEN_RECOMPENSE_${index + 1}]`;
            questLine = `${titre} + ${mj} ⁠- ${lien}`;
        }
        quetesList.push(questLine);
        objetsList.push(`${titre}: ${objetsText || '-'}`);
        poList.push(`${titre}: ${(questPO || 0).toFixed(2).replace(/\.00$/, '')} PO`);
    });

    return {
        quetesList,
        objetsList,
        poList,
        totalXPQuetes,
        totalMonnaies,
        objetsQuetes,
        autresQuetes,
        xpQuetes,
        recompensesQuetes
    };
}

// ===== GESTION DES NIVEAUX ET XP =====

function calculateXPProgression(xpActuels, xpObtenus, niveauActuel, niveauCible, classeGainNiveau) {
    const nouveauTotal = xpActuels + xpObtenus;
    let progressionText = '';
    let xpInfo = '';
    
    // XP requis pour passer au niveau suivant depuis le niveau actuel
    const xpRequisActuel = XP_TABLE[niveauActuel + 1] || '?';
    
    // Format de base : ancien/requis + XP ==> nouveau/requis
    progressionText = ` ==> ${nouveauTotal}/${xpRequisActuel}`;
    
    // Vérifier si level up possible
    if (nouveauTotal >= xpRequisActuel && xpRequisActuel !== '?') {
        const classeNom = getClasseForXP(classeGainNiveau);
        progressionText += ` ==> LEVEL UP ${classeNom} ${niveauCible}`;
        
        // Vérifier si c'est le niveau cible attendu
        if (niveauCible === niveauActuel + 1) {
            xpInfo = ' ✅';
        } else if (niveauCible > niveauActuel + 1) {
            // Plusieurs niveaux possibles
            let niveauPossible = niveauActuel;
            let xpRestants = nouveauTotal;
            
            while (niveauPossible < 20 && XP_TABLE[niveauPossible + 1] && xpRestants >= XP_TABLE[niveauPossible + 1]) {
                xpRestants -= XP_TABLE[niveauPossible + 1];
                niveauPossible++;
            }
            
            if (niveauCible <= niveauPossible) {
                xpInfo = ' 🚀';
            } else {
                xpInfo = ` 💡 Vous pourriez atteindre le niveau ${niveauPossible} !`;
            }
        }
    } else {
        // Pas de level up
        if (niveauCible > niveauActuel) {
            const manque = xpRequisActuel - nouveauTotal;
            xpInfo = ` ⚠️ (Manque ${manque} XP pour niveau ${niveauActuel + 1})`;
        }
    }
    
    return { progressionText, xpInfo };
}

// ===== GESTION DES PV =====

function calculatePVGain(classeText, niveauActuel, niveauCible, modConstitution, bonusPV, pvActuels) {
    if (niveauCible <= niveauActuel) return '';
    
    const niveauxGagnes = niveauCible - niveauActuel;
    
    // Extraire la classe principale pour les PV
    let classePrincipale = classeText;
    if (classeText.includes('/')) {
        // Multiclasse - prendre la première classe mentionnée
        classePrincipale = classeText.split('/')[0].trim();
    }
    
    // Extraire juste le nom de la classe (sans le niveau)
    const nomClasse = classePrincipale.split(' ')[0];
    const pvMoyenParNiveau = HP_AVERAGES[nomClasse] || 5;
    
    const pvDeVie = pvMoyenParNiveau * niveauxGagnes;
    const pvConstitution = modConstitution * niveauxGagnes;
    
    let calculText = `${pvActuels} PV + ${pvDeVie} PV obtenus (moyenne)`;
    let totalPVGain = pvDeVie;
    
    if (modConstitution !== 0) {
        const signe = modConstitution >= 0 ? ' +' : ' ';
        calculText += `${signe}${pvConstitution}PV (CON)`;
        totalPVGain += pvConstitution;
    }
    
    if (bonusPV && bonusPV.trim() !== '' && bonusPV !== '0') {
        // Gérer les bonus spéciaux comme "2(ROBUSTE)"
        calculText += ` +${bonusPV}`;
        
        // Extraire la valeur numérique pour le calcul
        const bonusMatch = bonusPV.match(/(\d+)/);
        if (bonusMatch) {
            const bonusNum = parseInt(bonusMatch[1]) * niveauxGagnes;
            totalPVGain += bonusNum;
        }
    }
    
    const nouveauPV = pvActuels + totalPVGain;
    calculText += ` = ${nouveauPV} PV`;
    
    return calculText;
}

// ===== GÉNÉRATION DU TEMPLATE =====

function getSectionTitle(type) {
    const titles = {
        'echange-inter-pj': 'ECHANGE INTER-PJ',
        'apprentissage-sorts': 'APPRENTISSAGE SORTS',
        'copie-grimoire': 'COPIE GRIMOIRE',
        'achat-composants': 'ACHAT COMPOSANTS',
        'craft': 'ARTISANAT',
        'autre': 'ACTIVITÉ SPÉCIALE'
    };
    return titles[type] || 'ACTIVITÉ SPÉCIALE';
}

function getClasseForXP(classeText) {
    // Extraire la classe principale pour l'affichage niveau
    if (!classeText || classeText === '[CLASSE]' || classeText === '[CLASSE_COMPLETE]') {
        return 'CLASSE';
    }
    
    if (classeText.includes('/')) {
        // Multiclasse - prendre la première
        return classeText.split('/')[0].trim().split(' ')[0];
    }
    return classeText.split(' ')[0]; // Enlever le niveau s'il y en a un
}

function generateTemplate() {
    const nomPJEl = document.getElementById('nom-pj');
    const nom = nomPJEl ? nomPJEl.value || '[NOM_PJ]' : '[NOM_PJ]';
    
    // Gestion classe simple vs multiclasse
    const multiclasseToggle = document.getElementById('multiclasse-toggle');
    const isMulticlasse = multiclasseToggle ? multiclasseToggle.checked : false;
    let classe;
    
    if (isMulticlasse) {
        const classeCompleteEl = document.getElementById('classe-complete');
        classe = classeCompleteEl ? classeCompleteEl.value || '[CLASSE_COMPLETE]' : '[CLASSE_COMPLETE]';
    } else {
        const classeEl = document.getElementById('classe');
        classe = classeEl ? classeEl.value || '[CLASSE]' : '[CLASSE]';
    }
    
    // Informations quête
    const { quetesList, objetsList, poList, totalXPQuetes, totalMonnaies, objetsQuetes, autresQuetes, xpQuetes, recompensesQuetes } = generateQuestesSection();
    let sectionQuete;

    if (quetesList.length > 0 && !quetesList[0].includes('[TITRE_QUETE_1]')) {
        const quetesLines = quetesList.map(q => `- ${q}`).join('\n');
        const objetsLines = objetsList.map(o => `- ${o}`).join('\n');
        const poLines = poList.map(p => `- ${p}`).join('\n');
        sectionQuete = `**Quête :**\nQuêtes:\n${quetesLines}\n\nObjets:\n${objetsLines}\n\nPO:\n${poLines}\n+${totalXPQuetes} XP`;
    } else {
        sectionQuete = '**Quête :** [TITRE_QUETE] + [NOM_MJ] ⁠- [LIEN_RECOMPENSES]';
    }
    
    // Informations XP/Niveau
    const xpActuelsEl = document.getElementById('xp-actuels');
    const niveauActuelEl = document.getElementById('niveau-actuel');
    const niveauCibleEl = document.getElementById('niveau-cible');
    const classeGainNiveauEl = document.getElementById('classe-gain-niveau');
    
    const xpActuels = xpActuelsEl ? parseInt(xpActuelsEl.value) || 0 : 0;
    const niveauActuel = niveauActuelEl ? parseInt(niveauActuelEl.value) || 1 : 1;
    const niveauCible = niveauCibleEl ? parseInt(niveauCibleEl.value) || 1 : 1;
    const classeGainNiveau = classeGainNiveauEl ? classeGainNiveauEl.value : '';
    
    // Informations PV
    const pvActuelsEl = document.getElementById('pv-actuels');
    const modConstitutionEl = document.getElementById('mod-constitution');
    const bonusPVEl = document.getElementById('bonus-pv');
    
    const pvActuels = pvActuelsEl ? parseInt(pvActuelsEl.value) || 0 : 0;
    const modConstitution = modConstitutionEl ? parseInt(modConstitutionEl.value) || 0 : 0;
    const bonusPV = bonusPVEl ? bonusPVEl.value : '';
    
    // Sorts et capacités
    const nouvellesCapacitesEl = document.getElementById('nouvelles-capacites');
    const nouveauDonEl = document.getElementById('nouveau-don');
    const donQueteEl = document.getElementById('don-quete');
    const nouveauxSortsEl = document.getElementById('nouveaux-sorts');
    const sortsRemplacesEl = document.getElementById('sorts-remplaces');

    const parseList = (el) => {
        if (!el || !el.value) return [];
        return el.value.split(/[\n,]+/).map(s => s.trim()).filter(Boolean);
    };

    const nouvellesCapacites = nouvellesCapacitesEl ? nouvellesCapacitesEl.value || '-' : '-';
    const nouveauDonList = parseList(nouveauDonEl);
    const donQueteList = parseList(donQueteEl);
    const nouveauxSortsList = parseList(nouveauxSortsEl);
    const sortsRemplacesList = parseList(sortsRemplacesEl);
    const nouveauxDons = nouveauDonList.length ? nouveauDonList.join(', ') : '-';
    const donsQuete = donQueteList.length ? donQueteList.join(', ') : '-';
    const nouveauxSorts = nouveauxSortsList.length ? nouveauxSortsList.join(', ') : '-';
    const sortsRemplaces = sortsRemplacesList.length ? sortsRemplacesList.join(', ') : '-';
    
    // Items et argent
    const objetsLootesEl = document.getElementById('objets-lootes');
    const poLootesEl = document.getElementById('po-lootees');
    const transactionsContainer = document.getElementById('transactions-container');
    const ancienSoldeEl = document.getElementById('ancien-solde');
    const poRecuesEl = document.getElementById('po-recues');

    const objetsLootesList = objetsLootesEl ? parseList(objetsLootesEl) : [];
    const objetsLootes = objetsLootesList.length ? objetsLootesList.join(', ') : '';
    const poLootees = poLootesEl ? parseFloat(poLootesEl.value) || 0 : 0;
    let transactionsText = '';
    let netPOMarchand = 0;

    if (transactionsContainer) {
        const lines = transactionsContainer.querySelectorAll('.transaction-line');
        const formatted = [];
        lines.forEach(line => {
            const type = line.querySelector('select')?.value;
            const desc = line.querySelector('input[type="text"]')?.value.trim();
            const qtyStr = line.querySelector('.quantity')?.value;
            const qty = parseInt(qtyStr) || 1;
            const priceStr = line.querySelector('.price')?.value;
            const price = parseFloat(priceStr);
            if (type && desc && !isNaN(price)) {
                const subtotal = qty * price;
                const lineText = qty > 1
                    ? `${type} : ${qty}×${desc} ${price.toFixed(2)}PO = ${subtotal.toFixed(2)}PO`
                    : `${type} : ${desc} ${subtotal.toFixed(2)}PO`;
                formatted.push(lineText);
                if (type === 'ACHAT') {
                    netPOMarchand -= subtotal;
                } else if (type === 'VENTE') {
                    netPOMarchand += subtotal;
                }
            }
        });
        transactionsText = formatted.join('\n');
    }

    const ancienSolde = ancienSoldeEl ? ancienSoldeEl.value || '[ANCIEN_SOLDE]' : '[ANCIEN_SOLDE]';
    const ancienSoldeNum = parseFloat(ancienSolde);
    const poRecues = poRecuesEl ? parseFloat(poRecuesEl.value) || 0 : 0;

    // Artisanat
    const artisanatNotesEl = document.getElementById('artisanat-notes');
    const artisanatItemsEl = document.getElementById('artisanat-items');
    const artisanatCostEl = document.getElementById('artisanat-cost');

    const artisanatNotes = artisanatNotesEl ? artisanatNotesEl.value.trim() : '';
    const artisanatItemsList = artisanatItemsEl ? parseList(artisanatItemsEl) : [];
    const artisanatCostRaw = artisanatCostEl ? artisanatCostEl.value.trim() : '';
    const artisanatCost = artisanatCostRaw !== '' ? parseFloat(artisanatCostRaw) || 0 : 0;
    
    // Section spéciale
    const typeSpecialEl = document.getElementById('type-special');
    const descriptionSpecialEl = document.getElementById('description-special');
    const includeMarchandEl = document.getElementById('section-marchand');
    
    const typeSpecial = typeSpecialEl ? typeSpecialEl.value : '';
    const descriptionSpecial = descriptionSpecialEl ? descriptionSpecialEl.value : '';
    const includeMarchand = includeMarchandEl ? includeMarchandEl.checked : false;
    
    // Calculs
    const { progressionText, xpInfo } = calculateXPProgression(xpActuels, totalXPQuetes, niveauActuel, niveauCible, classeGainNiveau || classe);
    const pvCalcul = calculatePVGain(classeGainNiveau || classe, niveauActuel, niveauCible, modConstitution, bonusPV, pvActuels);
    
    // Construction du template
    let template = `Nom du PJ : ${nom}
Classe : ${classe}`;

    // Section spéciale si définie
    if (typeSpecial && descriptionSpecial) {
        const sectionTitle = getSectionTitle(typeSpecial);
        template += `
/ =======================  ${sectionTitle}  ========================= \\ 
${descriptionSpecial}
\\ =======================  ${sectionTitle}  ========================= /`;
    }

    // Section PJ principale
    template += `
** / =======================  PJ  ========================= \\ **
${sectionQuete}`;

    // XP seulement si renseignés
    if (xpActuels >= 0 && totalXPQuetes > 0) {
        const xpRequisPourNiveau = XP_TABLE[niveauActuel + 1] || '?';
        const nouveauTotalXP = xpActuels + totalXPQuetes;
        const affichageXP = `**Solde XP :** ${xpActuels}/${xpRequisPourNiveau} + ${totalXPQuetes}XP obtenue ==> ${nouveauTotalXP}${progressionText}${xpInfo}`;
        template += `
${affichageXP}`;
    }

    // Gain de niveau seulement si différent
    if (niveauCible > niveauActuel) {
        template += `
**Gain de niveau :** Niveau ${niveauActuel} → **Niveau ${niveauCible}** 🎉`;
        
        // PV détaillés si montée de niveau
        if (pvCalcul && pvActuels > 0) {
            template += `
**PV :** ${pvCalcul}`;
        }
    }

    template += `
**¤ Capacités et sorts supplémentaires :**
Nouvelle(s) capacité(s) :
${nouvellesCapacites}
Nouveau(x) don(s) :
${nouveauxDons}
Don(s) (gain de quête) :
${donsQuete}
Nouveau(x) sort(s) :
${nouveauxSorts}
Sort(s) remplacé(s) :
${sortsRemplaces}`;

    // Inventaire seulement si renseigné
    const objetsLootesBase = objetsLootes || '';
    const objetsFromQuetes = objetsQuetes.length > 0 ? objetsQuetes.join(', ') : '';
    const tousObjets = [objetsLootesBase, objetsFromQuetes].filter(o => o).join(', ') || '';
    
    // Calculer les totaux de monnaies (quêtes + manuel)
    const totalPC = totalMonnaies.PC;
    const totalPA = totalMonnaies.PA;
    const totalPO = totalMonnaies.PO + poLootees;
    const totalPP = totalMonnaies.PP;

    // Convertir toutes les monnaies des quêtes en équivalent PO
    const questPO = totalMonnaies.PO
        + totalMonnaies.PA / 10
        + totalMonnaies.PC / 100
        + totalMonnaies.PP * 10;

    // Total des PO lootées (quêtes + PO entrées manuellement)
    const totalLootPO = poLootees + questPO;
    const totalLootPORounded = Number(totalLootPO.toFixed(2));

    const totalOrEl = document.getElementById('total-or');
    if (totalOrEl) {
        totalOrEl.value = `${totalLootPORounded.toFixed(2)} PO`;
    }

    // Construire le texte des monnaies lootées
    let monnaiesLootees = [];
    if (totalPC !== 0) monnaiesLootees.push(`${totalPC > 0 ? '+' : ''}${totalPC} PC`);
    if (totalPA !== 0) monnaiesLootees.push(`${totalPA > 0 ? '+' : ''}${totalPA} PA`);
    if (totalPO !== 0) monnaiesLootees.push(`${totalPO > 0 ? '+' : ''}${totalPO} PO`);
    if (totalPP !== 0) monnaiesLootees.push(`${totalPP > 0 ? '+' : ''}${totalPP} PP`);

    const monnaiesText = monnaiesLootees.length > 0 ? monnaiesLootees.join(' ') : '';
    
    if (tousObjets !== '' || monnaiesText !== '') {
        template += `
**¤ Inventaire**`;
        if (tousObjets !== '') {
            template += `
Objets lootés :
${tousObjets}`;
        }
        if (monnaiesText !== '') {
            template += `
Monnaies lootées: ${monnaiesText}`;
        }
    }

    template += `
** \\ =======================  PJ  ========================= / **`;

    // Section Marchand si demandée
    if (includeMarchand && transactionsText.trim() !== '') {
        template += `
/ =======================  MARCHAND  ========================= \\
${transactionsText}
\\ =======================  MARCHAND  ========================= /`;
    }

    // Calcul nouveau solde en convertissant toutes les monnaies des quêtes en PO
    const changeTotal = poRecues + poLootees + questPO + netPOMarchand - artisanatCost;
    const ancienSoldeAffiche = isNaN(ancienSoldeNum) ? ancienSolde : ancienSoldeNum.toFixed(2);
    const nouveauSoldeCalc = isNaN(ancienSoldeNum) ? '[NOUVEAU_SOLDE]' : (ancienSoldeNum + changeTotal).toFixed(2);

    const soldeLines = [];
    soldeLines.push(`ANCIEN SOLDE ${ancienSoldeAffiche}`);

    const formatChange = (val) => `${val >= 0 ? '+' : '-'}${Math.abs(val).toFixed(2)}`;
    if (poRecues !== 0) soldeLines.push(formatChange(poRecues));
    if (poLootees !== 0) soldeLines.push(formatChange(poLootees));
    if (questPO !== 0) soldeLines.push(formatChange(questPO));
    if (netPOMarchand !== 0) soldeLines.push(formatChange(netPOMarchand));
    if (artisanatCost > 0) soldeLines.push(`-${artisanatCost.toFixed(2)}`);
    soldeLines.push(`= ${nouveauSoldeCalc}`);

    template += `
**¤ Solde :**
${soldeLines.join('\n')}
*Fiche R20 à jour.*`;

    const hasArtisanat = artisanatNotes || artisanatItemsList.length > 0 || artisanatCostRaw !== '';
    if (hasArtisanat) {
        template += `
**Artisanat :** ${artisanatNotes}`;
        if (artisanatItemsList.length > 0) {
            template += `
Obtention des objets suivants :
${artisanatItemsList.map(i => `- ${i}`).join('\n')}`;
        }
        if (artisanatCost > 0) {
            const artisanatCostFormatted = artisanatCost.toFixed(2);
            template += `
Coût : ${artisanatCostFormatted} PO`;
        }
    }

    const outputEl = document.getElementById('discord-output');
    const outputPart2El = document.getElementById('discord-output-part2');
    const copyBtnPart2 = document.getElementById('copy-btn-part2');
    const splitWarning = document.getElementById('split-warning');
    const templateLength = template.length;
    const remaining = 1800 - templateLength;
    const indicator = document.getElementById('char-indicator');
    if (indicator) {
        indicator.textContent = `${remaining} caractères restants`;
        const nearLimit = remaining < 0 || remaining < 100;
        indicator.classList.toggle('warning', nearLimit);
    }

    if (templateLength > 1800) {
        const mid = Math.ceil(templateLength / 2);
        const part1 = template.slice(0, mid);
        const part2 = template.slice(mid);
        if (outputEl) {
            outputEl.textContent = part1;
        }
        if (outputPart2El) {
            outputPart2El.textContent = part2;
            outputPart2El.style.display = 'block';
        }
        if (copyBtnPart2) {
            copyBtnPart2.style.display = 'inline-block';
        }
        if (splitWarning) {
            splitWarning.textContent = '⚠️ Le message dépasse 1 800 caractères ; il a été divisé en deux parties';
            splitWarning.style.display = 'block';
        }
    } else {
        if (outputEl) {
            outputEl.textContent = template;
        }
        if (outputPart2El) {
            outputPart2El.textContent = '';
            outputPart2El.style.display = 'none';
        }
        if (copyBtnPart2) {
            copyBtnPart2.style.display = 'none';
        }
        if (splitWarning) {
            splitWarning.textContent = '';
            splitWarning.style.display = 'none';
        }
    }
}

// ===== FONCTIONS UTILITAIRES =====

function regenerateIfNeeded() {
    const nomPJ = document.getElementById('nom-pj');
    if (nomPJ && nomPJ.value) {
        generateTemplate();
    }
}

function copyToClipboard(text) {
    return navigator.clipboard.writeText(text).catch(err => {
        console.error('Erreur lors de la copie dans le presse-papiers :', err);
        throw err;
    });
}

// ===== INITIALISATION =====

document.addEventListener('DOMContentLoaded', function() {
    // Gestion du toggle multiclasse
    const multiclasseToggle = document.getElementById('multiclasse-toggle');
    if (multiclasseToggle) {
        multiclasseToggle.addEventListener('change', function() {
            const classeSimple = document.getElementById('classe-simple');
            const classeMulti = document.getElementById('classe-multi');
            
            if (classeSimple && classeMulti) {
                if (this.checked) {
                    classeSimple.style.display = 'none';
                    classeMulti.style.display = 'block';
                } else {
                    classeSimple.style.display = 'block';
                    classeMulti.style.display = 'none';
                }
            }
            
            regenerateIfNeeded();
        });
    }

    // Setup des listeners pour la première quête
    setupQueteListeners(0);

    // Bouton d'ajout de transaction
    const addTransactionBtn = document.getElementById('add-transaction');
    if (addTransactionBtn) {
        addTransactionBtn.addEventListener('click', addTransactionLine);
    }

    // Boutons de copie
    document.querySelectorAll('.copy-btn[data-target]').forEach(btn => {
        const targetId = btn.getAttribute('data-target');
        if (!targetId || !document.getElementById(targetId)) {
            console.error('Bouton de copie sans data-target valide:', btn);
            return;
        }

        const originalText = btn.textContent;
        btn.addEventListener('click', () => {
            const outputEl = document.getElementById(targetId);
            const text = outputEl ? outputEl.textContent : '';
            if (!text || text === 'Remplissez les champs à gauche pour voir le template généré...') {
                btn.textContent = '⚠️ Générer d\'abord';
                setTimeout(() => { btn.textContent = originalText; }, 2000);
                return;
            }

            copyToClipboard(text)
                .then(() => {
                    btn.textContent = '✅ Copié !';
                    btn.classList.add('success');
                    setTimeout(() => {
                        btn.textContent = originalText;
                        btn.classList.remove('success');
                    }, 2000);
                })
                .catch(() => {
                    btn.textContent = '❌ Erreur';
                    setTimeout(() => { btn.textContent = originalText; }, 2000);
                });
        });
    });

    // Listeners pour tous les autres champs
    const inputs = document.querySelectorAll(
        'input:not([id*="quete"]):not([data-listener-added]),'
        + ' select:not([data-listener-added]),'
        + ' textarea:not([id*="quete"]):not([data-listener-added]),'
        + ' textarea#don-quete:not([data-listener-added]),'
        + ' textarea#objets-lootes:not([data-listener-added]),'
        + ' input#po-lootees:not([data-listener-added]),'
        + ' input#po-recues:not([data-listener-added]),'
        + ' input#ancien-solde:not([data-listener-added]),'
        + ' textarea#artisanat-notes:not([data-listener-added]),'
        + ' textarea#artisanat-items:not([data-listener-added]),'
        + ' input#artisanat-cost:not([data-listener-added]),'
        + ' input#section-marchand:not([data-listener-added])'
    );
    inputs.forEach(input => {
        input.addEventListener('input', regenerateIfNeeded);
        input.setAttribute('data-listener-added', 'true');
    });

    // Setup initial des transactions si présentes
    document.querySelectorAll('#transactions-container .transaction-line').forEach(setupTransactionLine);

    // Génération initiale du template
    regenerateIfNeeded();
});