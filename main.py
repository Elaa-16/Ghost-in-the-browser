"""
main.py - Point d'entrée principal pour l'automatisation
"""
import time
import sys
from pathlib import Path

# Ajouter le répertoire courant au PATH
sys.path.append(str(Path(__file__).parent))

# Importer depuis config.settings
from config.settings import config_manager
from targets.facebook_automation import FacebookAutomation
from targets.whatsapp_automation import WhatsAppAutomation

class GhostInTheBrowser:
    def __init__(self):
        self.platforms = []
        self.results = []
        
    def load_config(self):
        """Charge la configuration depuis config/settings.py"""
        print("🔐 Chargement des identifiants...")
        
        try:
            credentials = config_manager.get_credentials()
            
            # Vérifier que les identifiants ne sont pas vides
            valid_platforms = []
            
            # Facebook
            fb_creds = credentials.get('facebook', {})
            if fb_creds.get('email') and fb_creds.get('password'):
                valid_platforms.append(('Facebook', FacebookAutomation(fb_creds)))
                print("✅ Facebook: Identifiants chargés")
            else:
                print("⚠️ Facebook: Identifiants manquants ou incomplets")
                
            # WhatsApp
            wa_creds = credentials.get('whatsapp', {})
            if wa_creds.get('phone'):
                valid_platforms.append(('WhatsApp', WhatsAppAutomation(wa_creds)))
                print(f"✅ WhatsApp: Numéro chargé ({wa_creds.get('phone')})")
            else:
                print("⚠️ WhatsApp: Numéro manquant")
            
            if not valid_platforms:
                print("\n❌ Aucun identifiant valide trouvé dans la configuration")
                print("📝 Veuillez remplir le fichier config/credentials.json")
                print("\nStructure attendue:")
                print("""
                        {
                        "facebook": {
                            "email": "votre_email@exemple.com",
                            "password": "votre_mot_de_passe"
                        }
                        "whatsapp": {
                            "phone": "+21654970604"
                        }
                        }
                """)
                return False
            
            self.platforms = valid_platforms
            
            print(f"\n📋 PLAN D'EXÉCUTION ({len(self.platforms)} plateformes):")
            for i, (name, _) in enumerate(self.platforms, 1):
                print(f"  {i}. {name}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur chargement configuration: {e}")
            return False
    
    def run_platform(self, platform_name, automation, platform_num, total_platforms):
        """Exécute l'automatisation pour une plateforme"""
        print(f"\n🎬 ÉTAPE {platform_num}/{total_platforms}: {platform_name}")
        print("-" * 40)
        
        print(f"\n{'='*60}")
        
        # Afficher l'action appropriée
        if platform_name == 'Facebook':
            action_text = "Envoi de message"
        elif platform_name == 'WhatsApp':
            action_text = "Envoi de message"
        else:
            action_text = "Exécution"
            
        print(f" {platform_name.upper()} - {action_text}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            # Lancer l'automatisation
            success = automation.run()
            
            elapsed_time = time.time() - start_time
            
            if success:
                print(f"✅ {platform_name}: Succès en {elapsed_time:.1f}s")
                self.results.append((platform_name, True, elapsed_time))
            else:
                print(f"❌ {platform_name}: Échec")
                self.results.append((platform_name, False, elapsed_time))
                
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"❌ Erreur inattendue {platform_name}: {e}")
            import traceback
            traceback.print_exc()
            self.results.append((platform_name, False, elapsed_time))
        
        return elapsed_time
    
    def run(self):
        """Exécute toutes les automations"""
        print("\n" + "="*60)
        print("GHOST IN THE BROWSER")
        print("="*60)
        print("Automatisation web responsable")
        print("="*60 + "\n")
        
        # Charger la configuration
        if not self.load_config():
            return
        
        total_start_time = time.time()
        
        # Exécuter chaque plateforme
        for i, (platform_name, automation) in enumerate(self.platforms, 1):
            elapsed_time = self.run_platform(platform_name, automation, i, len(self.platforms))
            
            # Pause entre les plateformes (sauf après la dernière)
            if i < len(self.platforms):
                pause_time = 10
                print(f"\n⏸️ Pause de {pause_time}s avant la prochaine plateforme...")
                time.sleep(pause_time)
        
        # Afficher le rapport final
        total_time = time.time() - total_start_time
        self.display_report(total_time)
    
    def display_report(self, total_time):
        """Affiche le rapport final"""
        print(f"\n{'='*60}")
        print(" 📊 RAPPORT FINAL - GHOST IN THE BROWSER")
        print(f"{'='*60}")
        print(f"⏱️ Temps total: {total_time:.1f}s")
        
        # Compter les succès et échecs
        successes = [r for r in self.results if r[1]]
        failures = [r for r in self.results if not r[1]]
        
        print(f"✅ Succès: {len(successes)}/{len(self.results)}")
        if failures:
            print(f"❌ Échecs: {len(failures)}/{len(self.results)}")
        
        print("-" * 40)
        
        # Afficher les plateformes réussies
        if successes:
            print("🎯 PLATEFORMES RÉUSSIES:")
            for name, success, elapsed in successes:
                print(f"  • {name}: {elapsed:.1f}s")
        
        # Afficher les plateformes en échec
        if failures:
            print("\n⚠️ PLATEFORMES EN ÉCHEC:")
            for name, success, elapsed in failures:
                print(f"  • {name}")
        
        # Résumé
        print(f"\n{'='*60}")
        if successes:
            print(f"🎉 {len(successes)} plateforme(s) automatisée(s) avec succès!")
        if failures:
            print(f"⚠️  {len(failures)} plateforme(s) nécessitent des ajustements.")
        
        print(f"\n👋 FIN DE L'EXÉCUTION")
        print("="*60)

if __name__ == "__main__":
    try:
        ghost = GhostInTheBrowser()
        ghost.run()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interruption par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur critique: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)