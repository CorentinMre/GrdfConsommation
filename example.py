

import GrdfConsommation


profil = GrdfConsommation.GRDFConsommation(
                                            email="<your email>", 
                                            password="<your password>",
                                            nbDays=10, # Number of days to recover from this day
                                            pce_id="<your pce id>" # For more speed you can enter your pce identifier (but it is not mandatory)
                                        )


data = profil.data()

print(data)

