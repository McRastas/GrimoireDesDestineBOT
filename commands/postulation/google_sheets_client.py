# commands/postulation/google_sheets_client.py
"""
Client pour récupérer les données depuis Google Sheets.
"""

import aiohttp
import csv
import logging
from typing import List, Dict, Optional
from io import StringIO

logger = logging.getLogger(__name__)


class GoogleSheetsClient:
    """Client pour interagir avec Google Sheets via l'API d'export CSV."""
    
    def __init__(self, sheet_id: str):
        """
        Initialise le client Google Sheets.
        
        Args:
            sheet_id: ID du Google Sheet
        """
        self.sheet_id = sheet_id
        self.base_url = "https://docs.google.com/spreadsheets/d"
        logger.info(f"GoogleSheetsClient initialisé pour sheet_id: {sheet_id}")
    
    def _build_csv_url(self, sheet_name: str, gid: str = "0") -> str:
        """
        Construit l'URL d'export CSV pour une feuille.
        
        Args:
            sheet_name: Nom de la feuille
            gid: GID de la feuille (optionnel)
            
        Returns:
            str: URL d'export CSV
        """
        # Format: https://docs.google.com/spreadsheets/d/SHEET_ID/export?format=csv&gid=GID
        url = f"{self.base_url}/{self.sheet_id}/export?format=csv&gid={gid}"
        logger.debug(f"URL CSV construite: {url}")
        return url
    
    async def fetch_sheet_data(self, sheet_name: str, gid: str = "0") -> List[Dict[str, str]]:
        """
        Récupère les données d'une feuille Google Sheets.
        
        Args:
            sheet_name: Nom de la feuille
            gid: GID de la feuille
            
        Returns:
            List[Dict[str, str]]: Liste des lignes sous forme de dictionnaires
        """
        url = self._build_csv_url(sheet_name, gid)
        
        try:
            logger.info(f"Récupération des données depuis '{sheet_name}' (GID: {gid})")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        logger.error(f"Erreur HTTP {response.status} lors de la récupération du sheet")
                        return []
                    
                    # Lire le contenu CSV
                    content = await response.text()
                    
                    if not content.strip():
                        logger.warning(f"Le sheet '{sheet_name}' est vide")
                        return []
                    
                    # Parser le CSV
                    csv_file = StringIO(content)
                    reader = csv.DictReader(csv_file)
                    
                    # Convertir en liste de dictionnaires
                    data = []
                    for row_index, row in enumerate(reader):
                        # Nettoyer les clés (enlever espaces superflus)
                        cleaned_row = {k.strip(): v.strip() if v else '' for k, v in row.items()}
                        data.append(cleaned_row)
                    
                    logger.info(f"✅ {len(data)} lignes récupérées depuis '{sheet_name}'")
                    return data
                    
        except aiohttp.ClientError as e:
            logger.error(f"Erreur réseau lors de la récupération du sheet: {e}")
            return []
        except csv.Error as e:
            logger.error(f"Erreur de parsing CSV: {e}")
            return []
        except Exception as e:
            logger.error(f"Erreur inattendue lors de la récupération du sheet: {e}")
            return []
    
    async def get_player_characters(
        self, 
        discord_id: str, 
        sheet_name: str, 
        gid: str = "0",
        columns_config: Dict[str, str] = None
    ) -> List[Dict[str, str]]:
        """
        Récupère les personnages d'un joueur spécifique.
        
        Args:
            discord_id: ID Discord du joueur
            sheet_name: Nom de la feuille
            gid: GID de la feuille
            columns_config: Configuration des colonnes
            
        Returns:
            List[Dict[str, str]]: Liste des personnages du joueur
        """
        if not columns_config:
            logger.error("Configuration des colonnes manquante")
            return []
        
        # Récupérer toutes les données
        all_data = await self.fetch_sheet_data(sheet_name, gid)
        
        if not all_data:
            logger.warning(f"Aucune donnée trouvée dans '{sheet_name}'")
            return []
        
        # Récupérer le nom de la colonne ID Discord
        discord_id_column = columns_config.get('discord_id', 'ID Discord')
        
        # Filtrer par ID Discord
        player_characters = []
        for row in all_data:
            row_discord_id = row.get(discord_id_column, '').strip()
            
            # Comparer les IDs (en string)
            if row_discord_id == str(discord_id):
                player_characters.append(row)
        
        logger.info(f"Trouvé {len(player_characters)} personnages pour Discord ID: {discord_id}")
        return player_characters
    
    async def test_connection(self, sheet_name: str, gid: str = "0") -> bool:
        """
        Teste la connexion au Google Sheet.
        
        Args:
            sheet_name: Nom de la feuille
            gid: GID de la feuille
            
        Returns:
            bool: True si la connexion fonctionne
        """
        url = self._build_csv_url(sheet_name, gid)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        logger.info(f"✅ Connexion au sheet '{sheet_name}' réussie")
                        return True
                    else:
                        logger.error(f"❌ Erreur HTTP {response.status} lors du test de connexion")
                        return False
        except Exception as e:
            logger.error(f"❌ Erreur lors du test de connexion: {e}")
            return False


