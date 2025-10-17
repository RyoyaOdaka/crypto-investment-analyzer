import redis.asyncio as redis
import json
from typing import Optional, Any
from app.core.config import settings


class RedisService:
    """Redisキャッシングサービス"""

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None

    async def connect(self):
        """Redisに接続"""
        self.redis_client = await redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )

    async def disconnect(self):
        """Redis接続を切断"""
        if self.redis_client:
            await self.redis_client.close()

    async def get(self, key: str) -> Optional[Any]:
        """キャッシュから値を取得"""
        if not self.redis_client:
            return None

        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Redis GET error: {e}")
            return None

    async def set(self, key: str, value: Any, expire: int = 60):
        """キャッシュに値を設定（デフォルト60秒）"""
        if not self.redis_client:
            return False

        try:
            await self.redis_client.setex(
                key,
                expire,
                json.dumps(value, default=str)
            )
            return True
        except Exception as e:
            print(f"Redis SET error: {e}")
            return False

    async def delete(self, key: str):
        """キャッシュから値を削除"""
        if not self.redis_client:
            return False

        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Redis DELETE error: {e}")
            return False


# グローバルインスタンス
redis_service = RedisService()
