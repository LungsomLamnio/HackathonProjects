import tkinter as tk
import requests
import string
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# Define Google Maps API key
API_KEY = 'AIzaSyAyR0scmCah89IF6SdLPXt61WGCMfC4mfI'  

@dataclass
class SnappedPoint:
    latitude: float
    longitude: float

@dataclass
class TrafficData:
    intensity: int
    road_name: str

def get_nearest_road(latitude: float, longitude: float, api_key: str) -> List[SnappedPoint]:
    roads_url = f'https://roads.googleapis.com/v1/nearestRoads?points={latitude},{longitude}&key={api_key}'
    
    try:
        response = requests.get(roads_url)
        response.raise_for_status()
        data = response.json()
        
        if 'snappedPoints' in data:
            return [SnappedPoint(point['location']['latitude'], point['location']['longitude']) 
                    for point in data['snappedPoints']]
        else:
            print("No snapped points found")
            return []
    except requests.RequestException as e:
        print(f"Error fetching data from Roads API: {e}")
        return []

def get_traffic_data(latitude: float, longitude: float, api_key: str) -> Optional[int]:
    traffic_url = f'https://maps.googleapis.com/maps/api/distancematrix/json?origins={latitude},{longitude}&destinations={latitude},{longitude}&departure_time=now&traffic_model=best_guess&key={api_key}'
    
    try:
        response = requests.get(traffic_url)
        response.raise_for_status()
        data = response.json()
        
        if 'rows' in data and data['rows'] and 'elements' in data['rows'][0] and data['rows'][0]['elements']:
            return data['rows'][0]['elements'][0].get('duration_in_traffic', {}).get('value')
        else:
            print("No traffic data available for the specified location")
            return None
    except requests.RequestException as e:
        print(f"Error fetching data from Traffic API: {e}")
        return None

def determine_high_traffic_road(snapped_points: List[SnappedPoint], api_key: str) -> Tuple[Optional[SnappedPoint], Optional[int]]:
    highest_traffic_intensity = -1
    high_traffic_road = None

    for point in snapped_points:
        traffic_intensity = get_traffic_data(point.latitude, point.longitude, api_key)
        if traffic_intensity is not None and traffic_intensity > highest_traffic_intensity:
            highest_traffic_intensity = traffic_intensity
            high_traffic_road = point

    return high_traffic_road, highest_traffic_intensity

class TrafficLightGUI:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, width=70, height=150)
        self.canvas.pack()
        self.colors = ["red", "yellow", "green"]
        self.draw_traffic_light()

    def draw_traffic_light(self):
        box_width, box_height = 50, 175
        box_left = (70 - box_width) / 2
        box_top = (150 - box_height) / 2
        self.canvas.create_rectangle(box_left, box_top, box_left + box_width, box_top + box_height, fill="black")
        
        light_size = 20
        light_left = (70 - light_size) / 2
        light_top = box_top + 20
        
        self.lights = [
            self.canvas.create_oval(light_left, light_top + i * (light_size + 40), 
                                    light_left + light_size, light_top + light_size + i * (light_size + 40), 
                                    fill="black") 
            for i in range(3)
        ]

    def update_light(self, color: str):
        for light in self.lights:
            self.canvas.itemconfig(light, fill="black")
        color_index = self.colors.index(color)
        self.canvas.itemconfig(self.lights[color_index], fill=color)

class TrafficCongestionApp:
    def __init__(self, master):
        self.master = master
        master.title("Traffic Congestion Analysis")
        
        self.create_widgets()

    def create_widgets(self):
        labels = ["Latitude:", "Longitude:", "Traffic Box ID:", "Range of Device (in km):", "Total Life Cycle (in seconds):"]
        self.entries = {}

        for i, label in enumerate(labels):
            tk.Label(self.master, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = tk.Entry(self.master)
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries[label] = entry

        submit_button = tk.Button(self.master, text="Fetch Traffic Data", command=self.submit)
        submit_button.grid(row=len(labels), column=0, columnspan=2, pady=10)

    def submit(self):
        try:
            latitude = float(self.entries["Latitude:"].get())
            longitude = float(self.entries["Longitude:"].get())
            traffic_box_id = self.entries["Traffic Box ID:"].get()
            range_km = float(self.entries["Range of Device (in km):"].get())
            life_cycle_seconds = int(self.entries["Total Life Cycle (in seconds):"].get())

            print(f"Location: {latitude}, {longitude}")
            print(f"Traffic Box ID: {traffic_box_id}")
            print(f"Range of Device: {range_km} km")
            print(f"Total Life Cycle: {life_cycle_seconds} seconds")

            snapped_points = get_nearest_road(latitude, longitude, API_KEY)
            self.process_traffic_data(snapped_points)
        except ValueError as e:
            print(f"Invalid input: {e}")

    def process_traffic_data(self, snapped_points: List[SnappedPoint]):
        num_roads = len(snapped_points)
        road_names = list(string.ascii_uppercase[:num_roads])
        
        print(f"Number of roads at the specified location: {num_roads}")
        for i, point in enumerate(snapped_points):
            print(f"Road {road_names[i]}: {point.latitude}, {point.longitude}")

        high_traffic_road, highest_traffic_intensity = determine_high_traffic_road(snapped_points, API_KEY)
        if high_traffic_road:
            road_name = road_names[snapped_points.index(high_traffic_road)]
            print(f"The road with higher traffic is Road {road_name} with coordinates: {high_traffic_road.latitude}, {high_traffic_road.longitude}")
            print(f"Highest traffic intensity: {highest_traffic_intensity}")
            self.create_traffic_lights(road_names, snapped_points)
        else:
            print("Unable to determine the road with higher traffic")

    def create_traffic_lights(self, road_names: List[str], snapped_points: List[SnappedPoint]):
        traffic_window = tk.Toplevel(self.master)
        traffic_window.title("Traffic Light Simulation")

        for i, (road_name, point) in enumerate(zip(road_names, snapped_points)):
            frame = tk.Frame(traffic_window)
            frame.pack(pady=10)

            tk.Label(frame, text=f"Road {road_name}").pack()

            traffic_light = TrafficLightGUI(frame)
            color = "green" if road_name == 'A' else "red" if road_name == 'B' else "yellow" if road_name == 'C' else "red"
            traffic_light.update_light(color)

def main():
    root = tk.Tk()
    app = TrafficCongestionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()