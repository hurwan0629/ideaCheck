// ============================================================
// app/popular-keywords/page.tsx — 인기 검색어 페이지 (/popular-keywords)
//
// 역할:
//   - 사용자들이 많이 검색하는 사업 아이디어 키워드를 시각화
//   - 태그 클라우드, 카테고리별 인기도 바, 실시간 순위 사이드바 표시
//
// 구성:
//   - (메인) 태그 클라우드: size(1~5)에 따라 글자 크기/색상 차별화
//   - (메인) 카테고리별 키워드: 각 키워드의 상대적 인기도 바
//   - (사이드바) 실시간 1~10위 순위 + 등락 배지 (▲상승 / ▼하락 / 유지 / NEW)
//
// 데이터:
//   - 마운트 시 keywordsAPI.get() 호출 → 실패 시 FALLBACK 사용
//   - 개인정보 보호: 정확한 수치 없이 상대적 수준(level, pct)만 표시
// ============================================================

"use client"; // useEffect, useState 사용으로 클라이언트 컴포넌트 필수

import { useEffect, useState } from "react";
import { keywordsAPI } from "@/lib/api";

// ── 타입 정의 ─────────────────────────────────────────────────
type CloudTag  = { keyword: string; size: number }; // size: 1(최대) ~ 5(최소)
type RankItem  = { rank: number; keyword: string; change: "up" | "down" | "same" | "new" };
type CatKeyword = { name: string; level: string; pct: number; color: string };

type KeywordsData = {
  cloud: CloudTag[];
  ranking: RankItem[];
  categories: Record<string, CatKeyword[]>; // 카테고리명 → 키워드 배열
};

// ── 상수: UI 스타일 매핑 ──────────────────────────────────────

/**
 * size 숫자 → 태그 클라우드 글자 크기 + 배경/글자색 클래스
 * size 1이 가장 크고 인기 있음, 5가 가장 작음
 */
const SIZE_STYLES: Record<number, string> = {
  1: "text-[22px] bg-blue-50 text-blue-700",
  2: "text-[18px] bg-emerald-50 text-emerald-700",
  3: "text-[15px] bg-yellow-50 text-yellow-700",
  4: "text-[13px] bg-purple-50 text-purple-700",
  5: "text-[12px] bg-slate-100 text-sym-text-light",
};

/** 1~3위 특별 색상, 나머지는 회색 */
const RANK_COLOR: Record<number, string> = {
  1: "text-red-500",
  2: "text-yellow-500",
  3: "text-primary",
};

/** 등락 배지 스타일 + 레이블 */
const CHANGE_BADGE: Record<string, { cls: string; label: string }> = {
  up:   { cls: "bg-emerald-50 text-emerald-700", label: "▲ 상승" },
  down: { cls: "bg-red-50 text-red-600",         label: "▼ 하락" },
  same: { cls: "bg-slate-100 text-sym-text-light", label: "— 유지" },
  new:  { cls: "bg-blue-50 text-primary",          label: "NEW" },
};

