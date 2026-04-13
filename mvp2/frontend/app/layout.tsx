// ============================================================
// app/layout.tsx — Next.js 루트 레이아웃
//
// 역할:
//   - 모든 페이지를 감싸는 공통 HTML 구조 정의
//   - <html>, <body> 태그를 여기서만 선언 (각 페이지에서는 선언 불가)
//   - Navbar와 Footer를 모든 페이지에 공통 적용
//   - SEO 메타데이터(title, description) 기본값 설정
//
// 구조:
//   <html>
//     <body class="flex flex-col min-h-screen">
//       <Navbar />          ← 상단 고정 네비게이션
//       <main>{children}</main> ← 각 페이지 내용
//       <Footer />          ← 하단 푸터
//     </body>
//   </html>
//
// globals.css:
//   Tailwind 지시어(@tailwind) + CSS 변수(--primary, --accent 등) + 공통 컴포넌트 스타일
// ============================================================

import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/layout/Footer";

// ── SEO 메타데이터 ────────────────────────────────────────────
// Next.js가 자동으로 <head>에 <title>, <meta name="description"> 생성
export const metadata: Metadata = {
  title: "SYM — Search Your Market",
  description: "AI 기반 시장 분석 플랫폼. 아이디어 검증부터 경쟁사 분석까지.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      {/*
        min-h-screen: 콘텐츠가 짧아도 화면 전체를 채움
        flex flex-col: Navbar, main, Footer를 세로로 배치
        Footer를 항상 최하단에 고정하기 위해 main에 flex-1 적용
      */}
      <body className="flex flex-col min-h-screen">
        <Navbar />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
