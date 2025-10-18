# commands/parchemin/google_sheets_client.py
"""
Client Google Sheets pour accéder aux données de sorts sans authentification.
Structure inspirée de boutique/google_sheets_client.py
"""

import aiohttp
import csv
import io
import logging
from typing import List, Dict, Optional
from urllib.parse import quote

logger = logging.getLogger(__name__)

class GoogleSheetsClient:
    """
    Client pour accéder aux Google Sheets publics via l'export CSV.
    Adapté pour les données de sorts - même structure que boutique.
    """
    
    def __init__(self, sheet_id: str):
        """
        Initialise le client Google Sheets pour les sorts.
        Même signature que boutique/google_sheets_client.py
        
        Args:
            sheet_id: ID du Google Sheets (extrait de l'URL)
        """
        self.sheet_id = sheet_id
        self.base_url = "https://docs.google.com/spreadsheets/d"
        
    def _build_csv_url(self, sheet_name: str = None, gid: str = None) -> str:
        """
        Construit l'URL pour exporter une feuille en CSV.
        Amélioré par rapport à boutique pour supporter les GID.
        
        Args:
            sheet_name: Nom de la feuille à exporter (optionnel)
            gid: GID de la feuille (optionnel, prioritaire sur sheet_name)
            
        Returns:
            str: URL complète pour l'export CSV
        """
        if gid and gid != '0':
            # Format avec GID (plus fiable): https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}
            return f"{self.base_url}/{self.sheet_id}/export?format=csv&gid={gid}"
        elif sheet_name:
            # Format avec nom de feuille (comme boutique): https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}
            encoded_sheet_name = quote(sheet_name)
            return f"{self.base_url}/{self.sheet_id}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}"
        else:
            # Format par défaut (première feuille)
            return f"{self.base_url}/{self.sheet_id}/export?format=csv"
    
    async def fetch_sheet_data(self, sheet_name: str = None, gid: str = None) -> List[Dict[str, str]]:
        """
        Récupère les données de sorts depuis Google Sheets.
        Même structure que boutique/fetch_sheet_data mais adapté aux sorts.
        
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
                    
                    # Récupération du contenu CSV (même logique que boutique)
                    csv_content = await response.text()
                    
                    # Parsing du CSV
                    csv_reader = csv.DictReader(io.StringIO(csv_content))
                    spells = []
                    
                    for row in csv_reader:
                        # Nettoyage des données (même logique que boutique)
                        cleaned_row = {key.strip(): value.strip() for key, value in row.items()}
                        
                        # Validation et nettoyage spécifique aux sorts
                        spell = self._clean_spell_data(cleaned_row)
                        if spell:  # Ignorer les lignes vides ou invalides
                            spells.append(spell)
                    
                    logger.info(f"Récupération réussie: {len(spells)} sorts")
                    return spells
                    
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des sorts: {e}")
            raise Exception(f"Impossible de récupérer les données des sorts: {e}")
    
    def _clean_spell_data(self, row: Dict[str, str]) -> Optional[Dict[str, str]]:
        """
        Nettoie et valide les données d'un sort.
        Équivalent de _clean_item_data dans boutique mais pour les sorts.
        
        Args:
            row: Ligne de données brutes du CSV
            
        Returns:
            Dict[str, str]: Données nettoyées du sort ou None si invalide
        """
        try:
            # Récupérer les colonnes essentielles (équivalent des colonnes objets)
            name = row.get('Name', '').strip()
            if not name:  # Ignorer les lignes sans nom (comme boutique ignore sans nom d'objet)
                return None
            
            level_str = row.get('Level', '0').strip()
            try:
                level = int(level_str) if level_str.isdigit() else 0
            except ValueError:
                level = 0
            
            school = row.get('School', '').strip()
            source = row.get('Source', '').strip()
            ritual_str = row.get('RITUEL', '').strip().upper()
            ritual = ritual_str == 'RITUEL'
            
            # Traitement des classes (équivalent du traitement des prix dans boutique)
            classes_str = row.get('CLASSE', '').strip()
            classes = []
            if classes_str:
                # Diviser par virgules et nettoyer (même logique que boutique)
                classes = [cls.strip() for cls in classes_str.split(',') if cls.strip()]
            
            return {
                'name': name,
                'source': source,
                'level': level,
                'school': school,
                'ritual': ritual,
                'classes': classes,
                'raw_data': row  # Garder les données brutes pour debug (comme boutique)
            }
            
        except Exception as e:
            logger.warning(f"Erreur lors du nettoyage des données de sort: {e}")
            return None
    
    async def test_connection(self, sheet_name: str = None, gid: str = None) -> bool:
        """
        Test la connexion au Google Sheets.
        Même structure que boutique/test_connection.
        
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
        Même structure que boutique/get_sheet_url mais avec support GID.
        
        Args:
            sheet_name: Nom de la feuille (optionnel)
            gid: GID de la feuille (optionnel)
            
        Returns:
            str: URL directe vers la feuille
        """
        if gid and gid != '0':
            # Format avec GID pour lien direct
            return f"{self.base_url}/{self.sheet_id}/edit#gid={gid}"
        else:
            # Format général (comme boutique)
            return f"{self.base_url}/{self.sheet_id}/edit"