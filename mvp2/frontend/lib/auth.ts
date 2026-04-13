// ============================================================
// lib/auth.ts — 인증 상태 관리 유틸리티
//
// 역할:
//   - JWT 토큰과 유저 정보를 쿠키에 저장/조회/삭제
//   - 컴포넌트에서 로그인 상태를 확인하는 헬퍼 함수 제공
//
// 저장 방식:
//   - 토큰  : Cookies.set("token", ..., { expires: 7 })  → 7일 유효
//   - 유저  : Cookies.set("user",  JSON.stringify(...))  → 7일 유효
//   - js-cookie 라이브러리 사용 (SSR/CSR 모두 동작)
//
// 주의:
//   - 쿠키에 저장된 user 정보는 캐시임. 최신 정보가 필요하면 authAPI.me() 호출
//   - 민감 정보(비밀번호 등)는 절대 저장하지 않음
// ============================================================

import Cookies from "js-cookie";

/** 유저 객체 타입 (백엔드 UserOut 스키마와 동일) */
export interface User {
  id: number;
  name: string;
  email: string;
  plan: "free" | "pro";
  monthly_analysis_count: number;
  created_at: string;
}

/**
 * 로그인 성공 후 토큰과 유저 정보를 쿠키에 저장.
 *
 * @param token  서버에서 받은 JWT 액세스 토큰
 * @param user   서버에서 받은 유저 정보 객체
 *
 * 사용 예:
 *   const res = await authAPI.login({ email, password });
 *   saveAuth(res.data.access_token, res.data.user);
 */
export function saveAuth(token: string, user: User) {
  Cookies.set("token", token, { expires: 7 }); // 7일 후 만료
  Cookies.set("user", JSON.stringify(user), { expires: 7 });
}

/**
 * 쿠키에서 유저 정보를 파싱해 반환.
 * 쿠키가 없거나 파싱 실패 시 null 반환.
 *
 * 사용 예:
 *   const user = getUser();
 *   if (user) console.log(user.name);
 */
export function getUser(): User | null {
  const raw = Cookies.get("user");
  if (!raw) return null;
  try {
    return JSON.parse(raw) as User;
  } catch {
    return null; // 잘못된 JSON이 저장된 경우 무시
  }
}

/**
 * 쿠키에서 JWT 토큰 반환. 없으면 null.
 * 직접 API 호출할 일이 있을 때 사용. 보통은 api.ts 인터셉터가 자동 처리.
 */
export function getToken(): string | null {
  return Cookies.get("token") ?? null;
}

/**
 * 로그아웃 처리. 쿠키에서 토큰과 유저 정보 삭제.
 *
 * 사용 예:
 *   const handleLogout = () => { logout(); router.push("/"); };
 */
export function logout() {
  Cookies.remove("token");
  Cookies.remove("user");
}

/**
 * 현재 로그인 여부 확인. 토큰 쿠키 존재 여부로만 판단.
 * 토큰 유효성(만료 등)은 서버 요청 시 인터셉터에서 확인됨.
 *
 * 사용 예:
 *   if (!isLoggedIn()) router.push("/login");
 */
export function isLoggedIn(): boolean {
  return !!Cookies.get("token");
}
