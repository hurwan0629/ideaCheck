// ============================================================
// app/market-share/page.tsx — 시장 점유율 페이지 (/market-share)
//
// 역할:
//   - 국내 주요 산업의 시장 점유율을 시각화
//   - 산업 탭으로 전환 (IT/테크, 식음료, 핀테크, 헬스케어)
//
// 시각화 방식:
//   - 도넛 차트: CSS conic-gradient로 순수 CSS 구현 (외부 차트 라이브러리 불필요)
//   - 기업별 바 차트: CSS 너비(pct%)로 구현
//   - 성장/위축 세그먼트: 2열 미니 카드
//
// 데이터:
//   - 탭 전환 시 marketAPI.share(industry)로 데이터 요청
//   - 준비 중 탭(PENDING_TABS): API 요청 없이 "준비 중" 플레이스홀더 표시
//   - 수치 변동(change 필드) 색상: + → 초록, - → 빨강, ± → 회색
// ============================================================

"use client"; // useEffect, useState 사용으로 클라이언트 컴포넌트 필수

import { useEffect, useState } from "react";
import { marketAPI } from "@/lib/api";

// ── 타입 정의 ─────────────────────────────────────────────────

/** 도넛 차트의 각 조각 */
type Segment = { name: string; pct: number; change: string; color: string };

/** 기업별 바 차트 항목 */
type Company = { name: string; pct: number; change: string; color: string };

/** 성장/위축 미니 카드 항목 */
type StatItem = { name: string; value: string };

/** 백엔드 /api/market/share 응답 구조 */
type MarketData = {
  title: string;
  subtitle: string;
  total_size: string;
  segments: Segment[];   // 도넛 차트용 세그먼트 (pct 합계 100%)
  companies: Company[];  // 기업별 바 차트
  growing: StatItem[];   // 성장 세그먼트 목록
  shrinking: StatItem[]; // 위축 세그먼트 목록
};

// ── 상수 ─────────────────────────────────────────────────────

/** 산업 탭 목록 */
const TABS = [
  { id: "it",     label: "IT / 테크" },
  { id: "food",   label: "식음료" },
  { id: "fin",    label: "핀테크" },
  { id: "health", label: "헬스케어" },
];

/** 데이터가 아직 준비되지 않은 탭 ID 목록 */
const PENDING_TABS = ["food", "fin", "health"];

