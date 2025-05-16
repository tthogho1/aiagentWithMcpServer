import requests
import os
from dotenv import load_dotenv
 
load_dotenv() 

API_KEY = os.getenv("FLIGHTAWARE_API_KEY")
apiUrl = "https://aeroapi.flightaware.com/aeroapi/"
# 例: 名古屋飛行場（小牧空港）
payload = {'max_pages': 1}
auth_header = {'x-apikey': API_KEY}

def get_flight_numbers_by_airport(airport):
    response = requests.get(
        apiUrl + f"airports/{airport}/flights",
        params=payload,
        headers=auth_header
    )
    if response.status_code == 200:
        data = response.json()
        # 各フライトのflight_numberを抽出して表示
        for flight in data.get('departures', []):
            print(f"ident : {flight.get('ident')}")
            print(f"fa_flight_id : {flight.get('fa_flight_id')}")
            print(f"flight number : {flight.get('flight_number')}")  
    else:
        print("Error executing request")

if __name__ == '__main__':
    airport = 'RJAA'  
    get_flight_numbers_by_airport(airport)