/** 백엔드 없이도 동작하는 폴백 데이터 */
const FALLBACK: KeywordsData = {
  cloud: [
    { keyword: "AI 서비스",    size: 1 }, { keyword: "1인 가구",   size: 2 }, { keyword: "구독 모델",  size: 1 },
    { keyword: "배달앱",       size: 3 }, { keyword: "건강식",     size: 2 }, { keyword: "반려동물",  size: 4 },
    { keyword: "친환경",       size: 3 }, { keyword: "노코드",     size: 2 }, { keyword: "중고거래",  size: 4 },
    { keyword: "SaaS",         size: 1 }, { keyword: "홈트레이닝", size: 3 }, { keyword: "시니어",    size: 4 },
    { keyword: "에듀테크",     size: 2 }, { keyword: "세컨드브레인", size: 5 }, { keyword: "뷰티테크", size: 3 },
  ],
  ranking: [
    { rank: 1,  keyword: "AI 기반 서비스",  change: "up" },
    { rank: 2,  keyword: "1인 가구 타겟",   change: "same" },
    { rank: 3,  keyword: "구독 서비스",      change: "up" },
    { rank: 4,  keyword: "친환경 비즈니스", change: "new" },
    { rank: 5,  keyword: "반려동물 서비스", change: "up" },
    { rank: 6,  keyword: "시니어 케어",      change: "up" },
    { rank: 7,  keyword: "소상공인 솔루션", change: "same" },
    { rank: 8,  keyword: "에듀테크",         change: "down" },
    { rank: 9,  keyword: "핀테크",           change: "same" },
    { rank: 10, keyword: "크리에이터 경제", change: "new" },
  ],
  categories: {
    "💻 IT / 테크": [
      { name: "AI 서비스",  level: "매우 높음", pct: 90, color: "#2563eb" },
      { name: "SaaS",       level: "높음",      pct: 70, color: "#2563eb" },
      { name: "노코드",     level: "중간",      pct: 55, color: "#2563eb" },
      { name: "스마트홈",   level: "보통",      pct: 40, color: "#2563eb" },
    ],
    "🍽️ 식음료": [
      { name: "구독 배달",  level: "매우 높음", pct: 85, color: "#10b981" },
      { name: "건강식",     level: "높음",      pct: 72, color: "#10b981" },
      { name: "밀키트",     level: "중간",      pct: 60, color: "#10b981" },
      { name: "비건",       level: "보통",      pct: 35, color: "#10b981" },
    ],
    "🏃 헬스 / 라이프": [
      { name: "홈트레이닝", level: "높음",      pct: 78, color: "#f59e0b" },
      { name: "반려동물",   level: "높음",      pct: 65, color: "#f59e0b" },
      { name: "시니어케어", level: "중간",      pct: 50, color: "#f59e0b" },
      { name: "웰니스",     level: "보통",      pct: 42, color: "#f59e0b" },
    ],
    "📚 교육 / 커리어": [
      { name: "에듀테크",   level: "높음",      pct: 68, color: "#8b5cf6" },
      { name: "원격학습",   level: "중간",      pct: 55, color: "#8b5cf6" },
      { name: "AI 튜터",    level: "높음",      pct: 80, color: "#8b5cf6" },
      { name: "코딩교육",   level: "보통",      pct: 44, color: "#8b5cf6" },
    ],
  },
};

