// ============================================================
// lib/api.ts — 백엔드 API 호출 공통 함수
//
// 역할:
//   fetch()를 직접 쓰면 매번 에러 처리 코드를 반복해야 한다.
//   이 파일은 그 반복을 없애는 "래퍼(wrapper)" 함수를 제공한다.
//
// 사용 예시:
//   const report = await apiFetch<ReportRow>('/report/abc123')
//   const list   = await apiFetch<ReportRow[]>('/user/reports', {
//     headers: { Authorization: `Bearer ${token}` }
//   })
// ============================================================

// 환경변수에서 백엔드 URL을 읽는다. 없으면 로컬 개발 서버 주소 사용.
const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/**
 * 백엔드 API를 호출하고 결과를 반환한다.
 *
 * @param path    - API 경로 (예: '/report/abc123')
 * @param options - fetch 옵션 (method, headers, body 등)
 * @returns       - 응답 JSON을 T 타입으로 반환
 * @throws        - 응답이 실패(4xx, 5xx)이면 에러를 던진다
 *
 * 제네릭 <T>:
 *   반환 타입을 호출하는 쪽에서 지정할 수 있다.
 *   예) apiFetch<ReportRow>('/report/id') → ReportRow 타입으로 반환
 */
export async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers, // 추가 헤더가 있으면 병합 (예: Authorization)
    },
  });

  if (!res.ok) {
    // 에러 응답이면 메시지를 읽어서 에러로 던진다
    const msg = await res.text().catch(() => res.statusText);
    throw new Error(msg);
  }

  return res.json(); // 응답을 JSON으로 파싱해서 반환
}
