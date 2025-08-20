// ===== CONFIGURATION ET DONNÉES =====

// Table XP système serveur (points d'XP pour passer au niveau suivant)
const XP_TABLE = {
    1: 1, 2: 2, 3: 2, 4: 3, 5: 3, 6: 4, 7: 4, 8: 4, 9: 4, 10: 4,
    11: 5, 12: 5, 13: 5, 14: 6, 15: 6, 16: 7, 17: 8, 18: 9, 19: 10, 20: 0
};

// PV par niveau par classe (dé de vie moyen)
const HP_PER_LEVEL = {
    'Artificier': 5, 'Barbare': 7, 'Barde': 5, 'Clerc': 5, 'Druide': 5,
    'Ensorceleur': 4, 'Guerrier': 6, 'Magicien': 4, 'Moine': 5, 
    'Occultiste': 5, 'Paladin': 6, 'Rôdeur': 6, 'Roublard': 5, 'Sorcier': 5
};

// Variables globales
let queteCounter = 0;
let recompenseCounters = {}; // Pour tracker les compteurs de récompenses par quête

// ===== GESTION DES ONGLETS =====

function showTab(tabName) {
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
    event.target.classList.add('active');
}

// ===== GESTION DES QUÊTES =====

function addQuete() {
    queteCounter++;
    const container = document.getElementById('quetes-container');
    
    const queteHtml = createQueteHTML(queteCounter);
    container.insertAdjacentHTML('beforeend', queteHtml);
    
    // Ajouter les event listeners pour la nouvelle quête
    setupQueteListeners(queteCounter);
    
    // Afficher le bouton de suppression de la première quête
    const firstDeleteBtn = document.querySelector('[data-quete="0"] .delete-quete');
    if (firstDeleteBtn) {
        firstDeleteBtn.style.display = 'block';
    }
    
    // Régénérer si au moins le nom est rempli
    const nomPJ = document.getElementById('nom-pj');
    if (nomPJ && nomPJ.value) {
        generateTemplate();
    }
}

function deleteQuete(index) {
    const queteBloc = document.querySelector(`[data-quete="${index}"]`);
    if (queteBloc) {
        queteBloc.remove();
        
        // Masquer le bouton de suppression s'il ne reste qu'une quête
        const remainingQuetes = document.querySelectorAll('.quete-bloc');
        if (remainingQuetes.length === 1) {
            const deleteBtn = document.querySelector('.delete-quete');
            if (deleteBtn) {
                deleteBtn.style.display = 'none';
            }
        }
        
        // Régénérer le template
        const nomPJ = document.getElementById('nom-pj');
        if (nomPJ && nomPJ.value) {
            generateTemplate();
        }
    }
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
                <input type="number" id="xp-quete-${index}" placeholder="1" min="0" max="10">
            </div>

            <div class="form-group">
                <h5 style="color: #2c3e50; margin-bottom: 10px;">🎁 Récompenses obtenues :</h5>
                <div id="recompenses-container-${index}"></div>
                <button type="button" class="add-recompense" onclick="addRecompense(${index})">
                    ➕ Ajouter une récompense
                </button>
            </div>

            <button type="button" class="delete-quete" onclick="deleteQuete(${index})">
                🗑️ Supprimer cette quête
            </button>
        </div>
    `;
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
    
    // Event listeners pour tous les champs de cette quête
    const queteInputs = document.querySelectorAll(`[id*="-${index}"]`);
    queteInputs.forEach(input => {
        input.addEventListener('input', regenerateIfNeeded);
    });
}

// ===== GESTION DES RÉCOMPENSES =====

function addRecompense(queteIndex) {
    if (!recompenseCounters[queteIndex]) {
        recompenseCounters[queteIndex] = 0;
    }
    
    const recompenseId = recompenseCounters[queteIndex]++;
    const container = document.getElementById(`recompenses-container-${queteIndex}`);
    
    if (container) {
        const recompenseHtml = createRecompenseHTML(queteIndex, recompenseId);
        container.insertAdjacentHTML('beforeend', recompenseHtml);
        
        // Ajouter event listeners pour la nouvelle récompense
        setupRecompenseListeners(queteIndex, recompenseId);
        
        // Générer le contenu initial
        updateRecompenseContent(queteIndex, recompenseId);
        
        regenerateIfNeeded();
    }
}

function deleteRecompense(queteIndex, recompenseId) {
    const recompenseItem = document.querySelector(`[data-recompense="${recompenseId}"]`);
    if (recompenseItem && recompenseItem.closest(`#recompenses-container-${queteIndex}`)) {
        recompenseItem.remove();
        regenerateIfNeeded();
    }
}

