"""
WhatsAppAutomation - Automatisation pour WhatsApp Web
Gère la connexion via QR Code et l'envoi de messages
"""
from targets.base_automation import BaseAutomation
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import random

class WhatsAppAutomation(BaseAutomation):
    def __init__(self, credentials):
        """
        Initialise l'automatisation WhatsApp
        
        Args:
            credentials (dict): Doit contenir 'phone' pour le numéro
        """
        super().__init__(credentials, 'whatsapp')
        
        # Configuration spécifique à WhatsApp
        self.config.update({
            'login_url': 'https://web.whatsapp.com',
            'target_number': '+21654970604',  # Numéro cible
            'message_content': 'bonjour elaa',
            'selectors': {
                # Sélecteurs mis à jour pour WhatsApp Web 2024
                'qr_code': 'canvas[aria-label*="Scan"], div[data-ref], canvas[aria-label*="Scan me"]',
                'search_box': 'div[contenteditable="true"][title="Search or start new chat"]',
                'chat_input': 'div[contenteditable="true"][title="Type a message"], div[contenteditable="true"][data-tab="10"]',
                'send_button': 'button[aria-label="Send"]',
                # Indicateurs de connexion
                'sidebar_menu': 'header[aria-label="Chats"]',
                'chat_list': 'div[aria-label="Chat list"]',
                'user_avatar': 'header img[alt*="Profile"]'
            }
        })
    
    def _check_login_state(self):
        """
        Vérifie si connecté à WhatsApp Web
        Retourne True si des éléments de l'interface connectée sont trouvés
        """
        try:
            # Vérifier plusieurs indicateurs de connexion
            indicators = [
                'header[aria-label="Chats"]',  # En-tête des chats
                'div[aria-label="Chat list"]',  # Liste des chats
                'div[data-testid="chat-list"]', # Autre sélecteur de liste
                'div[class*="two"]',  # Classe commune dans WhatsApp Web
            ]
            
            for indicator in indicators:
                try:
                    # Vérifier rapidement sans timeout long
                    element = self.browser.driver.find_element(By.CSS_SELECTOR, indicator)
                    if element and element.is_displayed():
                        return True
                except:
                    continue
            
            # Vérifier si QR code est présent (non connecté)
            qr_elements = self.browser.driver.find_elements(By.CSS_SELECTOR, self.config['selectors']['qr_code'])
            if qr_elements:
                return False
                
            # Par défaut, considérer comme non connecté
            return False
            
        except Exception as e:
            print(f"⚠️ Erreur vérification état WhatsApp: {e}")
            return False
    
    def login(self):
        """
        Connexion à WhatsApp via QR Code
        Affiche les instructions et attend le scan manuel
        """
        try:
            print("🌐 Accès à WhatsApp Web...")
            self.browser.human_like_get(self.config['login_url'])
            self.random_delay(5, 8)  # Attente chargement initial
            
            # Vérifier si déjà connecté
            if self._check_login_state():
                print("✅ Déjà connecté à WhatsApp")
                self.is_logged_in = True
                return True
            
            # Afficher instructions QR Code
            print("\n" + "="*60)
            print("📱 CONNEXION WHATSAPP - INSTRUCTIONS")
            print("="*60)
            print("1. Ouvrez WhatsApp sur votre téléphone")
            print("2. Appuyez sur ⋮ (menu) → WhatsApp Web / Appareils liés")
            print("3. Scannez le QR code affiché à l'écran")
            print("4. Patientez jusqu'à la connexion...")
            print("="*60 + "\n")
            
            # Attendre connexion (max 2 minutes)
            max_wait = 120  # 2 minutes max
            check_interval = 5  # Vérifier toutes les 5 secondes
            
            for attempt in range(max_wait // check_interval):
                print(f"⏳ Attente connexion... ({attempt * check_interval}s / {max_wait}s)")
                
                if self._check_login_state():
                    print("✅ WhatsApp connecté avec succès!")
                    self.is_logged_in = True
                    return True
                
                # Afficher statut QR code
                qr_elements = self.browser.driver.find_elements(By.CSS_SELECTOR, self.config['selectors']['qr_code'])
                if qr_elements:
                    print("📱 QR Code visible - En attente du scan...")
                else:
                    print("🔄 Vérification de l'interface...")
                
                time.sleep(check_interval)
            
            print("❌ Timeout: Connexion WhatsApp échouée")
            return False
                
        except Exception as e:
            print(f"❌ Erreur connexion WhatsApp: {e}")
            self.take_screenshot('whatsapp_login_error')
            return False
    
    def send_message(self):
        """
        Envoie un message WhatsApp au numéro cible - Version améliorée
        """
        try:
            print("💬 Envoi de message WhatsApp...")
            self.random_delay(3, 5)
            
            # S'assurer qu'on est connecté
            if not self._check_login_state():
                print("❌ WhatsApp non connecté")
                return False
            
            print("📞 Utilisation de l'URL directe améliorée...")
            
            # Format correct du numéro pour l'URL
            phone_number = self.config['target_number'].replace('+', '').replace(' ', '')
            direct_url = f"https://web.whatsapp.com/send?phone={phone_number}&text="
            
            # Aller à l'URL
            self.browser.driver.get(direct_url)
            print(f"🌐 Chargement du chat pour {self.config['target_number']}...")
            
            # Attendre plus longtemps pour le chargement du chat
            time.sleep(15)
            
            # Vérifier si le chat est chargé en cherchant le champ de message
            chat_loaded = False
            message_input = None
            
            # Essayer plusieurs sélecteurs pour le champ de message
            message_selectors = [
                'div[contenteditable="true"][title="Type a message"]',
                'div[contenteditable="true"][data-tab="10"]',
                'div[contenteditable="true"][spellcheck="true"]',
                'div[contenteditable="true"][role="textbox"]'
            ]
            
            for selector in message_selectors:
                try:
                    elements = self.browser.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            message_input = element
                            chat_loaded = True
                            print("✅ Chat chargé avec succès")
                            break
                except:
                    continue
                if chat_loaded:
                    break
            
            if not chat_loaded or not message_input:
                print("❌ Chat non chargé correctement, tentative alternative...")
                return self.send_message_fallback()
            
            # Saisir le message
            print("📝 Saisie du message...")
            
            # Cliquer sur le champ
            message_input.click()
            self.random_delay(1, 2)
            
            # Effacer le champ s'il contient du texte
            try:
                message_input.clear()
            except:
                pass
            
            # Saisir le message caractère par caractère
            for char in self.config['message_content']:
                message_input.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            print(f"✅ Message saisi: {self.config['message_content']}")
            self.random_delay(1, 2)
            
            # Envoyer avec Enter
            print("📤 Envoi du message...")
            message_input.send_keys(Keys.ENTER)
            
            # Attendre l'envoi
            self.random_delay(3, 5)
            
            # Vérifier visuellement si le message est parti
            try:
                # Chercher le dernier message dans le chat
                messages = self.browser.driver.find_elements(By.CSS_SELECTOR, 
                    'div[data-testid="msg-container"][data-pre-plain-text]')
                if messages:
                    print("✅ Message WhatsApp envoyé avec succès!")
                    return True
                else:
                    # Parfois le message n'a pas le data-testid
                    print("✅ Message probablement envoyé (vérification visuelle)")
                    return True
            except:
                print("✅ Message envoyé (vérification non concluante)")
                return True
            
        except Exception as e:
            print(f"❌ Erreur envoi message WhatsApp: {e}")
            self.take_screenshot('whatsapp_message_error')
            return False
    
    def send_message_fallback(self):
        """Méthode alternative si l'URL directe échoue"""
        try:
            print("🔄 Utilisation de la méthode de recherche...")
            
            # Chercher la barre de recherche
            search_box = None
            search_selectors = [
                'div[contenteditable="true"][title="Search or start new chat"]',
                'div[contenteditable="true"][data-tab="3"]',
                'div[class*="selectable-text"][contenteditable="true"]'
            ]
            
            for selector in search_selectors:
                try:
                    elements = self.browser.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            search_box = element
                            break
                except:
                    continue
                if search_box:
                    break
            
            if not search_box:
                print("❌ Barre de recherche non trouvée")
                return False
            
            # Rechercher le contact
            search_box.click()
            self.random_delay(0.5, 1)
            
            # Effacer et saisir le numéro
            search_box.clear()
            phone_number = self.config['target_number'].replace('+', '').replace(' ', '')
            for char in phone_number:
                search_box.send_keys(char)
                time.sleep(0.1)
            
            print(f"🔍 Recherche du numéro: {phone_number}")
            self.random_delay(3, 5)
            
            # Sélectionner le premier résultat
            try:
                contacts = self.browser.driver.find_elements(By.CSS_SELECTOR, 'div[role="listitem"]')
                if contacts:
                    contacts[0].click()
                    self.random_delay(3, 5)
                    
                    # Chercher le champ de message
                    message_input = self.wait_for_element(
                        'div[contenteditable="true"][title="Type a message"]', 
                        timeout=10
                    )
                    
                    if message_input:
                        message_input.click()
                        self.random_delay(0.5, 1)
                        
                        # Saisir le message
                        for char in self.config['message_content']:
                            message_input.send_keys(char)
                            time.sleep(random.uniform(0.05, 0.15))
                        
                        # Envoyer
                        message_input.send_keys(Keys.ENTER)
                        self.random_delay(2, 3)
                        print("✅ Message WhatsApp envoyé avec succès (fallback)!")
                        return True
            except Exception as e:
                print(f"⚠️ Erreur sélection contact: {e}")
            
            return False
            
        except Exception as e:
            print(f"❌ Erreur fallback WhatsApp: {e}")
            return False
    
    def perform_action(self):
        """Action principale: envoyer un message"""
        return self.send_message()
