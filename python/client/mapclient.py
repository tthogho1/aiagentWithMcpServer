from fastmcp import FastMCP
import asyncio
import json

async def main():
    client = FastMCP("google-maps-client")
    
    # 経路を計算する例
    origin = {"lat": 35.6814, "lng": 139.7670}  # 東京駅
    destination = {"lat": 35.6895, "lng": 139.7003}  # 新宿駅
    
    # toolメソッドを使用してdirectionsを呼び出す
    result = await client.tool(
        "directions",
        origin=json.dumps(origin),
        destination=json.dumps(destination),
        mode="driving"
    )

    print("経路計算結果:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())