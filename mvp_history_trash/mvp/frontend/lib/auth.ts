// ============================================================
// lib/auth.ts — Supabase 인증 헬퍼
//
// 역할:
//   로그인, 회원가입, 로그아웃, 세션 조회 함수를 제공한다.
//   Supabase Auth를 직접 쓰는 대신 이 파일을 통해 접근한다.
//
// createBrowserClient:
//   클라이언트(브라우저)에서만 동작하는 Supabase 클라이언트.
//   "use client" 컴포넌트에서 사용한다.
//
// 환경변수:
//   NEXT_PUBLIC_SUPABASE_URL      → Supabase 프로젝트 URL
//   NEXT_PUBLIC_SUPABASE_ANON_KEY → 공개용 키 (프론트에서 써도 됨)
// ============================================================

import { createBrowserClient } from "@supabase/ssr";

/** Supabase 클라이언트를 생성해서 반환한다. */
function getClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,       // ! : 반드시 있다고 단언 (없으면 런타임 에러)
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}

/**
 * 이메일 + 비밀번호로 로그인한다.
 * @returns 에러 메시지 문자열, 성공 시 null
 */
export async function signIn(email: string, password: string): Promise<string | null> {
  const { error } = await getClient().auth.signInWithPassword({ email, password });
  return error?.message ?? null; // 에러가 없으면 null 반환
}

/**
 * 이메일 + 비밀번호로 회원가입한다.
 * 성공하면 Supabase가 인증 이메일을 자동으로 보낸다.
 * @returns 에러 메시지 문자열, 성공 시 null
 */
export async function signUp(email: string, password: string): Promise<string | null> {
  const { error } = await getClient().auth.signUp({ email, password });
  return error?.message ?? null;
}

/** 로그아웃한다. 세션 쿠키가 삭제된다. */
export async function signOut() {
  await getClient().auth.signOut();
}

/**
 * 현재 세션 정보를 반환한다.
 * 로그인 상태가 아니면 null을 반환한다.
 */
export async function getSession() {
  const { data } = await getClient().auth.getSession();
  return data.session; // session이 null이면 비로그인 상태
}
