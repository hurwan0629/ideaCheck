# 이벤트 트리거 기반 재분석 큐.
# "정책 변경이 많은 경쟁사"를 분기까지 기다리지 않고 즉시 재분석하기 위한 대기열.
#
# 구현 방식: 메모리 내 set (Python 기본 자료구조)
#   - 장점: 별도 인프라 없이 간단
#   - 단점: 서버 재시작 시 큐가 초기화됨
#   - 개선안: 나중에 Redis나 DB 테이블로 교체하면 영속성 확보 가능
#     Redis 예시: https://redis.io/docs/data-types/sets/

# 재분석 대기 중인 competitor_id 집합
# set: 중복 없는 집합 자료구조. 같은 경쟁사가 여러 번 들어와도 1번만 처리됨.
reanalysis_queue: set[int] = set()


def add_to_queue(competitor_id: int) -> None:
    """
    재분석 대기열에 경쟁사 추가.
    policy_detector.py에서 정책 변경 임계치 초과 시 호출.
    """
    reanalysis_queue.add(competitor_id)


async def consume_reanalysis_queue() -> None:
    """
    큐에 쌓인 경쟁사를 모두 즉시 재분석하고 큐를 비움.
    매일 daily_job 마지막 단계에서 호출.
    """
    # import 순환 참조 방지를 위해 함수 안에서 import
    from app.collector.processors.analysis_generator import generate_analysis_for_one

    if not reanalysis_queue:
        return  # 큐가 비어있으면 아무것도 안 함

    # 처리할 목록을 복사 후 큐를 먼저 비움
    # (처리 도중 새 항목이 들어와도 이번 사이클에서 처리 안 함)
    targets = list(reanalysis_queue)
    reanalysis_queue.clear()

    for competitor_id in targets:
        # 각 경쟁사 개별 분석 (분기 전체 재분석과 동일한 함수, 단건으로 호출)
        await generate_analysis_for_one(competitor_id)
