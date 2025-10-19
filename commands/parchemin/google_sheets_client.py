# commands/parchemin/google_sheets_client.py
"""
Client Google Sheets pour accéder aux données de sorts sans authentification.
Utilise les noms de colonnes configurables depuis config_v2.py
"""

import aiohttp
import csv
import io
import logging
from typing import List, Dict, Optional
from urllib.parse import quote
from .config_v2 import get_config

logger = logging.getLogger(__name__)

class GoogleSheetsClient:
    """
    Client pour accéder aux Google Sheets publics via l'export CSV.
    Utilise les noms de colonnes depuis la configuration.
    """
    
    def __init__(self, sheet_id: str):
        """
        Initialise le client Google Sheets pour les sorts.
        
        Args:
            sheet_id: ID du Google Sheets (extrait de l'URL)
        """
        self.sheet_id = sheet_id
        self.base_url = "https://docs.google.com/spreadsheets/d"
        
        # Charger les noms de colonnes depuis la config
        config = get_config()
        self.columns = config.get('columns', {})
        
        logger.info(f"GoogleSheetsClient initialisé avec colonnes: {self.columns}")
        
    def _build_csv_url(self, sheet_name: str = None, gid: str = None) -> str:
        """
        Construit l'URL pour exporter une feuille en CSV.
        
        Args:
            sheet_name: Nom de la feuille à exporter (optionnel)
            gid: GID de la feuille (optionnel, prioritaire sur sheet_name)
            
        Returns:
            str: URL complète pour l'export CSV
        """
        if gid and gid != '0':
            return f"{self.base_url}/{self.sheet_id}/export?format=csv&gid={gid}"
        elif sheet_name:
            encoded_sheet_name = quote(sheet_name)
            return f"{self.base_url}/{self.sheet_id}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}"
        else:
            return f"{self.base_url}/{self.sheet_id}/export?format=csv"
    
    async def fetch_sheet_data(self, sheet_name: str = None, gid: str = None) -> List[Dict[str, str]]:
        """
        Récupère les données de sorts depuis Google Sheets.
        
        Args:
            sheet_name: Nom de la feuille à récupérer (optionnel)
            gid: GID de la feuille (optionnel, prioritaire)
            
        Returns:
            List[Dict[str, str]]: Liste des sorts avec leurs propriétés
            
        Raises:
            Exception: Si erreur de récupération des données
        """
        url = self._build_csv_url(sheet_name, gid)
        
        try:
            async with aiohttp.ClientSession() as session:
                logger.info(f"Récupération des sorts depuis: {url}")
                
                async with session.get(url) as response:
                    if response.status != 200:
                        raise Exception(f"Erreur HTTP {response.status}: {await response.text()}")
                    
                    csv_content = await response.text()
                    csv_reader = csv.DictReader(io.StringIO(csv_content))
                    spells = []
                    
                    for row in csv_reader:
                        # Nettoyer les clés (supprimer espaces)
                        cleaned_row = {key.strip(): value.strip() for key, value in row.items()}
                        
                        # Validation et nettoyage spécifique aux sorts
                        spell = self._clean_spell_data(cleaned_row)
                        if spell:
                            spells.append(spell)
                    
                    logger.info(f"Récupération réussie: {len(spells)} sorts")
                    return spells
                    
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des sorts: {e}")
            raise Exception(f"Impossible de récupérer les données des sorts: {e}")
    
    def _clean_spell_data(self, row: Dict[str, str]) -> Optional[Dict[str, str]]:
        """
        Nettoie et valide les données d'un sort.
        Utilise les noms de colonnes depuis la configuration.
        
        Args:
            row: Ligne de données brutes du CSV
            
        Returns:
            Dict[str, str]: Données nettoyées du sort ou None si invalide
        """
        try:
            # Récupérer les colonnes configurées
            col_name = self.columns.get('name', 'Name')
            col_name_vf = self.columns.get('name_vf', 'NameVF')
            col_level = self.columns.get('level', 'Level')
            col_school = self.columns.get('school', 'School')
            col_source = self.columns.get('source', 'Source')
            col_ritual = self.columns.get('ritual', 'RITUEL')
            col_classes = self.columns.get('classes', 'CLASSE')
            
            # Récupérer le nom du sort (essentiel)
            name = row.get(col_name, '').strip()
            if not name:
                logger.debug(f"Ligne ignorée: pas de nom de sort")
                return None
            
            # Récupérer le nom français
            name_vf = row.get(col_name_vf, '').strip()
            
            # Récupérer le niveau
            level_str = row.get(col_level, '0').strip()
            try:
                level = int(level_str) if level_str.isdigit() else 0
            except (ValueError, TypeError):
                level = 0
            
            # Récupérer l'école
            school = row.get(col_school, '').strip()
            if not school:
                school = 'Inconnue'
            
            # Récupérer la source
            source = row.get(col_source, '').strip()
            if not source:
                source = 'Manuel inconnu'
            
            # Récupérer le statut rituel
            ritual_str = row.get(col_ritual, '').strip().upper()
            ritual = ritual_str in ['RITUEL', 'OUI', 'TRUE', 'YES', 'Y', '1']
            
            # Récupérer les classes
            classes_str = row.get(col_classes, '').strip()
            classes = []
            if classes_str:
                classes = [cls.strip() for cls in classes_str.split(',') if cls.strip()]
            
            logger.debug(f"Sort nettoyé: {name} (niv. {level}, {school}, rituellement: {ritual})")
            
            return {
                'name': name,
                'name_vf': name_vf,
                'source': source,
                'level': level,
                'school': school,
                'ritual': ritual,
                'classes': classes,
                'raw_data': row  # Garder pour debug
            }
            
        except Exception as e:
            logger.warning(f"Erreur lors du nettoyage des données de sort: {e}")
            return None
    
    async def test_connection(self, sheet_name: str = None, gid: str = None) -> bool:
        """
        Test la connexion au Google Sheets.
        
        Args:
            sheet_name: Nom de la feuille à tester (optionnel)
            gid: GID de la feuille à tester (optionnel)
            
        Returns:
            bool: True si la connexion réussit
        """
        try:
            data = await self.fetch_sheet_data(sheet_name, gid)
            return len(data) > 0
        except Exception as e:
            logger.error(f"Test de connexion échoué: {e}")
            return False
    
    def get_sheet_url(self, sheet_name: str = None, gid: str = None) -> str:
        """
        Retourne l'URL directe vers la feuille Google Sheets.
        
        Args:
            sheet_name: Nom de la feuille (optionnel)
            gid: GID de la feuille (optionnel)
            
        Returns:
            str: URL complète vers le Google Sheets
        """
        if gid and gid != '0':
            return f"{self.base_url}/{self.sheet_id}/edit?gid={gid}"
        elif sheet_name:
            return f"{self.base_url}/{self.sheet_id}/edit"
        else:
            return f"{self.base_url}/{self.sheet_id}/edit"