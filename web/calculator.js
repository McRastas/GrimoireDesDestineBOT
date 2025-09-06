// =================================
// 🧮 CALCULATEUR DE PV D&D 5e - LOGIQUE ORIGINALE CONSERVÉE
// =================================

// Données D&D complètes (logique originale)
const DnDData = {
    classes: {
        'barbare': { dv: 12, name: 'Barbare', pvNiveau: 7 },
        'guerrier': { dv: 10, name: 'Guerrier', pvNiveau: 6 },
        'paladin': { dv: 10, name: 'Paladin', pvNiveau: 6 },
        'rodeur': { dv: 10, name: 'Rôdeur', pvNiveau: 6 },
        'sanguin': { dv: 10, name: 'Sanguin', pvNiveau: 6 },
        'artificier': { dv: 8, name: 'Artificier', pvNiveau: 5 },
        'barde': { dv: 8, name: 'Barde', pvNiveau: 5 },
        'clerc': { dv: 8, name: 'Clerc', pvNiveau: 5 },
        'druide': { dv: 8, name: 'Druide', pvNiveau: 5 },
        'moine': { dv: 8, name: 'Moine', pvNiveau: 5 },
        'occultiste': { dv: 8, name: 'Occultiste', pvNiveau: 5 },
        'roublard': { dv: 8, name: 'Roublard', pvNiveau: 5 },
        'ensorceleur': { dv: 6, name: 'Ensorceleur', pvNiveau: 4 },
        'magicien': { dv: 6, name: 'Magicien', pvNiveau: 4 }
    }
};

let characterId = 1;

// Fonction pour ajouter un personnage
function addCharacter() {
    const container = document.getElementById('characters-container');
    const id = characterId++;
    
    const characterHtml = `
        <div class="card character-card" id="character-${id}">
            <div class="card-header">
                <h3 class="card-title">🎭 Personnage ${id}</h3>
                ${characterId > 2 ? `<button class="btn btn-danger btn-sm delete-character" onclick="removeCharacter(${id})">🗑️ Supprimer</button>` : ''}
            </div>
            
            <div class="grid grid-2">
                <div class="form-group">
                    <label class="form-label">👤 Nom du personnage</label>
                    <input type="text" class="form-input" placeholder="Nom de votre héros..." onchange="updateCharacterPV(${id})">
                </div>
                
                <div class="form-group">
                    <label class="form-label">💪 Constitution</label>
                    <input type="number" class="form-input" min="1" max="30" value="10" onchange="updateCharacterPV(${id})">
                </div>
                
                <div class="form-group">
                    <label class="form-label">🧝 Race</label>
                    <select class="form-select" onchange="updateCharacterPV(${id})">
                        <option value="autre">Autre race</option>
                        <option value="nain-collines">Nain des collines (+1 PV/niveau)</option>
                        <option value="demi-orc">Demi-orc (+1 PV/niveau)</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label class="form-label">🎒 Dons et Objets Magiques</label>
                    <div class="checkbox-grid">
                        <label class="checkbox-item">
                            <input type="checkbox" class="don-resistant" onchange="updateCharacterPV(${id})">
                            <span>Don Résistant (+1 PV/niveau)</span>
                        </label>
                        <label class="checkbox-item">
                            <input type="checkbox" class="don-coriace" onchange="updateCharacterPV(${id})">
                            <span>Don Coriace (+4 PV au niveau 4)</span>
                        </label>
                        <label class="checkbox-item">
                            <input type="checkbox" class="armure-safeguard" onchange="updateCharacterPV(${id})">
                            <span>Armure Safeguard (+10 + niveau PV)</span>
                        </label>
                        <label class="checkbox-item">
                            <input type="checkbox" class="hache-berserker" onchange="updateCharacterPV(${id})">
                            <span>Hache du Berserker (+niveau PV)</span>
                        </label>
                        <label class="checkbox-item">
                            <input type="checkbox" class="ensorceleur-draconique" onchange="updateCharacterPV(${id})">
                            <span>Ensorceleur Draconique (+1 PV/niveau d'ensorceleur)</span>
                        </label>
                    </div>
                </div>
            </div>

            <div class="mt-3">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <h4 style="margin: 0; color: var(--primary-dark);">⚔️ Classes et Niveaux</h4>
                    <button class="btn btn-success btn-sm add-class" onclick="addClassToCharacter(${id})">➕ Ajouter une classe</button>
                </div>
                
                <div class="classes-container" id="classes-${id}">
                    ${generateClassHTML(id, 1)}
                </div>
            </div>

            <div class="breakdown">
                <h4>📊 Détail du Calcul</h4>
                <div class="breakdown-content">
                    <div class="breakdown-item">
                        <span>PV de base :</span>
                        <span class="base-pv">0</span>
                    </div>
                    <div class="breakdown-item">
                        <span>Modificateur Constitution :</span>
                        <span class="constitution-bonus">0</span>
                    </div>
                    <div class="breakdown-item">
                        <span>PV par niveaux :</span>
                        <span class="level-pv">0</span>
                    </div>
                    <div class="breakdown-item">
                        <span>Bonus racial :</span>
                        <span class="racial-bonus">0</span>
                    </div>
                    <div class="breakdown-item">
                        <span>Dons et objets :</span>
                        <span class="bonus-total">0</span>
                    </div>
                    <div class="breakdown-item breakdown-total">
                        <span><strong>TOTAL :</strong></span>
                        <span class="total-breakdown">0</span>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', characterHtml);
    updateCharacterPV(id);
    
    // Focus sur le nom du nouveau personnage
    setTimeout(() => {
        const nameInput = document.querySelector(`#character-${id} input[type="text"]`);
        if (nameInput) nameInput.focus();
    }, 100);
}

