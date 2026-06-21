"""
API 키 관리
안전한 API 키 저장 및 접근 관리
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class APIKeyManager:
    """API 키 관리자"""

    def __init__(self):
        self._api_key: Optional[str] = None
        self._load_from_env()

    def _load_from_env(self):
        """환경 변수에서 API 키 로드"""
        self._api_key = os.getenv("ANTHROPIC_API_KEY")

    def get_api_key(self) -> str:
        """API 키 반환"""
        if not self._api_key:
            raise ValueError(
                "API 키가 설정되지 않았습니다. "
                ".env 파일에 ANTHROPIC_API_KEY를 설정하거나 "
                "환경 변수로 설정해주세요."
            )
        return self._api_key

    def set_api_key(self, api_key: str):
        """API 키 설정 (개발용)"""
        if not api_key or not api_key.strip():
            raise ValueError("유효하지 않은 API 키입니다.")
        self._api_key = api_key.strip()

    def validate_api_key(self) -> bool:
        """API 키 유효성 검사"""
        try:
            key = self.get_api_key()
            return len(key) > 0 and key.startswith("sk-ant-")
        except (ValueError, AttributeError):
            return False

    def mask_api_key(self, api_key: Optional[str] = None) -> str:
        """API 키 마스킹 (로깅용)"""
        key = api_key or self._api_key
        if not key:
            return "Not set"
        if len(key) <= 10:
            return "*" * len(key)
        return f"{key[:7]}...{key[-4:]}"

    def get_safe_key_info(self) -> dict:
        """안전한 API 키 정보 반환"""
        try:
            return {
                "is_set": bool(self._api_key),
                "key_preview": self.mask_api_key(),
                "key_length": len(self._api_key) if self._api_key else 0,
                "is_valid_format": self.validate_api_key()
            }
        except Exception as e:
            return {
                "is_set": False,
                "key_preview": "Error",
                "key_length": 0,
                "is_valid_format": False,
                "error": str(e)
            }


# 전역 API 키 관리자 인스턴스
api_key_manager = APIKeyManager()


if __name__ == "__main__":
    # API 키 관리자 테스트
    manager = APIKeyManager()

    print("🔑 API 키 상태:")
    info = manager.get_safe_key_info()
    for key, value in info.items():
        print(f"  {key}: {value}")

    if info["is_valid_format"]:
        print("✅ API 키가 올바른 형식입니다.")
    else:
        print("❌ API 키가 올바르지 않은 형식입니다.")
        print("   .env 파일에 ANTHROPIC_API_KEY를 설정해주세요.")