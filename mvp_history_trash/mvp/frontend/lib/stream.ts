// ============================================================
// lib/stream.ts — SSE 스트리밍 읽기 유틸
//
// 역할:
//   백엔드 /analyze에서 오는 SSE(Server-Sent Events) 응답을
//   읽어서 콜백 함수로 전달한다.
//
// SSE란?
//   서버가 응답을 한 번에 보내지 않고 조금씩 여러 번 보내는 방식.
//   AI가 글을 생성하면서 타이핑 효과를 내려면 이 방식이 필요하다.
//
// SSE 데이터 형식 (백엔드에서 보내는 형태):
//   event: status\ndata: 검색 중...\n\n
//   event: chunk\ndata: {"summ\n\n
//   event: chunk\ndata: ary": "...\n\n
//   event: done\ndata: {"report_id": "uuid"}\n\n
// ============================================================

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface StreamCallbacks {
  onStatus?: (msg: string) => void;  // 상태 메시지 수신 시 호출 (예: "검색 중...")
  onChunk?: (chunk: string) => void; // AI 응답 조각 수신 시 호출
}

/**
 * 백엔드 /analyze에 POST 요청을 보내고 SSE 스트림을 읽는다.
 *
 * @param path      - API 경로 (예: '/analyze')
 * @param body      - 요청 데이터 (topic, target, revenue_model)
 * @param callbacks - 이벤트별 콜백 함수
 * @returns         - 분석 완료 후 report_id 반환. 실패 시 null.
 */
export async function readStream(
  path: string,
  body: Record<string, unknown>,
  callbacks: StreamCallbacks
): Promise<string | null> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.body) return null;

  // ReadableStream으로 응답을 조금씩 읽는다
  const reader = res.body.getReader();
  const decoder = new TextDecoder(); // 바이트 → 문자열 변환
  let buffer = "";  // 미완성 이벤트를 임시 보관
  let reportId: string | null = null;

  while (true) {
    const { done, value } = await reader.read(); // 다음 조각 읽기
    if (done) break; // 스트림 끝

    // 바이트를 문자열로 변환 (stream:true = 다음 조각과 연결 가능)
    buffer += decoder.decode(value, { stream: true });

    // "\n\n" 기준으로 완성된 이벤트 단위로 분리
    const events = buffer.split("\n\n");
    // 마지막 요소는 아직 완성 안 된 것일 수 있으므로 버퍼에 남김
    buffer = events.pop() ?? "";

    for (const evt of events) {
      // 이벤트 이름 파싱 (예: "event: status" → "status")
      const eventLine = evt.match(/^event: (\w+)/m)?.[1];
      // 데이터 파싱 (예: "data: 검색 중..." → "검색 중...")
      const dataLine = evt.match(/^data: (.+)/m)?.[1];
      if (!eventLine || !dataLine) continue;

      if (eventLine === "status") callbacks.onStatus?.(dataLine);
      if (eventLine === "chunk") callbacks.onChunk?.(dataLine);
      if (eventLine === "done") {
        // 완료 이벤트에서 report_id 추출
        try { reportId = JSON.parse(dataLine).report_id; } catch {}
      }
    }
  }

  return reportId;
}
