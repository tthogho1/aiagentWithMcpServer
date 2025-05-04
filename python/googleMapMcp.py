from fastmcp import FastMCP
import httpx
from dotenv import load_dotenv
import os
import asyncio
import sys

mcp = FastMCP("route-client")
load_dotenv()

print("スクリプトが開始されました。")
print(f"APIキー: {os.getenv('GOOGLE_MAPS_API_KEY')}")

@mcp.tool()
async def calculate_route(origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float) -> dict:
    origin = {"latitude": origin_lat, "longitude": origin_lng}
    destination = {"latitude": dest_lat, "longitude": dest_lng}
    print(f"ルート計算: {origin} から {destination}")
    
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": os.getenv("GOOGLE_MAPS_API_KEY"),
        "X-Goog-FieldMask": "routes.distanceMeters,routes.duration,routes.polyline.encodedPolyline"
    }
    payload = {
        "origin": {
            "location": {
                "latLng": origin
            }
        },
        "destination": {
            "location": {
                "latLng": destination
            }
        },
        "travelMode": "DRIVE",
        "routingPreference": "TRAFFIC_AWARE",
        "computeAlternativeRoutes": False,
        "routeModifiers": {
            "avoidTolls": False,
            "avoidHighways": False,
            "avoidFerries": False,
        },
        "languageCode": "ja-JP",
        "units": "METRIC"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
    return response.json()

async def main():
    if len(sys.argv) == 5:
        origin_lat = float(sys.argv[1])
        origin_lng = float(sys.argv[2])
        dest_lat = float(sys.argv[3])
        dest_lng = float(sys.argv[4])
        result = await calculate_route(origin_lat, origin_lng, dest_lat, dest_lng)
        print("ルート計算結果:")
        print(result)
    else:
        print("使用方法: python googleMapMcp.py <出発地の緯度> <出発地の経度> <目的地の緯度> <目的地の経度>")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        asyncio.run(main())
    else:
        print("FastMCPサーバーモードで起動します。")
        mcp.run(transport="stdio")