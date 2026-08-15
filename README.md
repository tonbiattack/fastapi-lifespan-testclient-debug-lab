# FastAPI lifespan と `TestClient` のデバッグラボ

この教材は、FastAPIアプリケーションの共有リソースを `lifespan` で初期化しているにもかかわらず、テストが `503 Service Unavailable` になる問題を再現します。原因はルート実装ではなく、`TestClient` をコンテキストマネージャとして起動していないことです。

## 前提

| 項目 | 固定値 |
| --- | --- |
| Python | 3.11以上（検証: 3.12.3） |
| FastAPI | 0.141.1 |
| HTTPX | 0.28.1 |
| テスト | pytest 9.1.1 |
| 外部サービス | 使用しない |

## 不具合状態を再現する

修正前コミットでは、`TestClient(app)` を生成するだけで `/health` を呼びます。lifespanは開始されないため、共有カタログが未初期化のままです。

```bash
python3 observe.py
python3 -m pytest tests/test_health.py -q
```

期待する観測は次のとおりです。

| 観測対象 | 不具合状態 |
| --- | --- |
| `/health` のHTTPステータス | `503` |
| 応答のdetail | `catalog is not initialized; lifespan has not started` |
| `catalog_is_loaded()` | リクエスト前後ともに `False` |
| テスト | 1失敗、1成功 |

## 構成

```text
.
├── app/main.py               # lifespanとヘルスチェック
├── tests/test_health.py      # 失敗する振る舞いテスト
├── observe.py                # HTTP応答と状態の観測
├── evidence/                 # 実行済みの観測証拠
└── RESEARCH_NOTES.md         # 題材選定と一次資料
```

## 修正後の確認

修正後は、`TestClient` を `with` 文で使い、lifespanの開始・終了をテストの境界として扱います。元の失敗テストを残し、全テストを成功させます。

## 参考資料

- [FastAPI: Testing Events](https://fastapi.tiangolo.com/advanced/testing-events/)
- [FastAPI: Lifespan Events](https://fastapi.tiangolo.com/advanced/events/)