function createRecompenseHTML(queteIndex, recompenseId) {
    return `
        <div class="recompense-item" data-recompense="${recompenseId}">
            <select id="type-recompense-${queteIndex}-${recompenseId}" style="flex: 0 0 120px;">
                <option value="monnaie">💰 Monnaie</option>
                <option value="item">🎒 Objet</option>
                <option value="reputation">⭐ Réputation</option>
                <option value="babiole">✨ Babiole</option>
                <option value="ration">🍖 Ration</option>
                <option value="potion">🧪 Potion</option>
                <option value="equipement">⚔️ Équipement</option>
                <option value="materiau">🔨 Matériau</option>
                <option value="autre">❓ Autre</option>
            </select>
            <div id="content-recompense-${queteIndex}-${recompenseId}" style="flex: 1; display: flex; gap: 5px;"></div>
            <button type="button" class="delete-recompense" onclick="deleteRecompense(${queteIndex}, ${recompenseId})">
                🗑️
            </button>
        </div>
    `;
}

function setupRecompenseListeners(queteIndex, recompenseId) {
    const typeSelect = document.getElementById(`type-recompense-${queteIndex}-${recompenseId}`);
    
    if (typeSelect) {
        typeSelect.addEventListener('change', function() {
            updateRecompenseContent(queteIndex, recompenseId);
            regenerateIfNeeded();
        });
    }
}

function updateRecompenseContent(queteIndex, recompenseId) {
    const typeSelect = document.getElementById(`type-recompense-${queteIndex}-${recompenseId}`);
    const contentDiv = document.getElementById(`content-recompense-${queteIndex}-${recompenseId}`);
    
    if (!typeSelect || !contentDiv) return;
    
    const type = typeSelect.value;
    
    if (type === 'monnaie') {
        // 4 champs pour les monnaies
        contentDiv.innerHTML = `
            <input type="number" id="pc-${queteIndex}-${recompenseId}" placeholder="PC" style="flex: 1;" title="Pièces de Cuivre">
            <input type="number" id="pa-${queteIndex}-${recompenseId}" placeholder="PA" style="flex: 1;" title="Pièces d'Argent">
            <input type="number" id="po-${queteIndex}-${recompenseId}" placeholder="PO" style="flex: 1;" title="Pièces d'Or">
            <input type="number" id="pp-${queteIndex}-${recompenseId}" placeholder="PP" style="flex: 1;" title="Pièces de Platine">
        `;
    } else {
        // Champ texte simple pour les autres types
        const placeholders = {
            'item': '1 Épée +1',
            'reputation': '+1 Faction des Mages',
            'babiole': '1 Pierre précieuse',
            'ration': '3 rations',
            'potion': '2 potions de soin',
            'equipement': '1 armure de cuir',
            'materiau': '5 lingots de fer',
            'autre': 'Description libre'
        };
        
        contentDiv.innerHTML = `
            <input type="text" id="desc-recompense-${queteIndex}-${recompenseId}" placeholder="${placeholders[type] || 'Description'}" style="flex: 1;">
        `;
    }
    
    // Ajouter les event listeners pour les nouveaux champs
    const newInputs = contentDiv.querySelectorAll('input');
    newInputs.forEach(input => {
        input.addEventListener('input', regenerateIfNeeded);
    });
}

// ===== GÉNÉRATION DU TEMPLATE =====

