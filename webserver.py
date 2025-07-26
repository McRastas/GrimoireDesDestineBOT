from flask import Flask, render_template_string, jsonify
from threading import Thread
from config import Config
import logging
import os
from datetime import datetime
from collections import deque

logger = logging.getLogger(__name__)


class LogHandler(logging.Handler):
    """Handler personnalisé pour capturer les logs en mémoire."""
    
    def __init__(self, max_logs=500):
        super().__init__()
        self.logs = deque(maxlen=max_logs)  # Garde les 500 derniers logs
        
    def emit(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S'),
            'level': record.levelname,
            'logger': record.name,
            'message': self.format(record),
            'raw': record
        }
        self.logs.append(log_entry)


class WebServer:
    """Serveur web simple pour visualiser les logs."""

    def __init__(self, bot=None):
        self.app = Flask(__name__)
        self.bot = bot
        
        # Handler pour capturer les logs
        self.log_handler = LogHandler()
        self.log_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        self.log_handler.setFormatter(formatter)
        
        # Ajouter le handler au logger root pour capturer tous les logs
        logging.getLogger().addHandler(self.log_handler)
        
        self._setup_routes()

    def _setup_routes(self):
        
        @self.app.route('/')
        def logs_dashboard():
            """Interface principale pour visualiser les logs."""
            html_template = """
            <!DOCTYPE html>
            <html lang="fr">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Bot Faerûn - Logs</title>
                <style>
                    * { margin: 0; padding: 0; box-sizing: border-box; }
                    
                    body {
                        font-family: 'Consolas', 'Monaco', monospace;
                        background: #1a1a1a;
                        color: #e0e0e0;
                        line-height: 1.4;
                    }
                    
                    .header {
                        background: #2d2d2d;
                        padding: 1rem 2rem;
                        border-bottom: 2px solid #ffd700;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        position: sticky;
                        top: 0;
                        z-index: 100;
                    }
                    
                    .title {
                        color: #ffd700;
                        font-size: 1.5rem;
                        font-weight: bold;
                    }
                    
                    .controls {
                        display: flex;
                        gap: 1rem;
                        align-items: center;
                    }
                    
                    .btn {
                        padding: 0.5rem 1rem;
                        background: #ffd700;
                        color: #1a1a1a;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        font-weight: bold;
                        text-decoration: none;
                        display: inline-block;
                    }
                    
                    .btn:hover { background: #ffed4e; }
                    
                    .btn-secondary {
                        background: #444;
                        color: #fff;
                    }
                    
                    .btn-secondary:hover { background: #555; }
                    
                    .status {
                        display: flex;
                        align-items: center;
                        gap: 0.5rem;
                        color: #4ade80;
                    }
                    
                    .status-dot {
                        width: 8px;
                        height: 8px;
                        background: #4ade80;
                        border-radius: 50%;
                        animation: pulse 2s infinite;
                    }
                    
                    @keyframes pulse {
                        0%, 100% { opacity: 1; }
                        50% { opacity: 0.5; }
                    }
                    
                    .stats-bar {
                        background: #2a2a2a;
                        padding: 0.8rem 2rem;
                        display: flex;
                        gap: 2rem;
                        font-size: 0.9rem;
                        border-bottom: 1px solid #444;
                    }
                    
                    .stat { color: #ccc; }
                    .stat strong { color: #ffd700; }
                    
                    .filters {
                        background: #333;
                        padding: 1rem 2rem;
                        display: flex;
                        gap: 1rem;
                        align-items: center;
                        flex-wrap: wrap;
                    }
                    
                    .filter-btn {
                        padding: 0.3rem 0.8rem;
                        background: #555;
                        color: #fff;
                        border: none;
                        border-radius: 20px;
                        cursor: pointer;
                        font-size: 0.8rem;
                    }
                    
                    .filter-btn.active { background: #ffd700; color: #1a1a1a; }
                    .filter-btn:hover:not(.active) { background: #666; }
                    
                    .logs-container {
                        max-height: calc(100vh - 200px);
                        overflow-y: auto;
                        padding: 1rem;
                        background: #1a1a1a;
                    }
                    
                    .log-entry {
                        padding: 0.5rem 1rem;
                        margin-bottom: 0.5rem;
                        border-radius: 4px;
                        border-left: 4px solid #666;
                        background: #252525;
                        transition: all 0.2s ease;
                    }
                    
                    .log-entry:hover {
                        background: #2a2a2a;
                        transform: translateX(5px);
                    }
                    
                    .log-entry.INFO { border-left-color: #3b82f6; }
                    .log-entry.WARNING { border-left-color: #f59e0b; }
                    .log-entry.ERROR { border-left-color: #ef4444; }
                    .log-entry.CRITICAL { border-left-color: #dc2626; }
                    .log-entry.DEBUG { border-left-color: #6b7280; }
                    
                    .log-header {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-bottom: 0.3rem;
                    }
                    
                    .log-time {
                        color: #888;
                        font-size: 0.8rem;
                    }
                    
                    .log-level {
                        padding: 0.2rem 0.5rem;
                        border-radius: 3px;
                        font-size: 0.7rem;
                        font-weight: bold;
                    }
                    
                    .log-level.INFO { background: #3b82f6; color: white; }
                    .log-level.WARNING { background: #f59e0b; color: white; }
                    .log-level.ERROR { background: #ef4444; color: white; }
                    .log-level.CRITICAL { background: #dc2626; color: white; }
                    .log-level.DEBUG { background: #6b7280; color: white; }
                    
                    .log-logger {
                        color: #ffd700;
                        font-size: 0.8rem;
                    }
                    
                    .log-message {
                        color: #e0e0e0;
                        word-break: break-word;
                    }
                    
                    .auto-scroll-indicator {
                        position: fixed;
                        bottom: 20px;
                        right: 20px;
                        background: #ffd700;
                        color: #1a1a1a;
                        padding: 0.5rem 1rem;
                        border-radius: 20px;
                        font-size: 0.8rem;
                        font-weight: bold;
                        cursor: pointer;
                    }
                    
                    .hidden { display: none; }
                    
                    /* Scrollbar custom */
                    .logs-container::-webkit-scrollbar { width: 8px; }
                    .logs-container::-webkit-scrollbar-track { background: #333; }
                    .logs-container::-webkit-scrollbar-thumb { 
                        background: #666; 
                        border-radius: 4px; 
                    }
                    .logs-container::-webkit-scrollbar-thumb:hover { background: #888; }
                    
                    @media (max-width: 768px) {
                        .header { flex-direction: column; gap: 1rem; }
                        .stats-bar { flex-direction: column; gap: 0.5rem; }
                        .filters { flex-direction: column; align-items: stretch; }
                    }
                </style>
            </head>
            <body>
                <div class="header">
                    <div class="title">🏰 Bot Faerûn - Logs</div>
                    <div class="controls">
                        <div class="status">
                            <div class="status-dot"></div>
                            <span id="bot-status">En ligne</span>
                        </div>
                        <button class="btn" onclick="clearLogs()">🗑️ Vider</button>
                        <button class="btn btn-secondary" onclick="downloadLogs()">💾 Export</button>
                        <a href="/api/health" class="btn btn-secondary">🔧 API</a>
                    </div>
                </div>
                
                <div class="stats-bar">
                    <div class="stat">Total: <strong id="total-logs">0</strong></div>
                    <div class="stat">Erreurs: <strong id="error-count">0</strong></div>
                    <div class="stat">Warnings: <strong id="warning-count">0</strong></div>
                    <div class="stat">Info: <strong id="info-count">0</strong></div>
                    <div class="stat">Dernière MAJ: <strong id="last-update">-</strong></div>
                </div>
                
                <div class="filters">
                    <span>Filtrer:</span>
                    <button class="filter-btn active" data-level="ALL" onclick="filterLogs('ALL')">Tous</button>
                    <button class="filter-btn" data-level="INFO" onclick="filterLogs('INFO')">Info</button>
                    <button class="filter-btn" data-level="WARNING" onclick="filterLogs('WARNING')">Warning</button>
                    <button class="filter-btn" data-level="ERROR" onclick="filterLogs('ERROR')">Error</button>
                    <button class="filter-btn" data-level="CRITICAL" onclick="filterLogs('CRITICAL')">Critical</button>
                    <button class="filter-btn" data-level="DEBUG" onclick="filterLogs('DEBUG')">Debug</button>
                </div>
                
                <div class="logs-container" id="logs-container">
                    <div style="text-align: center; color: #666; padding: 2rem;">
                        🔄 Chargement des logs...
                    </div>
                </div>
                
                <div class="auto-scroll-indicator hidden" id="auto-scroll" onclick="toggleAutoScroll()">
                    🔒 Auto-scroll: ON
                </div>
                
                <script>
                    let autoScroll = true;
                    let currentFilter = 'ALL';
                    let allLogs = [];
                    
                    // Chargement initial
                    loadLogs();
                    
                    // Mise à jour automatique toutes les 2 secondes
                    setInterval(loadLogs, 2000);
                    
                    async function loadLogs() {
                        try {
                            const response = await fetch('/api/logs');
                            const data = await response.json();
                            
                            allLogs = data.logs || [];
                            updateStats(data);
                            displayLogs();
                            
                        } catch (error) {
                            console.error('Erreur chargement logs:', error);
                            document.getElementById('bot-status').textContent = 'Erreur connexion';
                        }
                    }
                    
                    function displayLogs() {
                        const container = document.getElementById('logs-container');
                        
                        // Filtrer les logs
                        let filteredLogs = allLogs;
                        if (currentFilter !== 'ALL') {
                            filteredLogs = allLogs.filter(log => log.level === currentFilter);
                        }
                        
                        // Générer le HTML
                        const logsHtml = filteredLogs.map(log => `
                            <div class="log-entry ${log.level}">
                                <div class="log-header">
                                    <div>
                                        <span class="log-time">${log.timestamp}</span>
                                        <span class="log-logger">[${log.logger}]</span>
                                    </div>
                                    <span class="log-level ${log.level}">${log.level}</span>
                                </div>
                                <div class="log-message">${escapeHtml(log.message)}</div>
                            </div>
                        `).join('');
                        
                        container.innerHTML = logsHtml || '<div style="text-align: center; color: #666; padding: 2rem;">Aucun log à afficher</div>';
                        
                        // Auto-scroll vers le bas
                        if (autoScroll) {
                            container.scrollTop = container.scrollHeight;
                        }
                    }
                    
                    function updateStats(data) {
                        document.getElementById('total-logs').textContent = allLogs.length;
                        document.getElementById('error-count').textContent = allLogs.filter(l => l.level === 'ERROR').length;
                        document.getElementById('warning-count').textContent = allLogs.filter(l => l.level === 'WARNING').length;
                        document.getElementById('info-count').textContent = allLogs.filter(l => l.level === 'INFO').length;
                        document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
                        
                        // Statut bot
                        if (data.bot_online) {
                            document.getElementById('bot-status').textContent = 'En ligne';
                        } else {
                            document.getElementById('bot-status').textContent = 'Hors ligne';
                        }
                    }
                    
                    function filterLogs(level) {
                        currentFilter = level;
                        
                        // Mettre à jour les boutons
                        document.querySelectorAll('.filter-btn').forEach(btn => {
                            btn.classList.remove('active');
                        });
                        document.querySelector(`[data-level="${level}"]`).classList.add('active');
                        
                        displayLogs();
                    }
                    
                    function clearLogs() {
                        if (confirm('Vider tous les logs affichés ?')) {
                            fetch('/api/logs/clear', { method: 'POST' })
                                .then(() => loadLogs())
                                .catch(err => console.error('Erreur vidage logs:', err));
                        }
                    }
                    
                    function downloadLogs() {
                        const logsText = allLogs.map(log => 
                            `${log.timestamp} [${log.level}] ${log.logger}: ${log.message}`
                        ).join('\\n');
                        
                        const blob = new Blob([logsText], { type: 'text/plain' });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `bot-faerun-logs-${new Date().toISOString().split('T')[0]}.txt`;
                        a.click();
                        URL.revokeObjectURL(url);
                    }
                    
                    function toggleAutoScroll() {
                        autoScroll = !autoScroll;
                        const indicator = document.getElementById('auto-scroll');
                        indicator.textContent = autoScroll ? '🔒 Auto-scroll: ON' : '🔓 Auto-scroll: OFF';
                    }
                    
                    function escapeHtml(text) {
                        const div = document.createElement('div');
                        div.textContent = text;
                        return div.innerHTML;
                    }
                    
                    // Détection du scroll manuel pour désactiver l'auto-scroll
                    document.getElementById('logs-container').addEventListener('scroll', function() {
                        const container = this;
                        const isAtBottom = container.scrollTop + container.clientHeight >= container.scrollHeight - 10;
                        
                        if (!isAtBottom && autoScroll) {
                            toggleAutoScroll();
                        }
                    });
                </script>
            </body>
            </html>
            """
            return render_template_string(html_template)

        @self.app.route('/api/logs')
        def get_logs():
            """API pour récupérer les logs en JSON."""
            try:
                logs_data = list(self.log_handler.logs)  # Convertir deque en list
                
                return jsonify({
                    'logs': logs_data,
                    'total': len(logs_data),
                    'bot_online': self.bot.is_ready() if self.bot else False,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Erreur API logs: {e}")
                return jsonify({'error': str(e), 'logs': []}), 500

        @self.app.route('/api/logs/clear', methods=['POST'])
        def clear_logs():
            """API pour vider les logs."""
            try:
                self.log_handler.logs.clear()
                logger.info("Logs vidés via interface web")
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/health')
        def health():
            """Point de contrôle santé."""
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "bot_connected": self.bot.is_ready() if self.bot else False,
                "logs_count": len(self.log_handler.logs)
            })

    def run(self):
        self.app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=False)

    def start_in_thread(self):
        thread = Thread(target=self.run, daemon=True)
        thread.start()
        logger.info(f"🌐 Interface logs disponible sur http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
