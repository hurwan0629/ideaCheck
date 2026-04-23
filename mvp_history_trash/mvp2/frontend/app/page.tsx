// ============================================================
// app/page.tsx — 랜딩 페이지 (/)
//
// 역할:
//   - 서비스 소개 및 진입 페이지
//   - 히어로 섹션: 핵심 메시지 + CTA 카드 2개
//   - 통계 섹션: 서비스 누적 수치 4개
//   - 기능 소개 섹션: 주요 기능 3개 카드
//
// 참고:
//   - 서버 컴포넌트 (Server Component) — "use client" 없음
//   - 정적 컨텐츠만 있어 SSG(Static Site Generation)로 빌드됨
//   - 히어로 배경: linear-gradient + radial-gradient 조합으로 다크 글로우 효과
// ============================================================

import Link from "next/link";

export default function Home() {
  return (
    <>
      {/* ── 히어로 섹션 ─────────────────────────────────────────
          - 전체 화면 높이에서 Navbar(60px)를 뺀 높이로 설정
          - 다크 그라디언트 배경 + 중앙 파란 글로우 효과 */}
      <section
        className="min-h-[calc(100vh-60px)] flex flex-col items-center justify-center px-10 py-20 text-center relative overflow-hidden"
        style={{ background: "linear-gradient(160deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%)" }}
      >
        {/* 중앙 파란 글로우 배경 (장식용, pointer-events-none으로 클릭 무시) */}
        <div
          className="absolute w-[600px] h-[600px] rounded-full top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none"
          style={{ background: "radial-gradient(circle, rgba(37,99,235,0.15) 0%, transparent 70%)" }}
        />

        {/* 서비스 태그 배지 */}
        <div
          className="inline-block px-4 py-1.5 rounded-full text-[13px] mb-7 relative"
          style={{
            background: "rgba(6,182,212,0.15)",
            border: "1px solid rgba(6,182,212,0.3)",
            color: "var(--accent)",
          }}
        >
          AI 기반 시장 분석 플랫폼
        </div>

        {/* 메인 헤드라인 */}
        <h1 className="text-[56px] font-extrabold text-white leading-[1.1] mb-5 tracking-tight relative">
          당신의 아이디어,<br />
          <span style={{ color: "var(--accent)" }}>시장에서 검증</span>하세요
        </h1>

        {/* 서브 설명 */}
        <p className="text-[18px] text-[#94a3b8] max-w-[520px] leading-[1.7] mb-12 relative">
          생각 중인 사업 아이디어를 입력하면<br />
          경쟁사 분석부터 차별화 전략까지 AI가 정리해드립니다
        </p>

        {/* CTA 카드 2개: 아이디어 구상하기 / 지금 분석하기 */}
        <div className="grid grid-cols-2 gap-4 max-w-[640px] w-full relative">
          {/* CTA 카드 1: 아이디어 구상 (/find-idea) */}
          <Link
            href="/find-idea"
            className="no-underline rounded-2xl p-7 text-left transition-all duration-300 hover:-translate-y-0.5 hover:bg-white/10 hover:border-white/20"
            style={{
              background: "rgba(255,255,255,0.05)",
              border: "1px solid rgba(255,255,255,0.1)",
            }}
          >
            <div
              className="w-11 h-11 rounded-xl flex items-center justify-center text-xl mb-3.5"
              style={{ background: "rgba(6,182,212,0.2)" }}
            >
              💡
            </div>
            <h3 className="text-white text-[15px] font-bold mb-1.5">아이디어가 없나요?</h3>
            <p className="text-[#94a3b8] text-[13px] leading-[1.5] m-0">
              관심사 기반으로 사업 아이디어를 함께 구상해드립니다
            </p>
            <span className="inline-flex items-center gap-1 text-[13px] font-semibold mt-3" style={{ color: "var(--accent)" }}>
              아이디어 구상하기 →
            </span>
          </Link>

          {/* CTA 카드 2: 아이디어 분석 (/analyze) */}
          <Link
            href="/analyze"
            className="no-underline rounded-2xl p-7 text-left transition-all duration-300 hover:-translate-y-0.5 hover:bg-white/10 hover:border-white/20"
            style={{
              background: "rgba(255,255,255,0.05)",
              border: "1px solid rgba(255,255,255,0.1)",
            }}
          >
            <div
              className="w-11 h-11 rounded-xl flex items-center justify-center text-xl mb-3.5"
              style={{ background: "rgba(37,99,235,0.2)" }}
            >
              🔍
            </div>
            <h3 className="text-white text-[15px] font-bold mb-1.5">아이디어를 분석해보세요</h3>
            <p className="text-[#94a3b8] text-[13px] leading-[1.5] m-0">
              비즈니스 모델을 입력하고 경쟁사와 시장을 분석받으세요
            </p>
            <span className="inline-flex items-center gap-1 text-[13px] font-semibold mt-3" style={{ color: "var(--accent)" }}>
              지금 분석하기 →
            </span>
          </Link>
        </div>
      </section>

      {/* ── 통계 섹션 ──────────────────────────────────────────
          - 서비스 누적 수치 4개를 가로로 나열
          - 실제 서비스에서는 백엔드 API에서 동적으로 불러올 수 있음 */}
      <section className="py-16 bg-white border-b border-sym-border">
        <div className="max-w-[960px] mx-auto grid grid-cols-4 gap-8 text-center px-10">
          {[
            { num: "12,400+", label: "누적 분석 건수" },
            { num: "8,200+",  label: "분석된 경쟁사" },
            { num: "340+",    label: "산업 카테고리" },
            { num: "4.8★",    label: "사용자 만족도" },
          ].map((s) => (
            <div key={s.label}>
              <div className="text-[36px] font-extrabold text-primary">{s.num}</div>
              <div className="text-[14px] text-sym-text-light mt-1">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── 기능 소개 섹션 ─────────────────────────────────────
          - 주요 기능 3가지를 카드로 나열
          - hover 시 살짝 위로 뜨는 애니메이션 */}
      <section className="py-20 max-w-[960px] mx-auto px-10">
        <h2 className="section-title">왜 SYM인가요?</h2>
        <p className="section-sub">아이디어 검증부터 경쟁사 분석까지, 창업의 첫걸음을 도와드립니다</p>
        <div className="grid grid-cols-3 gap-5">
          {[
            {
              icon: "🧠",
              title: "AI 기반 아이디어 분석",
              desc: "PRD, 비즈니스 캔버스 형식으로 아이디어를 정리하고 강점/약점을 자동으로 분석합니다",
            },
            {
              icon: "📊",
              title: "실시간 경쟁사 분석",
              desc: "국내외 유사 서비스의 가격, 타겟 고객, 핵심 기능을 한눈에 비교해드립니다",
            },
            {
              icon: "📈",
              title: "시장 트렌드 리포트",
              desc: "요즘 뜨는 키워드와 시장 점유율 변화를 실시간으로 확인할 수 있습니다",
            },
          ].map((f) => (
            <div key={f.title} className="card hover:-translate-y-0.5 hover:shadow-lg transition-all duration-200">
              <div className="w-12 h-12 rounded-xl bg-blue-50 flex items-center justify-center text-[22px] mb-4">
                {f.icon}
              </div>
              <h3 className="text-[16px] font-bold mb-2 text-dark">{f.title}</h3>
              <p className="text-[14px] text-sym-text-light leading-[1.6]">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}