export default function MarketSharePage() {
  const [activeTab, setActiveTab] = useState("it"); // 기본 탭: IT
  const [data, setData] = useState<MarketData | null>(null);

  // 탭 변경 시 해당 산업 데이터 로드
  useEffect(() => {
    // 준비 중 탭은 API 요청 없이 null 유지 → "준비 중" 플레이스홀더 표시
    if (PENDING_TABS.includes(activeTab)) { setData(null); return; }
    marketAPI.share(activeTab)
      .then((res) => setData(res.data))
      .catch(() => {}); // 오류 시 null 유지 → 로딩 텍스트 표시
  }, [activeTab]);

  /**
   * 수치 변동 문자열(change)에 따른 색상 클래스 반환
   * "+3.1%" → green, "-2.1%" → red, "±0%" → gray
   */
  const changeColor = (v: string) =>
    v.startsWith("+") ? "text-green-500" : v.startsWith("-") ? "text-red-500" : "text-sym-text-light";

  return (
    <>
      {/* ── 히어로 헤더 바 ──────────────────────────────────── */}
      <div
        className="px-10 py-10 text-white"
        style={{ background: "linear-gradient(120deg, #1e293b, #1e3a5f)" }}
      >
        <h1 className="text-[28px] font-extrabold mb-1.5">시장 점유율 📊</h1>
        <p className="text-[#94a3b8] text-[14px]">국내 주요 산업의 시장 점유율 현황을 확인하세요</p>
        <div className="text-[12px] font-semibold mt-2" style={{ color: "var(--accent)" }}>
          ↑ 2026년 4월 기준 (분기별 업데이트)
        </div>
      </div>

      <div className="max-w-[1000px] mx-auto px-10 py-10">
        {/* ── 산업 탭 전환 버튼 ───────────────────────────────
            활성 탭: 파란 배경 / 비활성: 투명 배경 */}
        <div className="flex gap-1 mb-8 bg-white border border-sym-border rounded-xl p-1 w-fit">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-5 py-2 rounded-lg text-[14px] font-semibold cursor-pointer border-0 transition-all ${
                activeTab === tab.id ? "bg-primary text-white" : "bg-transparent text-sym-text-light hover:text-dark"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* ── 준비 중 탭 플레이스홀더 ─────────────────────────
            식음료, 핀테크, 헬스케어는 아직 데이터 미준비 */}
        {PENDING_TABS.includes(activeTab) ? (
          <div className="card text-center py-16">
            <div className="text-[40px] mb-4">
              {activeTab === "food" ? "🍽️" : activeTab === "fin" ? "💳" : "🏥"}
            </div>
            <div className="text-[18px] font-bold text-dark mb-2">
              {TABS.find((t) => t.id === activeTab)?.label} 시장 데이터 준비 중
            </div>
            <div className="text-[14px] text-sym-text-light">2026년 2분기 업데이트 예정</div>
          </div>
        ) : data ? (
          <>
            {/* ── 도넛 차트 + 범례 ──────────────────────────────
                CSS conic-gradient로 파이 차트 구현
                각 세그먼트의 시작 각도 = 이전 pct 합계 × 3.6° */}
            <div className="card mb-6">
              <div className="flex justify-between items-start mb-7">
                <div>
                  <div className="text-[18px] font-extrabold text-dark">{data.title}</div>
                  <div className="text-[13px] text-sym-text-light mt-1">{data.subtitle}</div>
                </div>
                <span className="tag text-[12px] py-1 px-3">{data.total_size}</span>
              </div>
              <div className="grid grid-cols-[240px_1fr] gap-10 items-center">
                {/* 도넛 차트 (CSS conic-gradient) */}
                <div className="flex justify-center">
                  <div className="relative w-[200px] h-[200px]">
                    <div
                      className="w-full h-full rounded-full flex items-center justify-center"
                      style={{
                        // 각 세그먼트의 시작/끝 각도를 계산해 conic-gradient 생성
                        background: `conic-gradient(${data.segments.map((s, i) => {
                          const prev = data.segments.slice(0, i).reduce((a, b) => a + b.pct, 0);
                          return `${s.color} ${prev * 3.6}deg ${(prev + s.pct) * 3.6}deg`;
                        }).join(", ")})`,
                      }}
                    >
                      {/* 도넛 구멍 (흰 원) */}
                      <div className="w-[110px] h-[110px] bg-white rounded-full flex flex-col items-center justify-center">
                        <div className="text-[22px] font-extrabold text-dark">{data.segments.length}개</div>
                        <div className="text-[11px] text-sym-text-light">주요 카테고리</div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* 범례: 세그먼트별 색상 + 이름 + 점유율 + 증감 */}
                <div className="flex flex-col gap-2.5">
                  {data.segments.map((seg) => (
                    <div key={seg.name} className="flex items-center gap-3 px-3.5 py-2.5 rounded-[10px] hover:bg-sym-bg transition-colors">
                      <div className="w-3 h-3 rounded-[3px] flex-shrink-0" style={{ background: seg.color }} />
                      <span className="text-[14px] font-semibold text-dark flex-1">{seg.name}</span>
                      <span className="text-[14px] font-extrabold text-dark">{seg.pct}%</span>
                      <span className={`text-[12px] font-bold w-[50px] text-right ${changeColor(seg.change)}`}>{seg.change}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* ── 기업별 점유율 바 차트 ─────────────────────────
                CSS width를 pct%로 설정하는 간단한 바 차트 */}
            <div className="card mb-6">
              <div className="text-[18px] font-extrabold text-dark mb-1.5">주요 기업별 점유율</div>
              <div className="text-[13px] text-sym-text-light mb-6">AI/클라우드 서비스 기업 기준</div>
              <div className="flex flex-col gap-3.5">
                {data.companies.map((co) => (
                  <div key={co.name} className="grid gap-4 items-center" style={{ gridTemplateColumns: "140px 1fr 60px 70px" }}>
                    <div className="text-[13px] font-semibold text-sym-text text-right">{co.name}</div>
                    {/* 바 차트 트랙 */}
                    <div className="bg-slate-100 rounded-full h-2.5 overflow-hidden">
                      <div className="h-full rounded-full" style={{ width: `${co.pct}%`, background: co.color }} />
                    </div>
                    <div className="text-[13px] font-bold text-dark">{co.pct}%</div>
                    <div className={`text-[12px] font-semibold ${changeColor(co.change)}`}>{co.change}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* ── 성장 / 위축 세그먼트 2열 카드 ───────────────── */}
            <div className="grid grid-cols-2 gap-5">
              {/* 성장 세그먼트 (초록 수치) */}
              <div className="card">
                <h3 className="text-[14px] font-bold text-sym-text-light mb-3.5 uppercase tracking-wide">성장률 상위 세그먼트</h3>
                {data.growing.map((item) => (
                  <div key={item.name} className="flex justify-between items-center py-2 border-b border-sym-border last:border-0 text-[13px]">
                    <span className="text-sym-text">{item.name}</span>
                    <span className="font-bold text-green-500">{item.value}</span>
                  </div>
                ))}
              </div>
              {/* 위축 세그먼트 (빨간 수치) */}
              <div className="card">
                <h3 className="text-[14px] font-bold text-sym-text-light mb-3.5 uppercase tracking-wide">시장 위축 세그먼트</h3>
                {data.shrinking.map((item) => (
                  <div key={item.name} className="flex justify-between items-center py-2 border-b border-sym-border last:border-0 text-[13px]">
                    <span className="text-sym-text">{item.name}</span>
                    <span className="font-bold text-red-500">{item.value}</span>
                  </div>
                ))}
              </div>
            </div>
          </>
        ) : (
          /* API 응답 대기 중 텍스트 */
          <div className="text-center py-20 text-sym-text-light">데이터 로딩 중...</div>
        )}
      </div>
    </>
  );
}
