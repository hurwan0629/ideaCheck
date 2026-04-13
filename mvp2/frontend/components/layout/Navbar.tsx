// ============================================================
// components/layout/Navbar.tsx — 전체 공통 네비게이션 바
//
// 역할:
//   - 상단 고정(sticky) 네비게이션 바 렌더링
//   - 로그인 상태에 따라 우측 버튼 변경
//     · 비로그인: 마이페이지, 요금제, [로그인] 버튼
//     · 로그인:   마이페이지, 요금제, [로그아웃] 버튼
//   - 현재 경로(pathname)에 따라 활성 링크 스타일 적용
//
// 상태 감지:
//   - pathname이 바뀔 때마다 getUser()를 재호출해 로그인 상태 갱신
//   - 쿠키 기반이므로 SSR 없이도 클라이언트에서 즉시 반영
// ============================================================

"use client"; // 쿠키 읽기 및 라우터 사용을 위해 클라이언트 컴포넌트 선언

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getUser, logout, type User } from "@/lib/auth";

export default function Navbar() {
  const pathname = usePathname(); // 현재 경로 (활성 링크 판별용)
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);

  // pathname이 바뀔 때마다 로그인 상태 갱신
  // (로그인/로그아웃 후 다른 페이지로 이동했을 때 즉시 반영됨)
  useEffect(() => {
    setUser(getUser());
  }, [pathname]);

  const handleLogout = () => {
    logout();          // 쿠키에서 토큰 + 유저 삭제
    router.push("/");  // 랜딩 페이지로 이동
  };

  // 현재 경로와 일치하면 활성 스타일 적용하는 네비게이션 링크 생성 헬퍼
  const navLink = (href: string, label: string) => (
    <Link
      href={href}
      className={`nav-link ${pathname === href ? "text-white bg-white/10" : ""}`}
    >
      {label}
    </Link>
  );

  return (
    <nav
      style={{ background: "var(--nav-bg)" }}
      className="px-10 h-[60px] flex items-center justify-between sticky top-0 z-50"
    >
      {/* 로고 */}
      <Link href="/" className="text-white text-xl font-extrabold no-underline tracking-tight">
        S<span style={{ color: "var(--accent)" }}>Y</span>M
      </Link>

      {/* 중앙 네비게이션: 공개 페이지 링크 */}
      <div className="flex gap-2">
        {navLink("/trend", "요즘 트렌드")}
        {navLink("/market-share", "시장 점유율")}
        {navLink("/popular-keywords", "인기 검색어")}
      </div>

      {/* 우측: 로그인 상태에 따라 분기 */}
      <div className="flex gap-2 items-center">
        {user ? (
          // ── 로그인 상태 ──────────────────────────────────────
          <>
            {navLink("/mypage", "마이페이지")}
            {navLink("/pricing", "요금제")}
            <button
              onClick={handleLogout}
              className="text-[#94a3b8] text-sm px-3.5 py-1.5 rounded-md border border-white/10 hover:bg-white/5 hover:text-white transition-all cursor-pointer bg-transparent"
            >
              로그아웃
            </button>
          </>
        ) : (
          // ── 비로그인 상태 ─────────────────────────────────────
          <>
            {navLink("/mypage", "마이페이지")}
            {navLink("/pricing", "요금제")}
            <Link
              href="/login"
              className="bg-primary text-white text-sm px-3.5 py-1.5 rounded-lg hover:bg-primary-dark transition-colors no-underline font-semibold"
            >
              로그인
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}
