"""
BrowserManager - Gestionnaire avancé du navigateur Chrome
Utilise undetected-chromedriver pour éviter la détection
"""
import time
import random
import os
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pathlib import Path

class AdvancedBrowserManager:
    def __init__(self, headless=False, user_data_dir=None):
        """
        Initialise le navigateur avec undetected-chromedriver
        
        Args:
            headless (bool): Mode sans affichage
            user_data_dir (str): Répertoire du profil utilisateur
        """
        self.headless = headless
        self.user_data_dir = user_data_dir
        self.driver = None
        self._init_driver()
    
    def _init_driver(self):
        """Initialise undetected-chromedriver avec compatibilité"""
        try:
            import undetected_chromedriver as uc
            print("🚀 Initialisation de Chrome avec undetected-chromedriver...")
            
            # Options de base
            options = uc.ChromeOptions()
            
            # Arguments standard pour éviter la détection
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-setuid-sandbox")
            
            # User-agent réaliste
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            ]
            selected_ua = random.choice(user_agents)
            options.add_argument(f'user-agent={selected_ua}')
            
            # Arguments pour la performance et discrétion
            options.add_argument("--disable-blink-features")
            options.add_argument("--disable-features=IsolateOrigins,site-per-process")
            options.add_argument("--disable-logging")
            options.add_argument("--log-level=3")
            options.add_argument("--silent")
            
            # Éviter les notifications
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-popup-blocking")
            
            # Mode headless
            if self.headless:
                options.add_argument("--headless=new")
                options.add_argument("--window-size=1920,1080")
            else:
                options.add_argument("--start-maximized")
            
            # Profil utilisateur (pour les cookies)
            if self.user_data_dir:
                try:
                    os.makedirs(self.user_data_dir, exist_ok=True)
                    options.add_argument(f"--user-data-dir={os.path.abspath(self.user_data_dir)}")
                    print(f"📁 Utilisation du profil: {self.user_data_dir}")
                except Exception as e:
                    print(f"⚠️ Erreur création profil: {e}")
            
            # Désactiver certaines fonctionnalités qui peuvent révéler l'automatisation
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-running-insecure-content")
            
            print(f"🔧 Configuration Chrome prête (UA: {selected_ua[:50]}...)")
            
            try:
                self.driver = uc.Chrome(
                    options=options,
                    use_subprocess=True,
                    driver_executable_path=None  
                )
                
                print("✅ Navigateur Chrome initialisé avec succès")
                
                # Masquer WebDriver via JavaScript
                self._hide_automation_traces()
                
                return self.driver
                
            except Exception as e:
                print(f"❌ Erreur création driver: {e}")
                # Fallback: essayer sans options spécifiques
                print("🔄 Tentative avec configuration minimale...")
                self.driver = uc.Chrome()
                self._hide_automation_traces()
                return self.driver
                
        except Exception as e:
            print(f"❌ Erreur initialisation Chrome: {e}")
            return self._fallback_to_selenium()
    
    def _hide_automation_traces(self):
        """Cache les traces d'automatisation dans le navigateur"""
        if not self.driver:
            return
            
        # Masquer WebDriver via JavaScript
        self.driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Surcharger les propriétés
            window.navigator.chrome = {
                runtime: {},
            };
            
            // Surcharger le language
            Object.defineProperty(navigator, 'language', {
                get: () => 'fr-FR'
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['fr-FR', 'fr', 'en-US', 'en']
            });
        """)
        
        # Cacher les traces via CDP
        try:
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => false
                    });
                '''
            })
        except:
            pass
    
    def _fallback_to_selenium(self):
        """Fallback vers Selenium standard si undetected-chromedriver échoue"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            
            print("🔄 Fallback: Selenium standard...")
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            
            # Masquer WebDriver
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("✅ Navigateur Selenium standard initialisé")
            return self.driver
            
        except Exception as fallback_error:
            print(f"❌ Erreur fallback: {fallback_error}")
            raise
    
    def human_like_get(self, url):
        """Charge une URL de manière humaine"""
        print(f"🌐 Chargement humain: {url}")
        
        # Petit délai avant chargement
        self.random_delay(1.0, 2.5)
        
        # Charger l'URL
        self.driver.get(url)
        
        # Attendre après chargement
        self.random_delay(2.0, 4.0)
        
        # Scroll aléatoire
        self.human_scroll()
    
    def human_scroll(self, min_scrolls=1, max_scrolls=3):
        """Scroll humain avec paramètres configurables"""
        scrolls = random.randint(min_scrolls, max_scrolls)
        for i in range(scrolls):
            distance = random.randint(200, 800)
            direction = 1 if random.random() > 0.5 else -1
            self.driver.execute_script(f"window.scrollBy(0, {distance * direction});")
            self.random_delay(0.5, 1.5)
    
    def human_mouse_move(self, element=None):
        """Mouvement de souris humain vers un élément ou position aléatoire"""
        try:
            if element:
                # Déplacer vers l'élément
                actions = ActionChains(self.driver)
                actions.move_to_element(element)
                actions.perform()
                self.random_delay(0.3, 0.8)
            else:
                # Mouvement aléatoire
                width = self.driver.execute_script("return window.innerWidth")
                height = self.driver.execute_script("return window.innerHeight")
                
                for _ in range(random.randint(1, 2)):
                    x = random.randint(10, width - 10)
                    y = random.randint(10, height - 10)
                    actions = ActionChains(self.driver)
                    actions.move_by_offset(x, y).perform()
                    self.random_delay(0.1, 0.3)
                    
        except Exception as e:
            print(f"⚠️ Erreur mouvement souris: {e}")
    
    def human_click(self, element):
        """Clic humain sur un élément"""
        try:
            # Mouvement vers l'élément
            self.human_mouse_move(element)
            self.random_delay(0.2, 0.5)
            
            # Cliquer
            element.click()
            return True
        except Exception as e:
            print(f"⚠️ Erreur clic humain: {e}")
            return False
    
    def safe_click(self, element, description="élément", retries=3):
        """Clique humain avec mouvements réalistes et retry"""
        for attempt in range(retries):
            try:
                # Scroll pour rendre l'élément visible
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                self.random_delay(0.3, 0.8)
                
                # Petit mouvement aléatoire avant clic
                actions = ActionChains(self.driver)
                offset_x = random.randint(-5, 5)
                offset_y = random.randint(-5, 5)
                
                # Approche progressive
                actions.move_to_element(element)
                actions.move_by_offset(offset_x, offset_y)
                actions.pause(random.uniform(0.1, 0.4))
                actions.click()
                actions.perform()
                
                print(f"✅ Clic humain sur {description}")
                self.random_delay(0.8, 2.0)
                return True
                
            except Exception as e:
                print(f"⚠️ Erreur clic sur {description} (tentative {attempt+1}/{retries}): {e}")
                if attempt < retries - 1:
                    self.random_delay(1.5, 3.0)
        return False
    
    def safe_send_keys(self, element, text, description="champ", retries=2):
        """Envoi de texte avec frappe humaine réaliste"""
        for attempt in range(retries):
            try:
                # Cliquer humainement sur l'élément
                actions = ActionChains(self.driver)
                actions.move_to_element(element)
                actions.click()
                actions.perform()
                self.random_delay(0.3, 0.7)
                
                # Effacer avec des backspaces occasionnels
                element.clear()
                self.random_delay(0.2, 0.5)
                
                # Frappe humaine avec variations
                for i, char in enumerate(text):
                    element.send_keys(char)
                    
                    # Variation de vitesse
                    if i % random.randint(3, 8) == 0:
                        time.sleep(random.uniform(0.12, 0.25))
                    elif random.random() < 0.05:
                        time.sleep(random.uniform(0.02, 0.06))
                    else:
                        time.sleep(random.uniform(0.06, 0.15))
                    
                    # Faute de frappe occasionnelle (rare)
                    if random.random() < 0.015:  # 1.5% de chance
                        element.send_keys(Keys.BACK_SPACE)
                        time.sleep(random.uniform(0.15, 0.3))
                        element.send_keys(char)
                        time.sleep(random.uniform(0.1, 0.2))
                
                print(f"✅ Texte saisi humainement dans {description}")
                return True
                
            except Exception as e:
                print(f"⚠️ Erreur saisie dans {description} (tentative {attempt+1}/{retries}): {e}")
                if attempt < retries - 1:
                    self.random_delay(2.0, 4.0)
        return False
    
    def wait_for_element(self, selector, by=By.CSS_SELECTOR, timeout=20, multiple=False):
        """Attend un élément avec timeout et gestion d'erreur améliorée"""
        try:
            if multiple:
                elements = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_all_elements_located((by, selector))
                )
                return elements if elements else []
            else:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((by, selector))
                )
                return element
        except Exception as e:
            print(f"⏳ Timeout sur l'élément: {selector}")
            return [] if multiple else None
    
    def wait_for_element_visible(self, selector, by=By.CSS_SELECTOR, timeout=15):
        """Attend qu'un élément soit visible"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, selector))
            )
            return element
        except Exception as e:
            print(f"⏳ Élément non visible: {selector}")
            return None
    
    def take_screenshot(self, name, platform_name=""):
        """Capture d'écran pour débogage"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        screenshot_dir = Path('data/screenshots')
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        if platform_name:
            filename = screenshot_dir / f'{platform_name}_{name}_{timestamp}.png'
        else:
            filename = screenshot_dir / f'{name}_{timestamp}.png'
        
        try:
            self.driver.save_screenshot(str(filename))
            print(f"📸 Capture sauvegardée: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Erreur capture d'écran: {e}")
            return None
    
    def random_delay(self, min_seconds=1, max_seconds=3):
        """Délai aléatoire pour simuler le comportement humain"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
        return delay
    
    def humanize_page(self):
        """Rendre la page plus humaine avant interaction"""
        try:
            # Scroll aléatoire
            if random.random() > 0.3:  # 70% de chance de scroller
                self.human_scroll(1, 2)
                self.random_delay(0.8, 1.8)
            
            # Mouvement de souris aléatoire
            if random.random() > 0.4:  # 60% de chance de bouger la souris
                self.human_mouse_move()
            
            # Simuler des frappes de touches aléatoires (très occasionnel)
            if random.random() > 0.8:  # 20% de chance
                actions = ActionChains(self.driver)
                actions.send_keys(Keys.TAB).pause(random.uniform(0.2, 0.5))
                actions.send_keys(Keys.TAB).pause(random.uniform(0.2, 0.5))
                actions.perform()
                
        except Exception as e:
            print(f"⚠️ Erreur humanisation: {e}")
    
    def smart_wait(self, min_seconds=2, max_seconds=5):
        """Attente intelligente avec humanisation aléatoire"""
        wait_time = random.uniform(min_seconds, max_seconds)
        
        # Pendant l'attente, faire occasionnellement des actions humaines
        if random.random() > 0.6:  # 40% de chance
            interval = wait_time / random.randint(2, 4)
            for i in range(random.randint(1, 3)):
                time.sleep(interval)
                if i % 2 == 0:
                    try:
                        # Petit scroll aléatoire
                        scroll = random.randint(50, 200)
                        self.driver.execute_script(f"window.scrollBy(0, {scroll});")
                    except:
                        pass
        else:
            time.sleep(wait_time)
        
        return wait_time
    
    def quit(self):
        """Ferme le navigateur"""
        if self.driver:
            try:
                self.driver.quit()
                print("✅ Navigateur fermé")
            except Exception as e:
                print(f"⚠️ Erreur fermeture navigateur: {e}")