export default function PopularKeywordsPage() {
  // FALLBACK을 초기값으로 → 백엔드 없어도 즉시 렌더
  const [data, setData] = useState<KeywordsData>(FALLBACK);

  // 마운트 시 API에서 최신 키워드 데이터 가져오기
  useEffect(() => {
    keywordsAPI.get()
      .then((res) => setData(res.data))
      .catch(() => {}); // 실패 시 FALLBACK 유지
  }, []);

  return (
    <>
      {/* ── 히어로 헤더 바 ──────────────────────────────────── */}
      <div
        className="px-10 py-10 text-white"
        style={{ background: "linear-gradient(120deg, #1e293b, #1e3a5f)" }}
      >
        <h1 className="text-[28px] font-extrabold mb-1.5">인기 검색어 🔍</h1>
        <p className="text-[#94a3b8] text-[14px]">사람들이 어떤 사업 아이디어를 많이 찾아보는지 대략적으로 확인하세요</p>
        <div className="text-[12px] font-semibold mt-2" style={{ color: "var(--accent)" }}>
          ↑ 2026년 4월 12일 실시간 업데이트
        </div>
        {/* 개인정보 보호 안내 배너 */}
        <div className="mt-3 inline-block text-[12px] px-3 py-1 rounded-md" style={{ background: "rgba(245,158,11,0.15)", border: "1px solid rgba(245,158,11,0.3)", color: "#fbbf24" }}>
          ⚠️ 구체적인 수치는 개인정보 보호를 위해 표시하지 않습니다
        </div>
      </div>

      <div className="max-w-[1000px] mx-auto px-10 py-10">
        {/* 메인(좌) + 사이드바(우) 2열 레이아웃 */}
        <div className="grid grid-cols-[1fr_320px] gap-6">
          {/* ── 메인 콘텐츠 ───────────────────────────────────── */}
          <div>
            {/* 태그 클라우드 카드 */}
            <div className="card mb-5">
              <h2 className="text-[16px] font-extrabold text-dark mb-5">🏷️ 이번 주 검색 키워드 클라우드</h2>
              <div className="flex flex-wrap gap-2.5">
                {data.cloud.map((tag) => (
                  /* size 숫자에 따라 글자 크기와 색상이 다름 */
                  <span
                    key={tag.keyword}
                    className={`px-4 py-2 rounded-full font-bold cursor-pointer hover:scale-105 transition-transform ${SIZE_STYLES[tag.size] || SIZE_STYLES[5]}`}
                  >
                    {tag.keyword}
                  </span>
                ))}
              </div>
            </div>

            {/* 카테고리별 인기도 카드 */}
            <div className="card">
              <h2 className="text-[16px] font-extrabold text-dark mb-5">📁 카테고리별 인기 키워드</h2>
              <div className="grid grid-cols-2 gap-3">
                {Object.entries(data.categories).map(([catName, keywords]) => (
                  <div key={catName} className="border border-sym-border rounded-[14px] p-4">
                    <div className="text-[13px] font-bold text-sym-text-light mb-3">{catName}</div>
                    <div className="flex flex-col gap-1.5">
                      {keywords.map((kw) => (
                        <div key={kw.name} className="flex items-center text-[13px]">
                          <span className="text-dark font-medium w-24">{kw.name}</span>
                          {/* 상대적 인기도 프로그레스 바 */}
                          <div className="flex-1 h-1.5 bg-slate-100 rounded-full mx-2.5 overflow-hidden">
                            <div className="h-full rounded-full" style={{ width: `${kw.pct}%`, background: kw.color }} />
                          </div>
                          {/* 수치 없이 레벨 텍스트만 표시 (개인정보 보호) */}
                          <span className="text-sym-text-light text-[11px] w-14 text-right">{kw.level}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* ── 사이드바: 실시간 순위 ────────────────────────── */}
          <div>
            <div className="bg-white border border-sym-border rounded-[20px] overflow-hidden">
              <div className="px-6 py-5 border-b border-sym-border flex justify-between items-center">
                <h2 className="text-[15px] font-extrabold text-dark">🏆 실시간 인기 주제</h2>
                <span className="text-[12px] text-sym-text-light">최근 7일</span>
              </div>

              {/* 1~10위 순위 목록 */}
              {data.ranking.map((item) => {
                const badge = CHANGE_BADGE[item.change];
                return (
                  <div key={item.rank} className="flex items-center px-6 py-3.5 border-b border-sym-border last:border-0 gap-3.5 hover:bg-sym-bg transition-colors">
                    {/* 순위 번호 (1~3위는 색상 강조) */}
                    <div className={`w-6 text-center text-[14px] font-extrabold flex-shrink-0 ${RANK_COLOR[item.rank] || "text-[#94a3b8]"}`}>
                      {item.rank}
                    </div>
                    <div className="flex-1 text-[14px] font-semibold text-dark">{item.keyword}</div>
                    {/* 등락 배지 */}
                    <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full ${badge.cls}`}>
                      {badge.label}
                    </span>
                  </div>
                );
              })}
            </div>

            {/* 개인정보 보호 안내 박스 */}
            <div className="mt-4 p-4 bg-white border border-sym-border rounded-[14px] text-[12px] text-sym-text-light leading-[1.6]">
              <strong className="text-dark block mb-1.5">📌 안내</strong>
              개인 식별이 가능한 구체적인 수치는 공개하지 않습니다. 표시된 데이터는 상대적 인기도만 나타냅니다.
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
