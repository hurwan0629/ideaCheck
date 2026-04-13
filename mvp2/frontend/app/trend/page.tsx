// ============================================================
// app/trend/page.tsx — 요즘 트렌드 페이지 (/trend)
//
// 역할:
//   - 현재 인기 있는 트렌드 아이템을 카드 형태로 표시
//   - 카테고리 필터 버튼으로 카테고리별 필터링
//   - 1위(is_hot=true): 가로 전체 너비의 강조 카드
//   - 2위 이하: 3열 그리드 카드
//
// 데이터:
//   - 마운트 시 trendsAPI.get() 호출 → 성공하면 API 데이터 사용
//   - 실패(백엔드 미실행 등) 시 FALLBACK 하드코딩 데이터 유지
//   - updated_at: 백엔드에서 받은 업데이트 시각 표시
//
// 카테고리 필터:
//   - "전체" 선택 시 전체 목록 표시
//   - 그 외 선택 시 버튼 텍스트에 아이템 category가 포함되는지 체크
// ============================================================

"use client"; // useEffect, useState 사용으로 클라이언트 컴포넌트 필수

import { useEffect, useState } from "react";
import { trendsAPI } from "@/lib/api";

// ── 타입 정의 ─────────────────────────────────────────────────
type TrendItem = {
  id: number;
  rank: number;
  title: string;
  category: string;
  description: string;
  growth: string;    // 전월 대비 증감률 문자열 ("+342%")
  tags: string[];
  emoji: string;
  img_class: string; // 이미지 배경 색상 키 (food, tech, life, fashion, health)
  is_hot: boolean;   // true면 1위 강조 카드로 렌더
};

// ── 상수 ─────────────────────────────────────────────────────

/** img_class 키에 따른 배경 그라디언트 색상 */
const IMG_GRADIENTS: Record<string, string> = {
  food:    "linear-gradient(135deg, #fff7ed, #fed7aa)",  // 주황빛
  tech:    "linear-gradient(135deg, #eff6ff, #bfdbfe)",  // 파란빛
  life:    "linear-gradient(135deg, #f0fdf4, #bbf7d0)",  // 초록빛
  fashion: "linear-gradient(135deg, #fdf4ff, #e9d5ff)",  // 보라빛
  health:  "linear-gradient(135deg, #f0fdfa, #99f6e4)",  // 청록빛
};

/** 카테고리 필터 버튼 목록 */
const CATEGORIES = ["전체", "🍽️ 식음료", "💻 IT/테크", "🌿 라이프스타일", "👗 패션/뷰티", "🏃 헬스/피트니스"];

/** 백엔드 없이도 UI 확인 가능한 폴백 데이터 */
const FALLBACK: TrendItem[] = [
  { id: 1, rank: 1, title: "버터 떡 열풍 — 전통+디저트의 만남", category: "식음료",    description: "버터를 품은 쫄깃한 떡이 MZ세대 사이에서 폭발적인 인기를 끌고 있습니다.", growth: "+342%", tags: ["인스타감성", "디저트", "MZ"], emoji: "🧈", img_class: "food",    is_hot: true },
  { id: 2, rank: 2, title: "미니 보냉백",                        category: "라이프스타일", description: "손바닥만 한 보냉백이 편의점 음료와 함께 필수품으로 자리 잡았어요.",             growth: "+178%", tags: ["실용성", "환경"],          emoji: "🧊", img_class: "life",    is_hot: false },
  { id: 3, rank: 3, title: "AI 영상 편집 툴",                   category: "IT/테크",    description: "유튜브·릴스 운영자들 사이에서 AI 자동 편집 도구 수요 폭발.",                   growth: "+156%", tags: ["크리에이터", "AI"],        emoji: "🤖", img_class: "tech",    is_hot: false },
  { id: 4, rank: 4, title: "고단백 편의식",                     category: "식음료",    description: "헬스 열풍과 함께 편의점 고단백 도시락, 닭가슴살 세트 매출이 전년 대비 2배 이상 성장.", growth: "+134%", tags: ["헬스", "편의점"],      emoji: "🥗", img_class: "food",    is_hot: false },
  { id: 5, rank: 5, title: "무광 네일 아트",                    category: "뷰티",       description: "기존 유광 네일에서 매트한 무광 텍스처로 트렌드 전환.",                          growth: "+121%", tags: ["뷰티", "홈케어"],         emoji: "💅", img_class: "fashion", is_hot: false },
  { id: 6, rank: 6, title: "필라테스 숏폼",                     category: "헬스/피트니스", description: "10분 이내 필라테스 루틴 영상이 유튜브·릴스에서 폭발적으로 성장.",             growth: "+115%", tags: ["홈트", "숏폼"],           emoji: "🧘", img_class: "health",  is_hot: false },
  { id: 7, rank: 7, title: "소형 보조배터리",                   category: "IT/테크",    description: "립스틱 크기의 초소형 고속충전 보조배터리.",                                     growth: "+97%",  tags: ["가전", "휴대용"],         emoji: "🔋", img_class: "tech",    is_hot: false },
  { id: 8, rank: 8, title: "두유 라떼",                         category: "식음료",    description: "비건과 유당불내증 인구 증가로 두유 기반 음료 수요 폭발.",                       growth: "+89%",  tags: ["비건", "카페"],           emoji: "☕", img_class: "food",    is_hot: false },
];

