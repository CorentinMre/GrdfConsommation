
import requests
import datetime

class GRDFConsommation:
    def __init__(self, email, password, pce_id, nbDays):
        self.email = email
        self.password = password
        self.pce = pce_id
        self.nbDays = nbDays

        self.session = requests.Session()

        self.headers = {"domain": "grdf.fr"}
        self.payload = {'email': self.email,
                        'password': self.password,
                        'capp': 'meg',
                        'goto': 'https://sofa-connexion.grdf.fr:443/openam/oauth2/externeGrdf/authorize?response_type=code&scope=openid%20profile%20email%20infotravaux%20%2Fv1%2Faccreditation%20%2Fv1%2Faccreditations%20%2Fdigiconso%2Fv1%20%2Fdigiconso%2Fv1%2Fconsommations%20new_meg&client_id=prod_espaceclient&state=0&redirect_uri=https%3A%2F%2Fmonespace.grdf.fr%2F_codexch&nonce=skywsNPCVa-AeKo1Rps0HjMVRNbUqA46j7XYA4tImeI&by_pass_okta=1&capp=meg'}

        
        self.endDate = datetime.date.today()
        self.startDate = self.endDate + datetime.timedelta(days=-self.nbDays)
        self.dataUrl = "https://monespace.grdf.fr/api/e-conso/pce/consommation/informatives?dateDebut={0}&dateFin={1}&pceList[]={2}"
        

        self.session.headers.update(self.headers)
    def data(self) -> list:
        self._update()
        data = []
        for day in self.__data:
            data.append({"day": day["journeeGaziere"], "consommation": day["energieConsomme"]})
        return data



    def _update(self):

        response = self.session.post('https://login.monespace.grdf.fr/sofit-account-api/api/v1/auth', data=self.payload)

        response.raise_for_status()

        loginData = response.json()
        if loginData["state"] != "SUCCESS":
            raise "Login failed"

        self.session.get(self.dataUrl.format(self.startDate, self.endDate, self.pce))

        response = self.session.get(self.dataUrl.format(self.startDate, self.endDate, self.pce))

        response.raise_for_status()

        self.__data = response.json()[self.pce]["releves"]
