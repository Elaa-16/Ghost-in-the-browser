"""
FacebookAutomation - Automatisation pour Facebook
Gère la connexion et l'envoi de messages via la recherche
"""
from targets.base_automation import BaseAutomation
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import random

class FacebookAutomation(BaseAutomation):
    def __init__(self, credentials):
        """
        Initialise l'automatisation Facebook
        
        Args:
            credentials (dict): Doit contenir 'email' et 'password'
        """
        super().__init__(credentials, 'facebook')
        
        # Configuration Facebook
        self.config.update({
            'login_url': 'https://www.facebook.com',
            'search_name': 'Doaa Chatbri',  # Nom à rechercher
            'message_content': 'Cutiee',
            'use_messenger_direct': True,  # Nouvelle option pour utiliser Messenger directement
            'max_search_attempts': 3,  # Nombre max de tentatives de recherche
            'selectors': {
                # Sélecteurs de connexion
                'email': 'input[name="email"]',
                'password': 'input[name="pass"]',
                'login_button': 'button[name="login"]',
                'login_button_alt': 'button[type="submit"]',
                # Sélecteurs pour la recherche et envoi de message
                'search_box': 'input[placeholder*="Rechercher"], input[placeholder*="Search"]',
                'search_result': 'div[role="listbox"] a[role="presentation"]',
                'profile_message_button': 'div[aria-label="Message"], div[aria-label="Envoyer un message"], span:contains("Message"), a[href*="/messages/"]',
                'message_input': 'div[contenteditable="true"][role="textbox"], div[contenteditable="true"][data-lexical-editor="true"], div[spellcheck="true"][contenteditable="true"]',
                'message_input_alt': 'div[aria-label*="Message"], div[aria-label*="Écrire un message"]',
                'send_button': 'div[aria-label*="Envoyer"][role="button"], div[aria-label*="Send"][role="button"]',
                # Nouveaux sélecteurs pour recherche améliorée
                'messenger_new_message': 'a[href="/messages/compose/"]',
                'messenger_recipient': 'input[placeholder*="Rechercher des personnes"], input[placeholder*="Search for people"]',
                'messenger_first_result': 'div[role="listbox"] div[role="option"]:first-child',
                'profile_alternative_links': 'a[role="link"][href*="facebook.com"]',
            }
        })
    
    def _check_login_state(self):
        """
        Vérifie si connecté à Facebook
        Vérifie plusieurs indicateurs de connexion
        """
        try:
            current_url = self.browser.driver.current_url.lower()
            if 'facebook.com/home' in current_url or '/feed/' in current_url or 'facebook.com/?sk=welcome' in current_url:
                return True
            
            logged_in_indicators = [
                'a[aria-label="Facebook"] svg',
                'div[aria-label="Créer une publication"]',
                'div[aria-label="Create a post"]',
                'a[href*="/me/"]',
                'div[data-pagelet="LeftRail"]'
            ]
            
            for indicator in logged_in_indicators:
                try:
                    element = self.browser.driver.find_element(By.CSS_SELECTOR, indicator)
                    if element.is_displayed():
                        return True
                except:
                    continue
                    
            return False
            
        except Exception as e:
            print(f"⚠️ Erreur vérification état Facebook: {e}")
            return False
    
    def login(self):
        """
        Connexion automatique à Facebook
        Gère les CAPTCHA et la vérification
        """
        try:
            print("🌐 Connexion à Facebook...")
            self.browser.human_like_get(self.config['login_url'])
            self.random_delay(3, 5)
            
            if self._check_login_state():
                print("✅ Déjà connecté à Facebook")
                self.is_logged_in = True
                return True
            
            self.handle_captcha()
            
            print("📝 Saisie de l'email...")
            email_field = self.wait_for_element(self.config['selectors']['email'], timeout=10)
            if email_field:
                self.safe_send_keys(email_field, self.credentials['email'], "email Facebook")
            else:
                print("❌ Champ email non trouvé")
                return False
            
            self.random_delay(1, 2)
            
            print("🔑 Saisie du mot de passe...")
            password_field = self.wait_for_element(self.config['selectors']['password'], timeout=10)
            if password_field:
                self.safe_send_keys(password_field, self.credentials['password'], "mot de passe Facebook")
            else:
                print("❌ Champ mot de passe non trouvé")
                return False
            
            self.random_delay(1, 2)
            
            print("🔐 Connexion...")
            login_button = self.wait_for_element(self.config['selectors']['login_button'], timeout=10)
            if not login_button:
                login_button = self.wait_for_element(self.config['selectors']['login_button_alt'], timeout=5)
            
            if login_button:
                self.safe_click(login_button, "bouton de connexion")
            else:
                print("❌ Bouton connexion non trouvé")
                return False
            
            self.random_delay(5, 8)
            
            if self._check_login_state():
                print("✅ Connexion Facebook réussie")
                self.is_logged_in = True
                return True
            else:
                print("⚠️ Connexion non confirmée, vérification manuelle...")
                self.random_delay(5, 10)
                if self._check_login_state():
                    print("✅ Connexion Facebook réussie (retardée)")
                    self.is_logged_in = True
                    return True
                else:
                    print("❌ Échec de connexion Facebook")
                    return False
                
        except Exception as e:
            print(f"❌ Erreur connexion Facebook: {e}")
            self.take_screenshot('facebook_login_error')
            return False
    
    def _search_profile_improved(self):
        """
        Méthode améliorée pour rechercher un profil
        Retourne l'élément du profil ou None si non trouvé
        """
        print("🔍 Recherche améliorée du profil...")
        
        # Essayer différentes formulations du nom
        search_variations = [
            self.config['search_name'],
            self.config['search_name'].split()[0] if ' ' in self.config['search_name'] else self.config['search_name'],
            self.config['search_name'].replace(' ', ''),
            f"{self.config['search_name']} facebook"
        ]
        
        for search_term in search_variations:
            if not search_term:
                continue
                
            print(f"🔎 Tentative avec: '{search_term}'")
            
            try:
                # Trouver la barre de recherche
                search_box = self.wait_for_element(self.config['selectors']['search_box'], timeout=10)
                if not search_box:
                    print("❌ Barre de recherche non trouvée")
                    continue
                
                # Saisir le terme de recherche
                self.safe_click(search_box, "barre de recherche")
                self.random_delay(0.5, 1)
                search_box.clear()
                
                # Saisir caractère par caractère pour être plus naturel
                for char in search_term:
                    search_box.send_keys(char)
                    time.sleep(random.uniform(0.03, 0.08))
                
                self.random_delay(2, 3)  # Attendre les suggestions
                
                # Vérifier si des résultats apparaissent
                result_selectors = [
                    'div[role="listbox"]',
                    'ul[role="listbox"]',
                    'div[data-visualcompletion="ignore-dynamic"]'
                ]
                
                results_container = None
                for selector in result_selectors:
                    try:
                        container = self.browser.driver.find_element(By.CSS_SELECTOR, selector)
                        if container.is_displayed():
                            results_container = container
                            break
                    except:
                        continue
                
                if results_container:
                    print("✅ Suggestions de recherche trouvées")
                    
                    # Essayer différents sélecteurs pour les profils
                    profile_selectors = [
                        'a[role="link"][href*="facebook.com"]',
                        'div[role="option"] a',
                        'div[data-visualcompletion="ignore-dynamic"] a',
                        'div[role="presentation"] a'
                    ]
                    
                    for selector in profile_selectors:
                        try:
                            profiles = results_container.find_elements(By.CSS_SELECTOR, selector)
                            for profile in profiles:
                                try:
                                    # Vérifier le texte ou l'URL
                                    text = profile.text.strip().lower()
                                    href = profile.get_attribute('href', '').lower()
                                    
                                    # Critères de correspondance
                                    search_lower = self.config['search_name'].lower()
                                    name_parts = [part.lower() for part in self.config['search_name'].split()]
                                    
                                    match_found = False
                                    
                                    # Vérifier différentes conditions de correspondance
                                    if search_lower in text or any(part in text for part in name_parts):
                                        match_found = True
                                    elif '/profile.php' in href or '/user/' in href:
                                        # Pour les profils sans nom visible
                                        match_found = True
                                    elif text and len(text) > 2:  # Un nom valide
                                        # Correspondance partielle
                                        for part in name_parts:
                                            if part and part in text:
                                                match_found = True
                                                break
                                    
                                    if match_found:
                                        print(f"✅ Profil potentiel trouvé: '{text[:50]}...'")
                                        return profile
                                    
                                except:
                                    continue
                        except:
                            continue
                
                # Si pas de résultats dans les suggestions, appuyer sur Entrée
                print("↩️ Appui sur Entrée pour recherche complète...")
                search_box.send_keys(Keys.ENTER)
                self.random_delay(3, 5)
                
                # Rechercher dans les résultats de page
                page_profile_selectors = [
                    'div[data-pagelet="SearchResults"] a[role="link"]',
                    'div[role="main"] a[href*="facebook.com"]',
                    'div[data-visualcompletion="ignore"] a'
                ]
                
                for selector in page_profile_selectors:
                    try:
                        profiles = self.browser.driver.find_elements(By.CSS_SELECTOR, selector)
                        for profile in profiles:
                            try:
                                text = profile.text.strip().lower()
                                if text and any(part in text for part in [p.lower() for p in self.config['search_name'].split()]):
                                    print(f"✅ Profil trouvé dans page: '{text[:50]}...'")
                                    return profile
                            except:
                                continue
                    except:
                        continue
                        
                print(f"❌ Aucun profil trouvé avec '{search_term}'")
                self.random_delay(1, 2)
                
            except Exception as e:
                print(f"⚠️ Erreur recherche avec '{search_term}': {e}")
                continue
        
        print("❌ Profil non trouvé après toutes les tentatives")
        return None
    
    def _use_messenger_directly(self):
        """
        Utiliser Messenger directement pour envoyer un message
        """
        print("💬 Utilisation de Messenger directement...")
        
        try:
            # Aller sur Messenger
            messenger_url = "https://www.facebook.com/messages"
            self.browser.human_like_get(messenger_url)
            self.random_delay(4, 6)
            
            # Chercher le bouton "Nouveau message"
            new_message_selectors = [
                'a[href="/messages/compose/"]',
                'a[aria-label*="Nouveau message"]',
                'a[aria-label*="New message"]',
                'div[aria-label*="Nouveau message"]',
                'div[aria-label*="New message"]',
                'div[role="button"][aria-label*="Message"]'
            ]
            
            new_message_btn = None
            for selector in new_message_selectors:
                try:
                    element = self.wait_for_element(selector, timeout=5)
                    if element:
                        new_message_btn = element
                        break
                except:
                    continue
            
            if not new_message_btn:
                print("❌ Bouton 'Nouveau message' non trouvé")
                return False
            
            # Cliquer pour créer un nouveau message
            self.safe_click(new_message_btn, "bouton Nouveau message")
            self.random_delay(2, 3)
            
            # Trouver le champ "À :"
            recipient_selectors = [
                'input[placeholder*="Rechercher des personnes"]',
                'input[placeholder*="Search for people"]',
                'input[aria-label*="Rechercher des personnes"]',
                'input[aria-label*="Search for people"]'
            ]
            
            recipient_field = None
            for selector in recipient_selectors:
                try:
                    element = self.wait_for_element(selector, timeout=5)
                    if element:
                        recipient_field = element
                        break
                except:
                    continue
            
            if not recipient_field:
                print("❌ Champ destinataire non trouvé")
                return False
            
            # Saisir le nom
            print(f"👤 Saisie du destinataire dans Messenger: {self.config['search_name']}")
            self.safe_send_keys(recipient_field, self.config['search_name'], "destinataire Messenger")
            self.random_delay(2, 3)
            
            # Sélectionner le premier résultat
            result_selectors = [
                'div[role="listbox"] div[role="option"]:first-child',
                'ul[role="listbox"] li:first-child',
                'div[data-visualcompletion="ignore"]:first-child'
            ]
            
            first_result = None
            for selector in result_selectors:
                try:
                    element = self.wait_for_element(selector, timeout=3)
                    if element:
                        first_result = element
                        break
                except:
                    continue
            
            if first_result:
                print("✅ Sélection du premier résultat...")
                self.safe_click(first_result, "premier résultat")
                self.random_delay(1, 2)
                return True
            else:
                print("⚠️ Aucun résultat dans Messenger")
                return False
                
        except Exception as e:
            print(f"❌ Erreur Messenger direct: {e}")
            return False
    
    def _send_message_to_profile(self, profile_element=None):
        """
        Envoie un message à un profil déjà trouvé
        """
        try:
            if profile_element:
                print("👤 Accès au profil...")
                self.safe_click(profile_element, "profil trouvé")
                self.random_delay(4, 6)
            
            # 1. Trouver et cliquer sur le bouton "Message"
            print("💬 Recherche du bouton Message sur le profil...")
            
            message_button = None
            message_button_selectors = [
                'div[aria-label="Message"]',
                'div[aria-label="Envoyer un message"]',
                'span:contains("Message")',
                'div:contains("Message")',
                'a[href*="/messages/"]',
                'div[role="button"][aria-label*="Message"]'
            ]
            
            for selector in message_button_selectors:
                try:
                    elements = self.browser.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        try:
                            if element.is_displayed():
                                message_button = element
                                print(f"✅ Bouton Message trouvé: {selector}")
                                break
                        except:
                            continue
                except:
                    continue
                if message_button:
                    break
            
            if not message_button:
                print("❌ Bouton Message non trouvé sur le profil")
                self.take_screenshot('message_button_not_found')
                return False
            
            # Cliquer sur le bouton Message
            self.safe_click(message_button, "bouton Message")
            self.random_delay(3, 5)
            
            # 2. Trouver le champ de message
            print("⏳ Attente du chargement de la fenêtre de message...")
            
            message_input = None
            max_attempts = 3
            
            for attempt in range(max_attempts):
                print(f"🔄 Tentative {attempt + 1}/{max_attempts} pour trouver le champ de message...")
                
                message_selectors = [
                    'div[contenteditable="true"][role="textbox"]',
                    'div[contenteditable="true"][data-lexical-editor="true"]',
                    'div[spellcheck="true"][contenteditable="true"]',
                    'div[aria-label*="Message"][contenteditable="true"]',
                    'div[aria-label*="Écrire un message"][contenteditable="true"]',
                    'div[data-lexical-editor="true"][contenteditable="true"]'
                ]
                
                for selector in message_selectors:
                    try:
                        elements = self.browser.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            try:
                                if element.is_displayed():
                                    message_input = element
                                    print(f"✅ Champ de message trouvé avec: {selector}")
                                    break
                            except:
                                continue
                    except:
                        continue
                    if message_input:
                        break
                
                if message_input:
                    break
                
                self.random_delay(1, 2)
            
            if not message_input:
                print("❌ Champ de message non trouvé")
                return False
            
            # 3. Activer le champ de message
            print("💾 Activation du champ de message...")
            
            activation_methods = [
                lambda: message_input.click(),
                lambda: self.browser.driver.execute_script("arguments[0].click();", message_input),
                lambda: self.browser.driver.execute_script("arguments[0].focus();", message_input),
                lambda: self.browser.driver.execute_script("""
                    var event = new Event('focus', { bubbles: true });
                    arguments[0].dispatchEvent(event);
                """, message_input)
            ]
            
            for i, method in enumerate(activation_methods, 1):
                try:
                    method()
                    print(f"✅ Méthode {i} d'activation réussie")
                    break
                except Exception as e:
                    print(f"⚠️ Méthode {i} d'activation échouée: {e}")
            
            self.random_delay(1, 2)
            
            # 4. Saisir le message
            print("📝 Saisie du message...")
            
            message_sent = False
            message_text = self.config['message_content']
            
            # Méthode 1: Saisie normale
            try:
                print("⌨️ Tentative de saisie normale...")
                for char in message_text:
                    message_input.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.15))
                message_sent = True
                print("✅ Saisie normale réussie")
            except Exception as e:
                print(f"⚠️ Échec saisie normale: {e}")
            
            # Méthode 2: Saisie JavaScript
            if not message_sent:
                try:
                    print("⌨️ Tentative de saisie JavaScript...")
                    self.browser.driver.execute_script("""
                        arguments[0].innerHTML = arguments[1];
                        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                    """, message_input, message_text)
                    message_sent = True
                    print("✅ Saisie JavaScript réussie")
                except Exception as e:
                    print(f"⚠️ Échec saisie JavaScript: {e}")
            
            if not message_sent:
                print("❌ Impossible de saisir le message")
                return False
            
            print(f"✅ Message saisi: {message_text}")
            self.random_delay(1, 2)
            
            # 5. Envoyer le message
            print("📤 Envoi du message...")
            
            # Méthode 1: Touche Entrée
            try:
                message_input.send_keys(Keys.ENTER)
                print("✅ Message envoyé avec Entrée")
                return True
            except Exception as e:
                print(f"⚠️ Échec envoi avec Entrée: {e}")
            
            # Méthode 2: Bouton d'envoi
            try:
                send_button = self.wait_for_element(self.config['selectors']['send_button'], timeout=5)
                if send_button:
                    self.safe_click(send_button, "bouton d'envoi")
                    print("✅ Message envoyé avec bouton")
                    return True
            except Exception as e:
                print(f"⚠️ Échec envoi avec bouton: {e}")
            
            # Méthode 3: JavaScript
            try:
                self.browser.driver.execute_script("""
                    var forms = document.querySelectorAll('form');
                    for (var i = 0; i < forms.length; i++) {
                        if (forms[i].querySelector('[contenteditable="true"]')) {
                            forms[i].submit();
                            break;
                        }
                    }
                """)
                print("✅ Message envoyé avec JavaScript")
                return True
            except Exception as e:
                print(f"⚠️ Échec envoi JavaScript: {e}")
            
            print("⚠️ Message peut-être envoyé sans confirmation")
            return True
            
        except Exception as e:
            print(f"❌ Erreur envoi message: {e}")
            return False
    
    def send_message(self):
        """
        Stratégie améliorée pour envoyer un message
        Essaie plusieurs méthodes
        """
        try:
            print("🚀 Lancement de la stratégie d'envoi de message...")
            
            # Méthode 1: Messenger direct (si activé)
            if self.config.get('use_messenger_direct', True):
                print("🔄 Tentative via Messenger direct...")
                if self._use_messenger_directly():
                    # Si Messenger fonctionne, continuer avec l'envoi du message
                    return self._send_message_to_profile()
                else:
                    print("⚠️ Messenger direct échoué, tentative méthode suivante...")
            
            # Méthode 2: Recherche traditionnelle améliorée
            print("🔄 Tentative via recherche traditionnelle améliorée...")
            for attempt in range(self.config.get('max_search_attempts', 3)):
                print(f"📋 Tentative de recherche {attempt + 1}/{self.config.get('max_search_attempts', 3)}")
                
                # Retourner à la page d'accueil
                self.browser.human_like_get("https://www.facebook.com")
                self.random_delay(2, 3)
                
                # Rechercher le profil
                profile = self._search_profile_improved()
                
                if profile:
                    # Envoyer le message
                    if self._send_message_to_profile(profile):
                        print("✅ Message envoyé avec succès via recherche!")
                        return True
                    else:
                        print("⚠️ Profil trouvé mais échec envoi message")
                else:
                    print(f"❌ Profil non trouvé à la tentative {attempt + 1}")
                
                # Attendre avant nouvelle tentative
                if attempt < self.config.get('max_search_attempts', 3) - 1:
                    wait_time = random.uniform(5, 10)
                    print(f"⏳ Attente de {wait_time:.1f} secondes avant nouvelle tentative...")
                    time.sleep(wait_time)
            
            print("❌ Toutes les méthodes ont échoué")
            return False
            
        except Exception as e:
            print(f"❌ Erreur critique dans send_message: {e}")
            self.take_screenshot('facebook_message_critical_error')
            return False
    
    def perform_action(self):
        """Action principale: envoyer un message via recherche"""
        return self.send_message()