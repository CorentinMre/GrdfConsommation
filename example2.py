
import GrdfConsommation
import datetime


profil = GrdfConsommation.GRDFConsommation(
                                            email="<your email>", 
                                            password="<your password>",
                                            nbDays=10, # Number of days to recover from this day
                                            pce_id="<your pce id>" # For more speed you can enter your pce identifier (but it is not mandatory)
                                        )

#données des n derniers jours
data = profil.data()

#-------------------------------------------------------#

#Change la date en celle de l'annier derniere
profil.endDate = datetime.date.today().replace(year=datetime.date.today().year - 1)
profil.startDate = profil.endDate + datetime.timedelta(days=-profil.nbDays)

#-------------------------------------------------------#

#données des n derniers jours d'il y a un an
data2 = profil.data()


#Consommation de cette année
for consom in data:
    print(consom["day"] + ":", consom["consommation"] , "kWh")

print("#---------------------------#")

#Consommation de l'année derniere
for consom in data2:
    print(consom["day"] + ":", consom["consommation"] , "kWh")