# Fonction utilitaire pour debug
async def debug_sheet_columns(sheet_id: str, sheet_name: str, gid: str = "0"):
    """
    Affiche les colonnes disponibles dans un sheet (pour debug).
    
    Args:
        sheet_id: ID du Google Sheet
        sheet_name: Nom de la feuille
        gid: GID de la feuille
    """
    client = GoogleSheetsClient(sheet_id)
    data = await client.fetch_sheet_data(sheet_name, gid)
    
    if data:
        print(f"\n📊 Colonnes disponibles dans '{sheet_name}':")
        print("=" * 60)
        for i, column in enumerate(data[0].keys(), 1):
            print(f"{i:2d}. {column}")
        print("=" * 60)
        print(f"\nNombre total de lignes: {len(data)}")
    else:
        print(f"❌ Impossible de récupérer les données de '{sheet_name}'")


if __name__ == "__main__":
    import asyncio
    
    # Test du client avec le sheet de personnages
    async def main():
        print("🧪 Test du GoogleSheetsClient pour postulation")
        print("=" * 60)
        
        # Configuration de test
        SHEET_ID = "1QPLhU1I594hKQdvg4LhrL6Tui6pko01hiRO0DUnvk2U"
        SHEET_NAME = "Suivi des personnages"
        GID = "0"
        
        client = GoogleSheetsClient(SHEET_ID)
        
        # Test 1: Connexion
        print("\n📡 Test de connexion...")
        connection_ok = await client.test_connection(SHEET_NAME, GID)
        
        if not connection_ok:
            print("❌ Échec du test de connexion")
            return
        
        # Test 2: Récupération des données
        print("\n📥 Récupération des données...")
        data = await client.fetch_sheet_data(SHEET_NAME, GID)
        print(f"✅ {len(data)} lignes récupérées")
        
        # Test 3: Afficher les colonnes
        if data:
            await debug_sheet_columns(SHEET_ID, SHEET_NAME, GID)
            
            # Test 4: Récupérer les personnages d'un joueur spécifique
            print("\n👤 Test de récupération des personnages d'un joueur...")
            test_discord_id = "256867885140541440"  # Premier ID du sheet
            
            columns_config = {
                'discord_id': 'ID Discord',
                'nom_pj': 'Nom du PJ',
                'joueur': 'Joueurs',
                'race': 'Races'
            }
            
            characters = await client.get_player_characters(
                test_discord_id, 
                SHEET_NAME, 
                GID,
                columns_config
            )
            
            if characters:
                print(f"✅ Trouvé {len(characters)} personnage(s) pour l'ID {test_discord_id}")
                for char in characters:
                    print(f"   • {char.get('Nom du PJ', 'Inconnu')} - {char.get('Races', 'Race inconnue')}")
            else:
                print(f"❌ Aucun personnage trouvé pour l'ID {test_discord_id}")
    
    asyncio.run(main())