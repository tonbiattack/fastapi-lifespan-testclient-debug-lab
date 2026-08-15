"""FastAPIのlifespanで共有カタログを初期化する最小アプリ。"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Request


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """アプリケーション起動時にだけ共有リソースを準備する。"""
    app.state.catalog = {"release": "2026.08"}
    yield
    del app.state.catalog


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health(request: Request) -> dict[str, str]:
    """共有カタログの初期化状態を利用したヘルスチェック。"""
    if not hasattr(request.app.state, "catalog"):
        raise HTTPException(
            status_code=503,
            detail="catalog is not initialized; lifespan has not started",
        )

    return {
        "status": "ready",
        "catalog_release": request.app.state.catalog["release"],
    }


def catalog_is_loaded() -> bool:
    """テストでライフサイクルの内外を観測するための補助関数。"""
    return hasattr(app.state, "catalog")
