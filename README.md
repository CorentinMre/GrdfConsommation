<p align="center"><img width="250" alt="CRDF Consommation" src="images/logo.png"></p>

<br/>

<h2 align="center">CRDF Consommation</h2>
<br/>

<br/>

## Requirements

- Install requirements (`pip install -r requirements.txt`)

## Usage

Here is an example script:

```python
import GrdfConsommation
from datetime import datetime, timedelta


client = GrdfConsommation.GRDFClient(
                                            username="<your email>",
                                            password="<your password>",
                                        )


data = client.get_consumption_data(
            # date_debut="2022-01-04",
            # date_fin="2025-01-04",

            # OU
            
            date_debut=(datetime.now() - timedelta(days=8)).strftime("%Y-%m-%d"), 
            date_fin=datetime.now().strftime("%Y-%m-%d")
        )

print(data)

```

Result example:

```json
[
            {
                "dateDebutReleve": <data>,
                "dateFinReleve": <data>,
                "journeeGaziere": <data>,
                "indexDebut": <data>,
                "indexFin": <data>,
                "volumeBrutConsomme": <data>,
                "energieConsomme": <data>,
                "pcs": <data>,
                "volumeConverti": <data>,
                "pta": <data>,
                "natureReleve": <data>,
                "qualificationReleve": <data>,
                "status": <data>,
                "coeffConversion": <data>,
                "frequenceReleve": <data>,
                "temperature": <data>
            },

            ...
]
```

And if you want to compare with last year:

```python
import GrdfConsommation
import datetime


client = GrdfConsommation.GRDFClient(
                                            username="<your email>",
                                            password="<your password>",
                                        )

#données des n derniers jours
current_data, previous_data = client.get_current_and_previous_consumption(nb_days=8)

#-------------------------------------------------------#
```