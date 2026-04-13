// ============================================================
// app/find-idea/page.tsx — 아이디어 구상 위저드 (/find-idea)
//
// 역할:
//   - 4단계 위저드로 사용자 선호도를 수집한 뒤 AI가 맞춤 아이디어 추천
//   - Step 1: 관심 분야 선택 (복수 선택)
//   - Step 2: 사업 형태 + 고객층 선택
//   - Step 3: 초기 자본 + 팀 규모 + 기술 수준 선택
//   - Step 4: AI 추천 아이디어 4개 카드 표시
//
// 인증:
//   - Step 3 → Step 4 전환 시 isLoggedIn() 확인
//   - 비로그인 상태면 /login으로 이동
//
// 에러 처리:
//   - AI API 실패 시 하드코딩된 샘플 아이디어 4개를 폴백으로 표시
//   - 에러가 나도 Step 4는 정상적으로 렌더됨
// ============================================================

"use client"; // useState, useRouter 사용으로 클라이언트 컴포넌트 필수

import { useState } from "react";
import { useRouter } from "next/navigation";
import { analyzeAPI } from "@/lib/api";
import { isLoggedIn } from "@/lib/auth";

// ── 선택지 상수 ───────────────────────────────────────────────
// 각 단계에서 사용자가 클릭할 수 있는 옵션 목록

/** Step 1: 관심 산업 분야 (복수 선택 가능) */
const INTERESTS = [
  { icon: "🍽️", label: "식음료" },
  { icon: "💻", label: "IT / 소프트웨어" },
  { icon: "🛍️", label: "커머스 / 리테일" },
  { icon: "🏃", label: "헬스 / 피트니스" },
  { icon: "📚", label: "교육 / 에듀테크" },
  { icon: "🌿", label: "환경 / 지속가능성" },
  { icon: "🎨", label: "콘텐츠 / 크리에이터" },
  { icon: "🏠", label: "부동산 / 생활" },
  { icon: "💊", label: "헬스케어 / 바이오" },
];

/** Step 2: 사업 형태 (단일 선택) */
const BUSINESS_TYPES = [
  { icon: "📱", label: "앱 / 플랫폼",   desc: "소프트웨어 기반 디지털 서비스" },
  { icon: "🏪", label: "오프라인 매장", desc: "실물 공간 기반 비즈니스" },
  { icon: "📦", label: "제품 판매",     desc: "물리적 상품 제조 및 판매" },
  { icon: "🤝", label: "B2B 서비스",   desc: "기업 대상 솔루션/서비스" },
];

/** Step 2: 고객층 (단일 선택) */
const CUSTOMER_TYPES = [
  { icon: "👤", label: "개인 소비자 (B2C)" },
  { icon: "🏢", label: "기업 고객 (B2B)" },
  { icon: "🏛️", label: "공공기관 (B2G)" },
  { icon: "🔄", label: "혼합" },
];

// ── 타입 정의 ─────────────────────────────────────────────────
/** AI 또는 폴백에서 받은 아이디어 항목 */
type IdeaResult = {
  tag: string;
  title: string;
  description: string;
  fit_score: number; // 0~100, 시장 적합도
};

