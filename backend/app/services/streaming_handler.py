"""
LangChain 스트리밍을 위한 커스텀 콜백 핸들러
"""
import json
import asyncio
from typing import Any, Dict, List, Optional, AsyncGenerator
from langchain.callbacks.base import AsyncCallbackHandler
from langchain.schema import LLMResult
import logging

logger = logging.getLogger(__name__)

class CurriculumStreamingHandler(AsyncCallbackHandler):
    """커리큘럼 생성을 위한 스트리밍 콜백 핸들러"""
    
    def __init__(self):
        self.tokens = []
        self.current_section = "introduction"
        self.sections = {
            "introduction": "커리큘럼을 생성하고 있습니다...",
            "planning": "학습 계획을 수립하고 있습니다...",
            "content": "주차별 내용을 작성하고 있습니다...",
            "finalization": "최종 검토 중입니다..."
        }
        self.queue = asyncio.Queue()
        self.finished = False
        
    async def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """LLM 시작 시 호출"""
        await self.queue.put({
            "type": "status",
            "message": "AI 커리큘럼 생성을 시작합니다...",
            "section": self.current_section
        })
        
    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """새 토큰이 생성될 때마다 호출"""
        self.tokens.append(token)
        
        # 토큰을 큐에 추가
        await self.queue.put({
            "type": "token",
            "content": token,
            "section": self.current_section
        })
        
        # 섹션 구분 (특정 키워드로 섹션 변경)
        full_text = "".join(self.tokens)
        if "주차별" in full_text and self.current_section == "introduction":
            self.current_section = "planning"
            await self.queue.put({
                "type": "section_change",
                "section": self.current_section,
                "message": self.sections[self.current_section]
            })
        elif "Week" in token or "주차" in token and self.current_section == "planning":
            self.current_section = "content"
            await self.queue.put({
                "type": "section_change", 
                "section": self.current_section,
                "message": self.sections[self.current_section]
            })
    
    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """LLM 완료 시 호출"""
        self.current_section = "finalization"
        await self.queue.put({
            "type": "section_change",
            "section": self.current_section,
            "message": self.sections[self.current_section]
        })
        
        # 완료 신호
        await self.queue.put({
            "type": "completed",
            "message": "커리큘럼 생성이 완료되었습니다!",
            "full_content": "".join(self.tokens)
        })
        self.finished = True
        
    async def on_llm_error(
        self, error: Exception, **kwargs: Any
    ) -> None:
        """LLM 에러 시 호출"""
        await self.queue.put({
            "type": "error",
            "message": f"생성 중 오류가 발생했습니다: {str(error)}"
        })
        self.finished = True
    
    async def get_stream(self) -> AsyncGenerator[Dict[str, Any], None]:
        """스트림 데이터를 비동기적으로 생성"""
        while not self.finished:
            try:
                # 0.1초 타임아웃으로 큐에서 데이터 가져오기
                data = await asyncio.wait_for(self.queue.get(), timeout=0.1)
                yield data
            except asyncio.TimeoutError:
                # 타임아웃 시 하트비트 전송
                yield {
                    "type": "heartbeat",
                    "timestamp": asyncio.get_event_loop().time()
                }
                continue
            except Exception as e:
                logger.error(f"스트리밍 에러: {str(e)}")
                yield {
                    "type": "error",
                    "message": str(e)
                }
                break
        
        # 스트림 종료 신호
        yield {
            "type": "stream_end",
            "message": "스트림이 종료되었습니다."
        }

class SimpleStreamingHandler(AsyncCallbackHandler):
    """간단한 스트리밍 핸들러 (디버깅용)"""
    
    def __init__(self):
        self.queue = asyncio.Queue()
        self.finished = False
        
    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """새 토큰 스트리밍"""
        await self.queue.put({
            "type": "token",
            "content": token
        })
        
    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """완료 신호"""
        await self.queue.put({
            "type": "completed"
        })
        self.finished = True
        
    async def get_stream(self) -> AsyncGenerator[Dict[str, Any], None]:
        """스트림 생성"""
        while not self.finished:
            try:
                data = await asyncio.wait_for(self.queue.get(), timeout=0.1)
                yield data
            except asyncio.TimeoutError:
                continue