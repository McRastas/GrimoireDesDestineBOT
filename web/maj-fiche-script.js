// ===== CONFIGURATION ET DONNÉES =====

// Table XP système serveur (extraite du CSV)
const XP_TABLE = {
    1: 1, 2: 2, 3: 2, 4: 3, 5: 3, 6: 4, 7: 4, 8: 4, 9: 4, 10: 4,
    11: 5, 12: 5, 13: 5, 14: 6, 15: 6, 16: 7, 17: 8, 18: 9, 19: 10, 20: 0
};

// PV moyens par classe (basé sur les dés de vie)
const HP_AVERAGES = {
    'Magicien': 4, 'Ensorceleur': 4, 'Sorcier': 4,  // d6 → 4
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
        <input type="number" class="quantity" min="1" step="1" placeholder="1">
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

// ===== GESTION DES CAPACITÉS EXTRAS =====

function addCapaciteExtraLine() {
    const container = document.getElementById('capacites-extras-container');
    if (!container) return;
    const line = document.createElement('div');
    line.className = 'capacite-extra-line';
    line.innerHTML = `
        <select class="cap-extra-type">
            <option value="sort-via">Sort via...</option>
            <option value="invocation-apprise">Invocation apprise</option>
            <option value="invocation-remplacee">Invocation remplacée</option>
        </select>
        <select class="cap-extra-provenance">
            <option value="Don">Don</option>
            <option value="Parchemin">Parchemin</option>
            <option value="Grimoire">Grimoire</option>
            <option value="Récompense">Récompense</option>
            <option value="Autre">Autre</option>
        </select>
        <textarea class="cap-extra-contenu" rows="2" placeholder="Un sort / invocation par ligne"></textarea>
        <button type="button" class="delete-capacite-extra">🗑️</button>
    `;
    container.appendChild(line);
    setupCapaciteExtraLine(line);
    regenerateIfNeeded();
}

function deleteCapaciteExtraLine(line) {
    line.remove();
    regenerateIfNeeded();
}

function setupCapaciteExtraLine(line) {
    const typeSelect = line.querySelector('.cap-extra-type');
    const provenanceSelect = line.querySelector('.cap-extra-provenance');
    const toggleProvenance = () => {
        provenanceSelect.style.display = typeSelect.value === 'sort-via' ? '' : 'none';
    };
    toggleProvenance();
    typeSelect.addEventListener('change', () => { toggleProvenance(); regenerateIfNeeded(); });
    provenanceSelect.addEventListener('change', regenerateIfNeeded);
    line.querySelector('.cap-extra-contenu').addEventListener('input', regenerateIfNeeded);
    line.querySelector('.delete-capacite-extra').addEventListener('click', () => deleteCapaciteExtraLine(line));
}

// ===== GESTION DES OBJETS (lignes dynamiques) =====

let objetCounters = {};

function addObjetLigne(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (objetCounters[containerId] === undefined) {
        objetCounters[containerId] = container.querySelectorAll('.objet-ligne').length;
    }

    const objetIndex = objetCounters[containerId]++;

    const html = `
        <div class="objet-ligne" data-objet="${objetIndex}">
            <input type="text" class="objet-desc" placeholder="Nom de l'objet">
            <input type="number" class="objet-total" placeholder="Total inv." min="0">
            <button type="button" class="delete-objet-ligne">🗑️</button>
        </div>
    `;

    container.insertAdjacentHTML('beforeend', html);

    const newLigne = container.querySelector(`.objet-ligne[data-objet="${objetIndex}"]`);
    setupObjetLigneListeners(newLigne, containerId);

    updateObjetDeleteButtons(containerId);
    regenerateIfNeeded();
}

function deleteObjetLigne(ligne, containerId) {
    ligne.remove();
    updateObjetDeleteButtons(containerId);
    regenerateIfNeeded();
}

function updateObjetDeleteButtons(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const lignes = container.querySelectorAll('.objet-ligne');
    lignes.forEach(ligne => {
        const deleteBtn = ligne.querySelector('.delete-objet-ligne');
        if (deleteBtn) {
            if (lignes.length > 1) {
                deleteBtn.classList.remove('hidden');
            } else {
                deleteBtn.classList.add('hidden');
            }
        }
    });
}

function setupObjetLigneListeners(ligne, containerId) {
    if (!ligne) return;

    const inputs = ligne.querySelectorAll('input');
    inputs.forEach(input => {
        if (!input.hasAttribute('data-objet-listener')) {
            input.addEventListener('input', regenerateIfNeeded);
            input.setAttribute('data-objet-listener', 'true');
        }
    });

    const deleteBtn = ligne.querySelector('.delete-objet-ligne');
    if (deleteBtn && !deleteBtn.hasAttribute('data-objet-listener')) {
        deleteBtn.addEventListener('click', () => deleteObjetLigne(ligne, containerId));
        deleteBtn.setAttribute('data-objet-listener', 'true');
    }
}

function initObjetContainer(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (objetCounters[containerId] === undefined) {
        objetCounters[containerId] = container.querySelectorAll('.objet-ligne').length;
    }

    container.querySelectorAll('.objet-ligne').forEach(ligne => {
        setupObjetLigneListeners(ligne, containerId);
    });

    updateObjetDeleteButtons(containerId);
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
        newDeleteBtn.classList.remove('hidden');
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
                deleteBtn.classList.add('hidden');
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
            <select class="recompense-select">
                <option value="monnaie" selected>💰 Monnaie</option>
                <option value="item">🎒 Objet</option>
            </select>
            <div class="recompense-details">
                <input type="number" placeholder="PC" class="flex-1">
                <input type="number" placeholder="PA" class="flex-1">
                <input type="number" placeholder="PO" class="flex-1">
                <input type="number" placeholder="PP" class="flex-1">
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
            details.innerHTML = `<input type="text" placeholder="Description" class="flex-1">`;
        } else {
            details.innerHTML = `
                <input type="number" placeholder="PC" class="flex-1">
                <input type="number" placeholder="PA" class="flex-1">
                <input type="number" placeholder="PO" class="flex-1">
                <input type="number" placeholder="PP" class="flex-1">
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
            <h4 class="quete-title">🎯 Quête ${index + 1}</h4>
            
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

            <div id="quete-multiple-details-${index}" class="form-group hidden">
                <label for="sessions-quete-${index}">Sessions de la quête :</label>
                <textarea id="sessions-quete-${index}" rows="4" placeholder="- https://discord.com/channels/.../... + 1XP,&#10;- https://discord.com/channels/.../... + 1 XP"></textarea>
            </div>

            <div class="form-group">
                <label for="xp-quete-${index}">XP de cette quête :</label>
                <input type="number" id="xp-quete-${index}" placeholder="1" min="0" max="10">
            </div>

            <div class="checkbox-group">
                <input type="checkbox" id="refuse-xp-${index}">
                <label for="refuse-xp-${index}">Refuser l’XP de cette quête</label>
            </div>

        <div class="form-group">
            <h5 class="reward-title">🎁 Récompenses (optionnelles) :</h5>

            <div class="checkbox-group">
                <label for="include-monnaies-${index}">
                    <input type="checkbox" id="include-monnaies-${index}" class="inline-checkbox">
                    Inclure monnaies
                </label>
            </div>
            <div id="monnaie-container-${index}" class="hidden">
                <div id="finances-lignes-${index}" class="finances-lignes">
                    <div class="finance-ligne" data-finance="0">
                        <select class="finance-type">
                            <option value="gain">+ Gain</option>
                            <option value="depense">- Dépense</option>
                        </select>
                        <div class="finance-monnaies">
                            <input type="number" class="finance-pc" placeholder="PC">
                            <input type="number" class="finance-pa" placeholder="PA">
                            <input type="number" class="finance-po" placeholder="PO">
                            <input type="number" class="finance-pp" placeholder="PP">
                        </div>
                        <button type="button" class="delete-finance-ligne hidden">🗑️</button>
                    </div>
                </div>
                <button type="button" class="add-finance-ligne" data-quete="${index}">➕ Ajouter une ligne</button>
                <input type="text" id="total-quete-or-${index}" placeholder="Total en PO" disabled class="monnaie-total">
            </div>

            <div class="checkbox-group">
                <label for="include-objets-${index}">
                    <input type="checkbox" id="include-objets-${index}" class="inline-checkbox">
                    Inclure objets
                </label>
            </div>
            <div id="objets-container-${index}" class="hidden">
                <div id="objets-lignes-${index}" class="objets-lignes">
                    <div class="objet-ligne" data-objet="0">
                        <input type="text" class="objet-desc" placeholder="Nom de l'objet">
                        <input type="number" class="objet-total" placeholder="Total inv." min="0">
                        <button type="button" class="delete-objet-ligne hidden">🗑️</button>
                    </div>
                </div>
                <button type="button" class="add-objet-ligne" data-container="objets-lignes-${index}">➕ Objet</button>
            </div>

            <div class="reward-type">
                <label>⭐ Autres récompenses :</label>
                <textarea id="autres-quete-${index}" rows="2" placeholder="Don du fruit blanc à Kornélius, Sort Interdiction dans le grimoire"></textarea>
            </div>
        </div>

            <button type="button" class="delete-quete hidden" onclick="deleteQuete(${index})">
                🗑️ Supprimer cette quête
            </button>
        </div>
    `;
}

function updateMonnaieTotal(index) {
    const container = document.getElementById(`finances-lignes-${index}`);
    const totalEl = document.getElementById(`total-quete-or-${index}`);
    if (!totalEl || !container) return;

    let totalPO = 0;
    const lignes = container.querySelectorAll('.finance-ligne');
    lignes.forEach(ligne => {
        const type = ligne.querySelector('.finance-type')?.value || 'gain';
        const pc = parseInt(ligne.querySelector('.finance-pc')?.value) || 0;
        const pa = parseInt(ligne.querySelector('.finance-pa')?.value) || 0;
        const po = parseInt(ligne.querySelector('.finance-po')?.value) || 0;
        const pp = parseInt(ligne.querySelector('.finance-pp')?.value) || 0;

        const lignePO = po + (pa / 10) + (pc / 100) + (pp * 10);
        if (type === 'gain') {
            totalPO += lignePO;
        } else {
            totalPO -= lignePO;
        }
    });

    totalEl.value = totalPO === 0 ? '' : `${totalPO.toFixed(2)} PO`;
}

// Compteurs pour les lignes de finances par quête
let financeCounters = {};

function addFinanceLigne(queteIndex) {
    const container = document.getElementById(`finances-lignes-${queteIndex}`);
    if (!container) return;

    if (financeCounters[queteIndex] === undefined) {
        financeCounters[queteIndex] = container.querySelectorAll('.finance-ligne').length;
    }

    const financeIndex = financeCounters[queteIndex]++;

    const html = `
        <div class="finance-ligne" data-finance="${financeIndex}">
            <select class="finance-type">
                <option value="gain">+ Gain</option>
                <option value="depense">- Dépense</option>
            </select>
            <div class="finance-monnaies">
                <input type="number" class="finance-pc" placeholder="PC">
                <input type="number" class="finance-pa" placeholder="PA">
                <input type="number" class="finance-po" placeholder="PO">
                <input type="number" class="finance-pp" placeholder="PP">
            </div>
            <button type="button" class="delete-finance-ligne">🗑️</button>
        </div>
    `;

    container.insertAdjacentHTML('beforeend', html);

    // Setup listeners pour la nouvelle ligne
    const newLigne = container.querySelector(`.finance-ligne[data-finance="${financeIndex}"]`);
    setupFinanceLigneListeners(newLigne, queteIndex);

    // Afficher les boutons de suppression s'il y a plus d'une ligne
    updateFinanceDeleteButtons(queteIndex);

    regenerateIfNeeded();
}

function deleteFinanceLigne(ligne, queteIndex) {
    ligne.remove();
    updateFinanceDeleteButtons(queteIndex);
    updateMonnaieTotal(queteIndex);
    regenerateIfNeeded();
}

function updateFinanceDeleteButtons(queteIndex) {
    const container = document.getElementById(`finances-lignes-${queteIndex}`);
    if (!container) return;

    const lignes = container.querySelectorAll('.finance-ligne');
    lignes.forEach(ligne => {
        const deleteBtn = ligne.querySelector('.delete-finance-ligne');
        if (deleteBtn) {
            if (lignes.length > 1) {
                deleteBtn.classList.remove('hidden');
            } else {
                deleteBtn.classList.add('hidden');
            }
        }
    });
}

function setupFinanceLigneListeners(ligne, queteIndex) {
    if (!ligne) return;

    const inputs = ligne.querySelectorAll('input, select');
    inputs.forEach(input => {
        if (!input.hasAttribute('data-finance-listener')) {
            input.addEventListener('input', () => {
                updateMonnaieTotal(queteIndex);
                regenerateIfNeeded();
            });
            input.addEventListener('change', () => {
                updateMonnaieTotal(queteIndex);
                regenerateIfNeeded();
            });
            input.setAttribute('data-finance-listener', 'true');
        }
    });

    const deleteBtn = ligne.querySelector('.delete-finance-ligne');
    if (deleteBtn && !deleteBtn.hasAttribute('data-finance-listener')) {
        deleteBtn.addEventListener('click', () => deleteFinanceLigne(ligne, queteIndex));
        deleteBtn.setAttribute('data-finance-listener', 'true');
    }
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
                    queteSimple.classList.add('hidden');
                    queteMultiple.classList.remove('hidden');
                } else {
                    queteSimple.classList.remove('hidden');
                    queteMultiple.classList.add('hidden');
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
                container.classList.toggle('hidden', !this.checked);
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
                container.classList.toggle('hidden', !this.checked);
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

    // Setup des lignes de finances existantes
    const financesContainer = document.getElementById(`finances-lignes-${index}`);
    if (financesContainer) {
        const lignes = financesContainer.querySelectorAll('.finance-ligne');
        lignes.forEach(ligne => {
            setupFinanceLigneListeners(ligne, index);
        });

        // Initialiser le compteur
        if (financeCounters[index] === undefined) {
            financeCounters[index] = lignes.length;
        }
    }

    // Bouton d'ajout de ligne de finance
    const addFinanceBtn = document.querySelector(`[data-quete="${index}"] .add-finance-ligne, .add-finance-ligne[data-quete="${index}"]`);
    if (addFinanceBtn && !addFinanceBtn.hasAttribute('data-listener-added')) {
        addFinanceBtn.addEventListener('click', () => addFinanceLigne(index));
        addFinanceBtn.setAttribute('data-listener-added', 'true');
    }

    updateMonnaieTotal(index);
    updateFinanceDeleteButtons(index);

    // Setup des lignes d'objets
    const objetsContainerId = `objets-lignes-${index}`;
    initObjetContainer(objetsContainerId);

    // Bouton d'ajout d'objet
    const addObjetBtn = document.querySelector(`[data-container="objets-lignes-${index}"]`);
    if (addObjetBtn && !addObjetBtn.hasAttribute('data-objet-btn-added')) {
        addObjetBtn.addEventListener('click', () => addObjetLigne(objetsContainerId));
        addObjetBtn.setAttribute('data-objet-btn-added', 'true');
    }

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
    let objetsList = []; // tableau de {desc, total, quete}
    let poList = []; // tableau de {titre, lines, total}

    quetes.forEach((quete, index) => {
        const dataIndex = quete.getAttribute('data-quete');
        const titreEl = document.getElementById(`titre-quete-${dataIndex}`);
        const mjEl = document.getElementById(`nom-mj-${dataIndex}`);
        const xpEl = document.getElementById(`xp-quete-${dataIndex}`);
        const refuseXP = document.getElementById(`refuse-xp-${dataIndex}`);
        const multipleEl = document.getElementById(`quete-multiple-${dataIndex}`);

        const titre = titreEl ? titreEl.value.trim() : '';
        const mj = mjEl ? mjEl.value.trim() : '';
        const xpQuete = xpEl && !refuseXP?.checked ? parseInt(xpEl.value) || 0 : 0;
        const isMultiple = multipleEl ? multipleEl.checked : false;

        // Récupérer les récompenses
        let recompensesText = '';

        // Monnaies - traitement des lignes multiples
        const includeMonnaies = document.getElementById(`include-monnaies-${dataIndex}`);
        let questPO = 0;
        let monnaieText = [];
        let financesDetails = []; // Détails des lignes de finances
        let rawLines = []; // Données brutes par ligne : {po, pa, pc, pp, sign}
        if (includeMonnaies && includeMonnaies.checked) {
            const financesContainer = document.getElementById(`finances-lignes-${dataIndex}`);
            if (financesContainer) {
                const lignes = financesContainer.querySelectorAll('.finance-ligne');
                lignes.forEach(ligne => {
                    const type = ligne.querySelector('.finance-type')?.value || 'gain';
                    const pc = parseInt(ligne.querySelector('.finance-pc')?.value) || 0;
                    const pa = parseInt(ligne.querySelector('.finance-pa')?.value) || 0;
                    const po = parseInt(ligne.querySelector('.finance-po')?.value) || 0;
                    const pp = parseInt(ligne.querySelector('.finance-pp')?.value) || 0;

                    if (pc !== 0 || pa !== 0 || po !== 0 || pp !== 0) {
                        const signe = type === 'gain' ? '+' : '-';
                        const lignePO = po + pa / 10 + pc / 100 + pp * 10;

                        // Construire le texte de cette ligne
                        let ligneMonnaies = [];
                        if (pc !== 0) ligneMonnaies.push(`${pc} PC`);
                        if (pa !== 0) ligneMonnaies.push(`${pa} PA`);
                        if (po !== 0) ligneMonnaies.push(`${po} PO`);
                        if (pp !== 0) ligneMonnaies.push(`${pp} PP`);

                        const ligneText = `${signe} ${ligneMonnaies.join(' ')}`;
                        financesDetails.push(ligneText);
                        rawLines.push({ po, pa, pc, pp, sign: type === 'gain' ? 1 : -1 });

                        // Ajouter aux totaux globaux
                        if (type === 'gain') {
                            totalMonnaies.PC += pc;
                            totalMonnaies.PA += pa;
                            totalMonnaies.PO += po;
                            totalMonnaies.PP += pp;
                            questPO += lignePO;
                        } else {
                            totalMonnaies.PC -= pc;
                            totalMonnaies.PA -= pa;
                            totalMonnaies.PO -= po;
                            totalMonnaies.PP -= pp;
                            questPO -= lignePO;
                        }
                    }
                });
            }

            // Construire le texte résumé des monnaies
            if (totalMonnaies.PC !== 0 || totalMonnaies.PA !== 0 || totalMonnaies.PO !== 0 || totalMonnaies.PP !== 0) {
                if (totalMonnaies.PC !== 0) monnaieText.push(`${totalMonnaies.PC > 0 ? '+' : ''}${totalMonnaies.PC} PC`);
                if (totalMonnaies.PA !== 0) monnaieText.push(`${totalMonnaies.PA > 0 ? '+' : ''}${totalMonnaies.PA} PA`);
                if (totalMonnaies.PO !== 0) monnaieText.push(`${totalMonnaies.PO > 0 ? '+' : ''}${totalMonnaies.PO} PO`);
                if (totalMonnaies.PP !== 0) monnaieText.push(`${totalMonnaies.PP > 0 ? '+' : ''}${totalMonnaies.PP} PP`);
            }
        }
        if (financesDetails.length > 0) {
            recompensesText += ', ' + financesDetails.join(', ');
        }

        // Objets
        let objetsText = '';
        let questObjets = []; // {desc, total}
        const includeObjets = document.getElementById(`include-objets-${dataIndex}`);
        if (includeObjets && includeObjets.checked) {
            const objetsContainer = document.getElementById(`objets-lignes-${dataIndex}`);
            if (objetsContainer) {
                objetsContainer.querySelectorAll('.objet-ligne').forEach(ligne => {
                    const desc = ligne.querySelector('.objet-desc')?.value.trim();
                    const total = ligne.querySelector('.objet-total')?.value.trim();
                    if (desc) {
                        questObjets.push({ desc, total });
                        objetsList.push({ desc, total, quete: titre || `Quête ${index + 1}` });
                    }
                });
            }
            if (questObjets.length > 0) {
                objetsText = questObjets.map(o => o.desc).join(', ');
                recompensesText += ', ' + objetsText;
                objetsQuetes.push(objetsText);
            }
        }

        // Autres
        let autresText = '';
        const autresEl = document.getElementById(`autres-quete-${dataIndex}`);
        if (autresEl && autresEl.value.trim()) {
            autresText = autresEl.value.trim();
            recompensesText += ', ' + autresText;
            autresQuetes.push(autresText);
        }

        const hasQuestData = titre || mj || xpQuete || monnaieText.length > 0 || objetsText || autresText;
        if (!hasQuestData) {
            return;
        }

        if (!refuseXP?.checked) {
            totalXPQuetes += xpQuete;
        }
        xpQuetes.push(xpQuete);

        recompensesQuetes.push(recompensesText.replace(/^,\s*/, ''));

        // Construire la liste des récompenses pour la ligne de quête
        let recompensesInline = [];
        if (xpQuete > 0) recompensesInline.push(`+${xpQuete} XP`);
        if (monnaieText.length > 0) recompensesInline.push(monnaieText.join(' '));
        if (objetsText) recompensesInline.push(objetsText);
        if (autresText) recompensesInline.push(autresText);

        const recompensesSuffix = recompensesInline.length > 0 ? ', ' + recompensesInline.join(', ') : '';

        // Construire les différentes listes
        let questLine;
        if (isMultiple) {
            const sessionsEl = document.getElementById(`sessions-quete-${dataIndex}`);
            const sessions = sessionsEl ? sessionsEl.value || `[SESSIONS_QUETE_${index + 1}]` : `[SESSIONS_QUETE_${index + 1}]`;
            questLine = `${titre || `[TITRE_QUETE_${index + 1}]`} - ${mj || `[MJ_${index + 1}]`} - [${sessions}]${recompensesSuffix}`;
        } else {
            const lienEl = document.getElementById(`lien-recompense-${dataIndex}`);
            const lien = lienEl ? lienEl.value || `⁠recompenses⁠` : `⁠recompenses⁠`;
            questLine = `${titre || `[TITRE_QUETE_${index + 1}]`} - ${mj || `[MJ_${index + 1}]`} - ${lien}${recompensesSuffix}`;
        }
        quetesList.push(questLine);
        if (monnaieText.length > 0) {
            poList.push({
                titre: titre || `[TITRE_QUETE_${index + 1}]`,
                lines: financesDetails,
                rawLines,
                total: questPO
            });
        }
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
    if (xpActuels === null) {
        return { progressionText: '', xpInfo: '', isLevelUp: false };
    }

    const nouveauTotal = xpActuels + xpObtenus;
    let progressionText = '';
    let xpInfo = '';
    let isLevelUp = false;

    // XP requis pour passer au niveau suivant depuis le niveau actuel
    const xpRequisActuel = XP_TABLE[niveauActuel] || '?';

    // Vérifier si level up possible
    if (nouveauTotal >= xpRequisActuel && xpRequisActuel !== '?') {
        isLevelUp = true;

        // Vérifier si c'est le niveau cible attendu
        if (niveauCible === niveauActuel + 1) {
            xpInfo = '';
        } else if (niveauCible > niveauActuel + 1) {
            // Plusieurs niveaux possibles
            let niveauPossible = niveauActuel;
            let xpRestants = nouveauTotal;

            while (niveauPossible < 20 && XP_TABLE[niveauPossible] && xpRestants >= XP_TABLE[niveauPossible]) {
                xpRestants -= XP_TABLE[niveauPossible];
                niveauPossible++;
            }

            if (niveauCible > niveauPossible) {
                xpInfo = ` (attention: niveau ${niveauPossible} max possible)`;
            }
        }
    } else {
        // Pas de level up
        if (niveauCible > niveauActuel) {
            const manque = xpRequisActuel - nouveauTotal;
            xpInfo = ` (manque ${manque} XP pour niveau ${niveauActuel + 1})`;
        }
    }

    return { progressionText, xpInfo, isLevelUp };
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

    const sousClasseEl = document.getElementById('sous-classe');
    const sousClasse = sousClasseEl ? sousClasseEl.value.trim() : '';

    // Informations quête
    const { quetesList, objetsList, poList, totalXPQuetes, totalMonnaies, objetsQuetes, autresQuetes, xpQuetes, recompensesQuetes } = generateQuestesSection();
    let sectionQuete = '';

    if (quetesList.length || objetsList.length || poList.length) {
        const quetesLines = quetesList.map(q => `- ${q}`).join('\n');

        // Objets : une entrée par objet avec quête d'origine
        const objetsLines = objetsList.map(o => {
            const totalPart = o.total ? ` (total inventaire : ${o.total})` : '';
            return `- ${o.desc}${totalPart}`;
        }).join('\n');

        // PO : détail par ligne de finance, total si plusieurs lignes
        const poLines = poList.map(p => {
            if (p.lines.length === 1) {
                return `- ${p.titre} : ${p.lines[0]}`;
            }
            const detail = p.lines.map(l => `  ${l}`).join('\n');
            const total = p.total.toFixed(2).replace(/\.00$/, '');
            return `- ${p.titre} :\n${detail}\n  = ${total} PO`;
        }).join('\n');

        const parts = [];
        if (quetesLines) parts.push(`Quêtes:\n${quetesLines}`);
        if (objetsLines) parts.push(`Objets:\n${objetsLines}`);
        if (poLines) parts.push(`PO:\n${poLines}`);
        parts.push(`+${totalXPQuetes} XP`);

        sectionQuete = `**Quête :**\n${parts.join('\n\n')}`;
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

    const nouvellesCapacites = (nouvellesCapacitesEl?.value || '').trim();
    const nouveauDonList = parseList(nouveauDonEl);
    const donQueteList = parseList(donQueteEl);
    const nouveauxSortsList = parseList(nouveauxSortsEl);
    const sortsRemplacesList = parseList(sortsRemplacesEl);
    const nouveauxDons = nouveauDonList.join(', ').trim();
    const donsQuete = donQueteList.join(', ').trim();
    const nouveauxSorts = nouveauxSortsList.join(', ').trim();
    const sortsRemplaces = sortsRemplacesList.join(', ').trim();

    // Blocs dynamiques capacités extras (sorts via tier, invocations)
    const capacitesExtrasContainer = document.getElementById('capacites-extras-container');
    const capacitesExtras = [];
    if (capacitesExtrasContainer) {
        capacitesExtrasContainer.querySelectorAll('.capacite-extra-line').forEach(line => {
            const type = line.querySelector('.cap-extra-type')?.value;
            const provenance = line.querySelector('.cap-extra-provenance')?.value;
            const contenu = line.querySelector('.cap-extra-contenu')?.value.trim();
            if (contenu) capacitesExtras.push({ type, provenance, contenu });
        });
    }
    
    // Items et argent
    const poLootesEl = document.getElementById('po-lootees');
    const transactionsContainer = document.getElementById('transactions-container');
    const ancienSoldeEl = document.getElementById('ancien-solde');
    const poRecuesEl = document.getElementById('po-recues');

    // Lire les objets lootés hors quête depuis les lignes dynamiques
    const objetsLootesLignes = [];
    const objetsLootesContainer = document.getElementById('objets-lootes-lignes');
    if (objetsLootesContainer) {
        objetsLootesContainer.querySelectorAll('.objet-ligne').forEach(ligne => {
            const desc = ligne.querySelector('.objet-desc')?.value.trim();
            const total = ligne.querySelector('.objet-total')?.value.trim();
            if (desc) objetsLootesLignes.push({ desc, total });
        });
    }
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

    // Artisanat - champs enrichis
    const artisanatTypeEl = document.getElementById('artisanat-type');
    const artisanatTempsEl = document.getElementById('artisanat-temps');
    const artisanatDDEl = document.getElementById('artisanat-dd');
    const artisanatJetEl = document.getElementById('artisanat-jet');
    const artisanatMateriauxEl = document.getElementById('artisanat-materiaux');
    const artisanatNotesEl = document.getElementById('artisanat-notes');
    const artisanatItemsEl = document.getElementById('artisanat-items');
    const artisanatCostEl = document.getElementById('artisanat-cost');
    const artisanatOtherCostEl = document.getElementById('artisanat-other-cost');

    const artisanatType = artisanatTypeEl ? artisanatTypeEl.value : '';
    const artisanatTemps = artisanatTempsEl ? artisanatTempsEl.value.trim() : '';
    const artisanatDD = artisanatDDEl ? artisanatDDEl.value.trim() : '';
    const artisanatJet = artisanatJetEl ? artisanatJetEl.value.trim() : '';
    const artisanatMateriaux = artisanatMateriauxEl ? artisanatMateriauxEl.value.trim() : '';
    const artisanatNotes = artisanatNotesEl ? artisanatNotesEl.value.trim() : '';
    const artisanatItemsList = artisanatItemsEl ? parseList(artisanatItemsEl) : [];
    const artisanatCostRaw = artisanatCostEl ? artisanatCostEl.value.trim() : '';
    const artisanatCost = artisanatCostRaw !== '' ? parseFloat(artisanatCostRaw) || 0 : 0;
    const artisanatOtherCostRaw = artisanatOtherCostEl ? artisanatOtherCostEl.value.trim() : '';
    const artisanatOtherCost = artisanatOtherCostRaw !== '' ? parseFloat(artisanatOtherCostRaw) || 0 : 0;
    const artisanatTotalCost = artisanatCost + artisanatOtherCost;
    
    // Formation
    const formationSectionEl = document.getElementById('formation-section');
    const formationVisible = formationSectionEl && !formationSectionEl.classList.contains('hidden');
    const formationTypeEl = document.getElementById('formation-type');
    const formationTempsTypeEl = document.getElementById('formation-temps-type');
    const formationDateDebutEl = document.getElementById('formation-date-debut');
    const formationDateFinEl = document.getElementById('formation-date-fin');
    const formationCoutEl = document.getElementById('formation-cout');
    const formationNoteEl = document.getElementById('formation-note');

    const formationType = formationTypeEl ? formationTypeEl.value.trim() : '';
    const formationTempsType = formationTempsTypeEl ? formationTempsTypeEl.value : 'Temps plein';
    const formationDateDebut = formationDateDebutEl ? formationDateDebutEl.value.trim() : '';
    const formationDateFin = formationDateFinEl ? formationDateFinEl.value.trim() : '';
    const formationCoutRaw = formationCoutEl ? formationCoutEl.value.trim() : '';
    const formationCout = formationCoutRaw !== '' ? parseFloat(formationCoutRaw) || 0 : 250;
    const formationNote = formationNoteEl ? formationNoteEl.value.trim() : '';
    const hasFormation = formationVisible && (formationType || formationDateDebut);

    // Section spéciale
    const typeSpecialEl = document.getElementById('type-special');
    const descriptionSpecialEl = document.getElementById('description-special');
    const includeMarchandEl = document.getElementById('section-marchand');

    const typeSpecial = typeSpecialEl ? typeSpecialEl.value : '';
    const descriptionSpecial = descriptionSpecialEl ? descriptionSpecialEl.value : '';
    const includeMarchand = includeMarchandEl ? includeMarchandEl.checked : false;
    
    // Calculs
    const { progressionText, xpInfo, isLevelUp } = calculateXPProgression(xpActuels, totalXPQuetes, niveauActuel, niveauCible, classeGainNiveau || classe);
    const pvCalcul = calculatePVGain(classeGainNiveau || classe, niveauActuel, niveauCible, modConstitution, bonusPV, pvActuels);
    
    // Construction du template
    let template = `**Nom du PJ :** ${nom}
**Classe :** ${classe}
`;

    // Section spéciale si définie (avant le bloc PJ)
    if (typeSpecial && descriptionSpecial) {
        const sectionTitle = getSectionTitle(typeSpecial);
        template += `
/ =======================  ${sectionTitle}  ========================= \\
${descriptionSpecial}
\\ =======================  ${sectionTitle}  ========================= /
`;
    }

    // ===== BLOC PJ (toujours présent) =====
    template += `
 / =======================  PJ  ========================= \\ `;

    if (sousClasse) {
        template += `
**Sous-classe :** ${sousClasse}`;
    }

    // Section Quête - format adapté selon le nombre de quêtes
    if (quetesList.length > 0) {
        if (quetesList.length === 1) {
            // Une seule quête : format simple avec tiret
            template += `
**Quête :** - ${quetesList[0]}`;
        } else {
            // Plusieurs quêtes : format avec crochets
            template += `
**Quête :** [
${quetesList.map(q => q).join('\n')}
]`;
        }
    }

    // XP seulement si renseigné ET qu'il y a de l'XP à ajouter
    const xpActuelsRaw = xpActuelsEl ? xpActuelsEl.value : '';
    const xpActuelsVal = xpActuelsRaw !== '' ? parseInt(xpActuelsRaw) : null;
    if (xpActuelsVal !== null && totalXPQuetes > 0) {
        const xpRequisPourNiveau = XP_TABLE[niveauActuel] || '?';
        const nouveauTotalXP = xpActuelsVal + totalXPQuetes;
        let affichageXP = `**Solde XP :** ${xpActuelsVal}/${xpRequisPourNiveau} + ${totalXPQuetes}XP obtenue ==> ${nouveauTotalXP}/${xpRequisPourNiveau}`;

        // Ajouter Level up si applicable
        if (isLevelUp && niveauCible > niveauActuel) {
            const classeNom = getClasseForXP(classeGainNiveau || classe);
            affichageXP += ` Level up ${classeNom} ${niveauCible}`;
        }
        if (xpInfo) {
            affichageXP += xpInfo;
        }

        template += `
${affichageXP}`;
    }

    // Gain de niveau seulement si niveau cible > niveau actuel
    if (niveauCible > niveauActuel) {
        template += `

**Gain de niveau :**`;

        // PV détaillés si renseignés
        if (pvCalcul && pvActuels > 0) {
            template += `
**PV :** ${pvCalcul}`;
        }
    }

    // Capacités et sorts supplémentaires
    const hasExtras = [nouvellesCapacites, nouveauxDons, donsQuete, nouveauxSorts, sortsRemplaces].some(Boolean) || capacitesExtras.length > 0;
    if (hasExtras) {
        template += `

**¤ Capacités et sorts supplémentaires :**`;
        if (nouvellesCapacites) {
            template += `
*Nouvelle(s) capacité(s) :*
${nouvellesCapacites}`;
        }
        if (nouveauxDons) {
            template += `
*Nouveau(x) don(s) :*
${nouveauxDons}`;
        }
        if (donsQuete) {
            template += `
*Don(s) (gain de quête) :*
${donsQuete}`;
        }
        if (nouveauxSorts) {
            template += `
*Nouveau(x) sort(s) :*
${nouveauxSorts}`;
        }
        if (sortsRemplaces) {
            template += `
*Sort(s) remplacé(s) :*
${sortsRemplaces}`;
        }
        capacitesExtras.forEach(({ type, provenance, contenu }) => {
            let label;
            if (type === 'sort-via') {
                label = provenance === 'Don'
                    ? 'Nouveau(x) sort(s) lié au don :'
                    : `Nouveau(x) sort(s) appris via ${provenance} :`;
            } else if (type === 'invocation-apprise') {
                label = 'Invocation(s) Occulte(s) apprise(s) :';
            } else {
                label = 'Invocation(s) Occulte(s) remplacée(s) :';
            }
            template += `
*${label}*
${contenu}`;
        });
    }

    // Inventaire seulement si renseigné
    // Combiner objets des quêtes + objets hors quête en une liste unifiée {desc, total}
    const tousObjetsLignes = [...objetsList, ...objetsLootesLignes];

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

    // Construire le texte des monnaies lootées (détail ligne par ligne)
    let monnaiesPartsDisplay = [];
    poList.forEach(p => {
        p.rawLines.forEach((rl, idx) => {
            let parts = [];
            if (rl.pc !== 0) parts.push(`${rl.pc} PC`);
            if (rl.pa !== 0) parts.push(`${rl.pa} PA`);
            if (rl.po !== 0) parts.push(`${rl.po} PO`);
            if (rl.pp !== 0) parts.push(`${rl.pp} PP`);
            const amountStr = parts.join(' ');
            if (idx === 0 && monnaiesPartsDisplay.length === 0) {
                monnaiesPartsDisplay.push(rl.sign === 1 ? `+${amountStr}` : `-${amountStr}`);
            } else {
                monnaiesPartsDisplay.push(rl.sign === 1 ? `+${amountStr}` : `-${amountStr}`);
            }
        });
    });
    if (poLootees !== 0) {
        const sign = poLootees > 0 ? '+' : '-';
        monnaiesPartsDisplay.push(`${sign}${Math.abs(poLootees).toFixed(2).replace(/\.00$/, '')} PO`);
    }

    const monnaiesText = monnaiesPartsDisplay.length > 0 ? monnaiesPartsDisplay.join(' ') : '';

    const hasInventaire = tousObjetsLignes.length > 0 || monnaiesText !== '';

    if (hasInventaire) {
        template += `

**¤ Inventaire**`;
        if (tousObjetsLignes.length > 0) {
            template += `
*Objets lootés :*`;
            tousObjetsLignes.forEach(o => {
                const totalPart = o.total ? ` (total inventaire : ${o.total})` : '';
                template += `
- ${o.desc}${totalPart}`;
            });
        }
        if (monnaiesText !== '') {
            template += `
*PO lootées :* ${monnaiesText}`;
        }
    }

    // ===== FIN BLOC PJ =====
    template += `
 \\ =======================  PJ  ========================= /
`;

    // Section Marchand si demandée (APRÈS le bloc PJ)
    if (includeMarchand && transactionsText.trim() !== '') {
        template += `
/ ===================== Marchand ===================== \\
**¤ Inventaire**
${transactionsText}
 \\ ==================== Marchand ====================== /
`;
    }

    // ===== FORMATION (après les blocs PJ et Marchand) =====
    if (hasFormation) {
        let formationLine = 'Début formation';
        if (formationType) formationLine += ` : ${formationType}`;
        if (formationDateDebut) formationLine += ` ${formationDateDebut}`;
        formationLine += ` → ${formationTempsType}`;
        if (formationDateFin) formationLine += `, fin le ${formationDateFin}`;
        if (formationNote) formationLine += ` (${formationNote})`;

        template += `
**¤ Formation :**
${formationLine}`;
        if (formationCout > 0) {
            template += `
Dépenses : ${formationCout.toFixed(2).replace(/\.00$/, '')} PO pour la formation`;
        }
        template += '\n';
    }

    // ===== SOLDE (toujours après les blocs PJ et Marchand) =====
    const changeTotal = poRecues + totalLootPO + netPOMarchand - artisanatTotalCost - (hasFormation ? formationCout : 0);

    // Construire la ligne de solde
    let soldeParts = [];
    soldeParts.push(`ANCIEN SOLDE ${ancienSolde || '[SOLDE]'}`);

    // Ajouter les variations de PO (détail par quête, parenthèses si multiple)
    const needsParens = poList.length > 1;
    poList.forEach(p => {
        if (p.rawLines.length === 0) return;
        const useParens = needsParens || p.rawLines.length > 1;
        const innerParts = p.rawLines.map((rl, idx) => {
            let parts = [];
            if (rl.pc !== 0) parts.push(`${rl.pc} PC`);
            if (rl.pa !== 0) parts.push(`${rl.pa} PA`);
            if (rl.po !== 0) parts.push(`${rl.po} PO`);
            if (rl.pp !== 0) parts.push(`${rl.pp} PP`);
            const amountStr = parts.join(' ');
            return rl.sign === 1 ? (idx === 0 ? amountStr : `+${amountStr}`) : `-${amountStr}`;
        });
        if (useParens) {
            soldeParts.push(`+ (${innerParts.join('')})`);
        } else {
            const rl = p.rawLines[0];
            let parts = [];
            if (rl.pc !== 0) parts.push(`${rl.pc} PC`);
            if (rl.pa !== 0) parts.push(`${rl.pa} PA`);
            if (rl.po !== 0) parts.push(`${rl.po} PO`);
            if (rl.pp !== 0) parts.push(`${rl.pp} PP`);
            soldeParts.push(`${rl.sign === 1 ? '+' : '-'} ${parts.join(' ')}`);
        }
    });
    if (poLootees !== 0) {
        const sign = poLootees >= 0 ? '+' : '-';
        soldeParts.push(`${sign} ${Math.abs(poLootees).toFixed(2).replace(/\.00$/, '')} PO`);
    }
    if (netPOMarchand !== 0) {
        const sign = netPOMarchand >= 0 ? '+' : '-';
        soldeParts.push(`${sign} ${Math.abs(netPOMarchand).toFixed(2).replace(/\.00$/, '')} PO`);
    }
    if (artisanatTotalCost > 0) {
        soldeParts.push(`- ${artisanatTotalCost.toFixed(2).replace(/\.00$/, '')} PO (artisanat)`);
    }
    if (hasFormation && formationCout > 0) {
        soldeParts.push(`- ${formationCout.toFixed(2).replace(/\.00$/, '')} PO (formation)`);
    }
    if (poRecues !== 0) {
        const sign = poRecues >= 0 ? '+' : '-';
        const label = poRecues >= 0 ? ' PO reçues' : ' PO dépensées';
        soldeParts.push(`${sign} ${Math.abs(poRecues).toFixed(2).replace(/\.00$/, '')}${label}`);
    }

    // Calculer le nouveau solde
    // Essayer d'extraire la partie PO de l'ancien solde et préserver le reste (PA, PC, PP)
    let nouveauSolde;
    let autresMonnaies = '';

    // Regex pour extraire les différentes monnaies de l'ancien solde
    // Format attendu : "866 PO, 1 PA" ou "866 PO 1 PA" ou "866"
    const poMatch = ancienSolde ? ancienSolde.match(/^([\d.]+)\s*(?:PO)?/) : null;
    const paMatch = ancienSolde ? ancienSolde.match(/(\d+)\s*PA/) : null;
    const pcMatch = ancienSolde ? ancienSolde.match(/(\d+)\s*PC/) : null;
    const ppMatch = ancienSolde ? ancienSolde.match(/(\d+)\s*PP/) : null;

    if (poMatch) {
        const ancienPO = parseFloat(poMatch[1]);
        const nouveauPO = (ancienPO + changeTotal).toFixed(2).replace(/\.00$/, '');

        // Reconstruire avec les autres monnaies préservées
        let monnaiesParts = [`${nouveauPO} PO`];
        if (paMatch) monnaiesParts.push(`${paMatch[1]} PA`);
        if (pcMatch) monnaiesParts.push(`${pcMatch[1]} PC`);
        if (ppMatch) monnaiesParts.push(`${ppMatch[1]} PP`);

        nouveauSolde = monnaiesParts.join(', ');
    } else if (!isNaN(ancienSoldeNum)) {
        nouveauSolde = (ancienSoldeNum + changeTotal).toFixed(2).replace(/\.00$/, '') + ' PO';
    } else {
        nouveauSolde = '[NOUVEAU_SOLDE]';
    }

    soldeParts.push(`= ${nouveauSolde}`);

    template += `
**¤ Solde :**
${soldeParts.join(' ')}

*Fiche R20 à jour.*`;

    // Artisanat si renseigné (après le solde)
    const hasArtisanat = artisanatType || artisanatTemps || artisanatDD || artisanatJet || artisanatMateriaux || artisanatNotes || artisanatItemsList.length > 0 || artisanatTotalCost > 0;
    if (hasArtisanat) {
        // Titre avec type d'artisanat
        const artisanatTitre = artisanatType ? `**Artisanat (${artisanatType}) :**` : '**Artisanat :**';
        template += `

${artisanatTitre}`;

        // Infos de session (temps, DD, jet)
        let sessionInfo = [];
        if (artisanatTemps) sessionInfo.push(`Temps : ${artisanatTemps}`);
        if (artisanatDD) sessionInfo.push(`DD ${artisanatDD}`);
        if (artisanatJet) sessionInfo.push(`Jet : ${artisanatJet}`);
        if (sessionInfo.length > 0) {
            template += `
${sessionInfo.join(' | ')}`;
        }

        // Matériaux utilisés
        if (artisanatMateriaux) {
            template += `
*Matériaux :* ${artisanatMateriaux}`;
        }

        // Objets fabriqués
        if (artisanatItemsList.length > 0) {
            template += `
*Objets fabriqués :*
${artisanatItemsList.map(i => `- ${i}`).join('\n')}`;
        }

        // Coûts
        if (artisanatTotalCost > 0) {
            let coutDetails = [];
            if (artisanatCost > 0) {
                coutDetails.push(`${artisanatCost.toFixed(2).replace(/\.00$/, '')} PO (matériaux)`);
            }
            if (artisanatOtherCost > 0) {
                coutDetails.push(`${artisanatOtherCost.toFixed(2).replace(/\.00$/, '')} PO (autres frais)`);
            }
            const totalFormatted = artisanatTotalCost.toFixed(2).replace(/\.00$/, '');
            if (coutDetails.length > 1) {
                template += `
*Coût total :* ${coutDetails.join(' + ')} = ${totalFormatted} PO`;
            } else {
                template += `
*Coût :* ${totalFormatted} PO`;
            }
        }

        // Notes supplémentaires
        if (artisanatNotes) {
            template += `
${artisanatNotes}`;
        }
    }

    const outputEl = document.getElementById('discord-output');
    const outputPart2El = document.getElementById('discord-output-part2');
    const copyBtnPart2 = document.getElementById('copy-btn-part2');
    const splitWarning = document.getElementById('split-warning');
    const outputBlock2 = document.getElementById('output-block-2');
    const outputBlockTitle1 = document.getElementById('output-block-title-1');
    const templateLength = template.length;
    const remaining = 1800 - templateLength;
    const indicator = document.getElementById('char-indicator');
    if (indicator) {
        indicator.textContent = `${remaining} caractères restants`;
        const nearLimit = remaining < 0 || remaining < 100;
        indicator.classList.toggle('warning', nearLimit);
    }

    if (templateLength > 1800) {
        // Trouver un point de coupure propre sur un saut de ligne, le plus proche du milieu
        const mid = Math.ceil(templateLength / 2);
        let splitIndex = template.lastIndexOf('\n', mid);
        if (splitIndex <= 0) splitIndex = template.indexOf('\n', mid);
        if (splitIndex <= 0) splitIndex = mid;

        const part1 = template.slice(0, splitIndex) + '\n*(Suite dans le message suivant ↓)*';
        const part2 = '*(Suite du message précédent ↑)*\n' + template.slice(splitIndex).replace(/^\n/, '');

        if (outputEl) {
            outputEl.textContent = part1;
        }
        if (outputPart2El) {
            outputPart2El.textContent = part2;
            outputPart2El.style.display = 'block';
        }
        if (outputBlock2) {
            outputBlock2.classList.remove('hidden');
        }
        if (outputBlockTitle1) {
            outputBlockTitle1.textContent = '📨 Message (Partie 1)';
        }
        if (splitWarning) {
            splitWarning.innerHTML =
                '⚠️ Le message dépasse 1 800 caractères ; il a été divisé en deux parties.<br>' +
                '<strong>Procédure :</strong> ' +
                '1 ) Copiez la <strong>Partie 1</strong> et envoyez-la dans le salon Discord. ' +
                '2 ) Copiez ensuite la <strong>Partie 2</strong> et envoyez-la dans le <em>même</em> salon, juste en dessous.';
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
        if (outputBlock2) {
            outputBlock2.classList.add('hidden');
        }
        if (outputBlockTitle1) {
            outputBlockTitle1.textContent = '📨 Message';
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

function toggleFormation() {
    const section = document.getElementById('formation-section');
    const btn = document.getElementById('toggle-formation-btn');
    if (!section || !btn) return;

    const isHidden = section.classList.toggle('hidden');
    btn.textContent = isHidden ? 'Ajouter formation' : 'Retirer formation';
}

function toggleArtisanat() {
    const section = document.getElementById('artisanat-section');
    const btn = document.getElementById('toggle-artisanat-btn');
    if (!section || !btn) return;

    const isHidden = section.classList.toggle('hidden');
    btn.textContent = isHidden ? 'Ajouter artisanat' : 'Retirer artisanat';
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
                    classeSimple.classList.add('hidden');
                    classeMulti.classList.remove('hidden');
                } else {
                    classeSimple.classList.remove('hidden');
                    classeMulti.classList.add('hidden');
                }
            }

            regenerateIfNeeded();
        });
    }

    // Gestion du toggle formation
    const formationBtn = document.getElementById('toggle-formation-btn');
    if (formationBtn) {
        formationBtn.addEventListener('click', toggleFormation);
    }

    // Gestion du toggle artisanat
    const artisanatBtn = document.getElementById('toggle-artisanat-btn');
    if (artisanatBtn) {
        artisanatBtn.addEventListener('click', toggleArtisanat);
    }

    // Setup des listeners pour la première quête
    setupQueteListeners(0);

    // Initialiser le container d'objets hors quête (onglet Items)
    initObjetContainer('objets-lootes-lignes');
    const addObjetLootesBtn = document.querySelector('[data-container="objets-lootes-lignes"]');
    if (addObjetLootesBtn && !addObjetLootesBtn.hasAttribute('data-objet-btn-added')) {
        addObjetLootesBtn.addEventListener('click', () => addObjetLigne('objets-lootes-lignes'));
        addObjetLootesBtn.setAttribute('data-objet-btn-added', 'true');
    }

    // Bouton d'ajout de transaction
    const addTransactionBtn = document.getElementById('add-transaction');
    if (addTransactionBtn) {
        addTransactionBtn.addEventListener('click', addTransactionLine);
    }

    // Bouton d'ajout de bloc capacité extra
    const addCapaciteExtraBtn = document.getElementById('add-capacite-extra');
    if (addCapaciteExtraBtn) {
        addCapaciteExtraBtn.addEventListener('click', addCapaciteExtraLine);
    }
    document.querySelectorAll('#capacites-extras-container .capacite-extra-line').forEach(setupCapaciteExtraLine);

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
        + ' input#po-lootees:not([data-listener-added]),'
        + ' input#po-recues:not([data-listener-added]),'
        + ' input#ancien-solde:not([data-listener-added]),'
        + ' select#artisanat-type:not([data-listener-added]),'
        + ' input#artisanat-temps:not([data-listener-added]),'
        + ' input#artisanat-dd:not([data-listener-added]),'
        + ' input#artisanat-jet:not([data-listener-added]),'
        + ' textarea#artisanat-materiaux:not([data-listener-added]),'
        + ' textarea#artisanat-notes:not([data-listener-added]),'
        + ' textarea#artisanat-items:not([data-listener-added]),'
        + ' input#artisanat-cost:not([data-listener-added]),'
        + ' input#artisanat-other-cost:not([data-listener-added]),'
        + ' input#section-marchand:not([data-listener-added]),'
        + ' button#toggle-artisanat-btn:not([data-listener-added]),'
        + ' button#toggle-formation-btn:not([data-listener-added]),'
        + ' input#formation-type:not([data-listener-added]),'
        + ' select#formation-temps-type:not([data-listener-added]),'
        + ' input#formation-date-debut:not([data-listener-added]),'
        + ' input#formation-date-fin:not([data-listener-added]),'
        + ' input#formation-cout:not([data-listener-added]),'
        + ' input#formation-note:not([data-listener-added])'
    );
    inputs.forEach(input => {
        if (input.tagName === 'BUTTON') {
            input.addEventListener('click', regenerateIfNeeded);
        } else {
            input.addEventListener('input', regenerateIfNeeded);
        }
        input.setAttribute('data-listener-added', 'true');
    });

    // Setup initial des transactions si présentes
    document.querySelectorAll('#transactions-container .transaction-line').forEach(setupTransactionLine);

    // Génération initiale du template
    regenerateIfNeeded();
});