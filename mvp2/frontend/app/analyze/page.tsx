// ============================================================
// app/analyze/page.tsx — 아이디어 분석 페이지 (/analyze)
//
// 역할:
//   - 비즈니스 아이디어를 입력받아 AI가 분석한 결과를 표시
//   - view 상태로 "입력 화면" ↔ "결과 화면" 전환
//
// 입력 섹션 (view === "input"):
//   - 기본 정보: 서비스명, 카테고리, 한 줄 소개, 해결 문제
//   - 비즈니스 모델: 타겟 고객, 수익 모델, 가치 제안, 가격, 자본
//   - 추가 정보: 알고 있는 경쟁사, 기타
//
// 결과 섹션 (view === "result"):
//   - 리포트 헤더: 서비스명 + 요약 + 태그
//   - SWOT 분석: 4분면 그리드 (강점/약점/기회/위협)
//   - 시장 가능성 평가: 5개 지표 + 프로그레스 바 + 종합 평가
//   - 경쟁사 분석: 위협 수준 배지 + 메타 정보 + 차별화 포인트
//   - 차별화 전략: 번호 있는 전략 목록
//
// 에러 처리:
//   - 비로그인: /login 리다이렉트
//   - FREE 플랜 한도 초과 (403): alert 안내
//   - 기타 오류: alert 안내
//   - 로딩 중: 전체 화면 오버레이 + 스피너
// ============================================================

"use client"; // useState, useRouter 사용으로 클라이언트 컴포넌트 필수

import { useState } from "react";
import { useRouter } from "next/navigation";
import { analyzeAPI } from "@/lib/api";
import { isLoggedIn } from "@/lib/auth";

// ── 타입 정의 ─────────────────────────────────────────────────

/** AI 분석 결과 타입 (백엔드 ai_service.py가 반환하는 JSON 구조와 일치) */
type AnalysisResult = {
  summary: string;
  tags: string[];
  scores: {
    market_growth: number;     // 시장 성장성 (0~100)
    competition: number;        // 경쟁 강도 (0~100)
    entry_barrier: number;      // 진입 장벽 (0~100)
    profitability: number;      // 수익성 전망 (0~100)
    differentiation: number;    // 차별화 가능성 (0~100)
  };
  overall_comment: string;
  swot: {
    strengths: string[];
    weaknesses: string[];
    opportunities: string[];
    threats: string[];
  };
  competitors: {
    name: string;
    type: string;
    threat_level: string;       // "high" | "medium" | "low"
    price: string;
    target: string;
    monthly_visitors: string;
    founded: string;
    features: string[];
    differentiation: string;
  }[];
  strategies: { title: string; description: string }[];
};

/** 서버에 저장된 분석 응답 (AnalysisOut 스키마와 일치) */
type SavedAnalysis = {
  id: number;
  service_name: string;
  result: AnalysisResult;
};

// ── 상수: UI 표시용 매핑 ──────────────────────────────────────

/** 점수 키 → 한국어 레이블 */
const SCORE_LABELS: Record<string, string> = {
  market_growth: "시장 성장성",
  competition: "경쟁 강도",
  entry_barrier: "진입 장벽",
  profitability: "수익성 전망",
  differentiation: "차별화 가능성",
};

/** 점수 키 → 프로그레스 바 색상 */
const SCORE_COLORS: Record<string, string> = {
  market_growth: "#2563eb",
  competition: "#f59e0b",
  entry_barrier: "#10b981",
  profitability: "#2563eb",
  differentiation: "#10b981",
};

/** 경쟁사 위협 수준 → 배지 스타일 + 레이블 */
const THREAT_BADGE: Record<string, { bg: string; color: string; label: string }> = {
  high:   { bg: "#fef2f2", color: "#dc2626", label: "강력한 경쟁자" },
  medium: { bg: "#fefce8", color: "#ca8a04", label: "주의 경쟁자" },
  low:    { bg: "#f0fdf4", color: "#16a34a", label: "참고 경쟁자" },
};

