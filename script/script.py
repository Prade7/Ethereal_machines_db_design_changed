import time
import requests
from datetime import datetime
import json

file_path = 'cnc.txt'
api_url = 'http://127.0.0.1:8000/api/machines/'

url = "http://127.0.0.1:8000/api/login/"

payload = json.dumps({
    "employee_id": "18ITR012",
    "password": "9942142",
    "role": "manager"
})
headers = {
    'Content-Type': 'application/json'
}

response = requests.post(url, headers=headers, data=payload)

if response.status_code == 200 or response.status_code==201:
    print(response.json())
    jwt_token = response.json()  
    print("Successfully logged in. JWT token obtained.")
else:
    print(f"Failed to login. Status Code: {response.status_code}, Response: {response.text}")
    jwt_token = None

def parse_cnc_file(file_path):
    machines = []   
    current_machine = {}
    
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith("Name"):
                if current_machine:
                    machines.append(current_machine)
                    current_machine = {}
                current_machine['name'] = line.split()[1]
            elif line.startswith("acceleration"):
                current_machine['acceleration'] = float(line.split()[1].replace(',', '.'))
            elif line.startswith("actual_position"):
                positions = [float(x.replace(',', '.')) for x in line.split()[1:]]
                current_machine['actual_position'] = {
                    'x': positions[0],
                    'y': positions[1],
                    'z': positions[2],
                    'a': positions[3],
                    'c': positions[4]
                }
            elif line.startswith("distance_to_go"):
                distances = [float(x.replace(',', '.')) for x in line.split()[1:]]
                current_machine['distance_to_go'] = {
                    'x': distances[0],
                    'y': distances[1],
                    'z': distances[2],
                    'a': distances[3],
                    'c': distances[4]
                }
            elif line.startswith("homed"):
                homed = [False if x != '1' else True for x in line.split()[1:]]
                current_machine['homed'] = {
                    'x': homed[0],
                    'y': homed[1],
                    'z': homed[2],
                    'a': homed[3],
                    'c': homed[4]
                }
            elif line.startswith("tool_offset"):
                offsets = [float(x.replace(',', '.')) for x in line.split()[1:]]
                current_machine['tool_offset'] = {
                    'x': offsets[0],
                    'y': offsets[1],
                    'z': offsets[2],
                    'a': offsets[3],
                    'c': offsets[4]
                }
            elif line.startswith("velocity"):
                current_machine['velocity'] = float(line.split()[1].replace(',', '.'))

    if current_machine:
        machines.append(current_machine)

    return machines

def send_machine_data(machine):
    if not jwt_token:
        print("No JWT token available. Cannot send data.")
        return
    
    headers = {
        'Authorization': jwt_token,  
        'Content-Type': 'application/json'
    }

    data = {
        'name': machine['name'],
        'acceleration': machine['acceleration'],
        'actual_position': machine['actual_position'],
        'distance_to_go': machine['distance_to_go'],
        'homed': machine['homed'],
        'tool_offset': machine['tool_offset'],
        'velocity': machine['velocity'],
    }
    
    print(f"Sending data for machine {machine['name']}: {json.dumps(data, indent=2)}")
    response = requests.post(api_url, json=data, headers=headers)
    if response.status_code == 200:
        print(f"Data for {machine['name']} sent successfully.")
    elif response.status_code == 201:
        print(f"Data created for {machine['name']}")
    else:
        print(f"Failed to send data for {machine['name']}. Status Code: {response.status_code}, Response: {response.text}")

def main():
    while True:
        machines = parse_cnc_file(file_path)
        for machine in machines:
            send_machine_data(machine)
        time.sleep(1)

if __name__ == '__main__':
    main()