export default function FindIdeaPage() {
  const router = useRouter();

  // ── 위저드 상태 ───────────────────────────────────────────
  const [step, setStep] = useState(1);          // 현재 단계 (1~4)
  const [loading, setLoading] = useState(false); // AI 요청 중 표시
  const [results, setResults] = useState<IdeaResult[]>([]); // 추천 아이디어 목록
  const [picked, setPicked] = useState<number[]>([]); // 선택된 카드 인덱스

  // ── 각 단계별 선택값 ──────────────────────────────────────
  const [interests, setInterests] = useState<string[]>([]);  // Step 1: 복수 선택
  const [businessType, setBusinessType] = useState("");       // Step 2: 단일 선택
  const [customerType, setCustomerType] = useState("");       // Step 2: 단일 선택
  const [capital, setCapital] = useState("");                 // Step 3: 단일 선택
  const [teamSize, setTeamSize] = useState("");               // Step 3: 단일 선택
  const [skills, setSkills] = useState("");                   // Step 3: 단일 선택

  /** Step 1 관심 분야 토글 (이미 선택 → 제거, 미선택 → 추가) */
  const toggleInterest = (label: string) => {
    setInterests((prev) =>
      prev.includes(label) ? prev.filter((i) => i !== label) : [...prev, label]
    );
  };

  /** Step 3 "아이디어 추천받기" 클릭 → AI 호출 */
  const getIdeas = async () => {
    // 비로그인 시 로그인 페이지로 이동
    if (!isLoggedIn()) { router.push("/login"); return; }
    setLoading(true);
    try {
      const res = await analyzeAPI.findIdea({
        interests,
        business_type: businessType,
        customer_type: customerType,
        capital,
        team_size: teamSize,
        skills,
      });
      setResults(res.data.ideas);
      setStep(4); // 결과 단계로 이동
    } catch {
      // AI 오류 시 샘플 아이디어 폴백 표시
      setResults([
        {
          tag: "IT / 구독",
          title: "AI 반찬 구독 서비스",
          description: "식단 선호도를 분석해 매주 맞춤 반찬을 배달해주는 구독형 서비스. 1인 가구 급증 트렌드와 맞물려 성장 가능성 높음.",
          fit_score: 92,
        },
        {
          tag: "헬스 / 플랫폼",
          title: "동네 운동 모임 매칭 앱",
          description: "관심사 기반으로 같은 동네 운동 파트너를 연결해주는 플랫폼. 초기 자본 최소화, 커뮤니티 성장에 강점.",
          fit_score: 87,
        },
        {
          tag: "교육 / B2B",
          title: "소상공인 SNS 마케팅 SaaS",
          description: "마케팅이 어려운 소상공인을 위한 AI 기반 콘텐츠 생성 및 스케줄링 도구. 월 구독 모델로 안정적인 수익 구조.",
          fit_score: 84,
        },
        {
          tag: "환경 / 커머스",
          title: "중고 아동복 거래 플랫폼",
          description: "빠르게 옷이 작아지는 아이들 특성을 활용한 친환경 중고 거래 커뮤니티. 부모 커뮤니티와 연동 가능.",
          fit_score: 79,
        },
      ]);
      setStep(4);
    } finally {
      setLoading(false);
    }
  };

  // 단계 표시 레이블
  const stepLabels = ["관심 분야", "선호 방식", "여건 확인", "아이디어 추천"];

  return (
    <div className="max-w-[720px] mx-auto px-10 py-16">
      {/* ── 단계 표시 바 ─────────────────────────────────────
          완료된 단계: 초록 / 현재 단계: 파랑 / 미완료: 회색 */}
      <div className="flex items-center mb-12">
        {stepLabels.map((label, i) => (
          <div key={label} className="flex items-center">
            <div className={`flex items-center gap-2 text-[13px] font-medium ${
              i + 1 < step ? "text-green-500" : i + 1 === step ? "text-primary" : "text-sym-text-light"
            }`}>
              {/* 단계 번호 원형 */}
              <div className={`w-7 h-7 rounded-full border-2 flex items-center justify-center text-[12px] font-bold ${
                i + 1 < step
                  ? "border-green-500 bg-green-500 text-white"  // 완료
                  : i + 1 === step
                  ? "border-primary bg-primary text-white"       // 현재
                  : "border-sym-border"                          // 미완료
              }`}>
                {i + 1 < step ? "✓" : i + 1}
              </div>
              {label}
            </div>
            {/* 단계 사이 연결선 */}
            {i < stepLabels.length - 1 && (
              <div className={`flex-1 h-0.5 mx-3 w-8 ${i + 1 < step ? "bg-green-500" : "bg-sym-border"}`} />
            )}
          </div>
        ))}
      </div>

      {/* ── Step 1: 관심 분야 선택 ──────────────────────────── */}
      {step === 1 && (
        <div>
          <h1 className="text-[28px] font-extrabold text-dark mb-2">어떤 분야에 관심 있으세요?</h1>
          <p className="text-sym-text-light text-[15px] mb-8">관심 있는 분야를 모두 선택해주세요 (복수 선택 가능)</p>
          <div className="text-[16px] font-bold text-dark mb-4">관심 산업 분야</div>
          <div className="grid grid-cols-3 gap-2.5 mb-7">
            {INTERESTS.map((item) => (
              <button
                key={item.label}
                onClick={() => toggleInterest(item.label)}
                className={`flex items-center gap-3 p-4 rounded-xl border-2 transition-all cursor-pointer text-left ${
                  interests.includes(item.label)
                    ? "border-primary bg-blue-50"                         // 선택됨
                    : "border-sym-border bg-white hover:border-blue-300 hover:bg-blue-50" // 미선택
                }`}
              >
                <span className="text-[22px]">{item.icon}</span>
                <span className="text-[14px] font-semibold text-dark">{item.label}</span>
              </button>
            ))}
          </div>
          <div className="flex justify-end">
            <button className="btn-primary" onClick={() => setStep(2)}>다음 →</button>
          </div>
        </div>
      )}

      {/* ── Step 2: 사업 형태 + 고객층 선택 ────────────────── */}
      {step === 2 && (
        <div>
          <h1 className="text-[28px] font-extrabold text-dark mb-2">어떤 방식의 사업을 원하세요?</h1>
          <p className="text-sym-text-light text-[15px] mb-8">선호하는 비즈니스 형태를 선택해주세요</p>

          <div className="text-[16px] font-bold text-dark mb-4">사업 형태</div>
          <div className="grid grid-cols-2 gap-2.5 mb-7">
            {BUSINESS_TYPES.map((item) => (
              <button
                key={item.label}
                onClick={() => setBusinessType(item.label)}
                className={`flex items-center gap-3 p-4 rounded-xl border-2 transition-all cursor-pointer text-left ${
                  businessType === item.label
                    ? "border-primary bg-blue-50"
                    : "border-sym-border bg-white hover:border-blue-300 hover:bg-blue-50"
                }`}
              >
                <span className="text-[22px]">{item.icon}</span>
                <div>
                  <div className="text-[14px] font-semibold text-dark">{item.label}</div>
                  <div className="text-[12px] text-sym-text-light mt-0.5">{item.desc}</div>
                </div>
              </button>
            ))}
          </div>

          <div className="text-[16px] font-bold text-dark mb-4">고객층</div>
          <div className="grid grid-cols-2 gap-2.5 mb-7">
            {CUSTOMER_TYPES.map((item) => (
              <button
                key={item.label}
                onClick={() => setCustomerType(item.label)}
                className={`flex items-center gap-3 p-4 rounded-xl border-2 transition-all cursor-pointer ${
                  customerType === item.label
                    ? "border-primary bg-blue-50"
                    : "border-sym-border bg-white hover:border-blue-300 hover:bg-blue-50"
                }`}
              >
                <span className="text-[22px]">{item.icon}</span>
                <span className="text-[14px] font-semibold text-dark">{item.label}</span>
              </button>
            ))}
          </div>

          <div className="flex justify-end gap-3">
            <button className="btn-secondary" onClick={() => setStep(1)}>← 이전</button>
            <button className="btn-primary" onClick={() => setStep(3)}>다음 →</button>
          </div>
        </div>
      )}

      {/* ── Step 3: 여건 확인 ────────────────────────────────── */}
      {step === 3 && (
        <div>
          <h1 className="text-[28px] font-extrabold text-dark mb-2">현재 여건을 알려주세요</h1>
          <p className="text-sym-text-light text-[15px] mb-8">상황에 맞는 아이디어를 추천해드립니다</p>

          {/* 초기 자본금 선택 */}
          <div className="text-[16px] font-bold text-dark mb-4">예상 초기 자본금</div>
          <div className="flex gap-2 mb-7">
            {["500만원 미만", "500~2천만원", "2천~5천만원", "5천만원 이상"].map((v) => (
              <button
                key={v}
                onClick={() => setCapital(v)}
                className={`flex-1 py-3 px-2 text-center border-2 rounded-[10px] text-[13px] font-semibold cursor-pointer transition-all ${
                  capital === v
                    ? "border-primary text-primary bg-blue-50"
                    : "border-sym-border text-sym-text-light bg-white hover:border-blue-300 hover:text-primary"
                }`}
              >
                {v}
              </button>
            ))}
          </div>

          {/* 팀 규모 선택 */}
          <div className="text-[16px] font-bold text-dark mb-4">함께할 팀원</div>
          <div className="flex gap-2 mb-7">
            {["혼자", "2~3명", "4~6명", "7명 이상"].map((v) => (
              <button
                key={v}
                onClick={() => setTeamSize(v)}
                className={`flex-1 py-3 px-2 text-center border-2 rounded-[10px] text-[13px] font-semibold cursor-pointer transition-all ${
                  teamSize === v
                    ? "border-primary text-primary bg-blue-50"
                    : "border-sym-border text-sym-text-light bg-white hover:border-blue-300 hover:text-primary"
                }`}
              >
                {v}
              </button>
            ))}
          </div>

          {/* 기술/전문성 선택 */}
          <div className="text-[16px] font-bold text-dark mb-4">기술/전문성 보유 여부</div>
          <div className="grid grid-cols-2 gap-2.5 mb-7">
            {[
              { icon: "💪", label: "개발 가능",         desc: "직접 코딩 또는 팀원 보유" },
              { icon: "🎯", label: "특정 분야 전문가",  desc: "업계 경력 또는 자격증" },
              { icon: "🌱", label: "특별한 전문성 없음", desc: "아이디어와 열정만 있음" },
              { icon: "🤖", label: "AI/노코드 활용",    desc: "기술 없이 도구로 해결" },
            ].map((item) => (
              <button
                key={item.label}
                onClick={() => setSkills(item.label)}
                className={`flex items-center gap-3 p-4 rounded-xl border-2 transition-all cursor-pointer text-left ${
                  skills === item.label
                    ? "border-primary bg-blue-50"
                    : "border-sym-border bg-white hover:border-blue-300 hover:bg-blue-50"
                }`}
              >
                <span className="text-[22px]">{item.icon}</span>
                <div>
                  <div className="text-[14px] font-semibold text-dark">{item.label}</div>
                  <div className="text-[12px] text-sym-text-light mt-0.5">{item.desc}</div>
                </div>
              </button>
            ))}
          </div>

          <div className="flex justify-end gap-3">
            <button className="btn-secondary" onClick={() => setStep(2)}>← 이전</button>
            {/* 비로그인 상태면 /login 이동, 로그인 상태면 AI 호출 */}
            <button className="btn-primary" onClick={getIdeas} disabled={loading}>
              {loading ? "AI 분석 중..." : "아이디어 추천받기 ✨"}
            </button>
          </div>
        </div>
      )}

      {/* ── Step 4: 추천 결과 ────────────────────────────────── */}
      {step === 4 && (
        <div>
          <h1 className="text-[28px] font-extrabold text-dark mb-2">맞춤 아이디어 추천 결과</h1>
          <p className="text-sym-text-light text-[15px] mb-6">
            선택하신 관심사와 여건을 바탕으로 {results.length}가지 아이디어를 추천해드립니다
          </p>

          {/* 아이디어 카드 그리드 — 클릭으로 선택/해제 */}
          <div className="grid grid-cols-2 gap-3.5 mb-7">
            {results.map((idea, i) => (
              <div
                key={i}
                onClick={() => setPicked((prev) =>
                  prev.includes(i) ? prev.filter((p) => p !== i) : [...prev, i]
                )}
                className={`card cursor-pointer transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md ${
                  picked.includes(i) ? "border-primary bg-blue-50" : "hover:border-primary"
                }`}
              >
                <span className="tag mb-2.5">{idea.tag}</span>
                <h3 className="text-[15px] font-extrabold text-dark mb-1.5">{idea.title}</h3>
                <p className="text-[13px] text-sym-text-light leading-[1.55]">{idea.description}</p>
                <div className="flex items-center gap-1.5 mt-3 text-[12px] font-bold text-green-500">
                  📈 시장 적합도 {idea.fit_score}%
                </div>
              </div>
            ))}
          </div>

          {/* 분석 페이지 이동 링크 */}
          <a
            href="/analyze"
            className="block text-center py-3.5 bg-primary text-white rounded-xl text-[15px] font-bold hover:bg-primary-dark transition-colors no-underline"
          >
            선택한 아이디어 분석하러 가기 →
          </a>

          {/* 처음부터 다시 시작 */}
          <div className="text-center mt-4">
            <button
              className="btn-secondary text-[13px] py-2.5 px-5"
              onClick={() => { setStep(1); setPicked([]); setResults([]); }}
            >
              다시 처음부터
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
