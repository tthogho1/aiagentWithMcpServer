import asyncio
import json
import sys
import logging
import subprocess
from typing import Optional, Dict, Any
import dotenv

class GoogleMapsMCPClient:
    def __init__(self):
        """
        Google Maps MCP Serverクライアントの初期化
        """
        # 環境変数を読み込む
        dotenv.load_dotenv()
        # ロギングの設定
        logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # サーバープロセスの管理
        self.server_process = None
        self.stdin = None
        self.stdout = None
        self.stderr = None

    async def start_server(self):
        """
        Google Maps MCPサーバーを起動
        """
        try:
            # npxでサーバーを起動
            self.server_process = await asyncio.create_subprocess_exec(
                'node', '-e', 
                'require("@modelcontextprotocol/server-google-maps")',
                shell=False,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.stdin = self.server_process.stdin
            self.stdout = self.server_process.stdout
            self.stderr = self.server_process.stderr
            
            self.logger.info("Google Maps MCPサーバーを起動しました。")
        except Exception as e:
            self.logger.error(f"サーバー起動中にエラーが発生しました: {e}")
            raise

    async def send_message(self, message: Dict[str, Any]):
        """
        サーバーにメッセージを送信
        
        :param message: 送信するメッセージ（辞書形式）
        """
        try:
            # JSONに変換して送信
            json_message = json.dumps(message) + '\n'
            self.stdin.write(json_message.encode())
            await self.stdin.drain()
            self.logger.info(f"送信メッセージ: {json_message.strip()}")
        except Exception as e:
            self.logger.error(f"メッセージ送信中にエラーが発生しました: {e}")

    async def receive_message(self) -> Optional[Dict[str, Any]]:
        """
        サーバーからメッセージを受信
        
        :return: 受信したメッセージ（辞書形式）
        """
        try:
            # 標準出力から1行読み取り
            message_line = await self.stdout.readline()
            if not message_line:
                return None
            
            # JSONをパース
            message = json.loads(message_line.decode().strip())
            self.logger.info(f"受信メッセージ: {message}")
            return message
        except json.JSONDecodeError:
            self.logger.error("無効なJSON形式のメッセージを受信")
            return None
        except Exception as e:
            self.logger.error(f"メッセージ受信中にエラーが発生しました: {e}")
            return None

    async def connect(self):
        """
        Google Maps MCP Serverに接続
        """
        try:
            # 接続開始メッセージの送信
            await self.send_message({
                "type": "connect",
                "protocol": "google-maps-mcp",
                "version": "1.0"
            })

            # 接続確認メッセージの待機
            response = await self.receive_message()
            if response and response.get('type') == 'connected':
                self.logger.info("Google Maps MCP Serverに正常に接続しました。")
                return True
            else:
                self.logger.error("サーバー接続に失敗しました。")
                return False
        except Exception as e:
            self.logger.error(f"接続中にエラーが発生しました: {e}")
            return False

    async def request_location(self, query: str):
        """
        特定の場所の情報をリクエスト
        
        :param query: 検索するロケーション
        """
        try:
            await self.send_message({
                "type": "location_request",
                "query": query
            })

            # レスポンスの待機
            response = await self.receive_message()
            if response and response.get('type') == 'location_response':
                # 受信したロケーション情報の処理
                location_info = response.get('location', {})
                self.logger.info(f"ロケーション情報: {location_info}")
                return location_info
            else:
                self.logger.warning("ロケーション情報の取得に失敗しました。")
                return None
        except Exception as e:
            self.logger.error(f"ロケーションリクエスト中にエラーが発生しました: {e}")
            return None

    async def main_loop(self):
        """
        メインの対話ループ
        """
        try:
            # サーバーを起動
            await self.start_server()

            # サーバーに接続
            if not await self.connect():
                return

            # サンプルリクエスト
            await self.request_location("東京タワー")

            # 継続的なメッセージ処理
            while True:
                # サーバーからのメッセージを待機
                message = await self.receive_message()
                if not message:
                    break

                # メッセージの種類に応じた処理
                if message.get('type') == 'location_update':
                    self.logger.info(f"ロケーション更新: {message}")
                elif message.get('type') == 'error':
                    self.logger.error(f"サーバーエラー: {message}")

        except Exception as e:
            self.logger.error(f"メインループでエラーが発生しました: {e}")
        finally:
            # 切断メッセージの送信
            await self.send_message({
                "type": "disconnect",
                "reason": "normal_closure"
            })
            
            # サーバープロセスの終了
            if self.server_process:
                self.server_process.terminate()
                await self.server_process.wait()

async def main():
    """
    Google Maps MCP Serverクライアントの実行
    """
    client = GoogleMapsMCPClient()
    await client.main_loop()

if __name__ == '__main__':
    # asyncioを使用してメインの非同期関数を実行
    asyncio.run(main())
