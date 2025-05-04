import json
import sys
import subprocess
import dotenv
import select

# 環境変数を読み込む
dotenv.load_dotenv()

def read_stdin_with_timeout(timeout=5):
    rlist, _, _ = select.select([sys.stdin], [], [], timeout)
    if rlist:
        return sys.stdin.readline()
    else:
        print("Timeout: No input received")
        return None
    
def send_request(method, params):
    """MCPサーバーにリクエストを送信する関数"""
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    
    # リクエストをJSON形式で標準出力に書き込む
    json.dump(payload, sys.stdout)
    sys.stdout.write("\n")
    sys.stdout.flush()
    #json_str = json.dumps(payload)
    #sys.stdout.buffer.write(json_str.encode('utf-8'))
    #sys.stdout.buffer.write(b'\n')
    #sys.stdout.buffer.flush()
    input_data = read_stdin_with_timeout()
    if input_data:
        try:
            response = json.loads(input_data)
            print(response)
        except json.JSONDecodeError:
            print("Invalid JSON input")
    
    
    # レスポンスを標準入力から読み取る
    #response = json.loads(sys.stdin.readline())
    
    if "result" in response:
        return response["result"]
    elif "error" in response:
        print(f"エラーが発生しました: {response['error']}")
        return None
    else:
        print("不明なレスポンス形式です")
        return None

def get_route(origin, destination):
    """指定された出発地から目的地までのルートを取得する関数"""
    method = 'getRoute'
    params = {
        "origin": origin,
        "destination": destination
    }
    return send_request(method, params)

def main():
    # MCPサーバーを起動
    server_process = subprocess.Popen(
        ["npx", "-y", "@modelcontextprotocol/server-google-maps"],
        shell = True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    # 標準入出力をサーバープロセスにリダイレクト
    #sys.stdin = server_process.stdout
    #sys.stdout = server_process.stdin


    if server_process.poll() is None:
        print("Server process is still running")
    else:
        print("Server process has terminated")
        
    # 例: 東京駅から札幌までの行き方を検索
    origin = "東京駅"
    destination = "札幌"
    route = get_route(origin, destination)
    
    if route:
        print(f"{origin}から{destination}までのルート情報:")
        print(json.dumps(route, indent=2, ensure_ascii=False))
    else:
        print("ルート情報を取得できませんでした。")

    # サーバープロセスを終了
    server_process.terminate()

if __name__ == "__main__":
    main()
