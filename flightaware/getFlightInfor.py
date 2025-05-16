import requests
import os
from dotenv import load_dotenv
 
load_dotenv() 


API_KEY = os.getenv("FLIGHTAWARE_API_KEY")
apiUrl = "https://aeroapi.flightaware.com/aeroapi/"
auth_header = {'x-apikey': API_KEY}

def get_flight_route(flight_number):
    # ステップ1: フライト番号で検索してfa_flight_idを取得
    search_params = {
        'query': f'ident:{flight_number}',
        'max_pages': 1
    }
    
    search_response = requests.get(
        apiUrl + "flights/search",
        params=search_params,
        headers=auth_header
    )
    
    if search_response.status_code == 200:
        flights = search_response.json().get('flights', [])
        if flights:
            fa_flight_id = flights[0]['fa_flight_id']
            
            # ステップ2: 取得したfa_flight_idで経路情報を取得
            track_response = requests.get(
                apiUrl + f"flights/{fa_flight_id}/track",
                headers=auth_header
            )
            
            if track_response.status_code == 200:
                print(track_response.json())
            else:
                print(f"経路取得エラー: {track_response.status_code}")
        else:
            print("該当フライトが見つかりません")
    else:
        error_data = search_response.json()
        print(f"エラー詳細: {error_data}")
        print(f"検索エラー: {search_response.status_code}")

if __name__ == '__main__':
    flight_number="ALK455"
    get_flight_route(flight_number)  # フライト番号を直接指定