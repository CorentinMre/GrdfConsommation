

import GrdfConsommation


profil = GrdfConsommation.GRDFConsommation(
                                            email="<your email>", 
                                            password="<your password>",
                                            nbDays=10, # Nombre de jours à récupérer depuis ce jour
                                            pce_id="<your pce id>" # Pour plus de rapidité vous pouvez entrez votre identifiant pce (mais il n'est pas obligatoire)
                                        )


data = profil.data()

print(data)

