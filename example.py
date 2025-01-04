

import GrdfConsommation
from datetime import datetime, timedelta


client = GrdfConsommation.GRDFClient(
                                            username="<username>", 
                                            password="<password>", 
                                        )


data = client.get_consumption_data(
            # date_debut="2022-01-04",
            # date_fin="2025-01-04",
            date_debut=(datetime.now() - timedelta(days=8)).strftime("%Y-%m-%d"),
            date_fin=datetime.now().strftime("%Y-%m-%d")
        )


print(data)