function generateQuestesSection() {
    const quetes = document.querySelectorAll('.quete-bloc');
    let questesText = '';
    let totalXPQuetes = 0;
    let totalMonnaies = { PC: 0, PA: 0, PO: 0, PP: 0 };
    let objetsQuetes = [];
    
    quetes.forEach((quete, index) => {
        const dataIndex = quete.getAttribute('data-quete');
        const titreEl = document.getElementById(`titre-quete-${dataIndex}`);
        const mjEl = document.getElementById(`nom-mj-${dataIndex}`);
        const xpEl = document.getElementById(`xp-quete-${dataIndex}`);
        const multipleEl = document.getElementById(`quete-multiple-${dataIndex}`);
        
        const titre = titreEl ? titreEl.value || `[TITRE_QUETE_${index + 1}]` : `[TITRE_QUETE_${index + 1}]`;
        const mj = mjEl ? mjEl.value || `[MJ_${index + 1}]` : `[MJ_${index + 1}]`;
        const xpQuete = xpEl ? parseInt(xpEl.value) || 0 : 0;
        const isMultiple = multipleEl ? multipleEl.checked : false;
        
        totalXPQuetes += xpQuete;
        
        // Récupérer les récompenses de cette quête
        const recompensesContainer = document.getElementById(`recompenses-container-${dataIndex}`);
        let recompensesText = '';
        
        if (recompensesContainer) {
            const recompenseItems = recompensesContainer.querySelectorAll('.recompense-item');
            recompenseItems.forEach(item => {
                const typeSelect = item.querySelector('select');
                
                if (typeSelect) {
                    const type = typeSelect.value;
                    
                    if (type === 'monnaie') {
                        // Traiter les 4 types de monnaies
                        const recompenseId = item.getAttribute('data-recompense');
                        const pcEl = document.getElementById(`pc-${dataIndex}-${recompenseId}`);
                        const paEl = document.getElementById(`pa-${dataIndex}-${recompenseId}`);
                        const poEl = document.getElementById(`po-${dataIndex}-${recompenseId}`);
                        const ppEl = document.getElementById(`pp-${dataIndex}-${recompenseId}`);
                        
                        const pc = pcEl ? parseInt(pcEl.value) || 0 : 0;
                        const pa = paEl ? parseInt(paEl.value) || 0 : 0;
                        const po = poEl ? parseInt(poEl.value) || 0 : 0;
                        const pp = ppEl ? parseInt(ppEl.value) || 0 : 0;
                        
                        // Ajouter aux totaux
                        totalMonnaies.PC += pc;
                        totalMonnaies.PA += pa;
                        totalMonnaies.PO += po;
                        totalMonnaies.PP += pp;
                        
                        // Construire le texte des récompenses avec gestion des signes
                        let monnaieText = [];
                        if (pc !== 0) {
                            monnaieText.push(`${pc > 0 ? '+' : ''}${pc} PC`);
                        }
                        if (pa !== 0) {
                            monnaieText.push(`${pa > 0 ? '+' : ''}${pa} PA`);
                        }
                        if (po !== 0) {
                            monnaieText.push(`${po > 0 ? '+' : ''}${po} PO`);
                        }
                        if (pp !== 0) {
                            monnaieText.push(`${pp > 0 ? '+' : ''}${pp} PP`);
                        }
                        
                        if (monnaieText.length > 0) {
                            recompensesText += `, ${monnaieText.join(' ')}`;
                        }
                    } else {
                        // Autres récompenses
                        const descInput = item.querySelector('input[type="text"]');
                        if (descInput && descInput.value.trim()) {
                            const desc = descInput.value.trim();
                            recompensesText += `, +${desc}`;
                            objetsQuetes.push(desc);
                        }
                    }
                }
            });
        }
        
        if (isMultiple) {
            const sessionsEl = document.getElementById(`sessions-quete-${dataIndex}`);
            const sessions = sessionsEl ? sessionsEl.value || `[SESSIONS_QUETE_${index + 1}]` : `[SESSIONS_QUETE_${index + 1}]`;
            questesText += `- ${titre} + MJ ${mj} ⁠- [
${sessions}
] +${xpQuete} XP${recompensesText}`;
        } else {
            const lienEl = document.getElementById(`lien-recompense-${dataIndex}`);
            const lien = lienEl ? lienEl.value || `[LIEN_RECOMPENSE_${index + 1}]` : `[LIEN_RECOMPENSE_${index + 1}]`;
            questesText += `- ${titre} + ${mj} ⁠- ${lien}, +${xpQuete} XP${recompensesText}`;
        }
        
        // Ajouter une ligne vide entre les quêtes sauf pour la dernière
        if (index < quetes.length - 1) {
            questesText += '\n';
        }
    });
    
    return { 
        questesText: questesText.trim(), 
        totalXPQuetes, 
        totalMonnaies,
        objetsQuetes
    };
}

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
    const { questesText, totalXPQuetes, totalMonnaies, objetsQuetes } = generateQuestesSection();
    let sectionQuete;
    
    if (questesText && questesText !== '' && !questesText.includes('[TITRE_QUETE_1]')) {
        sectionQuete = `**Quête :** [
${questesText}
] +${totalXPQuetes} XP`;
    } else {
        sectionQuete = '**Quête :** [TITRE_QUETE] + [NOM_MJ] ⁠- [LIEN_RECOMPENSES]';
    }
    
    // Remplacer xpObtenus par le total des quêtes
    const xpObtenus = totalXPQuetes;
    
    // Informations XP/Niveau
    const xpActuelsEl = document.getElementById('xp-actuels');
    const niveauActuelEl = document.getElementById('niveau-actuel');
    const niveauCibleEl = document.getElementById('niveau-cible');
    
    const xpActuels = xpActuelsEl ? parseInt(xpActuelsEl.value) || 0 : 0;
    const niveauActuel = niveauActuelEl ? parseInt(niveauActuelEl.value) || 1 : 1;
    const niveauCible = niveauCibleEl ? parseInt(niveauCibleEl.value) || 1 : 1;
    
    // Informations PV détaillées
    const pvActuelsEl = document.getElementById('pv-actuels');
    const deVieEl = document.getElementById('de-vie');
    const modConstitutionEl = document.getElementById('mod-constitution');
    const bonusPVEl = document.getElementById('bonus-pv');
    
    const pvActuels = pvActuelsEl ? parseInt(pvActuelsEl.value) || 0 : 0;
    const deVie = deVieEl ? parseInt(deVieEl.value) || 0 : 0;
    const modConstitution = modConstitutionEl ? parseInt(modConstitutionEl.value) || 0 : 0;
    const bonusPV = bonusPVEl ? bonusPVEl.value : '';
    
    // Calcul PV détaillé
    let calculPV = '';
    let totalPV = pvActuels;
    
    if (pvActuels > 0 || deVie > 0) {
        calculPV = `PV : ${pvActuels}`;
        
        if (deVie > 0) {
            calculPV += `+ ${deVie}`;
            totalPV += deVie;
        }
        
        if (modConstitution !== 0) {
            const signeMod = modConstitution >= 0 ? '+' : '';
            calculPV += `${signeMod}${modConstitution}(MOD_CONST)`;
            totalPV += modConstitution;
        }
        
        if (bonusPV && bonusPV.trim() !== '' && bonusPV !== '0') {
            // Si c'est juste un nombre
            if (/^\d+$/.test(bonusPV.trim())) {
                const bonusNum = parseInt(bonusPV);
                calculPV += `+${bonusNum}`;
                totalPV += bonusNum;
            } else {
                // Extraire les nombres du bonus pour le calcul
                const bonusNum = bonusPV.match(/\d+/g);
                let bonusTotal = 0;
                if (bonusNum) {
                    bonusTotal = bonusNum.reduce((sum, num) => sum + parseInt(num), 0);
                    totalPV += bonusTotal;
                }
                calculPV += `+${bonusPV}`;
            }
        }
        
        calculPV += ` = ${totalPV}`;
    }
    
    // Sorts et capacités
    const nouvellesCapacitesEl = document.getElementById('nouvelles-capacites');
    const nouveauSortsEl = document.getElementById('nouveaux-sorts');
    const sortRemplaceEl = document.getElementById('sort-remplace');
    
    const nouvellesCapacites = nouvellesCapacitesEl ? nouvellesCapacitesEl.value || '-' : '-';
    const nouveauSorts = nouveauSortsEl ? nouveauSortsEl.value || '-' : '-';
    const sortRemplace = sortRemplaceEl ? sortRemplaceEl.value || '-' : '-';
    
    // Items
    const objetsLootesEl = document.getElementById('objets-lootes');
    const achatsVentesEl = document.getElementById('achats-ventes');
    const poLootesEl = document.getElementById('po-lootees');
    
    const objetsLootes = objetsLootesEl ? objetsLootesEl.value || '-' : '-';
    const achatsVentes = achatsVentesEl ? achatsVentesEl.value || '-' : '-';
    const poLootees = poLootesEl ? parseInt(poLootesEl.value) || 0 : 0;
    
    // Argent
    const ancienSoldeEl = document.getElementById('ancien-solde');
    const poRecuesEl = document.getElementById('po-recues');
    
    const ancienSolde = ancienSoldeEl ? ancienSoldeEl.value || '0 PO' : '0 PO';
    const poRecues = poRecuesEl ? parseInt(poRecuesEl.value) || 0 : 0;
    
    // Section spéciale
    const typeSpecialEl = document.getElementById('type-special');
    const descriptionSpecialEl = document.getElementById('description-special');
    const includeMarchandEl = document.getElementById('section-marchand');
    
    const typeSpecial = typeSpecialEl ? typeSpecialEl.value : '';
    const descriptionSpecial = descriptionSpecialEl ? descriptionSpecialEl.value : '';
    const includeMarchand = includeMarchandEl ? includeMarchandEl.checked : false;
    
    // Calculs automatiques
    const nouveauTotalXP = xpActuels + xpObtenus;
    
    // Calcul nouveau solde (gestion format PO/PA)
    let nouveauSolde;
    if (ancienSolde.includes('PO') || ancienSolde.includes('PA')) {
        // Format complexe avec PA
        const changeTotal = poRecues + poLootees;
        if (changeTotal === 0) {
            nouveauSolde = `${ancienSolde} inchangées`;
        } else {
            nouveauSolde = `${ancienSolde} ${changeTotal >= 0 ? '+' : ''}${changeTotal} = [NOUVEAU_SOLDE]`;
        }
    } else {
        const ancienSoldeNum = parseInt(ancienSolde) || 0;
        const changeTotal = poRecues + poLootees;
        nouveauSolde = `${ancienSoldeNum} ${changeTotal >= 0 ? '+' : ''}${changeTotal} = ${ancienSoldeNum + changeTotal}`;
    }
    
    // Vérification niveau avec le nouveau système
    let xpInfo = '';
    let progressionText = '';
    
    if (niveauActuel && niveauCible && xpActuels >= 0 && xpObtenus >= 0) {
        const nouveauTotal = xpActuels + xpObtenus;
        
        // Calculer si le niveau cible est atteignable
        let xpCumules = nouveauTotal;
        let niveauPossible = niveauActuel;
        
        while (niveauPossible < 20 && XP_TABLE[niveauPossible + 1] && xpCumules >= XP_TABLE[niveauPossible + 1]) {
            xpCumules -= XP_TABLE[niveauPossible + 1];
            niveauPossible++;
        }
        
        if (niveauCible > niveauPossible) {
            // Niveau cible impossible à atteindre
            let xpManquants = 0;
            let tempNiveau = niveauActuel;
            let tempXP = nouveauTotal;
            
            while (tempNiveau < niveauCible && XP_TABLE[tempNiveau + 1]) {
                const xpRequis = XP_TABLE[tempNiveau + 1];
                if (tempXP >= xpRequis) {
                    tempXP -= xpRequis;
                    tempNiveau++;
                } else {
                    xpManquants += (xpRequis - tempXP);
                    tempXP = 0;
                    tempNiveau++;
                }
            }
            
            const xpRequisActuel = XP_TABLE[niveauActuel + 1] || '?';
            progressionText = ` ==> ${nouveauTotal}/${xpRequisActuel}`;
            xpInfo = ` ❌ IMPOSSIBLE ! (Manque ${xpManquants} XP pour niveau ${niveauCible})`;
            
        } else if (niveauCible === niveauPossible) {
            // Niveau cible atteignable
            if (niveauCible === niveauActuel + 1) {
                // Passage de niveau simple
                const xpRequis = XP_TABLE[niveauCible];
                progressionText = ` ==> ${nouveauTotal}/${xpRequis}`;
                if (nouveauTotal >= xpRequis) {
                    progressionText += ` ==> passage au niveau ${niveauCible} ${getClasseForXP(classe)}`;
                    xpInfo = ' ✅';
                }
            } else if (niveauCible > niveauActuel + 1) {
                // Plusieurs niveaux
                progressionText = ` ==> passage au niveau ${niveauCible} ${getClasseForXP(classe)}`;
                xpInfo = ' 🚀';
            }
        } else if (niveauCible < niveauPossible) {
            // Le joueur pourrait monter plus haut
            const xpRequisActuel = XP_TABLE[niveauActuel + 1] || '?';
            progressionText = ` ==> ${nouveauTotal}/${xpRequisActuel}`;
            xpInfo = ` 💡 Vous pourriez atteindre le niveau ${niveauPossible} !`;
        }
        
        // Cas où pas encore de passage de niveau
        if (niveauCible === niveauActuel && XP_TABLE[niveauActuel + 1]) {
            const xpRequis = XP_TABLE[niveauActuel + 1];
            progressionText = ` ==> ${nouveauTotal}/${xpRequis}`;
            if (nouveauTotal < xpRequis) {
                const manque = xpRequis - nouveauTotal;
                xpInfo = ` ⚠️ (Manque ${manque} XP pour niveau ${niveauActuel + 1})`;
            }
        }
    }

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
    if (xpActuels >= 0 && (xpObtenus > 0 || niveauActuel)) {
        const xpRequisPourNiveau = XP_TABLE[niveauActuel + 1] || '?';
        const affichageXP = `**Solde XP :** ${xpActuels}/${xpRequisPourNiveau} + ${xpObtenus}XP obtenue = ${nouveauTotalXP}${progressionText}${xpInfo}`;
        template += `
${affichageXP}`;
    }

    // Gain de niveau seulement si différent
    if (niveauCible > niveauActuel) {
        template += `
**Gain de niveau :** Niveau ${niveauActuel} → **Niveau ${niveauCible}** 🎉`;
    }

    // PV seulement si renseignés
    if (calculPV) {
        template += `
${calculPV}`;
    }

    template += `
**¤ Capacités et sorts supplémentaires :**
Nouvelle(s) capacité(s) :
${nouvellesCapacites}
Nouveau(x) sort(s) :
${nouveauSorts}
Sort remplacé :
${sortRemplace}`;

    // Inventaire seulement si renseigné
    const objetsLootesBase = objetsLootes !== '-' ? objetsLootes : '';
    const objetsFromQuetes = objetsQuetes.length > 0 ? objetsQuetes.join(', ') : '';
    const tousObjets = [objetsLootesBase, objetsFromQuetes].filter(o => o).join(', ') || '-';
    
    // Calculer les totaux de monnaies (quêtes + manuel)
    const totalPC = totalMonnaies.PC;
    const totalPA = totalMonnaies.PA;
    const totalPO = totalMonnaies.PO + poLootees;
    const totalPP = totalMonnaies.PP;
    
    // Construire le texte des monnaies lootées avec gestion des signes
    let monnaiesLootees = [];
    if (totalPC !== 0) {
        monnaiesLootees.push(`${totalPC > 0 ? '+' : ''}${totalPC} PC`);
    }
    if (totalPA !== 0) {
        monnaiesLootees.push(`${totalPA > 0 ? '+' : ''}${totalPA} PA`);
    }
    if (totalPO !== 0) {
        monnaiesLootees.push(`${totalPO > 0 ? '+' : ''}${totalPO} PO`);
    }
    if (totalPP !== 0) {
        monnaiesLootees.push(`${totalPP > 0 ? '+' : ''}${totalPP} PP`);
    }
    
    const monnaiesText = monnaiesLootees.length > 0 ? monnaiesLootees.join(' ') : '0';
    
    if (tousObjets !== '-' || monnaiesLootees.length > 0) {
        template += `
**¤ Inventaire**
Objets lootés :
${tousObjets}
Monnaies lootées: ${monnaiesText}`;
    }

    template += `
** \\ =======================  PJ  ========================= / **`;

    // Section Marchand si demandée
    if (includeMarchand && achatsVentes !== '-') {
        template += `
**/ ===================== Marchand ===================== \\ **
**¤ Inventaire**
${achatsVentes}
** \\ ==================== Marchand ====================== / **`;
    }

    template += `
**¤ Solde :**
ANCIEN SOLDE ${nouveauSolde}
*Fiche R20 à jour.*`;

    const outputEl = document.getElementById('discord-output');
    if (outputEl) {
        outputEl.textContent = template;
    }
}

