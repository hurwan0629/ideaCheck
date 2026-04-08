// ============================================================
// lib/format.ts — 데이터 변환 유틸
//
// 역할:
//   백엔드에서 받은 JSON 데이터를 화면에 표시하기 좋은 형태로 바꾼다.
//   타입 안전성을 위해 명시적인 타입 변환도 함께 수행한다.
// ============================================================

/**
 * 리포트 result JSON을 화면 렌더링용 구조로 변환한다.
 *
 * 백엔드 result는 jsonb로 저장된 자유 형식이라 타입이 불확실하다.
 * 이 함수로 변환하면 컴포넌트에서 안전하게 사용할 수 있다.
 *
 * @param result - DB의 reports.result (jsonb → any 딕셔너리)
 */
export function formatReport(result: Record<string, any>) {
  return {
    summary: result.summary ?? "",          // 없으면 빈 문자열로 처리
    competitors: (result.competitors ?? []) as {
      name: string;
      description: string;
      url?: string;       // 선택: 경쟁사 URL
      strength?: string;  // 선택: 강점
      weakness?: string;  // 선택: 약점
    }[],
    marketSize: result.market_size ?? {},   // TAM, SAM, SOM 등
    actionPlan: (result.action_plan ?? []) as string[],  // 실행 단계 목록
    sources: (result.sources ?? []) as string[],         // 참고 URL 목록
  };
}

/**
 * ISO 8601 날짜 문자열을 한국어 형식으로 변환한다.
 *
 * 예) "2026-04-08T10:30:00Z" → "2026년 4월 8일"
 *
 * @param iso - ISO 8601 형식의 날짜 문자열
 */
export function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}
