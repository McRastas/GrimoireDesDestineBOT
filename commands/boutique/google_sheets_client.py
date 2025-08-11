# commands/boutique/google_sheets_client.py
"""
Client Google Sheets pour accéder aux données publiques sans authentification.
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
    Pas besoin de credentials pour les feuilles publiques.
    """
    
    def __init__(self, sheet_id: str):
        """
        Initialise le client Google Sheets.
        
        Args:
            sheet_id: ID du Google Sheets (extrait de l'URL)
        """
        self.sheet_id = sheet_id
        self.base_url = "https://docs.google.com/spreadsheets/d"
        
    def _build_csv_url(self, sheet_name: str) -> str:
        """
        Construit l'URL pour exporter une feuille en CSV.
        
        Args:
            sheet_name: Nom de la feuille à exporter
            
        Returns:
            str: URL complète pour l'export CSV
        """
        # URL format: https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}
        encoded_sheet_name = quote(sheet_name)
        return f"{self.base_url}/{self.sheet_id}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}"
    
    async def fetch_sheet_data(self, sheet_name: str) -> List[Dict[str, str]]:
        """
        Récupère les données d'une feuille Google Sheets.
        
        Args:
            sheet_name: Nom de la feuille à récupérer
            
        Returns:
            List[Dict[str, str]]: Liste des lignes avec les colonnes comme clés
            
        Raises:
            Exception: Si erreur de récupération des données
        """
        url = self._build_csv_url(sheet_name)
        
        try:
            async with aiohttp.ClientSession() as session:
                logger.info(f"Récupération des données depuis: {url}")
                
                async with session.get(url) as response:
                    if response.status != 200:
                        raise Exception(f"Erreur HTTP {response.status}: {await response.text()}")
                    
                    # Récupération du contenu CSV
                    csv_content = await response.text()
                    
                    # Parsing du CSV
                    csv_reader = csv.DictReader(io.StringIO(csv_content))
                    data = []
                    
                    for row in csv_reader:
                        # Nettoyage des données (suppression des espaces)
                        cleaned_row = {key.strip(): value.strip() for key, value in row.items()}
                        data.append(cleaned_row)
                    
                    logger.info(f"Récupération réussie: {len(data)} lignes")
                    return data
                    
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données: {e}")
            raise Exception(f"Impossible de récupérer les données du Google Sheets: {e}")
    
    async def test_connection(self, sheet_name: str) -> bool:
        """
        Test la connexion au Google Sheets.
        
        Args:
            sheet_name: Nom de la feuille à tester
            
        Returns:
            bool: True si la connexion réussit
        """
        try:
            data = await self.fetch_sheet_data(sheet_name)
            return len(data) > 0
        except Exception as e:
            logger.error(f"Test de connexion échoué: {e}")
            return False
    
    def get_sheet_url(self, sheet_name: str) -> str:
        """
        Retourne l'URL directe vers la feuille Google Sheets.
        
        Args:
            sheet_name: Nom de la feuille
            
        Returns:
            str: URL directe vers la feuille
        """
        # Format: https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid={GID}
        # Pour simplifier, on retourne l'URL générale
        return f"{self.base_url}/{self.sheet_id}/edit"