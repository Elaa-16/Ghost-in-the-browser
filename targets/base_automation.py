"""
BaseAutomation - Classe de base pour toutes les automatisations
Fournit les méthodes communes de gestion du navigateur, connexion, etc.
"""
from abc import ABC, abstractmethod
import time
import random
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from core.browser_manager import AdvancedBrowserManager
from core.session_manager import SessionManager


class BaseAutomation(ABC):
    def __init__(self, credentials, platform_name):
        """
        Initialise l'automatisation avec credentials et nom de plateforme
        
        Args:
            credentials (dict): Identifiants pour la plateforme
            platform_name (str): Nom de la plateforme (facebook, whatsapp, etc.)
        """
        self.credentials = credentials
        self.platform_name = platform_name
        self.browser = None
        self.session_manager = SessionManager(session_dir=f"data/sessions/{platform_name}")
        self.is_logged_in = False
        
        # Configuration par défaut
        self.config = {
            'login_url': '',
            'timeouts': {
                'page_load': 30,
                'element': 20,  # Augmenté pour plus de tolérance
                'between_actions': (1.5, 4.5)  # Délais plus réalistes
            },
            'selectors': {}
        }

    def initialize_browser(self, headless=False):
        """Initialise le navigateur avec undetected-chromedriver"""
        try:
            print(f"🌐 Initialisation du navigateur pour {self.platform_name}...")
            
            # Utiliser un profil utilisateur pour chaque plateforme
            user_data_dir = f"data/profiles/{self.platform_name}"
            Path(user_data_dir).mkdir(parents=True, exist_ok=True)
            
            self.browser = AdvancedBrowserManager(
                headless=headless,
                user_data_dir=user_data_dir
            )
            
            return self.browser
            
        except Exception as e:
            print(f"❌ Erreur d'initialisation du navigateur: {e}")
            raise

    def random_delay(self, min_seconds=1.0, max_seconds=3.5):
        """Délai aléatoire pour simuler le comportement humain"""
        return self.browser.random_delay(min_seconds, max_seconds)

    def humanize_page(self):
        """Rendre la page plus humaine avant interaction"""
        self.browser.humanize_page()

    def take_screenshot(self, name):
        """Capture d'écran pour débogage"""
        return self.browser.take_screenshot(name, self.platform_name)

    def safe_click(self, element, description="élément", retries=3):
        """Clique humain avec mouvements réalistes"""
        return self.browser.safe_click(element, description, retries)

    def safe_send_keys(self, element, text, description="champ", retries=2):
        """Envoi de texte avec frappe humaine réaliste"""
        return self.browser.safe_send_keys(element, text, description, retries)

    def wait_for_element(self, selector, by=By.CSS_SELECTOR, timeout=20, multiple=False):
        """Attend un élément avec timeout et gestion d'erreur améliorée"""
        return self.browser.wait_for_element(selector, by, timeout, multiple)

    def wait_for_element_visible(self, selector, by=By.CSS_SELECTOR, timeout=15):
        """Attend qu'un élément soit visible"""
        return self.browser.wait_for_element_visible(selector, by, timeout)

    def handle_captcha(self):
        """Gestion des CAPTCHA - méthode simplifiée"""
        try:
            print("🔍 Vérification de CAPTCHA...")
            captcha_selectors = [
                'img[src*="captcha"]',
                'div.g-recaptcha',
                'iframe[src*="recaptcha"]',
                'div[class*="captcha"]'
            ]
            
            for selector in captcha_selectors:
                elements = self.browser.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"⚠️ CAPTCHA détecté: {selector}")
                    print("⏳ Pause pour résolution manuelle (20s)...")
                    time.sleep(20)
                    break
            
            return True
        except Exception as e:
            print(f"⚠️ Erreur gestion CAPTCHA: {e}")
            return True  # Continuer même en cas d'erreur

    def save_session(self):
        """Sauvegarde la session (cookies) pour réutilisation"""
        if self.browser and self.browser.driver:
            try:
                return self.session_manager.save_cookies(self.platform_name, self.browser.driver)
            except Exception as e:
                print(f"⚠️ Erreur sauvegarde session: {e}")
                return False
        return False

    def load_session(self):
        """Charge une session précédemment sauvegardée"""
        if self.browser and self.browser.driver:
            try:
                # WhatsApp ne peut pas charger de session
                if self.platform_name == 'whatsapp':
                    return False
                
                # Vérifier si une session récente existe
                if not self.session_manager.is_session_recent(self.platform_name):
                    return False
                
                # Charger les cookies via SessionManager
                if self.session_manager.load_cookies(self.platform_name, self.browser.driver):
                    # Humaniser avant rafraîchissement
                    self.humanize_page()
                    
                    # Rafraîchir pour appliquer les cookies
                    self.browser.driver.refresh()
                    self.random_delay(4, 7)
                    
                    # Vérifier si toujours connecté
                    if self._check_login_state():
                        self.is_logged_in = True
                        print(f"✅ Session chargée pour {self.platform_name}")
                        return True
                return False
            except Exception as e:
                print(f"⚠️ Erreur chargement session: {e}")
                return False
        return False

    def smart_wait(self, min_seconds=2, max_seconds=5):
        """Attente intelligente avec humanisation aléatoire"""
        return self.browser.smart_wait(min_seconds, max_seconds)

    @abstractmethod
    def _check_login_state(self):
        """À implémenter: vérifie si l'utilisateur est connecté"""
        pass

    @abstractmethod
    def login(self):
        """À implémenter: processus de connexion spécifique"""
        pass

    @abstractmethod
    def perform_action(self):
        """À implémenter: action principale à effectuer"""
        pass

    def run(self):
        """Exécute le processus complet d'automatisation"""
        print(f"\n{'='*60}")
        print(f"🚀 Démarrage {self.platform_name.upper()}")
        print(f"{'='*60}")
        
        try:
            # 1. Initialiser le navigateur
            self.initialize_browser(headless=False)
            
            # 2. Essayer de charger une session existante
            if self.load_session():
                print(f"✅ Session chargée pour {self.platform_name}")
            else:
                # 3. Se connecter
                print(f"🔑 Connexion à {self.platform_name}...")
                if not self.login():
                    print(f"❌ Échec connexion {self.platform_name}")
                    self.take_screenshot('login_failed')
                    return False
            
            # 4. Effectuer l'action principale
            print(f"⚡ Exécution de l'action sur {self.platform_name}...")
            if not self.perform_action():
                print(f"❌ Échec action {self.platform_name}")
                self.take_screenshot('action_failed')
                return False
            
            # 5. Sauvegarder la session (sauf WhatsApp)
            if self.platform_name != 'whatsapp':
                self.save_session()
            
            print(f"✅ {self.platform_name.upper()} - Succès!")
            return True
            
        except Exception as e:
            print(f"❌ Erreur critique {self.platform_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            self.take_screenshot('critical_error')
            return False
        
        finally:
            # 6. Fermer proprement le navigateur
            if self.browser and self.browser.driver:
                try:
                    self.random_delay(2, 4)
                    self.browser.quit()
                except Exception as e:
                    print(f"⚠️ Erreur fermeture navigateur: {e}")