import tkinter as tk
import requests
import string

# Define your Google Maps API key
API_KEY = 'AIzaSyD5M6O9EEhMUKTOwbCUvKAwcimStjqXJms'

def get_nearest_road(latitude, longitude, api_key):
    # Define the Roads API endpoint
    roads_url = f'https://roads.googleapis.com/v1/nearestRoads?points={latitude},{longitude}&key={api_key}'

    # Make a GET request to the Roads API
    response = requests.get(roads_url)
    
    # Parse the JSON response
    if response.status_code == 200:
        data = response.json()
        if 'snappedPoints' in data:
            # Return the list of snapped points
            return data['snappedPoints']
        else:
            print("No snapped points found")
            return []
    else:
        print("Error fetching data from Roads API")
        return []

def count_nearby_roads(latitude, longitude, api_key):
    # Get snapped points (nearest roads)
    snapped_points = get_nearest_road(latitude, longitude, api_key)

    # Count the number of snapped points (roads)
    num_roads = len(snapped_points)
    return snapped_points, num_roads

def get_traffic_data(latitude, longitude, api_key):
    # Define the Traffic API endpoint
    traffic_url = f'https://maps.googleapis.com/maps/api/distancematrix/json?origins={latitude},{longitude}&destinations={latitude},{longitude}&departure_time=now&traffic_model=best_guess&key={api_key}'

    # Make a GET request to the Traffic API
    response = requests.get(traffic_url)
    
    # Parse the JSON response
    if response.status_code == 200:
        data = response.json()
        if 'rows' in data and 'elements' in data['rows'][0] and 'duration_in_traffic' in data['rows'][0]['elements'][0]:
            # Extract the traffic intensity value
            traffic_intensity = data['rows'][0]['elements'][0]['duration_in_traffic']['value']
            return traffic_intensity
        else:
            print("No traffic data available for the specified location")
            return None
    else:
        print("Error fetching data from Traffic API")
        return None

def determine_high_traffic_road(snapped_points, api_key):
    highest_traffic_intensity = -1
    high_traffic_road = None

    for i, point in enumerate(snapped_points):
        # Get traffic data for each road
        traffic_intensity = get_traffic_data(point['location']['latitude'], point['location']['longitude'], api_key)
        if traffic_intensity is not None and traffic_intensity > highest_traffic_intensity:
            highest_traffic_intensity = traffic_intensity
            high_traffic_road = point

    return high_traffic_road, highest_traffic_intensity

def submit(latitude_entry, longitude_entry, box_id_entry, range_entry, life_cycle_entry):
    latitude = float(latitude_entry.get())
    longitude = float(longitude_entry.get())
    traffic_box_id = box_id_entry.get()
    range_km = float(range_entry.get())
    life_cycle_seconds = int(life_cycle_entry.get())

    print("Location (Latitude, Longitude):", latitude, longitude)
    print("Traffic Box ID:", traffic_box_id)
    print("Range of Device (in km):", range_km)
    print("Total Life Cycle (in seconds):", life_cycle_seconds)

    # Count the number of roads and lanes
    snapped_points, num_roads = count_nearby_roads(latitude, longitude, API_KEY)

    # Print the number of roads and assign them names like a, b, c, etc.
    road_names = list(string.ascii_uppercase)[:num_roads]
    print(f"Number of roads at the specified location: {num_roads}")
    for i, point in enumerate(snapped_points):
        print(f"Road {road_names[i]}: {point['location']['latitude']}, {point['location']['longitude']}")

    # Determine which road has higher traffic
    high_traffic_road, highest_traffic_intensity = determine_high_traffic_road(snapped_points, API_KEY)
    if high_traffic_road:
        road_name = road_names[snapped_points.index(high_traffic_road)]
        print(f"The road with higher traffic is Road {road_name} with coordinates: {high_traffic_road['location']['latitude']}, {high_traffic_road['location']['longitude']}")
        print(f"Highest traffic intensity: {highest_traffic_intensity}")

        # Create traffic light boxes for each road
        create_traffic_lights(road_names, snapped_points, num_roads)
    else:
        print("Unable to determine the road with higher traffic")