function generateClassHTML(characterId, classId) {
    return `
        <div class="class-section" id="class-${characterId}-${classId}">
            <div class="class-header">
                <span class="class-title">Classe ${classId}</span>
                <button class="btn btn-danger btn-sm remove-class" onclick="removeClass(${characterId}, ${classId})" style="display: none;">🗑️</button>
            </div>
            
            <div class="class-inputs">
                <div class="form-group">
                    <label class="form-label">Classe</label>
                    <select class="form-select" onchange="updateCharacterPV(${characterId})">
                        ${Object.entries(DnDData.classes).map(([key, cls]) => 
                            `<option value="${key}">${cls.name} (d${cls.dv})</option>`
                        ).join('')}
                    </select>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Niveau</label>
                    <input type="number" class="form-input" min="1" max="20" value="1" onchange="updateCharacterPV(${characterId})">
                </div>
            </div>
        </div>
    `;
}

function addClassToCharacter(characterId) {
    const container = document.getElementById(`classes-${characterId}`);
    const classes = container.querySelectorAll('.class-section');
    const newClassId = classes.length + 1;
    
    container.insertAdjacentHTML('beforeend', generateClassHTML(characterId, newClassId));
    
    // Afficher les boutons de suppression s'il y a plus d'une classe
    if (newClassId > 1) {
        container.querySelectorAll('.remove-class').forEach(btn => {
            btn.style.display = 'inline-block';
        });
    }
    
    updateCharacterPV(characterId);
}

function removeClass(characterId, classId) {
    const container = document.getElementById(`classes-${characterId}`);
    const classes = container.querySelectorAll('.class-section');
    
    if (classes.length <= 1) {
        alert('Un personnage doit avoir au moins une classe !');
        return;
    }
    
    document.getElementById(`class-${characterId}-${classId}`).remove();
    
    // Masquer les boutons de suppression s'il ne reste qu'une classe
    const remainingClasses = container.querySelectorAll('.class-section');
    if (remainingClasses.length <= 1) {
        container.querySelectorAll('.remove-class').forEach(btn => {
            btn.style.display = 'none';
        });
    }
    
    updateCharacterPV(characterId);
}

function removeCharacter(id) {
    if (confirm('Supprimer ce personnage ?')) {
        document.getElementById(`character-${id}`).remove();
    }
}

