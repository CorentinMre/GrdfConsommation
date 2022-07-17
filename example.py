

import GrdfConsommation


profil = GrdfConsommation.GRDFConsommation(
                                            email="<your email>", 
                                            password="<your password>", 
                                            pce_id="<your pce id>", 
                                            nbDays=10 # Nombre de jours à récupérer depuis ce jour
                                        )


data = profil.data()

print(data)

