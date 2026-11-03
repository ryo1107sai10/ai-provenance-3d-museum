# AI Provenance Platform — Pro Spec

社内AI研修動画 真正性公証（Provenance）＆ 3D殿堂ミュージアム
原典: 企画提案書 + 実装指示書 (2026-11, ユーザー提供)

## 構成
- `contracts/VideoProvenanceRegistry.sol` — Solidity 0.8.20, Polygon Amoy (Chain ID 80002)
  存在証明・先後関係・重複防止に特化。pHash候補検索 / pause / admin移譲を追加したプロ版。
- `backend/notary_pipeline.py` — SHA-256 + pHash 算出
- `backend/record_to_blockchain.py` — 元の実装指示書の刻印スクリプト（web3.py, システムウォレット代理実行）
- Webアプリ本体 — Muse上の「AI Provenance 3D Museum」(fullstack artifact)
  Three.js 3Dホール、実SHA-256計算、重複チェック、verifyByHash相当の照会、証明書表示を実装。

## デプロイ手順 (Amoy, 無料検証)
1. Remix IDE でコントラクトを 0.8.20 でコンパイル → Injected Provider - MetaMask → Amoyへデプロイ
2. Polygon Faucet でテストMATIC取得
3. `.env` に RPC_URL / CONTRACT_ADDRESS / SYSTEM_WALLET_ADDRESS / SYSTEM_PRIVATE_KEY を設定
   ※ 秘密鍵は Secrets Manager / 環境変数のみ。Git・フロントに絶対に入れない
4. `pip install -r backend/requirements.txt` 後、`record_to_blockchain.py` の
   `notarize_video_artifact()` を生成パイプラインから呼ぶ
5. 返却 `explorerUrl` (amoy.polygonscan.com) で VideoNotarized イベントを確認

## 本番移行時の注意
- pHash は ffmpeg でキーフレーム抽出 → imagehash.phash に差し替えること（現フォールバックは仮）
- Mainnet 移行時はガス・鍵管理・監査を別途実施

## デプロイ（決定: GitHub Pages / Vercelは使わない）
- 公開URL（予定）: https://ryo1107sai10.github.io/ai-provenance-3d-museum/
- 方式: `frontend/` の静的ビルドを GitHub Actions (`.github/workflows/deploy-pages.yml`) で Pages へ自動デプロイ（mainへpushで発動）
- リポジトリは Public（無料プランの Pages 要件）
- 台帳データはスタンドアロン版ではブラウザ保存（localStorage/IndexedDB）。オンチェーン刻印は backend/ + contracts/ を使用
