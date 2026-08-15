# FastAPI lifespan と `TestClient` のデバッグラボ

この教材は、FastAPIアプリケーションの共有リソースを `lifespan` で初期化しているにもかかわらず、テストが `503 Service Unavailable` になる問題を再現し、`TestClient` をコンテキストマネージャとして使う最小修正を示します。原因はルート実装ではなく、テストがアプリケーションのlifespanを開始していないことです。

## 前提

| 項目 | 固定値 |
| --- | --- |
| Python | 3.11以上（検証: 3.12.3） |
| FastAPI | 0.141.1 |
| HTTPX | 0.28.1 |
| テスト | pytest 9.1.1 |
| 外部サービス | 使用しない |

## 修正済みの状態を検証する

デフォルトブランチは修正済みです。`with TestClient(app) as client:` がlifespanの開始・終了をテストの境界にします。

```bash
python3 observe.py
python3 -m pytest -q
```

| 観測対象 | 修正後の実測 |
| --- | --- |
| TestClient生成前 | カタログ未初期化 (`False`) |
| `with TestClient` の内部 | カタログ初期化済み (`True`) |
| `/health` のHTTPステータス | `200` |
| TestClient終了後 | カタログ後始末済み (`False`) |
| テスト | 2件成功 |

## 不具合状態を再現する

不具合状態のコミットでは、`TestClient(app)` を単独で生成して `/health` を呼びます。lifespanは開始されないため、共有カタログが未初期化のままです。

```bash
# 修正前: 503となり、1件のテストが失敗する
git checkout b175390
python3 observe.py
python3 -m pytest tests/test_health.py -q

# 修正後: 元の失敗テストを残したまま成功する
git checkout master
python3 observe.py
python3 -m pytest -q
```

## 構成

```text
.
├── app/main.py               # lifespanとヘルスチェック
├── tests/test_health.py      # 失敗ケースと回帰テスト
├── observe.py                # HTTP応答と状態の観測
├── evidence/                 # 修正前後の実行証拠
└── RESEARCH_NOTES.md         # 題材選定と一次資料
```

## このラボで守る契約

`lifespan` に置いた共有リソースは、アプリケーションがリクエストを受ける前に初期化され、終了時に後始末されます。FastAPIのテストでこの契約を検証する場合は、`TestClient` を `with` 文で使い、リクエストとアサーションをコンテキスト内に置きます。[1] [2]

## 参考資料

[1]: https://fastapi.tiangolo.com/advanced/testing-events/ "FastAPI: Testing Events: lifespan and startup - shutdown"
[2]: https://fastapi.tiangolo.com/advanced/events/ "FastAPI: Lifespan Events"
[3]: https://fastapi.tiangolo.com/tutorial/testing/ "FastAPI: Testing"
