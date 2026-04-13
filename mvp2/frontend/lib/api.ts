// ============================================================
// lib/api.ts — Axios 인스턴스 및 API 호출 함수 모음
//
// 역할:
//   - baseURL, 인터셉터가 설정된 axios 인스턴스 생성
//   - 요청 인터셉터: 쿠키에서 토큰을 읽어 Authorization 헤더에 자동 첨부
//   - 응답 인터셉터: 401 응답 시 자동 로그아웃 + 로그인 페이지 리다이렉트
//   - 각 도메인별 API 함수 그룹(authAPI, analyzeAPI, ...)을 export
//
// Next.js의 next.config.ts에서 /api/* → http://localhost:8000/api/*
// 로 프록시되므로 baseURL은 그냥 "/api"로 설정
// ============================================================

import axios from "axios";
import Cookies from "js-cookie";

// ── Axios 인스턴스 생성 ──────────────────────────────────────
const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
});

// ── 요청 인터셉터 ─────────────────────────────────────────────
// 모든 요청이 나가기 전에 실행됨
// 쿠키에 토큰이 있으면 Authorization: Bearer <token> 헤더 자동 추가
api.interceptors.request.use((config) => {
  const token = Cookies.get("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ── 응답 인터셉터 ─────────────────────────────────────────────
// 서버 응답이 오면 실행됨
// 401 (인증 실패): 쿠키 삭제 + 로그인 페이지로 강제 이동
api.interceptors.response.use(
  (res) => res, // 성공 응답은 그대로 통과
  (err) => {
    if (err.response?.status === 401) {
      Cookies.remove("token");
      Cookies.remove("user");
      // 브라우저 환경에서만 리다이렉트 (SSR 환경 방어)
      if (typeof window !== "undefined") window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export default api;

// ============================================================
// 도메인별 API 함수 그룹
// 컴포넌트에서는 직접 axios를 사용하지 않고 아래 함수들을 사용
// ============================================================

// ── 인증 API ─────────────────────────────────────────────────
export const authAPI = {
  /** 회원가입. 성공 시 { access_token, user } 반환 */
  register: (data: { name: string; email: string; password: string }) =>
    api.post("/auth/register", data),

  /** 로그인. 성공 시 { access_token, user } 반환 */
  login: (data: { email: string; password: string }) =>
    api.post("/auth/login", data),

  /** 현재 로그인 유저 정보 조회 */
  me: () => api.get("/auth/me"),
};

// ── 분석 API ─────────────────────────────────────────────────
export const analyzeAPI = {
  /** 아이디어 AI 분석 요청. 분석 결과 포함한 Analysis 객체 반환 */
  create: (data: Record<string, string>) => api.post("/analyze/idea", data),

  /** 내 분석 히스토리 목록 조회 (최신순) */
  history: () => api.get("/analyze/history"),

  /** 특정 분석 결과 조회 */
  get: (id: number) => api.get(`/analyze/${id}`),

  /** 분석 결과 삭제 */
  delete: (id: number) => api.delete(`/analyze/${id}`),

  /** 선호도 기반 맞춤 아이디어 4개 추천 */
  findIdea: (prefs: Record<string, unknown>) =>
    api.post("/analyze/find-idea", prefs),
};

// ── 아이디어 노트 API ─────────────────────────────────────────
export const ideasAPI = {
  /** 아이디어 노트 목록 조회 */
  list: () => api.get("/ideas/"),

  /** 새 아이디어 노트 생성 */
  create: (data: { title: string; body?: string }) =>
    api.post("/ideas/", data),

  /** 아이디어 노트 수정 (PATCH — 보낸 필드만 업데이트) */
  update: (id: number, data: Record<string, unknown>) =>
    api.patch(`/ideas/${id}`, data),

  /** 아이디어 노트 삭제 */
  delete: (id: number) => api.delete(`/ideas/${id}`),
};

// ── 트렌드 API ────────────────────────────────────────────────
export const trendsAPI = {
  /** 트렌드 목록 조회. category 파라미터로 필터링 가능 */
  get: (category?: string) =>
    api.get("/trends/", { params: category ? { category } : {} }),
};

// ── 시장 점유율 API ───────────────────────────────────────────
export const marketAPI = {
  /** 특정 산업의 시장 점유율 데이터 조회. industry 기본값: "it" */
  share: (industry = "it") =>
    api.get("/market/share", { params: { industry } }),
};

// ── 인기 검색어 API ───────────────────────────────────────────
export const keywordsAPI = {
  /** 태그 클라우드 + 랭킹 + 카테고리별 데이터 조회 */
  get: () => api.get("/keywords/"),
};
