
import os
import json
from pathlib import Path
from typing import Dict, Any


class SecureConfig:
    # Gestionnaire de configuration 

    def __init__(self):
        # Dossier racine du projet
        self.base_dir = Path(__file__).parent.parent

        # Chemin vers credentials.json
        self.creds_path = self.base_dir / 'config' / 'credentials.json'

        # Créer le fichier s’il n’existe pas
        if not self.creds_path.exists():
            self._create_default_credentials()

    def _create_default_credentials(self):
        # Création d’identifiants par défaut
        print("⚠️  Création d'identifiants par défaut...")

        default_creds = {
             {
                "facebook": {
                    "email": "chatbrielaa@gmail.com",
                    "password": "ElaaGhostTest1604"
                },
                "whatsapp": {
                    "phone": "+21654970604"
                }
                }
        }

        # Sauvegarde dans le fichier JSON
        with open(self.creds_path, 'w', encoding='utf-8') as f:
            json.dump(default_creds, f, indent=2)

        print(f"✅ Identifiants par défaut créés: {self.creds_path}")

    def get_credentials(self) -> Dict[str, Any]:
        # Charger les identifiants depuis le fichier
        if not self.creds_path.exists():
            self._create_default_credentials()

        try:
            with open(self.creds_path, 'r', encoding='utf-8') as f:
                credentials = json.load(f)

            # Vérification des plateformes requises
            required_platforms = ['facebook', 'whatsapp']
            for platform in required_platforms:
                if platform not in credentials:
                    print(f"⚠️ Plateforme manquante: {platform}")
                    if platform in ['facebook']:
                        credentials[platform] = {'email': '', 'password': ''}
                    else:
                        credentials[platform] = {'phone': ''}

            return credentials

        except json.JSONDecodeError as e:
            print(f"❌ JSON invalide: {e}")
            return self._get_fallback_credentials()

        except Exception as e:
            print(f"❌ Erreur chargement: {e}")
            return self._get_fallback_credentials()

    def _get_fallback_credentials(self) -> Dict[str, Any]:
        # Identifiants de secours pour eviter le plantage de l'application
        return {
            'facebook': {'email': '', 'password': ''},
            'whatsapp': {'phone': ''}
        }

    def save_credentials(self, credentials: Dict[str, Any]) -> bool:
        # Sauvegarder les identifiants
        try:
            with open(self.creds_path, 'w', encoding='utf-8') as f:
                json.dump(credentials, f, indent=2)

            print(f"✅ Identifiants sauvegardés: {self.creds_path}")
            return True

        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
            return False


# Instance globale du gestionnaire
config_manager = SecureConfig()
