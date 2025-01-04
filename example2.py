import GrdfConsommation
import matplotlib.pyplot as plt
from datetime import datetime, timedelta



client = GrdfConsommation.GRDFClient(
                                            username="<username>", 
                                            password="<password>", 
                                        )



# get data
current_data, previous_data = client.get_current_and_previous_consumption(nb_days=8)


# -> dict with date as key and energy as value
current_dict = {
    datetime.strptime(r['journeeGaziere'], '%Y-%m-%d'): r['energieConsomme']
    for r in current_data
}

previous_dict = {
    datetime.strptime(r['journeeGaziere'], '%Y-%m-%d'): r['energieConsomme']
    for r in previous_data
}

# get unique dates
all_previous_dates = sorted(previous_dict.keys())

# Pair each date with the same date from the previous year
paired_dates = []
for prev_date in all_previous_dates:
    next_year_date = prev_date + timedelta(days=365)
    paired_dates.append((prev_date, next_year_date))

# Extract data for the paired dates
x_dates = []
y_current = []
y_previous = []

for prev_date, curr_date in paired_dates:
    x_dates.append(prev_date.strftime('%d/%m'))
    # data for the current year (if available)
    y_current.append(current_dict.get(curr_date))
    # data for the previous year (available)
    y_previous.append(previous_dict[prev_date])

# Plot the data
plt.figure(figsize=(12, 6))


x_points = range(len(x_dates))

# Define a function to plot lines with gaps
def plot_with_gaps(x, y, **kwargs):
    valid_points = [(x_, y_) for x_, y_ in zip(x, y) if y_ is not None]
    if valid_points:
        x_valid, y_valid = zip(*valid_points)
        plt.plot(x_valid, y_valid, **kwargs)

plot_with_gaps(x_points, y_current, color='k', linewidth=2.5, label='Cette année')
plot_with_gaps(x_points, y_previous, color='gray', linewidth=1.5, linestyle='-', label='Année précédente')

plt.ylabel('Énergie consommée (kWh)')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()

# Display the dates on the x-axis
plt.xticks(x_points, x_dates, rotation=45)
plt.tight_layout()
plt.show()