export default function AnalyzePage() {
  const router = useRouter();

  // ── 화면 상태 ─────────────────────────────────────────────
  const [view, setView] = useState<"input" | "result">("input"); // 입력 | 결과 화면 전환
  const [loading, setLoading] = useState(false);
  const [savedAnalysis, setSavedAnalysis] = useState<SavedAnalysis | null>(null);

  // ── 폼 입력값 상태 ────────────────────────────────────────
  const [form, setForm] = useState({
    service_name: "",
    category: "IT / 소프트웨어",
    description: "",
    problem: "",
    target_customer: "",
    revenue_model: "월정액 구독",
    value_proposition: "",
    price_range: "",
    capital: "500만원 미만",
    known_competitors: "",
    extra_notes: "",
  });

  /**
   * 폼 입력 핸들러 팩토리
   * set("service_name") → onChange 이벤트 핸들러 반환
   */
  const set = (key: string) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
      setForm((prev) => ({ ...prev, [key]: e.target.value }));

  /** AI 분석 시작 */
  const handleAnalyze = async () => {
    // 비로그인 → 로그인 페이지로 이동
    if (!isLoggedIn()) { router.push("/login"); return; }
    setLoading(true);
    try {
      const res = await analyzeAPI.create(form);
      setSavedAnalysis(res.data); // 서버에 저장된 분석 결과 저장
      setView("result");          // 결과 화면으로 전환
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } }).response?.status;
      if (status === 403) {
        // FREE 플랜 월 5회 한도 초과
        alert("월 분석 횟수를 초과했습니다. PRO 플랜으로 업그레이드하세요.");
      } else {
        alert("분석 중 오류가 발생했습니다.");
      }
    } finally {
      setLoading(false);
      window.scrollTo(0, 0); // 결과 화면 상단으로 스크롤
    }
  };

  const result = savedAnalysis?.result;

  return (
    <div className="max-w-[900px] mx-auto px-10 py-12">
      {/* ── 로딩 오버레이 ───────────────────────────────────────
          AI 분석 중 전체 화면을 덮는 반투명 레이어 + 스피너 */}
      {loading && (
        <div className="fixed inset-0 z-50 flex flex-col items-center justify-center gap-4" style={{ background: "rgba(15,23,42,0.7)" }}>
          <div className="w-12 h-12 rounded-full border-4 border-white/20 border-t-accent animate-spin" />
          <div className="text-white text-[15px] font-semibold">AI가 시장을 분석하고 있습니다...</div>
        </div>
      )}

      {/* ── 입력 화면 ───────────────────────────────────────── */}
      {view === "input" && (
        <>
          <h1 className="text-[28px] font-extrabold text-dark mb-1.5">아이디어 분석</h1>
          <p className="text-sym-text-light text-[15px] mb-8">비즈니스 아이디어를 입력하면 경쟁사와 시장 기회를 분석해드립니다</p>

          {/* 기본 정보 카드 */}
          <div className="card mb-5">
            <h3 className="text-[15px] font-bold text-dark mb-4 flex items-center gap-2">📝 기본 정보</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="form-label">서비스/제품명</label>
                <input className="form-input" placeholder="예: 반찬 AI 구독 서비스" value={form.service_name} onChange={set("service_name")} />
              </div>
              <div>
                <label className="form-label">산업 카테고리</label>
                <select className="form-input" value={form.category} onChange={set("category")}>
                  {["식음료", "IT / 소프트웨어", "헬스케어", "교육", "커머스", "환경", "기타"].map((c) => (
                    <option key={c}>{c}</option>
                  ))}
                </select>
              </div>
              <div className="col-span-2">
                <label className="form-label">한 줄 소개</label>
                <input className="form-input" placeholder="예: AI로 식단을 분석해 맞춤 반찬을 배달해드리는 구독 서비스" value={form.description} onChange={set("description")} />
              </div>
              <div className="col-span-2">
                <label className="form-label">해결하려는 문제</label>
                <textarea className="form-input resize-y min-h-[80px]" placeholder="어떤 문제를 해결하려 하나요?" value={form.problem} onChange={set("problem")} />
              </div>
            </div>
          </div>

          {/* 비즈니스 모델 카드 */}
          <div className="card mb-5">
            <h3 className="text-[15px] font-bold text-dark mb-4 flex items-center gap-2">🎯 비즈니스 모델</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="form-label">타겟 고객</label>
                <input className="form-input" placeholder="예: 20~40대 맞벌이 가구" value={form.target_customer} onChange={set("target_customer")} />
              </div>
              <div>
                <label className="form-label">수익 모델</label>
                <select className="form-input" value={form.revenue_model} onChange={set("revenue_model")}>
                  {["월정액 구독", "건당 결제", "광고 기반", "B2B 라이선스", "수수료 (플랫폼)", "프리미엄 (Freemium)"].map((r) => (
                    <option key={r}>{r}</option>
                  ))}
                </select>
              </div>
              <div className="col-span-2">
                <label className="form-label">핵심 가치 제안 (Value Proposition)</label>
                <textarea className="form-input resize-y min-h-[80px]" placeholder="경쟁사 대비 어떤 차별점을 줄 수 있나요?" value={form.value_proposition} onChange={set("value_proposition")} />
              </div>
              <div>
                <label className="form-label">예상 가격대</label>
                <input className="form-input" placeholder="예: 월 39,900원" value={form.price_range} onChange={set("price_range")} />
              </div>
              <div>
                <label className="form-label">초기 자본 규모</label>
                <select className="form-input" value={form.capital} onChange={set("capital")}>
                  {["500만원 미만", "500만~2천만원", "2천만~5천만원", "5천만원 이상"].map((c) => (
                    <option key={c}>{c}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* 추가 정보 카드 (선택 입력) */}
          <div className="card mb-5">
            <h3 className="text-[15px] font-bold text-dark mb-4 flex items-center gap-2">✨ 추가 정보 (선택)</h3>
            <div className="grid grid-cols-1 gap-4">
              <div>
                <label className="form-label">이미 알고 있는 경쟁사</label>
                <input className="form-input" placeholder="예: 마켓컬리, 오늘의집 (쉼표로 구분)" value={form.known_competitors} onChange={set("known_competitors")} />
              </div>
              <div>
                <label className="form-label">기타 참고사항</label>
                <textarea className="form-input resize-y min-h-[80px]" placeholder="추가로 분석에 포함됐으면 하는 내용을 자유롭게 입력해주세요" value={form.extra_notes} onChange={set("extra_notes")} />
              </div>
            </div>
          </div>

          {/* 분석 시작 버튼 — service_name 없으면 비활성화 */}
          <button
            onClick={handleAnalyze}
            disabled={!form.service_name || loading}
            className="w-full py-4 bg-primary text-white rounded-xl text-[16px] font-bold hover:bg-primary-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 cursor-pointer border-0"
          >
            🔍 AI 분석 시작하기
          </button>
        </>
      )}

      {/* ── 결과 화면 ───────────────────────────────────────── */}
      {view === "result" && result && savedAnalysis && (
        <>
          {/* 상단 버튼 영역 */}
          <div className="flex items-center gap-2 mb-6">
            <button onClick={() => setView("input")} className="btn-secondary text-[13px] py-2.5 px-5">
              ← 다시 입력하기
            </button>
            <button
              onClick={() => alert("마이페이지에 저장되었습니다!")}
              className="ml-auto py-2.5 px-6 bg-green-500 text-white rounded-[10px] text-[14px] font-bold hover:bg-green-600 transition-colors cursor-pointer border-0"
            >
              💾 분석 저장하기
            </button>
          </div>

          {/* ── 리포트 헤더 (다크 배경) ───────────────────────── */}
          <div
            className="rounded-2xl p-7 text-white mb-6"
            style={{ background: "linear-gradient(120deg, #1e3a5f, #1e293b)" }}
          >
            <h2 className="text-[22px] font-extrabold mb-1.5">{savedAnalysis.service_name} — 시장 분석 리포트</h2>
            <p className="text-[#94a3b8] text-[14px]">{result.summary}</p>
            {/* AI가 생성한 키워드 태그 */}
            <div className="flex gap-2 mt-3.5 flex-wrap">
              {result.tags?.map((tag) => (
                <span key={tag} className="text-[#e2e8f0] text-[12px] px-3 py-1 rounded-full" style={{ background: "rgba(255,255,255,0.1)", border: "1px solid rgba(255,255,255,0.2)" }}>
                  {tag}
                </span>
              ))}
            </div>
          </div>

          {/* ── SWOT + 점수 그리드 (2열) ─────────────────────── */}
          <div className="grid grid-cols-2 gap-5 mb-6">
            {/* SWOT 분석 4분면 */}
            <div className="card">
              <h3 className="text-[14px] font-bold text-sym-text-light mb-4 uppercase tracking-wide">SWOT 분석</h3>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { key: "strengths",    label: "S 강점", cls: "bg-green-50",  titleCls: "text-green-700" },
                  { key: "weaknesses",   label: "W 약점", cls: "bg-yellow-50", titleCls: "text-yellow-700" },
                  { key: "opportunities",label: "O 기회", cls: "bg-blue-50",   titleCls: "text-blue-700" },
                  { key: "threats",      label: "T 위협", cls: "bg-red-50",    titleCls: "text-red-700" },
                ].map(({ key, label, cls, titleCls }) => (
                  <div key={key} className={`rounded-[10px] p-3.5 ${cls}`}>
                    <div className={`text-[11px] font-extrabold tracking-wide mb-2 ${titleCls}`}>{label}</div>
                    <ul className="list-none">
                      {(result.swot[key as keyof typeof result.swot] || []).map((item: string, i: number) => (
                        <li key={i} className="text-[12px] text-sym-text py-0.5">• {item}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>

            {/* 시장 가능성 평가 점수 바 */}
            <div className="card">
              <h3 className="text-[14px] font-bold text-sym-text-light mb-4 uppercase tracking-wide">시장 가능성 평가</h3>
              {Object.entries(result.scores || {}).map(([key, val]) => (
                <div key={key} className="mb-3.5">
                  <div className="flex justify-between items-center mb-1.5">
                    <span className="text-[13px] text-sym-text">{SCORE_LABELS[key]}</span>
                    <span className="text-[13px] font-bold text-dark">{val}/100</span>
                  </div>
                  {/* 프로그레스 바 */}
                  <div className="bg-slate-100 rounded-full h-2 overflow-hidden">
                    <div
                      className="h-full rounded-full"
                      style={{ width: `${val}%`, background: SCORE_COLORS[key] || "#2563eb" }}
                    />
                  </div>
                </div>
              ))}
              {/* 종합 평가 텍스트 */}
              <div className="mt-4 p-3 bg-green-50 rounded-[10px] text-[13px] text-green-800">
                <strong>종합 평가:</strong> {result.overall_comment}
              </div>
            </div>
          </div>

          {/* ── 경쟁사 분석 ───────────────────────────────────── */}
          <div className="mb-6">
            <h2 className="text-[20px] font-extrabold text-dark mb-1.5">경쟁사 분석</h2>
            <p className="text-[14px] text-sym-text-light mb-5">발견된 주요 경쟁사 및 대체제 {result.competitors?.length || 0}개</p>
            {(result.competitors || []).map((comp, i) => {
              const badge = THREAT_BADGE[comp.threat_level] || THREAT_BADGE.low;
              return (
                <div key={i} className="card mb-4">
                  <div className="flex justify-between items-start mb-3.5">
                    <div>
                      <div className="text-[17px] font-extrabold text-dark">{comp.name}</div>
                      <div className="text-[12px] text-sym-text-light mt-0.5">{comp.type}</div>
                    </div>
                    {/* 위협 수준 배지 */}
                    <span className="text-[11px] font-bold px-3 py-1 rounded-full" style={{ background: badge.bg, color: badge.color }}>
                      {badge.label}
                    </span>
                  </div>
                  {/* 경쟁사 메타 정보 */}
                  <div className="flex gap-5 mb-3.5">
                    {[["가격대", comp.price], ["타겟", comp.target], ["월 방문자", comp.monthly_visitors], ["설립", comp.founded]].map(([label, val]) => (
                      <div key={label} className="text-[12px]">
                        <div className="text-sym-text-light mb-0.5">{label}</div>
                        <div className="font-bold text-dark">{val}</div>
                      </div>
                    ))}
                  </div>
                  {/* 주요 기능 태그 */}
                  <div className="flex gap-1.5 flex-wrap mb-3.5">
                    {(comp.features || []).map((f) => (
                      <span key={f} className="bg-slate-100 text-sym-text text-[11px] px-2.5 py-1 rounded-md">{f}</span>
                    ))}
                  </div>
                  {/* 차별화 포인트 (파란 왼쪽 테두리) */}
                  <div className="bg-blue-50 border-l-[3px] border-primary rounded-r-lg pl-3.5 py-2.5 text-[13px] text-sym-text">
                    <strong className="text-primary">차별화 포인트:</strong> {comp.differentiation}
                  </div>
                </div>
              );
            })}
          </div>

          {/* ── 차별화 전략 목록 ──────────────────────────────── */}
          <div className="card">
            <h3 className="text-[14px] font-bold text-sym-text-light mb-4 uppercase tracking-wide">차별화 전략 제안</h3>
            <ul className="list-none">
              {(result.strategies || []).map((s, i) => (
                <li key={i} className="flex gap-3 py-3.5 border-b border-sym-border last:border-0 text-[14px]">
                  {/* 순번 원형 아이콘 */}
                  <div className="w-6 h-6 rounded-full bg-primary text-white flex items-center justify-center text-[12px] font-extrabold flex-shrink-0">
                    {i + 1}
                  </div>
                  <div>
                    <strong>{s.title}</strong> — {s.description}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </>
      )}
    </div>
  );
}
