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
    
    regenerateIfNeeded();
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
        
        regenerateIfNeeded();
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
                <input type="number" id="xp-quete-${index}" placeholder="1" min="0" max="10" value="1">
            </div>

            <div class="form-group">
                <h5 style="color: #2c3e50; margin-bottom: 10px;">🎁 Récompenses (optionnelles) :</h5>
                
                <!-- XP est géré au-dessus, ici on a Monnaie, Objets, Autre -->
                <div class="reward-section">
                    <div class="reward-type">
                        <label>💰 Monnaies :</label>
                        <div class="monnaie-inputs" style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 5px;">
                            <input type="number" id="pc-quete-${index}" placeholder="PC" min="0">
                            <input type="number" id="pa-quete-${index}" placeholder="PA" min="0">
                            <input type="number" id="po-quete-${index}" placeholder="PO" min="0">
                            <input type="number" id="pp-quete-${index}" placeholder="PP" min="0">
                        </div>
                    </div>
                    
                    <div class="reward-type">
                        <label>🎒 Objets :</label>
                        <textarea id="objets-quete-${index}" rows="2" placeholder="2 émeraudes d'une valeur de 200PO, un étrange engrenage en rotation perpétuelle"></textarea>
                    </div>
                    
                    <div class="reward-type">
                        <label>⭐ Autres récompenses :</label>
                        <textarea id="autres-quete-${index}" rows="2" placeholder="Don du fruit blanc à Kornélius, Sort Interdiction dans le grimoire"></textarea>
                    </div>
                </div>
            </div>

            <button type="button" class="delete-quete" onclick="deleteQuete(${index})" style="display: none;">
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
    const queteInputs = document.querySelectorAll(`[id*="-${index}"], [id*="-quete-${index}"]`);
    queteInputs.forEach(input => {
        if (!input.hasAttribute('data-listener-added')) {
            input.addEventListener('input', regenerateIfNeeded);
            input.setAttribute('data-listener-added', 'true');
        }
    });
}

// ===== GÉNÉRATION DES QUÊTES =====

function generateQuestesSection() {
    const quetes = document.querySelectorAll('.quete-bloc');
    let questesText = '';
    let totalXPQuetes = 0;
    let totalMonnaies = { PC: 0, PA: 0, PO: 0, PP: 0 };
    let objetsQuetes = [];
    let autresQuetes = [];
    
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
        
        // Récupérer les récompenses
        let recompensesText = '';
        
        // Monnaies
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
        
        // Objets
        const objetsEl = document.getElementById(`objets-quete-${dataIndex}`);
        if (objetsEl && objetsEl.value.trim()) {
            recompensesText += ', ' + objetsEl.value.trim();
            objetsQuetes.push(objetsEl.value.trim());
        }
        
        // Autres
        const autresEl = document.getElementById(`autres-quete-${dataIndex}`);
        if (autresEl && autresEl.value.trim()) {
            recompensesText += ', ' + autresEl.value.trim();
            autresQuetes.push(autresEl.value.trim());
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
        objetsQuetes,
        autresQuetes
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
    const { questesText, totalXPQuetes, totalMonnaies, objetsQuetes, autresQuetes } = generateQuestesSection();
    let sectionQuete;
    
    if (questesText && questesText !== '' && !questesText.includes('[TITRE_QUETE_1]')) {
        sectionQuete = `**Quête :** [
${questesText}
] +${totalXPQuetes} XP`;
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
    const nouveauSortsEl = document.getElementById('nouveaux-sorts');
    const sortRemplaceEl = document.getElementById('sort-remplace');
    
    const nouvellesCapacites = nouvellesCapacitesEl ? nouvellesCapacitesEl.value || '-' : '-';
    const nouveauSorts = nouveauSortsEl ? nouveauSortsEl.value || '-' : '-';
    const sortRemplace = sortRemplaceEl ? sortRemplaceEl.value || '-' : '-';
    
    // Items et argent
    const objetsLootesEl = document.getElementById('objets-lootes');
    const poLootesEl = document.getElementById('po-lootees');
    const achatsVentesEl = document.getElementById('achats-ventes');
    const ancienSoldeEl = document.getElementById('ancien-solde');
    const poRecuesEl = document.getElementById('po-recues');
    
    const objetsLootes = objetsLootesEl ? objetsLootesEl.value || '' : '';
    const poLootees = poLootesEl ? parseInt(poLootesEl.value) || 0 : 0;
    const achatsVentes = achatsVentesEl ? achatsVentesEl.value || '' : '';
    const ancienSolde = ancienSoldeEl ? ancienSoldeEl.value || '[ANCIEN_SOLDE]' : '[ANCIEN_SOLDE]';
    const poRecues = poRecuesEl ? parseInt(poRecuesEl.value) || 0 : 0;
    
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
Nouveau(x) sort(s) :
${nouveauSorts}
Sort remplacé :
${sortRemplace}`;

    // Inventaire seulement si renseigné
    const objetsLootesBase = objetsLootes || '';
    const objetsFromQuetes = objetsQuetes.length > 0 ? objetsQuetes.join(', ') : '';
    const tousObjets = [objetsLootesBase, objetsFromQuetes].filter(o => o).join(', ') || '';
    
    // Calculer les totaux de monnaies (quêtes + manuel)
    const totalPC = totalMonnaies.PC;
    const totalPA = totalMonnaies.PA;
    const totalPO = totalMonnaies.PO + poLootees;
    const totalPP = totalMonnaies.PP;
    
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
    if (includeMarchand && achatsVentes !== '') {
        template += `
**/ ===================== Marchand ===================== \\ **
**¤ Inventaire**
${achatsVentes}
** \\ ==================== Marchand ====================== / **`;
    }

    // Calcul nouveau solde
    const changeTotal = poRecues + (poLootees + totalMonnaies.PO);
    let nouveauSolde;
    if (changeTotal === 0) {
        nouveauSolde = `${ancienSolde} inchangé`;
    } else {
        nouveauSolde = `${ancienSolde} ${changeTotal >= 0 ? '+' : ''}${changeTotal} = [NOUVEAU_SOLDE]`;
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

async function copyToClipboard(event) {
    const outputEl = document.getElementById('discord-output');
    if (!outputEl) return;
    
    const output = outputEl.textContent;
    
    if (output === 'Remplissez les champs à gauche pour voir le template généré...') {
        alert('Veuillez d\'abord générer un template !');
        return;
    }

    try {
        await navigator.clipboard.writeText(output);
        const btn = event.currentTarget;
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
            const btn = event.currentTarget;
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
    const inputs = document.querySelectorAll('input:not([id*="quete"]):not([data-listener-added]), select:not([data-listener-added]), textarea:not([id*="quete"]):not([data-listener-added])');
    inputs.forEach(input => {
        input.addEventListener('input', regenerateIfNeeded);
        input.setAttribute('data-listener-added', 'true');
    });

    // Génération initiale du template
    regenerateIfNeeded();
});