# 경쟁사 AI 종합 분석 생성 + 임베딩 벡터 저장.
#
# RAG (Retrieval Augmented Generation) 란?
#   "검색 기반 AI 생성" — AI에게 관련 정보를 미리 꺼내서 넣어주는 방식.
#
#   문제: 아이디어 분석 시 "DB에 있는 경쟁사 300개 정보를 전부 Claude에 넘겨" 라고 하면
#         비용 폭발 (토큰 = 돈) + 컨텍스트 한계 초과
#
#   해결: 텍스트를 숫자 벡터(embedding)로 변환해두고,
#         아이디어 입력 시 벡터 유사도로 "비슷한 경쟁사 Top-5"만 꺼내서 Claude에 전달
#         → 토큰 절감 + 더 정확한 분석
#
#   흐름:
#     [사전 작업] 경쟁사 정보 → 임베딩 → pgvector에 저장
#     [분석 시]  아이디어 → 임베딩 → pgvector에서 유사도 검색 → Top-K 경쟁사만 AI에 전달
#
# pgvector: PostgreSQL에 벡터 검색 기능을 추가하는 확장.
#   설치: pip install pgvector
#   공식문서: https://github.com/pgvector/pgvector-python
import json
import anthropic

from pgvector.sqlalchemy import Vector  # pgvector SQLAlchemy 타입

claude = anthropic.AsyncAnthropic()

# 임베딩 벡터 차원 수. 사용하는 모델에 따라 다름.
# Anthropic 임베딩 모델은 현재 없으므로 OpenAI text-embedding-3-small (1536차원) 사용 예정
# 또는 오픈소스 모델 (sentence-transformers 등) 사용 가능
EMBEDDING_DIM = 1536


async def generate_analyses_for_all() -> None:
    """
    DB에 등록된 전 경쟁사 종합 분석 생성.
    분기 quarterly_job에서 호출.
    """
    # 실제로는 DB에서 SELECT * FROM COMPETITORS
    competitor_ids = [1, 2, 3]  # 구조 파악용 더미

    for competitor_id in competitor_ids:
        await generate_analysis_for_one(competitor_id)


async def generate_analysis_for_one(competitor_id: int) -> None:
    """
    특정 경쟁사 1개 분석 생성.
    이벤트 트리거(재분석 큐)에서도 이 함수를 단건으로 호출.
    """
    # 1단계: 해당 경쟁사의 관련 데이터 수집 (DB에서)
    context = await _gather_competitor_context(competitor_id)

    # 2단계: Claude로 STRENGTH, WEAKNESS, CHARACTERISTIC 생성
    analysis = await _generate_with_ai(context)

    if not analysis:
        return

    # 3단계: COMPETITOR_ANALYSES에 새 행 저장 (UPDATE 없이 이력 보존)
    await _save_analysis(competitor_id, analysis)

    # 4단계: 임베딩 벡터 생성 후 pgvector에 저장 (RAG용)
    embedding_text = _build_embedding_text(context, analysis)
    embedding_vector = await _create_embedding(embedding_text)
    await _save_embedding(competitor_id, embedding_vector)


async def _gather_competitor_context(competitor_id: int) -> dict:
    """
    분석에 필요한 데이터를 DB에서 수집.
    COMPETITORS + COMPETITOR_FEATURES + 최근 COMPETITOR_POLICIES 취합.
    """
    # TODO: DB 세션으로 실제 데이터 조회
    return {
        "name": "토스",
        "description": "금융 슈퍼앱",
        "target_customer": "MZ세대 개인",
        "features": ["간편 송금", "투자", "보험"],
        "recent_policies": ["프리미엄 구독 도입", "동남아 진출"],
    }


async def _generate_with_ai(context: dict) -> dict | None:
    """
    Claude에게 경쟁사 정보를 주고 강점/약점/시장 특성 분석 요청.
    confidence + basis 포함해서 수치 근거 명시.
    """
    prompt = f"""
다음 경쟁사 정보를 분석해서 JSON으로만 답해줘.

경쟁사 정보:
{json.dumps(context, ensure_ascii=False, indent=2)}

답변 형식:
{{
  "strength": ["강점1", "강점2"],
  "weakness": ["약점1", "약점2"],
  "characteristic": {{
    "market_share": {{
      "estimated_pct": "10-20%",
      "confidence": "low",
      "basis": "추정 근거 (앱 리뷰 수, 언론 노출 등)"
    }},
    "growth": {{
      "yoy_pct": null,
      "trend": "up",
      "confidence": "medium",
      "basis": "성장 판단 근거"
    }},
    "keywords": ["키워드1", "키워드2"]
  }}
}}

실수치 데이터가 없으면 yoy_pct는 null로 두고 confidence를 low로 설정.
"""

    response = await claude.messages.create(
        model="claude-sonnet-4-6",  # 종합 분석은 더 정확한 Sonnet 사용
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    try:
        return json.loads(response.content[0].text)
    except json.JSONDecodeError:
        return None


def _build_embedding_text(context: dict, analysis: dict) -> str:
    """
    임베딩용 텍스트 구성.
    벡터 유사도 검색 시 "이 경쟁사가 어떤 회사인가"를 잘 담아야 정확한 매칭이 됨.
    description + target_customer + 강점 + 약점 + 키워드를 합쳐서 하나의 문자열로.
    """
    parts = [
        context.get("description", ""),
        f"타겟 고객: {context.get('target_customer', '')}",
        f"강점: {', '.join(analysis.get('strength', []))}",
        f"약점: {', '.join(analysis.get('weakness', []))}",
        f"키워드: {', '.join(analysis.get('characteristic', {}).get('keywords', []))}",
    ]
    return " | ".join(filter(None, parts))


async def _create_embedding(text: str) -> list[float]:
    """
    텍스트 → 숫자 벡터(임베딩) 변환.

    임베딩이란?
      "세무 자동화 앱"과 "자동 세금 신고" 같은 비슷한 의미의 텍스트가
      벡터 공간에서 가까운 위치에 놓이게 변환하는 것.
      벡터 간 거리(코사인 유사도)로 "얼마나 비슷한가"를 수치로 계산 가능.

    OpenAI Embeddings API 사용 예시:
      공식문서: https://platform.openai.com/docs/guides/embeddings
    """
    # 실제 구현 예시 (OpenAI):
    # import openai
    # client = openai.AsyncOpenAI()
    # response = await client.embeddings.create(
    #     model="text-embedding-3-small",
    #     input=text,
    # )
    # return response.data[0].embedding  # 1536차원 float 리스트

    return [0.0] * EMBEDDING_DIM  # 구조 파악용 더미 벡터


async def _save_analysis(competitor_id: int, analysis: dict) -> None:
    """COMPETITOR_ANALYSES에 새 행 저장."""
    # TODO: DB 세션 열어서 INSERT
    pass


async def _save_embedding(competitor_id: int, vector: list[float]) -> None:
    """
    pgvector에 임베딩 벡터 저장.
    실제로는 COMPETITOR_ANALYSES 행에 vector 컬럼을 추가하거나
    별도 임베딩 테이블을 만들어서 저장.

    pgvector 쿼리 예시 (아이디어 분석 시 유사도 검색):
      SELECT competitor_id, embedding <=> :query_vector AS distance
      FROM competitor_embeddings
      ORDER BY distance
      LIMIT 5;
      (<=> 연산자: 코사인 거리. 0에 가까울수록 유사)
    """
    # TODO: DB 세션 열어서 upsert
    pass
