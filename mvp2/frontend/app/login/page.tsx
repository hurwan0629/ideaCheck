// ============================================================
// app/login/page.tsx — 로그인 / 회원가입 페이지 (/login)
//
// 역할:
//   - 탭(tab) 상태로 로그인 폼과 회원가입 폼을 전환
//   - 로그인: 이메일 + 비밀번호 → authAPI.login() → 쿠키 저장 → /mypage
//   - 회원가입: 이름 + 이메일 + 비밀번호(확인) → authAPI.register() → 쿠키 저장 → /mypage
//   - 에러: 서버 응답의 detail 메시지를 상단 빨간 박스에 표시
//
// 소셜 로그인 (Google, 카카오):
//   - 버튼 UI만 구현됨, 실제 OAuth 연동은 미구현
//
// 상태 변수:
//   tab           — "login" | "signup" (탭 전환)
//   loading       — API 요청 중 버튼 비활성화 + 텍스트 변경
//   error         — 에러 메시지 표시 (빈 문자열이면 숨김)
//   loginEmail / loginPassword       — 로그인 폼 입력값
//   signupName / signupEmail / ...   — 회원가입 폼 입력값
// ============================================================

"use client"; // 훅(useState, useRouter) 사용으로 클라이언트 컴포넌트 필수

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { authAPI } from "@/lib/api";
import { saveAuth } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();

  // 탭 상태: "login" (기본) | "signup"
  const [tab, setTab] = useState<"login" | "signup">("login");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // ── 로그인 폼 상태 ────────────────────────────────────────
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");

  // ── 회원가입 폼 상태 ──────────────────────────────────────
  const [signupName, setSignupName] = useState("");
  const [signupEmail, setSignupEmail] = useState("");
  const [signupPassword, setSignupPassword] = useState("");
  const [signupPasswordConfirm, setSignupPasswordConfirm] = useState("");

  // ── 로그인 핸들러 ─────────────────────────────────────────
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await authAPI.login({ email: loginEmail, password: loginPassword });
      // 토큰과 유저 정보를 쿠키에 저장 (7일 유효)
      saveAuth(res.data.access_token, res.data.user);
      router.push("/mypage"); // 로그인 성공 → 마이페이지로 이동
    } catch (err: unknown) {
      // 서버 에러 메시지(detail) 또는 기본 메시지 표시
      const msg = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail;
      setError(msg || "로그인에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  };

  // ── 회원가입 핸들러 ───────────────────────────────────────
  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // 비밀번호 일치 여부 클라이언트 검증 (서버 요청 전에 먼저 확인)
    if (signupPassword !== signupPasswordConfirm) {
      setError("비밀번호가 일치하지 않습니다.");
      return;
    }

    setLoading(true);
    try {
      const res = await authAPI.register({
        name: signupName,
        email: signupEmail,
        password: signupPassword,
      });
      saveAuth(res.data.access_token, res.data.user);
      router.push("/mypage"); // 회원가입 성공 → 마이페이지로 이동
    } catch (err: unknown) {
      // 이메일 중복 등 서버 에러 처리
      const msg = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail;
      setError(msg || "회원가입에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="min-h-[calc(100vh-60px)] flex items-center justify-center p-10"
      style={{ background: "linear-gradient(160deg, #0f172a 0%, #1e3a5f 60%, #0f172a 100%)" }}
    >
      <div className="bg-white rounded-[20px] p-11 w-full max-w-[420px] shadow-2xl">
        {/* 로고 */}
        <div className="text-center text-2xl font-extrabold text-dark mb-1.5">
          S<span style={{ color: "var(--accent)" }}>Y</span>M
        </div>
        <div className="text-center text-[13px] text-sym-text-light mb-8">Search Your Market</div>

        {/* ── 탭 전환 버튼 ─────────────────────────────────
            활성 탭: 흰 배경 + 그림자 / 비활성 탭: 투명 배경 */}
        <div className="grid grid-cols-2 gap-1 bg-slate-100 rounded-[10px] p-1 mb-7">
          {(["login", "signup"] as const).map((t) => (
            <button
              key={t}
              onClick={() => { setTab(t); setError(""); }} // 탭 전환 시 에러 초기화
              className={`py-2 rounded-lg text-sm font-semibold transition-all cursor-pointer border-0 ${
                tab === t
                  ? "bg-white text-dark shadow-sm"
                  : "bg-transparent text-sym-text-light"
              }`}
            >
              {t === "login" ? "로그인" : "회원가입"}
            </button>
          ))}
        </div>

        {/* ── 에러 메시지 박스 ─────────────────────────────
            서버 에러 또는 비밀번호 불일치 시 표시 */}
        {error && (
          <div className="bg-red-50 text-red-600 text-[13px] px-4 py-2.5 rounded-lg mb-4 border border-red-200">
            {error}
          </div>
        )}

        {/* ── 로그인 폼 ─────────────────────────────────── */}
        {tab === "login" ? (
          <form onSubmit={handleLogin}>
            <div className="mb-4">
              <label className="form-label">이메일</label>
              <input
                type="email"
                className="form-input"
                placeholder="your@email.com"
                value={loginEmail}
                onChange={(e) => setLoginEmail(e.target.value)}
                required
              />
            </div>
            <div className="mb-2">
              <label className="form-label">비밀번호</label>
              <input
                type="password"
                className="form-input"
                placeholder="비밀번호 입력"
                value={loginPassword}
                onChange={(e) => setLoginPassword(e.target.value)}
                required
              />
            </div>
            <div className="text-right mb-5">
              {/* 비밀번호 찾기 — 미구현 */}
              <a href="#" className="text-[12px] text-sym-text-light hover:text-primary">
                비밀번호를 잊으셨나요?
              </a>
            </div>
            <button type="submit" className="btn-primary w-full text-[15px] py-3.5" disabled={loading}>
              {loading ? "로그인 중..." : "로그인"}
            </button>

            {/* 구분선 */}
            <div className="flex items-center gap-3 my-5 text-sym-text-light text-[12px]">
              <div className="flex-1 h-px bg-sym-border" />
              또는
              <div className="flex-1 h-px bg-sym-border" />
            </div>

            {/* 소셜 로그인 버튼 (UI만, OAuth 미구현) */}
            <a
              href="#"
              className="flex items-center justify-center gap-2.5 w-full py-3 border border-sym-border rounded-[10px] text-[14px] font-semibold text-sym-text bg-white hover:bg-sym-bg transition-colors no-underline mb-2.5"
            >
              <GoogleIcon /> Google로 계속하기
            </a>
            <a
              href="#"
              className="flex items-center justify-center gap-2.5 w-full py-3 border border-sym-border rounded-[10px] text-[14px] font-semibold text-sym-text bg-white hover:bg-sym-bg transition-colors no-underline"
            >
              <KakaoIcon /> 카카오로 계속하기
            </a>
          </form>
        ) : (
          /* ── 회원가입 폼 ────────────────────────────────── */
          <form onSubmit={handleSignup}>
            <div className="mb-4">
              <label className="form-label">이름</label>
              <input
                type="text"
                className="form-input"
                placeholder="홍길동"
                value={signupName}
                onChange={(e) => setSignupName(e.target.value)}
                required
              />
            </div>
            <div className="mb-4">
              <label className="form-label">이메일</label>
              <input
                type="email"
                className="form-input"
                placeholder="your@email.com"
                value={signupEmail}
                onChange={(e) => setSignupEmail(e.target.value)}
                required
              />
            </div>
            <div className="mb-4">
              <label className="form-label">비밀번호</label>
              <input
                type="password"
                className="form-input"
                placeholder="8자 이상"
                value={signupPassword}
                onChange={(e) => setSignupPassword(e.target.value)}
                minLength={8}
                required
              />
            </div>
            <div className="mb-5">
              <label className="form-label">비밀번호 확인</label>
              <input
                type="password"
                className="form-input"
                placeholder="비밀번호 재입력"
                value={signupPasswordConfirm}
                onChange={(e) => setSignupPasswordConfirm(e.target.value)}
                required
              />
            </div>
            <button type="submit" className="btn-primary w-full text-[15px] py-3.5" disabled={loading}>
              {loading ? "가입 중..." : "회원가입"}
            </button>

            {/* 로그인 탭으로 전환 링크 */}
            <div className="text-center mt-5 text-[13px] text-sym-text-light">
              이미 계정이 있으신가요?{" "}
              <button
                type="button"
                onClick={() => setTab("login")}
                className="text-primary font-semibold bg-transparent border-0 cursor-pointer"
              >
                로그인
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

// ── 소셜 로그인 아이콘 컴포넌트 ──────────────────────────────────
// SVG 인라인으로 직접 포함 (외부 이미지 의존성 없음)

/** Google 컬러 로고 아이콘 */
function GoogleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 48 48">
      <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z" />
      <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z" />
      <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z" />
      <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.18 1.48-4.97 2.31-8.16 2.31-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z" />
    </svg>
  );
}

/** 카카오 노란 로고 아이콘 */
function KakaoIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24">
      <rect width="24" height="24" rx="4" fill="#FEE500" />
      <path d="M12 5.5c-3.87 0-7 2.46-7 5.5 0 1.96 1.31 3.68 3.3 4.67l-.84 3.13 3.6-2.37c.3.04.62.07.94.07 3.87 0 7-2.46 7-5.5S15.87 5.5 12 5.5z" fill="#3A1D1D" />
    </svg>
  );
}