// ===== FONCTIONS UTILITAIRES =====

function regenerateIfNeeded() {
    const nomPJ = document.getElementById('nom-pj');
    if (nomPJ && nomPJ.value) {
        generateTemplate();
    }
}

function suggestHPForClass() {
    const multiclasseToggle = document.getElementById('multiclasse-toggle');
    const isMulticlasse = multiclasseToggle ? multiclasseToggle.checked : false;
    
    if (!isMulticlasse) {
        const classeEl = document.getElementById('classe');
        const deVieEl = document.getElementById('de-vie');
        
        if (classeEl && deVieEl) {
            const classe = classeEl.value;
            const suggestedHP = HP_PER_LEVEL[classe];
            if (suggestedHP && !deVieEl.value) {
                deVieEl.placeholder = `${suggestedHP} (moy. ${classe})`;
            }
        }
    }
}

async function copyToClipboard() {
    const outputEl = document.getElementById('discord-output');
    if (!outputEl) return;
    
    const output = outputEl.textContent;
    
    if (output === 'Remplissez les champs à gauche pour voir le template généré...') {
        alert('Veuillez d\'abord générer un template !');
        return;
    }

    try {
        await navigator.clipboard.writeText(output);
        const btn = event.target;
        const originalText = btn.textContent;
        
        btn.textContent = '✅ Copié !';
        btn.classList.add('success');
        
        setTimeout(() => {
            btn.textContent = originalText;
            btn.classList.remove('success');
        }, 2000);
    } catch (err) {
        // Fallback pour les navigateurs plus anciens
        const textArea = document.createElement('textarea');
        textArea.value = output;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            const btn = event.target;
            const originalText = btn.textContent;
            
            btn.textContent = '✅ Copié !';
            btn.classList.add('success');
            
            setTimeout(() => {
                btn.textContent = originalText;
                btn.classList.remove('success');
            }, 2000);
        } catch (fallbackErr) {
            alert('Impossible de copier automatiquement. Sélectionnez et copiez le texte manuellement.');
        }
        document.body.removeChild(textArea);
    }
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
    
    // Listeners pour tous les autres champs
    const inputs = document.querySelectorAll('input:not([id*="quete"]), select, textarea:not([id*="quete"])');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            // Suggestions automatiques
            if (input.id === 'classe') {
                suggestHPForClass();
            }
            
            regenerateIfNeeded();
        });
    });
});