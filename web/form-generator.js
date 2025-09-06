// =================================
// 📝 GÉNÉRATEUR DE FICHE D&D 5e
// =================================

class FormGenerator {
    constructor() {
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadFromStorage();
        this.generateMessage(); // Générer l'aperçu initial
    }
    
    setupEventListeners() {
        // Onglets
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });
        
        // Génération du message
        document.getElementById('generate-message').addEventListener('click', () => {
            this.generateMessage();
        });
        
        // Copie du message
        document.getElementById('copy-message').addEventListener('click', () => {
            this.copyToClipboard();
        });
        
        // Effacement du formulaire
        document.getElementById('clear-form').addEventListener('click', () => {
            if (confirm('Effacer tout le formulaire ?')) {
                this.clearForm();
            }
        });
        
        // Génération automatique en temps réel
        document.addEventListener('input', (e) => {
            if (e.target.closest('.form-container')) {
                this.debounce(() => {
                    this.generateMessage();
                    this.saveToStorage();
                }, 500);
            }
        });
        
        document.addEventListener('change', (e) => {
            if (e.target.closest('.form-container')) {
                this.generateMessage();
                this.saveToStorage();
            }
        });
    }
    
    // Utilitaire debounce
    debounce(func, wait) {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(func, wait);
    }
    
    switchTab(tabName) {
        // Désactiver tous les onglets
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        
        // Activer l'onglet sélectionné
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        document.getElementById(`tab-${tabName}`).classList.add('active');
    }
    
    generateMessage() {
        const data = this.getFormData();
        const message = this.buildMessage(data);
        
        document.getElementById('discord-preview').innerHTML = `
            <div class="discord-message">
                <pre>${message}</pre>
            </div>
        `;
        
        // Compteur de caractères
        const charCount = message.length;
        const charCountElement = document.getElementById('char-count');
        charCountElement.textContent = charCount;
        
        // Couleur selon la longueur
        if (charCount > 2000) {
            charCountElement.style.color = '#e74c3c';
        } else if (charCount > 1800) {
            charCountElement.style.color = '#e67e22';
        } else {
            charCountElement.style.color = '#27ae60';
        }
    }
    
    getFormData() {
        return {
            characterName: document.getElementById('character-name').value.trim(),
            currentLevel: parseInt(document.getElementById('current-level').value) || 1,
            newLevel: parseInt(document.getElementById('new-level').value) || 2,
            characterClass: document.getElementById('character-class').value,
            newAbilities: document.getElementById('new-abilities').value.trim(),
            statImprovements: document.getElementById('stat-improvements').value.trim(),
            newItems: document.getElementById('new-items').value.trim(),
            lostItems: document.getElementById('lost-items').value.trim(),
            moneyGained: document.getElementById('money-gained').value.trim(),
            moneySpent: document.getElementById('money-spent').value.trim(),
            currentMoney: document.getElementById('current-money').value.trim(),
            completedQuests: document.getElementById('completed-quests').value.trim(),
            newQuests: document.getElementById('new-quests').value.trim(),
            rpNotes: document.getElementById('rp-notes').value.trim()
        };
    }
    
    buildMessage(data) {
        let message = '';
        
        // En-tête du personnage
        if (data.characterName) {
            message += `🎭 **${data.characterName}**\n`;
            message += `📈 Niveau ${data.currentLevel} → ${data.newLevel} (${this.getClassName(data.characterClass)})\n\n`;
        } else {
            message += `📈 **Montée de niveau ${data.currentLevel} → ${data.newLevel}**\n`;
            message += `⚔️ Classe: ${this.getClassName(data.characterClass)}\n\n`;
        }
        
        // Nouvelles capacités
        if (data.newAbilities || data.statImprovements) {
            message += `🔮 **Nouvelles Capacités**\n`;
            if (data.newAbilities) {
                message += `${data.newAbilities}\n`;
            }
            if (data.statImprovements) {
                message += `📊 Améliorations: ${data.statImprovements}\n`;
            }
            message += '\n';
        }
        
        // Équipement
        if (data.newItems || data.lostItems) {
            message += `🎒 **Équipement**\n`;
            if (data.newItems) {
                message += `➕ Nouveaux objets:\n${data.newItems}\n`;
            }
            if (data.lostItems) {
                message += `➖ Objets perdus/utilisés:\n${data.lostItems}\n`;
            }
            message += '\n';
        }
        
        // Argent
        if (data.moneyGained || data.moneySpent || data.currentMoney) {
            message += `💰 **Finances**\n`;
            if (data.moneyGained) {
                message += `➕ Gains: ${data.moneyGained}\n`;
            }
            if (data.moneySpent) {
                message += `➖ Dépenses: ${data.moneySpent}\n`;
            }
            if (data.currentMoney) {
                message += `💵 Total actuel: ${data.currentMoney}\n`;
            }
            message += '\n';
        }
        
        // Quêtes
        if (data.completedQuests || data.newQuests) {
            message += `⚔️ **Quêtes**\n`;
            if (data.completedQuests) {
                message += `✅ Terminées:\n${data.completedQuests}\n`;
            }
            if (data.newQuests) {
                message += `🆕 Nouvelles:\n${data.newQuests}\n`;
            }
            message += '\n';
        }
        
        // Notes RP
        if (data.rpNotes) {
            message += `📝 **Notes RP**\n${data.rpNotes}\n\n`;
        }
        
        // Pied de page
        message += `---\n`;
        message += `✨ *Mise à jour générée le ${new Date().toLocaleDateString('fr-FR')}*`;
        
        return message.trim();
    }
    
    getClassName(classKey) {
        const classes = {
            'artificier': 'Artificier',
            'barbare': 'Barbare',
            'barde': 'Barde',
            'clerc': 'Clerc',
            'druide': 'Druide',
            'ensorceleur': 'Ensorceleur',
            'guerrier': 'Guerrier',
            'magicien': 'Magicien',
            'moine': 'Moine',
            'occultiste': 'Occultiste',
            'paladin': 'Paladin',
            'rodeur': 'Rôdeur',
            'roublard': 'Roublard',
            'sanguin': 'Sanguin'
        };
        return classes[classKey] || 'Guerrier';
    }
    
    async copyToClipboard() {
        const previewElement = document.querySelector('#discord-preview pre');
        if (!previewElement) return;
        
        const text = previewElement.textContent;
        
        try {
            if (navigator.clipboard) {
                await navigator.clipboard.writeText(text);
            } else {
                // Fallback pour navigateurs plus anciens
                const textArea = document.createElement('textarea');
                textArea.value = text;
                textArea.style.position = 'fixed';
                textArea.style.left = '-999999px';
                textArea.style.top = '-999999px';
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                document.execCommand('copy');
                textArea.remove();
            }
            
            // Feedback visuel
            const copyBtn = document.getElementById('copy-message');
            const originalText = copyBtn.textContent;
            copyBtn.textContent = '✅ Copié !';
            copyBtn.style.background = '#27ae60';
            
            setTimeout(() => {
                copyBtn.textContent = originalText;
                copyBtn.style.background = '';
            }, 2000);
            
        } catch (error) {
            console.error('Erreur lors de la copie:', error);
            alert('Impossible de copier automatiquement. Veuillez sélectionner le texte manuellement.');
        }
    }
    
    clearForm() {
        // Réinitialiser tous les champs
        const inputs = [
            'character-name', 'current-level', 'new-level', 'character-class',
            'new-abilities', 'stat-improvements', 'new-items', 'lost-items',
            'money-gained', 'money-spent', 'current-money',
            'completed-quests', 'new-quests', 'rp-notes'
        ];
        
        inputs.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                if (element.type === 'number') {
                    if (id === 'current-level') element.value = '1';
                    else if (id === 'new-level') element.value = '2';
                    else element.value = '';
                } else if (element.tagName === 'SELECT') {
                    element.value = element.options[0].value;
                } else {
                    element.value = '';
                }
            }
        });
        
        // Revenir au premier onglet
        this.switchTab('capacites');
        
        // Effacer l'aperçu
        document.getElementById('discord-preview').innerHTML = `
            <div class="preview-placeholder">
                👆 Remplissez le formulaire pour voir l'aperçu
            </div>
        `;
        
        // Réinitialiser le compteur
        document.getElementById('char-count').textContent = '0';
        document.getElementById('char-count').style.color = '#27ae60';
        
        // Effacer le stockage
        localStorage.removeItem('faerun-form-generator');
    }
    
    saveToStorage() {
        const data = this.getFormData();
        const saveData = {
            ...data,
            timestamp: new Date().toISOString()
        };
        localStorage.setItem('faerun-form-generator', JSON.stringify(saveData));
    }
    
    loadFromStorage() {
        try {
            const saved = localStorage.getItem('faerun-form-generator');
            if (saved) {
                const data = JSON.parse(saved);
                
                // Restaurer les valeurs
                Object.keys(data).forEach(key => {
                    if (key !== 'timestamp') {
                        const element = document.getElementById(key.replace(/([A-Z])/g, '-$1').toLowerCase());
                        if (element && data[key] !== undefined) {
                            element.value = data[key];
                        }
                    }
                });
                
                console.log('Données du générateur de fiches restaurées');
                return true;
            }
        } catch (error) {
            console.error('Erreur lors du chargement des données:', error);
        }
        return false;
    }
    
    // Méthodes utilitaires
    validateForm() {
        const data = this.getFormData();
        const errors = [];
        
        // Vérifications de base
        if (data.newLevel <= data.currentLevel) {
            errors.push('Le nouveau niveau doit être supérieur au niveau actuel');
        }
        
        if (data.newLevel > 20 || data.currentLevel < 1) {
            errors.push('Les niveaux doivent être entre 1 et 20');
        }
        
        return {
            isValid: errors.length === 0,
            errors
        };
    }
    
    exportData() {
        const data = this.getFormData();
        const exportData = {
            ...data,
            message: this.buildMessage(data),
            timestamp: new Date().toISOString(),
            version: '1.0'
        };
        
        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `fiche-${data.characterName || 'personnage'}-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
    }
    
    importData(jsonData) {
        try {
            const data = typeof jsonData === 'string' ? JSON.parse(jsonData) : jsonData;
            
            // Vider le formulaire d'abord
            this.clearForm();
            
            // Restaurer les données
            Object.keys(data).forEach(key => {
                if (key !== 'timestamp' && key !== 'version' && key !== 'message') {
                    const elementId = key.replace(/([A-Z])/g, '-$1').toLowerCase();
                    const element = document.getElementById(elementId);
                    if (element && data[key] !== undefined) {
                        element.value = data[key];
                    }
                }
            });
            
            // Regénérer le message
            this.generateMessage();
            console.log('Données importées avec succès');
            
        } catch (error) {
            console.error('Erreur lors de l\'importation:', error);
            alert('Erreur lors de l\'importation du fichier');
        }
    }
}

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    const formGenerator = new FormGenerator();
    
    // Sauvegarde automatique toutes les 30 secondes
    setInterval(() => {
        formGenerator.saveToStorage();
    }, 30000);
    
    // Sauvegarde avant fermeture de la page
    window.addEventListener('beforeunload', () => {
        formGenerator.saveToStorage();
    });
    
    // Exposer pour le debug
    window.formGenerator = formGenerator;
    
    console.log('Générateur de fiches D&D initialisé');
});