import json
import os
import requests
import pytz
from datetime import datetime, timedelta
from typing import Any, Callable, Set, Dict, List, Optional
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("Flight Server")
API_KEY = os.getenv("FLIGHTAWARE_API_KEY")
AEROAPI_BASE_URL = "https://aeroapi.flightaware.com/aeroapi"


# Prepare an empty list as a global variable
airports_data = None


@mcp.tool()
def get_nearest_largeairport_fromLatLng(
    latitude: float, longitude: float
) -> Dict[str, Any]:
    """Returns Nearest International Airport from Latitude and Longitude"""
    global airports_data  # Use global variable

    if airports_data is None:
        # Load from file only on the first call
        airports_file_path = os.path.join(
            os.path.dirname(__file__), "airport_icao_code.tsv"
        )
        airports_data = []
        with open(airports_file_path, "r", encoding="utf-8") as f:
            next(f)  # Skip the first line (header)
            for line in f:
                line = line.strip()
                if not line:
                    continue
                fields = line.split("\t")
                if len(fields) < 5:
                    continue
                airport_data = {
                    "type": fields[0],
                    "name": fields[1],
                    "latitude": float(fields[2]),
                    "longitude": float(fields[3]),
                    "ICAO_code": fields[4],
                }
                if airport_data["type"] == "large_airport":
                    airports_data.append(airport_data)

    nearest_airport = None
    nearest_distance = float("inf")
    for airport in airports_data:
        airport_latitude = airport["latitude"]
        airport_longitude = airport["longitude"]
        distance = (
            (latitude - airport_latitude) ** 2 + (longitude - airport_longitude) ** 2
        ) ** 0.5
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_airport = airport

    if nearest_airport:
        return {
            "airport": nearest_airport["name"],
            "ICAO_code": nearest_airport["ICAO_code"],
            "latitude": nearest_airport["latitude"],
            "longitude": nearest_airport["longitude"],
        }
    else:
        return {"error": "No international airport found near the given coordinates."}


@mcp.tool()
def get_flight_numbers_by_airport(ICAO_code):
    """Returns Flight Numbers by Airport"""
    AEROAPI_KEY = API_KEY

    def get_api_session():
        session = requests.Session()
        session.headers.update({"x-apikey": AEROAPI_KEY})
        return session

    def fetch_flight_numbers(ICAO_code, session):
        api_resource = f"/airports/{ICAO_code}/flights"

        params = {}
        params["max_pages"] = 4

        try:
            response = session.get(f"{AEROAPI_BASE_URL}{api_resource}", params=params)
            response.raise_for_status()
            json_data = response.json()

            # Print the response for debugging
            # print("API Response:", json.dumps(json_data, indent=2))

            if "departures" not in json_data or len(json_data["departures"]) == 0:
                return None

            return json_data["departures"]
        except Exception as e:
            print(f"Error fetching flight numbers: {e}")
            return None

    session = get_api_session()
    flight_data = fetch_flight_numbers(ICAO_code, session)

    if flight_data is None:
        return json.dumps(
            {
                "error": "Failed to retrieve flight data. Check the API key and flight ID.",
                "airport": ICAO_code,
            }
        )

    try:
        flights = []
        for flight in flight_data:
            flights.append(
                {
                    "ident": flight.get("ident"),
                    "fa_flight_id": flight.get("fa_flight_id"),
                    "flight_number": flight.get("flight_number"),
                }
            )
        # MCPサーバの戻り値として辞書で返す
        return {"flights": flights, "count": len(flights)}
        # return json.dumps({"flights": flights, "count": len(flights)})
    except Exception as e:
        print(f"Error processing flight data: {e}")
        return json.dumps(
            {"error": f"Error processing flight number: {str(e)}", "airport": ICAO_code}
        )