// LOGIQUE DE CALCUL ORIGINALE CONSERVÉE
function calculateCharacterPV(characterId) {
    const character = document.getElementById(`character-${characterId}`);
    if (!character) return { total: 0, base: 0, constitution: 0, level: 0, racial: 0, bonus: 0 };
    
    const constitution = parseInt(character.querySelector('input[type="number"]').value) || 10;
    const race = character.querySelector('select').value;
    
    // Classes et niveaux
    const classes = character.querySelectorAll('.class-section');
    let basePV = 0;
    let levelPV = 0;
    let totalLevel = 0;
    let sorcererLevels = 0;
    
    classes.forEach((classSection, index) => {
        const classSelect = classSection.querySelector('select');
        const levelInput = classSection.querySelector('input[type="number"]');
        const classKey = classSelect.value;
        const level = parseInt(levelInput.value) || 1;
        
        totalLevel += level;
        
        const classData = DnDData.classes[classKey];
        if (classData) {
            if (index === 0) {
                // Première classe : PV maximum au niveau 1
                basePV = classData.dv;
                levelPV += classData.pvNiveau * (level - 1);
            } else {
                // Classes supplémentaires : moyenne pour tous les niveaux
                levelPV += classData.pvNiveau * level;
            }
            
            // Compter les niveaux d'ensorceleur pour le bonus draconique
            if (classKey === 'ensorceleur') {
                sorcererLevels += level;
            }
        }
    });
    
    // Modificateur de Constitution
    const constitutionMod = Math.floor((constitution - 10) / 2);
    const constitutionBonus = constitutionMod * totalLevel;
    
    // Bonus racial
    let racialBonus = 0;
    if (race === 'nain-collines' || race === 'demi-orc') {
        racialBonus = totalLevel;
    }
    
    // Dons et objets
    let featBonus = 0;
    const donResistant = character.querySelector('.don-resistant').checked;
    const donCoriace = character.querySelector('.don-coriace').checked;
    
    if (donResistant) {
        featBonus += totalLevel;
    }
    if (donCoriace && totalLevel >= 4) {
        featBonus += 4;
    }
    
    // Objets magiques
    let itemBonus = 0;
    const armureSafeguard = character.querySelector('.armure-safeguard').checked;
    const hacheBerserker = character.querySelector('.hache-berserker').checked;
    
    if (armureSafeguard) {
        itemBonus += 10 + totalLevel;
    }
    if (hacheBerserker) {
        itemBonus += totalLevel;
    }
    
    // Bonus ensorceleur draconique
    const ensorceleurDraconique = character.querySelector('.ensorceleur-draconique').checked;
    const draconicBonus = ensorceleurDraconique ? sorcererLevels : 0;
    
    const totalPV = basePV + constitutionBonus + levelPV + racialBonus + featBonus + itemBonus + draconicBonus;
    
    return {
        total: totalPV,
        base: basePV,
        constitution: constitutionBonus,
        level: levelPV + draconicBonus,
        racial: racialBonus,
        bonus: featBonus + itemBonus
    };
}

function updateCharacterPV(characterId) {
    const result = calculateCharacterPV(characterId);
    const character = document.getElementById(`character-${characterId}`);
    
    if (!character) return;
    
    // Mettre à jour le détail du breakdown
    character.querySelector('.base-pv').textContent = result.base;
    character.querySelector('.constitution-bonus').textContent = result.constitution;
    character.querySelector('.level-pv').textContent = result.level;
    character.querySelector('.racial-bonus').textContent = result.racial;
    character.querySelector('.bonus-total').textContent = result.bonus;
    character.querySelector('.total-breakdown').textContent = result.total + ' PV';
}

