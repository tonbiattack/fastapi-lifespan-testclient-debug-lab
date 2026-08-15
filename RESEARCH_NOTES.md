# FastAPI TestClientとlifespanの題材選定メモ

## 採用題材

**`TestClient(app)` を生成するだけではlifespanが起動せず、共有リソースへ依存するエンドポイントがテストで失敗する。`with TestClient(app) as client:` がライフサイクル開始・終了の境界になる**というFastAPI固有のテスト契約を扱う。

| 観点 | 内容 |
| --- | --- |
| 対象 | Python 3.11以上、FastAPI、`fastapi.testclient.TestClient`、pytest |
| 期待 | テスト中の `/health` が、lifespanで初期化した共有リソースを読み `{"status": "ready"}` を返す |
| 実際 | `TestClient(app)` を単独で作るとlifespan未実行のため、リソースが未初期化になり `503` を返す |
| 根本原因 | TestClientの生成と、アプリケーションのlifespan開始・終了は同じ操作ではない |
| 最小修正 | `with TestClient(app) as client:` のコンテキスト内でリクエストとアサーションを実行する |

## 既存題材との差分

既存のFastAPI下書きには、`if patch.completed:` が明示した `false` を落とす部分更新の問題と、FastAPI・MySQLで在庫数を直接更新して履歴を失う問題がある。前者は**入力値の真偽値と未指定の区別**、後者は**更新意味論・台帳・並行更新**を扱う。

今回の題材は、**テストハーネスがアプリケーションlifespanを開始・終了させる条件**を扱う。発火条件、観測対象、修正箇所が既存題材と異なる。既存の公開・非公開記事で `TestClient` または `lifespan` を中心に扱う記事は確認できなかった。

## 一次資料で確認した事実

1. FastAPIのlifespan文書は、`yield` より前の処理をアプリケーションがリクエストを受ける前に一度実行し、後ろの処理をアプリケーションの処理終了後に実行すると説明している。共有リソースの初期化と後始末が主な用途である。
2. FastAPIの「Testing Events」文書は、テストでlifespanを実行したい場合に `with TestClient(app) as client:` を使う例を示している。withブロックの内部でlifespanが開始し、ブロックを抜けると終了・後始末が実行される。
3. FastAPIのテスト文書は、`fastapi.testclient.TestClient` がStarlette由来であり、通常のpytest関数からHTTPリクエストを送れると説明している。

## 参考資料

- [FastAPI: Testing Events: lifespan and startup - shutdown](https://fastapi.tiangolo.com/advanced/testing-events/)
- [FastAPI: Lifespan Events](https://fastapi.tiangolo.com/advanced/events/)
- [FastAPI: Testing](https://fastapi.tiangolo.com/tutorial/testing/)

## 検証する仮説

| 仮説 | 予測 | 最小実験 | 判定基準 |
| --- | --- | --- | --- |
| A. ルート実装の不備 | lifesp​​an開始後も `503` | `with TestClient` で `/health` を呼ぶ | `200` なら棄却 |
| B. `TestClient` の単独生成でもlifespanが開始する | 単独生成でも `200` | `TestClient(app)` で `/health` を呼ぶ | `503` なら棄却 |
| C. `with TestClient` がlifespan境界である | with内で `200`、with後に未初期化 | withの内外で状態を観測する | 期待どおりなら採用 |

作成日: 2026-08-15
