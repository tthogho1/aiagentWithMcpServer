import subprocess

def start_server():
    try:
        # npxコマンドを実行してサーバーを起動
        server_process = subprocess.Popen(
            ["npx", "-y", "@modelcontextprotocol/server-google-maps"],
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        # サーバーの標準出力をリアルタイムで読み取る
        for line in server_process.stdout:
            print(f"STDOUT: {line.strip()}")

    except FileNotFoundError as e:
        print(f"FileNotFoundError: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    start_server()