export default function TrendPage() {
  // FALLBACK을 초기값으로 설정 → 백엔드 없어도 UI 동작
  const [items, setItems] = useState<TrendItem[]>(FALLBACK);
  const [activeCategory, setActiveCategory] = useState("전체");
  const [updatedAt, setUpdatedAt] = useState(""); // 업데이트 시각 표시용

  // 마운트 시 API에서 최신 트렌드 데이터 가져오기
  useEffect(() => {
    trendsAPI.get()
      .then((res) => {
        setItems(res.data.items);
        setUpdatedAt(res.data.updated_at); // 서버 시각으로 업데이트
      })
      .catch(() => {}); // 실패 시 FALLBACK 데이터 유지 (에러 표시 안 함)
  }, []);

  // 선택된 카테고리에 맞게 필터링
  // 카테고리 버튼에 이모지가 포함되어 있어 includes로 체크
  const displayed = activeCategory === "전체"
    ? items
    : items.filter((t) => activeCategory.includes(t.category));

  return (
    <>
      {/* ── 히어로 헤더 바 ──────────────────────────────────── */}
      <div
        className="px-10 py-10 text-white"
        style={{ background: "linear-gradient(120deg, #1e293b, #1e3a5f)" }}
      >
        <h1 className="text-[28px] font-extrabold mb-1.5">요즘 트렌드 🔥</h1>
        <p className="text-[#94a3b8] text-[14px]">지금 뜨고 있는 아이템과 키워드를 모아봤어요</p>
        {/* 업데이트 시각 (API에서 받은 경우만 표시) */}
        {updatedAt && (
          <div className="text-[12px] font-semibold mt-2" style={{ color: "var(--accent)" }}>
            ↑ {new Date(updatedAt).toLocaleString("ko-KR")} 업데이트
          </div>
        )}
      </div>

      <div className="max-w-[1100px] mx-auto px-10 py-10">
        {/* ── 카테고리 필터 버튼 ──────────────────────────────
            활성 카테고리: 파란 배경 / 비활성: 흰 배경 */}
        <div className="flex gap-2 mb-7 flex-wrap">
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`px-4 py-1.5 rounded-full text-[13px] font-semibold border-[1.5px] transition-all cursor-pointer ${
                activeCategory === cat
                  ? "bg-primary text-white border-primary"
                  : "bg-white text-sym-text-light border-sym-border hover:border-primary hover:text-primary"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* ── 트렌드 카드 그리드 ──────────────────────────────
            is_hot=true(1위): col-span-3 가로 전체 레이아웃
            그 외: 일반 3열 카드 */}
        <div className="grid grid-cols-3 gap-5">
          {displayed.map((item) =>
            item.is_hot ? (
              /* 1위 HOT 카드: 가로 레이아웃 (이모지 이미지 + 텍스트) */
              <div key={item.id} className="col-span-3 flex border border-sym-border rounded-2xl overflow-hidden hover:shadow-lg transition-all cursor-pointer">
                {/* 이모지 이미지 영역 */}
                <div
                  className="w-[280px] min-h-[160px] flex items-center justify-center text-[80px] flex-shrink-0"
                  style={{ background: IMG_GRADIENTS[item.img_class] || IMG_GRADIENTS.tech }}
                >
                  {item.emoji}
                </div>
                {/* 텍스트 정보 영역 */}
                <div className="p-6 flex-1">
                  <span className="inline-flex items-center gap-1 bg-red-50 text-red-500 text-[11px] font-extrabold px-2.5 py-0.5 rounded-full mb-2">
                    🔥 이번 주 1위
                  </span>
                  <div className="flex justify-between items-center mb-2">
                    <span className="tag">{item.category}</span>
                    <span className="text-[12px] text-sym-text-light font-semibold">#1 HOT</span>
                  </div>
                  <div className="text-[20px] font-extrabold text-dark mb-1.5">{item.title}</div>
                  <div className="text-[14px] text-sym-text-light leading-[1.55] mb-3">{item.description}</div>
                  <div className="flex justify-between items-center">
                    <span className="text-[13px] font-bold text-green-500">📈 {item.growth} (검색량 기준)</span>
                    <div className="flex gap-1">
                      {item.tags.map((t) => (
                        <span key={t} className="bg-slate-100 text-sym-text-light text-[11px] px-2 py-0.5 rounded">{t}</span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              /* 일반 순위 카드: 세로 레이아웃 (이모지 + 텍스트 위아래) */
              <div key={item.id} className="border border-sym-border rounded-2xl overflow-hidden bg-white hover:shadow-lg hover:-translate-y-0.5 transition-all cursor-pointer">
                {/* 이모지 배경 이미지 */}
                <div
                  className="h-[140px] flex items-center justify-center text-[60px]"
                  style={{ background: IMG_GRADIENTS[item.img_class] || IMG_GRADIENTS.tech }}
                >
                  {item.emoji}
                </div>
                {/* 카드 본문 */}
                <div className="p-4">
                  <div className="flex justify-between items-center mb-2">
                    <span className="tag">{item.category}</span>
                    <span className="text-[12px] text-sym-text-light font-semibold">#{item.rank}</span>
                  </div>
                  <div className="text-[16px] font-extrabold text-dark mb-1.5">{item.title}</div>
                  <div className="text-[13px] text-sym-text-light leading-[1.55] mb-3">{item.description}</div>
                  <div className="flex justify-between items-center">
                    <span className="text-[13px] font-bold text-green-500">📈 {item.growth}</span>
                    <div className="flex gap-1">
                      {item.tags.map((t) => (
                        <span key={t} className="bg-slate-100 text-sym-text-light text-[11px] px-2 py-0.5 rounded">{t}</span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )
          )}
        </div>
      </div>
    </>
  );
}
