import requests
from bs4 import BeautifulSoup
import json
import re
import codecs
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import time

class GRDFClient:
    """
    Client pour accéder aux données de consommation GRDF.
    """

    def __init__(self, username: str, password: str):
        """
        Initialise le client GRDF.
        
        Args:
            username: Nom d'utilisateur GRDF
            password: Mot de passe GRDF
        """
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.base_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        }
        self.session.headers.update(self.base_headers)
        
        # État de l'authentification et informations de session
        self._authenticated = False
        self.pce = None

    @staticmethod
    def _decode_string(s: str) -> str:
        """Décode une chaîne contenant des séquences d'échappement unicode."""
        return codecs.decode(s, 'unicode_escape')

    @staticmethod
    def _extract_state_token(json_str: str) -> Optional[str]:
        """
        Extrait le stateToken du JSON en utilisant une regex.
        
        Args:
            json_str: Chaîne JSON contenant le stateToken
        
        Returns:
            Le stateToken s'il est trouvé, None sinon
        """
        match = re.search(r'"stateToken"\s*:\s*"([^"]+)"', json_str)
        return match.group(1) if match else None

    def _get_initial_state_token(self) -> str:
        """
        Récupère le stateToken initial depuis la page de connexion.
        
        Returns:
            Le stateToken initial
            
        Raises:
            Exception: Si le stateToken ne peut pas être extrait
        """
        response = self.session.get('https://monespace.grdf.fr/')
        if response.status_code != 200:
            raise Exception(f"Erreur lors de l'accès à la page de connexion: {response.status_code}")

        soup = BeautifulSoup(response.text, 'html.parser')
        okta_script = None

        for script in soup.find_all('script', type='text/javascript'):
            if script.string and 'var oktaData = ' in script.string:
                okta_script = script.string
                break

        if not okta_script:
            raise Exception("Script oktaData non trouvé dans la page")

        try:
            okta_data_str = okta_script.split('var oktaData = ')[1].split('};')[0] + '}'
            okta_data_str = self._decode_string(okta_data_str)
            state_token = self._extract_state_token(okta_data_str)
            
            if not state_token:
                raise Exception("State token non trouvé dans les données Okta")
                
            return state_token
            
        except Exception as e:
            raise Exception(f"Erreur lors de l'extraction des données oktaData: {str(e)}")

    def _authenticate(self) -> None:
        """
        Effectue le processus d'authentification complet.
        Ne s'authentifie que si nécessaire.
        
        Raises:
            Exception: Si l'authentification échoue
        """
        if self._authenticated:
            return

        # get initial state token
        state_token = self._get_initial_state_token()

        # init the user
        identify_response = self.session.post(
            "https://connexion.grdf.fr/idp/idx/identify",
            json={
                "stateHandle": state_token,
                "identifier": self.username,
            }
        )
        if identify_response.status_code != 200:
            raise Exception(f"Erreur lors de l'identification: {identify_response.status_code}")

        # pass the challenge
        state_handle = identify_response.json().get("stateHandle")
        if not state_handle:
            raise Exception("State handle non trouvé dans la réponse d'identification")

        challenge_response = self.session.post(
            "https://connexion.grdf.fr/idp/idx/challenge/answer",
            json={
                "credentials": {"passcode": self.password},
                "stateHandle": state_handle,
            }
        )
        if challenge_response.status_code != 200:
            raise Exception(f"Erreur lors du challenge: {challenge_response.status_code}")

        # get the redirect URL
        challenge_data = challenge_response.json()
        if "success" not in challenge_data or "href" not in challenge_data["success"]:
            raise Exception("URL de redirection non trouvée dans la réponse du challenge")

        redirect_url = challenge_data["success"]["href"]
        self.session.get(redirect_url)

        # update headers
        self.session.headers.update({
            "Host": "monespace.grdf.fr",
            "Connection": "keep-alive",
        })

        # get PCE
        resp = self.session.get("https://monespace.grdf.fr/api/e-conso/pce")
        if resp.status_code != 200:
            raise Exception(f"Erreur lors de la récupération du PCE: {resp.status_code}")

        pce_data = resp.json()
        if not pce_data:
            raise Exception("Aucun PCE trouvé dans la réponse")

        self.pce = pce_data[0]["pce"]
        self._authenticated = True

    def get_consumption_data(self, date_debut: str, date_fin: str, max_retries: int = 3, retry_delay: float = 2.0) -> Dict:
        """
        Récupère les données de consommation pour la période spécifiée.
        
        Args:
            date_debut: Date de début au format YYYY-MM-DD
            date_fin: Date de fin au format YYYY-MM-DD
            max_retries: Nombre maximal de tentatives en cas d'erreur 429 (défaut: 3)
            retry_delay: Délai en secondes entre les tentatives (défaut: 2.0)
            
        Returns:
            Les données de consommation au format JSON
            
        Raises:
            Exception: Si la récupération des données échoue après toutes les tentatives
        """
        # login if not authenticated
        self._authenticate()

        for attempt in range(max_retries):
            response = self.session.get(
                "https://monespace.grdf.fr/api/e-conso/pce/consommation/informatives",
                params={
                    "dateDebut": date_debut,
                    "dateFin": date_fin,
                    f"pceList[]": self.pce
                }
            )

            if response.status_code == 200:
                data = response.json()
                releves = data.get(self.pce, {}).get("releves", [])
                return releves
            
            elif response.status_code in (401, 403):
                # Session expirée, on réauthentifie
                self._authenticated = False
                self._authenticate()
                continue
                
            elif response.status_code == 429:
                if attempt < max_retries - 1:  # S'il reste des tentatives
                    time.sleep(retry_delay * (attempt + 1))  # Délai croissant
                    continue
                    
            # Si on arrive ici, c'est une erreur non récupérable
            raise Exception(f"Erreur lors de la récupération des données: {response.status_code}")

    def get_current_and_previous_consumption(self, nb_days: int = 7) -> Tuple[Dict, Dict]:
        """
        Récupère les données de consommation actuelles et celles de l'année précédente
        pour la même période.
        
        Args:
            nb_days: Nombre de jours de données à récupérer (défaut: 7)
            
        Returns:
            Tuple contenant (données actuelles, données de l'année précédente)
        """
        date_fin = datetime.now()
        date_debut = date_fin - timedelta(days=nb_days)
        
        # Dates pour l'année en cours
        current_data = self.get_consumption_data(
            date_debut=date_debut.strftime("%Y-%m-%d"),
            date_fin=date_fin.strftime("%Y-%m-%d")
        )
        
        # Ajout d'un délai entre les requêtes
        time.sleep(2.0)
        
        # Dates pour l'année précédente
        previous_data = self.get_consumption_data(
            date_debut=(date_debut - timedelta(days=365)).strftime("%Y-%m-%d"),
            date_fin=(date_fin - timedelta(days=365)).strftime("%Y-%m-%d")
        )
        
        return current_data, previous_data
