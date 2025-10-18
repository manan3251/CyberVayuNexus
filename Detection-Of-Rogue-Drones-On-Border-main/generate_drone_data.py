import pandas as pd
from datetime import datetime
import random

# Function to generate random drone data
def generate_drone_data(num_records):
    data = []
    for _ in range(num_records):
        record = {
            "Drone ID": f"D{random.randint(1, 1000):03}",
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Latitude": round(random.uniform(34.0, 35.0), 4),
            "Longitude": round(random.uniform(-119.0, -118.0), 4),
            "Altitude": random.randint(50, 150),
            "Speed": random.randint(20, 80),
            "Direction": random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
            "Signal Strength": random.randint(-80, -50),
            "Known": random.choice([True, False])
        }
        data.append(record)
    return data

# Generate 100 sample records
sample_data = generate_drone_data(100)

# Create a DataFrame
df = pd.DataFrame(sample_data)

# Save to CSV
csv_filename = "drone_data.csv"
df.to_csv(csv_filename, index=False)

print(f"Sample drone data saved to {csv_filename}") 