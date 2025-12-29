"""
SessionManager - Gestionnaire de sessions et cookies
Permet de sauvegarder et charger les cookies pour maintenir les sessions
Version avec force login activé par défaut
"""
import pickle
import json
import logging
import time
import random
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self, session_dir: str = "data/sessions", force_login: bool = True):
        """
        Initialise le gestionnaire de sessions
        
        Args:
            session_dir (str): Répertoire de stockage des sessions
            force_login (bool): Force la connexion à chaque exécution (True par défaut)
        """
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.force_login = force_login
        
        # Supprimer les sessions existantes si force_login est True
        if self.force_login:
            self.clear_all_sessions()
            logger.info("🔓 Mode FORCE LOGIN activé - toutes les sessions ont été supprimées")

    def clear_all_sessions(self):
        """Supprime toutes les sessions existantes"""
        try:
            pattern = "*_cookies_*.pkl"
            deleted_count = 0
            
            for file in self.session_dir.glob(pattern):
                try:
                    file.unlink()
                    deleted_count += 1
                    logger.debug(f"🗑️ Session supprimée: {file.name}")
                except Exception as e:
                    logger.error(f"❌ Erreur suppression {file}: {e}")
            
            if deleted_count > 0:
                logger.info(f"🗑️ {deleted_count} sessions supprimées (force login activé)")
        except Exception as e:
            logger.error(f"❌ Erreur lors de la suppression des sessions: {e}")

    def save_cookies(self, platform: str, driver) -> bool:
        """
        Sauvegarde les cookies au format pickle
        
        Args:
            platform (str): Nom de la plateforme
            driver: Instance Selenium WebDriver
            
        Returns:
            bool: True si sauvegarde réussie
        """
        try:
            cookies = driver.get_cookies()
            if not cookies:
                logger.warning(f"Aucun cookie à sauvegarder pour {platform}")
                return False
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{platform}_cookies_{timestamp}.pkl"
            filepath = self.session_dir / filename

            with open(filepath, 'wb') as f:
                pickle.dump(cookies, f)

            logger.info(f"✅ {len(cookies)} cookies sauvegardés pour {platform}")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde cookies {platform}: {e}")
            return False

    def load_cookies(self, platform: str, driver) -> bool:
        """
        Charge les cookies les plus récents
        
        Args:
            platform (str): Nom de la plateforme
            driver: Instance Selenium WebDriver
            
        Returns:
            bool: True si chargement réussi
        """
        # Si force_login est activé, on retourne toujours False
        if self.force_login:
            logger.info(f"🔓 Force login activé - connexion requise pour {platform}")
            return False
            
        try:
            # Chercher les fichiers de cookies pour la plateforme
            pattern = f"{platform}_cookies_*.pkl"
            files = list(self.session_dir.glob(pattern))
            
            if not files:
                logger.info(f"ℹ️ Aucune session trouvée pour {platform}")
                return False

            # Prendre le fichier le plus récent
            latest_file = max(files, key=lambda x: x.stat().st_mtime)
            
            # Vérifier l'âge de la session (max 24h)
            file_age = datetime.now() - datetime.fromtimestamp(latest_file.stat().st_mtime)
            if file_age.total_seconds() > 24 * 3600:
                logger.info(f"ℹ️ Session expirée pour {platform} ({file_age})")
                return False

            with open(latest_file, 'rb') as f:
                cookies = pickle.load(f)

            # Naviguer d'abord sur le domaine
            if platform == 'facebook':
                driver.get("https://www.facebook.com")
            elif platform == 'instagram':
                driver.get("https://www.instagram.com")
            elif platform == 'whatsapp':
                driver.get("https://web.whatsapp.com")
            else:
                driver.get("https://www." + platform + ".com")
                
            self.random_delay(2, 3)

            # Ajouter chaque cookie
            added_count = 0
            for cookie in cookies:
                try:
                    # Nettoyer les clés non supportées
                    clean_cookie = {}
                    valid_keys = ['name', 'value', 'domain', 'path', 'expiry', 'secure', 'httpOnly']
                    for key in valid_keys:
                        if key in cookie:
                            clean_cookie[key] = cookie[key]
                    
                    driver.add_cookie(clean_cookie)
                    added_count += 1
                except Exception as e:
                    logger.debug(f"Cookie ignoré {cookie.get('name', 'unknown')}: {e}")

            logger.info(f"✅ {added_count} cookies chargés pour {platform}")
            return added_count > 0
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement cookies {platform}: {e}")
            return False

    def is_session_recent(self, platform: str, max_age_hours: int = 24) -> bool:
        """
        Vérifie si une session récente existe
        
        Args:
            platform (str): Nom de la plateforme
            max_age_hours (int): Âge maximum en heures
            
        Returns:
            bool: True si session récente existe
        """
        # Si force_login est activé, on retourne toujours False
        if self.force_login:
            return False
            
        files = list(self.session_dir.glob(f"{platform}_cookies_*.pkl"))
        if not files:
            return False
            
        latest = max(files, key=lambda x: x.stat().st_mtime)
        age_hours = (datetime.now() - datetime.fromtimestamp(latest.stat().st_mtime)).total_seconds() / 3600
        return age_hours < max_age_hours

    def clear_old_sessions(self, platform: str = None, max_age_hours: int = 48):
        """
        Supprime les sessions trop anciennes
        
        Args:
            platform (str): Plateforme spécifique ou None pour toutes
            max_age_hours (int): Âge maximum en heures
        """
        pattern = f"{platform}_cookies_*.pkl" if platform else "*_cookies_*.pkl"
        deleted_count = 0
        
        for file in self.session_dir.glob(pattern):
            age_hours = (datetime.now() - datetime.fromtimestamp(file.stat().st_mtime)).total_seconds() / 3600
            if age_hours > max_age_hours:
                try:
                    file.unlink()
                    deleted_count += 1
                    logger.info(f"🗑️ Session supprimée: {file.name}")
                except Exception as e:
                    logger.error(f"❌ Erreur suppression {file}: {e}")
        
        if deleted_count > 0:
            logger.info(f"✅ {deleted_count} sessions anciennes supprimées")

    def random_delay(self, min_seconds: float = 1, max_seconds: float = 3):
        """Pause aléatoire pour imiter le comportement humain"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

    def disable_force_login(self):
        """Désactive le mode force login"""
        self.force_login = False
        logger.info("🔓 Mode force login désactivé")

    def enable_force_login(self):
        """Active le mode force login et supprime les sessions existantes"""
        self.force_login = True
        self.clear_all_sessions()
        logger.info("🔓 Mode force login activé - toutes les sessions supprimées")

    def get_session_files(self, platform: str = None) -> List[Path]:
        """
        Récupère la liste des fichiers de session
        
        Args:
            platform (str): Plateforme spécifique ou None pour toutes
            
        Returns:
            List[Path]: Liste des fichiers de session
        """
        pattern = f"{platform}_cookies_*.pkl" if platform else "*_cookies_*.pkl"
        return list(self.session_dir.glob(pattern))

    def get_latest_session_file(self, platform: str) -> Optional[Path]:
        """
        Récupère le fichier de session le plus récent
        
        Args:
            platform (str): Nom de la plateforme
            
        Returns:
            Optional[Path]: Chemin du fichier ou None
        """
        files = self.get_session_files(platform)
        if not files:
            return None
        return max(files, key=lambda x: x.stat().st_mtime)

    def get_session_age_hours(self, platform: str) -> Optional[float]:
        """
        Récupère l'âge de la dernière session en heures
        
        Args:
            platform (str): Nom de la plateforme
            
        Returns:
            Optional[float]: Âge en heures ou None
        """
        latest = self.get_latest_session_file(platform)
        if not latest:
            return None
        age_seconds = (datetime.now() - datetime.fromtimestamp(latest.stat().st_mtime)).total_seconds()
        return age_seconds / 3600

    def clean_all_sessions(self):
        """Nettoie toutes les sessions (alias pour compatibilité)"""
        return self.clear_all_sessions()

    def __str__(self) -> str:
        """Représentation textuelle du gestionnaire de sessions"""
        session_files = self.get_session_files()
        count = len(session_files)
        
        if self.force_login:
            status = "🔓 FORCE LOGIN ACTIVÉ"
        else:
            status = "🔒 Sessions activées"
            
        platforms = {}
        for file in session_files:
            name = file.name
            # Extraire le nom de la plateforme
            if name.startswith("facebook"):
                platforms["facebook"] = platforms.get("facebook", 0) + 1
            elif name.startswith("instagram"):
                platforms["instagram"] = platforms.get("instagram", 0) + 1
            elif name.startswith("whatsapp"):
                platforms["whatsapp"] = platforms.get("whatsapp", 0) + 1
        
        platform_info = ", ".join([f"{k}: {v}" for k, v in platforms.items()])
        
        return f"SessionManager: {status}\nSessions totales: {count}\nPlateformes: {platform_info if platform_info else 'Aucune'}"


# Exemple d'utilisation
if __name__ == "__main__":
    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Création d'une instance avec force login activé (par défaut)
    session_manager = SessionManager(force_login=True)
    
    # Afficher l'état
    print(session_manager)
    
    # Pour désactiver le force login (si nécessaire)
    # session_manager.disable_force_login()
    
    # Pour réactiver le force login
    # session_manager.enable_force_login()
    
    # Exemple d'utilisation dans un script de connexion
    print("\nExemple d'utilisation dans un script de connexion:")
    print("1. Créer SessionManager avec force_login=True (défaut)")
    print("2. Appeler load_cookies() qui retournera toujours False")
    print("3. Exécuter la procédure de connexion manuelle")
    print("4. Sauvegarder les cookies avec save_cookies()")
    print("5. Les cookies seront supprimés à la prochaine exécution")