def create_traffic_lights(road_names, snapped_points, num_roads):
    root = tk.Tk()
    root.title("Traffic Light Simulation")

    for i in range(num_roads):
        road_name = road_names[i]
        point = snapped_points[i]
        frame = tk.Frame(root)
        frame.pack(pady=10)

        # Create traffic light for each road
        label = tk.Label(frame, text=f"Road {road_name}")
        label.pack()

        traffic_light = TrafficLightGUI(frame)
        if road_name == 'A':
            traffic_light.update_light("green")
        elif road_name == 'B':
            traffic_light.update_light("red")
        elif road_name == 'C':
            traffic_light.update_light("yellow")
        else:
            traffic_light.update_light("red")

    root.mainloop()

# Traffic Light Simulation Class
class TrafficLightGUI:
    def __init__(self, master):
        self.master = master

        self.canvas = tk.Canvas(master, width=70, height=150)
        self.canvas.pack()

        # Traffic light colors
        self.colors = ["red", "yellow", "green"]
        self.current_color_index = 0

        # Draw the traffic light
        self.draw_traffic_light()

    def draw_traffic_light(self):
        # Coordinates for the traffic light box
        box_width = 50
        box_height = 175
        box_left = (70 - box_width) / 2
        box_top = (150 - box_height) / 2
        box_right = box_left + box_width
        box_bottom = box_top + box_height

        self.canvas.create_rectangle(box_left, box_top, box_right, box_bottom, fill="black")
        
        # Coordinates for the lights
        light_size = 20
        light_left = (70 - light_size) / 2
        light_top = box_top + 20
        light_bottom = light_top + light_size

        self.lights = [
            self.canvas.create_oval(light_left, light_top + i * (light_size + 40), light_left + light_size, light_bottom + i * (light_size + 40), fill="black") 
            for i in range(3)
        ]

    def update_light(self, color):
        # Reset all lights to black
        for light in self.lights:
            self.canvas.itemconfig(light, fill="black")

        # Turn on the specified color
        color_index = self.colors.index(color)
        self.canvas.itemconfig(self.lights[color_index], fill=color)

def main():
    # GUI setup
    root = tk.Tk()
    root.title("Traffic Congestion Analysis")

    # Latitude
    latitude_label = tk.Label(root, text="Latitude:")
    latitude_label.grid(row=0, column=0, padx=10, pady=5)
    latitude_entry = tk.Entry(root)
    latitude_entry.grid(row=0, column=1, padx=10, pady=5)

    # Longitude
    longitude_label = tk.Label(root, text="Longitude:")
    longitude_label.grid(row=1, column=0, padx=10, pady=5)
    longitude_entry = tk.Entry(root)
    longitude_entry.grid(row=1, column=1, padx=10, pady=5)

    # Traffic Box ID
    box_id_label = tk.Label(root, text="Traffic Box ID:")
    box_id_label.grid(row=2, column=0, padx=10, pady=5)
    box_id_entry = tk.Entry(root)
    box_id_entry.grid(row=2, column=1, padx=10, pady=5)

    # Range of Device (in km)
    range_label = tk.Label(root, text="Range of Device (in km):")
    range_label.grid(row=3, column=0, padx=10, pady=5)
    range_entry = tk.Entry(root)
    range_entry.grid(row=3, column=1, padx=10, pady=5)

    # Total Life Cycle (in seconds)
    life_cycle_label = tk.Label(root, text="Total Life Cycle (in seconds):")
    life_cycle_label.grid(row=4, column=0, padx=10, pady=5)
    life_cycle_entry = tk.Entry(root)
    life_cycle_entry.grid(row=4, column=1, padx=10, pady=5)

    # Submit Button
    submit_button = tk.Button(root, text="Fetch Traffic Data", command=lambda: submit(latitude_entry, longitude_entry, box_id_entry, range_entry, life_cycle_entry))
    submit_button.grid(row=5, column=0, columnspan=2, pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
