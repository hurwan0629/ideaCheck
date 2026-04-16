from sqlalchemy.orm import Session

# 메모리 내 set으로 관리. 서버 재시작 시 초기화됨.
# 추후 Redis나 DB 테이블로 교체하면 영속성 확보 가능.
reanalysis_queue: set[int] = set()


def add_to_queue(competitor_id: int) -> None:
    """재분석 대기열에 경쟁사 추가. policy_detector에서 임계치 초과 시 호출."""
    reanalysis_queue.add(competitor_id)


def consume_reanalysis_queue(db: Session) -> None:
    """
    큐에 쌓인 경쟁사를 모두 재분석하고 큐를 비움.
    매일 daily_job 마지막 단계에서 호출.
    """
    from app.collector.processors.analysis_generator import generate_analysis_for_one

    if not reanalysis_queue:
        return

    # 처리 목록을 복사 후 큐 먼저 비움 (처리 중 새로 들어온 항목은 다음 사이클에 처리)
    targets = list(reanalysis_queue)
    reanalysis_queue.clear()

    # targets는 최근ㄷ에 3번 이상 변경된 경쟁사들의 id 목록(int)
    for competitor_id in targets:
        generate_analysis_for_one(db, competitor_id)