function resetAll() {
    if (confirm('Supprimer tous les personnages ?')) {
        document.getElementById('characters-container').innerHTML = '';
        characterId = 1;
        addCharacter();
    }
}

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    addCharacter();
    
    // Connecter les boutons principaux
    document.getElementById('add-character').addEventListener('click', addCharacter);
    document.getElementById('reset-all').addEventListener('click', resetAll);
    
    // Système de sauvegarde/chargement automatique
    const saveData = () => {
        const characters = [];
        document.querySelectorAll('.character-card').forEach(card => {
            const id = card.id.split('-')[1];
            const result = calculateCharacterPV(id);
            const name = card.querySelector('input[type="text"]').value;
            characters.push({ id, name, ...result });
        });
        localStorage.setItem('faerun-calculator', JSON.stringify(characters));
    };
    
    // Charger les données sauvegardées
    const loadData = () => {
        try {
            const saved = localStorage.getItem('faerun-calculator');
            if (saved) {
                const data = JSON.parse(saved);
                console.log('Données précédentes trouvées:', data.length, 'personnages');
                // Note: Pour une implémentation complète du chargement,
                // il faudrait recréer les personnages depuis les données sauvegardées
            }
        } catch (error) {
            console.error('Erreur lors du chargement:', error);
        }
    };
    
    // Charger les données au démarrage
    loadData();[type="text"]').value;
            characters.push({ id, name, ...result });
        });
        localStorage.setItem('faerun-calculator', JSON.stringify(characters));
    };
    
    // Sauvegarder toutes les 10 secondes
    setInterval(saveData, 10000);
    
    // Sauvegarder avant fermeture
    window.addEventListener('beforeunload', saveData);
});[type="text"]').value;
            characters.push({ id, name, ...result });
        });
        localStorage.setItem('faerun-calculator', JSON.stringify(characters));
    };
    
    // Sauvegarder toutes les 10 secondes
    setInterval(saveData, 10000);
    
    // Sauvegarder avant fermeture
    window.addEventListener('beforeunload', saveData);
});Items.forEach(itemId => {
            const item = DnDData.bonusItems.find(bonus => bonus.id === itemId);
            if (item) {
                if (item.id === 'resistant') {
                    // Don Résistant : +1 PV par niveau
                    breakdown.itemBonus += item.bonus * totalLevels;
                } else {
                    // Autres bonus : bonus fixe
                    breakdown.itemBonus += item.bonus;
                }
            }
        });
        
        // Total
        breakdown.total = breakdown.basePV + breakdown.constitutionBonus + 
                         breakdown.levelPV + breakdown.racialBonus + breakdown.itemBonus;
        
        // Minimum 1 PV par niveau
        breakdown.total = Math.max(breakdown.total, totalLevels);
        
        // Mettre à jour l'affichage
        this.updateBreakdownDisplay(character, breakdown);
    }
    
    updateBreakdownDisplay(character, breakdown) {
        const breakdownElement = document.querySelector(`#breakdown-${character.id} .breakdown-content`);
        if (!breakdownElement) return;
        
        const constitutionMod = Math.floor((character.constitution - 10) / 2);
        const totalLevels = character.classes.reduce((sum, cls) => sum + cls.level, 0);
        const modifierSign = constitutionMod >= 0 ? '+' : '';
        
        breakdownElement.innerHTML = `
            <div class="breakdown-item">
                <span>🎲 PV de base (niveau 1)</span>
                <span>${breakdown.basePV}</span>
            </div>
            <div class="breakdown-item">
                <span>💪 Modificateur Constitution (${modifierSign}${constitutionMod})</span>
                <span>${modifierSign}${breakdown.constitutionBonus}</span>
            </div>
            <div class="breakdown-item">
                <span>📈 PV par niveaux supplémentaires</span>
                <span>+${breakdown.levelPV}</span>
            </div>
            <div class="breakdown-item">
                <span>🧝 Bonus racial</span>
                <span>+${breakdown.racialBonus}</span>
            </div>
            <div class="breakdown-item">
                <span>🎒 Dons et objets</span>
                <span>+${breakdown.itemBonus}</span>
            </div>
            <div class="breakdown-item breakdown-total">
                <span><strong>🏆 TOTAL</strong></span>
                <span><strong>${breakdown.total} PV</strong></span>
            </div>
            
            <div style="text-align: center; margin-top: 10px; font-size: 0.8rem; opacity: 0.8;">
                ${character.name || 'Personnage'} - Niveau total: ${totalLevels}
            </div>
        `;
    }
    
    resetAll() {
        this.characters = [];
        this.nextId = 1;
        document.getElementById('characters-container').innerHTML = '';
        this.addCharacter();
    }
    
    // Méthodes utilitaires pour sauvegarde (localStorage)
    saveToStorage() {
        const data = {
            characters: this.characters,
            nextId: this.nextId,
            timestamp: new Date().toISOString()
        };
        localStorage.setItem('faerun-calculator', JSON.stringify(data));
    }
    
    loadFromStorage() {
        try {
            const saved = localStorage.getItem('faerun-calculator');
            if (saved) {
                const data = JSON.parse(saved);
                this.characters = data.characters || [];
                this.nextId = data.nextId || 1;
                
                // Re-render tous les personnages
                document.getElementById('characters-container').innerHTML = '';
                this.characters.forEach(character => {
                    this.renderCharacter(character);
                });
                this.calculateAll();
                
                return true;
            }
        } catch (error) {
            console.error('Erreur lors du chargement:', error);
        }
        return false;
    }
}

// Initialisation quand la page est chargée
document.addEventListener('DOMContentLoaded', () => {
    const calculator = new HPCalculator();
    
    // Tentative de chargement des données sauvegardées
    if (!calculator.loadFromStorage()) {
        // Si pas de sauvegarde, garder le personnage par défaut
        console.log('Nouveau calculateur initialisé');
    } else {
        console.log('Données précédentes chargées');
    }
    
    // Sauvegarde automatique toutes les 10 secondes
    setInterval(() => {
        calculator.saveToStorage();
    }, 10000);
    
    // Sauvegarde avant fermeture de la page
    window.addEventListener('beforeunload', () => {
        calculator.saveToStorage();
    });
    
    // Exposer pour le debug
    window.calculator = calculator;
});