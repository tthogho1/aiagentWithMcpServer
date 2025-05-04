const { MCPClient } = require('@modelcontextprotocol/client');

async function main() {
  // MCP クライアントの初期化
  const client = new MCPClient();

  try {
    // 利用可能なツールのリストを取得
    const tools = await client.listTools();
    console.log('利用可能なツール:', tools);

    // 'searchNearby' ツールを使用する例
    if (tools.searchNearby) {
      const searchResult = await client.execute('searchNearby', {
        location: '東京駅',
        radius: 1000,
        keyword: 'レストラン'
      });
      console.log('検索結果:', searchResult);
    }

    // 'getDirections' ツールを使用する例
    if (tools.getDirections) {
      const directionsResult = await client.execute('getDirections', {
        origin: '東京駅',
        destination: '秋葉原駅',
        mode: 'transit'
      });
      console.log('経路案内結果:', directionsResult);
    }

  } catch (error) {
    console.error('エラーが発生しました:', error);
  }
}

main();