@mcp.tool()
def get_flight_status(fa_flight_id):
    """Returns Flight Information"""
    AEROAPI_KEY = API_KEY

    def get_api_session():
        session = requests.Session()
        session.headers.update({"x-apikey": AEROAPI_KEY})
        return session

    def fetch_flight_data(fa_flight_id, session):
        if "flight_id=" in fa_flight_id:
            fa_flight_id = fa_flight_id.split("flight_id=")[1]

        start_date = datetime.now().date().strftime("%Y-%m-%d")
        end_date = (datetime.now().date() + timedelta(days=1)).strftime("%Y-%m-%d")
        api_resource = f"/flights/{fa_flight_id}?start={start_date}&end={end_date}"  # Fixed &amp; to &amp;

        try:
            response = session.get(f"{AEROAPI_BASE_URL}{api_resource}")
            response.raise_for_status()
            json_data = response.json()

            # Print the response for debugging
            # print("API Response:", json.dumps(json_data, indent=2))

            if "flights" not in json_data or len(json_data["flights"]) == 0:
                return None

            return json_data["flights"][0]
        except Exception as e:
            print(f"Error fetching flight data: {e}")
            return None

    def utc_to_local(utc_date_str, local_timezone_str):
        utc_datetime = datetime.strptime(utc_date_str, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=pytz.utc
        )
        local_timezone = pytz.timezone(local_timezone_str)
        local_datetime = utc_datetime.astimezone(local_timezone)
        return local_datetime.strftime("%Y-%m-%d %H:%M:%S")

    session = get_api_session()
    flight_data = fetch_flight_data(fa_flight_id, session)

    if flight_data is None:
        return {
            "error": "Failed to retrieve flight data. Check the API key and flight ID.",
            "flight": fa_flight_id,
        }

    try:
        dep_key = (
            "estimated_out"
            if "estimated_out" in flight_data and flight_data["estimated_out"]
            else (
                "actual_out"
                if "actual_out" in flight_data and flight_data["actual_out"]
                else "scheduled_out"
            )
        )

        arr_key = (
            "estimated_in"
            if "estimated_in" in flight_data and flight_data["estimated_in"]
            else (
                "actual_in"
                if "actual_in" in flight_data and flight_data["actual_in"]
                else "scheduled_in"
            )
        )

        return {
            "flight": fa_flight_id,
            "source": flight_data["origin"]["city"],
            "destination": flight_data["destination"]["city"],
            "departure_time": utc_to_local(
                flight_data[dep_key], flight_data["origin"]["timezone"]
            ),
            "arrival_time": utc_to_local(
                flight_data[arr_key], flight_data["destination"]["timezone"]
            ),
            "status": flight_data["status"],
        }
    except Exception as e:
        print(f"Error processing flight data: {e}")
        return {
            "error": f"Error processing flight data: {str(e)}",
            "flight": fa_flight_id,
        }


# listで渡したfa_flight_idのflightステータスをjson配列で返す
@mcp.tool()
def get_flight_statuses(fa_flight_ids: List[str]) -> List[Dict[str, Any]]:
    """Returns Flight Information for a list of flight IDs"""
    statuses = []
    file_path = "c:\\temp\\light_statuses.json"
    for flight_id in fa_flight_ids:
        try:
            status = get_flight_status(flight_id)
            with open(file_path, "a", encoding="utf-8") as f:
                json.dump(status, f, indent=4, ensure_ascii=False)
                f.write("\n")  # レコードごとに改行を入れると見やすいです
            statuses.append(status)
        except Exception as e:
            print(f"Error processing flight_id {flight_id}: {e}")
            statuses.append(
                {"flight": flight_id, "error": f"An error occurred: {str(e)}"}
            )

    return statuses


if __name__ == "__main__":
    mcp.run()
    # airport = "RJAA"
    # retult = get_flight_numbers_by_airport(airport)
    # print(retult)
    # unitest
    # Example usage
    # flight_numbers = ["ADO43-1747636070-airline-1348p",
    #                   "QTR807-1747638311-airline-1152p",
    #                   "MAS71-1747638838-airline-1980p",
    #                   "N868FD-1747833103-adhoc-387p"]  # Replace with actual flight number
    # result = get_flight_statuses(flight_numbers)
    # print("\nTest Result:")
    # print(result)
    # result = get_nearest_largeairport_fromLatLng(
    #    latitude=35.6947, longitude=139.982
    # )  # Tokyo Station
    # print(result)
