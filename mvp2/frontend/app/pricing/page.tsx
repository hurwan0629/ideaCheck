"use client";

import { useState } from "react";
import Link from "next/link";

const FREE_FEATURES = [
  { ok: true, text: "월 5회 아이디어 분석" },
  { ok: true, text: "경쟁사 최대 3개 분석" },
  { ok: true, text: "SWOT 분석 기본 제공" },
  { ok: true, text: "아이디어 노트 20개 저장" },
  { ok: true, text: "트렌드 / 인기 검색어 열람" },
  { ok: false, text: "PDF 리포트 다운로드" },
  { ok: false, text: "심층 차별화 전략 제안" },
  { ok: false, text: "무제한 분석" },
];

const PRO_FEATURES = [
  { ok: true, text: "무제한 아이디어 분석" },
  { ok: true, text: "경쟁사 최대 10개 심층 분석" },
  { ok: true, text: "SWOT + 포터 5힘 분석" },
  { ok: true, text: "차별화 전략 3가지 제안" },
  { ok: true, text: "PDF 리포트 다운로드" },
  { ok: true, text: "아이디어 노트 무제한" },
  { ok: true, text: "시장 규모 추정 데이터" },
  { ok: true, text: "우선 고객 지원" },
];

const COMPARE_ROWS = [
  ["월 분석 횟수", "5회", "무제한"],
  ["분석 경쟁사 수", "3개", "10개"],
  ["SWOT 분석", "✓", "✓"],
  ["포터 5힘 분석", "✗", "✓"],
  ["차별화 전략 제안", "1가지", "3가지"],
  ["PDF 리포트 다운로드", "✗", "✓"],
  ["시장 규모 추정", "✗", "✓"],
  ["아이디어 노트 저장", "20개", "무제한"],
  ["트렌드 / 인기 검색어", "✓", "✓"],
  ["고객 지원", "이메일", "우선 지원"],
];

const FAQ_ITEMS = [
  {
    q: "언제든지 해지할 수 있나요?",
    a: "네, 언제든지 해지 가능합니다. 해지 후에는 현재 결제 기간이 끝날 때까지 PRO 기능을 그대로 사용할 수 있습니다. 위약금이나 추가 요금은 없습니다.",
  },
  {
    q: "무료 플랜에서 PRO로 업그레이드하면 기존 데이터는 유지되나요?",
    a: "물론입니다. 무료 플랜에서 작성한 분석 히스토리와 아이디어 노트는 PRO 업그레이드 후에도 그대로 유지됩니다.",
  },
  {
    q: "연간 결제로 전환하면 언제부터 할인이 적용되나요?",
    a: "연간 결제로 전환하는 즉시 할인이 적용됩니다. 기존 월간 결제 잔여 기간은 환불 처리 후 연간 결제로 전환됩니다.",
  },
  {
    q: "팀 플랜이 있나요?",
    a: "현재는 개인 플랜만 제공하고 있습니다. 팀 플랜은 2026년 3분기 출시 예정입니다. 관심 있으시면 이메일로 사전 등록해두시면 오픈 시 우선 안내 드립니다.",
  },
];

export default function PricingPage() {
  const [yearly, setYearly] = useState(false);
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  const proPrice = yearly ? "4,917" : "5,900";
  const proNote = yearly ? "연간 결제 시 (월 환산) · 연 59,000원" : "월간 결제 기준";

  return (
    <>
      {/* Hero */}
      <div
        className="px-10 py-16 text-center text-white"
        style={{ background: "linear-gradient(160deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%)" }}
      >
        <h1 className="text-[36px] font-extrabold mb-3">시작은 무료로,<br />성장하면 함께</h1>
        <p className="text-[#94a3b8] text-[16px]">아이디어 검증이 필요한 예비 창업자부터 깊은 분석이 필요한 팀까지</p>
        <div className="flex justify-center items-center gap-3 mt-10">
          <span className={`text-[14px] font-semibold ${!yearly ? "text-white" : "text-[#94a3b8]"}`}>월간 결제</span>
          <button
            onClick={() => setYearly((v) => !v)}
            className={`w-12 h-6.5 rounded-full relative cursor-pointer border-0 transition-colors ${yearly ? "bg-primary" : "bg-primary"}`}
            style={{ height: "26px" }}
          >
            <div
              className={`w-5 h-5 bg-white rounded-full absolute top-0.5 transition-transform ${yearly ? "translate-x-6" : "translate-x-0.5"}`}
            />
          </button>
          <span className={`text-[14px] font-semibold ${yearly ? "text-white" : "text-[#94a3b8]"}`}>
            연간 결제{" "}
            <span className="text-[11px] font-extrabold px-2 py-0.5 rounded-full ml-1" style={{ background: "var(--accent)", color: "#fff" }}>
              2개월 무료
            </span>
          </span>
        </div>
      </div>

      <div className="max-w-[900px] mx-auto px-10 py-16">
        {/* Plans */}
        <div className="grid grid-cols-2 gap-6 mb-16">
          {/* Free */}
          <div className="border-2 border-sym-border rounded-[24px] p-9 bg-white hover:shadow-xl transition-all">
            <div className="text-[14px] font-bold text-sym-text-light mb-2 uppercase tracking-widest">FREE</div>
            <div className="mb-1.5">
              <span className="text-[44px] font-black text-dark leading-none">0</span>
              <span className="text-[14px] text-sym-text-light">원</span>
            </div>
            <div className="text-[13px] text-sym-text-light mb-5">무료로 시작하기</div>
            <div className="text-[14px] text-sym-text-light mb-6 leading-[1.6]">
              아이디어 검증을 처음 시작하는 분들을 위한 플랜. 핵심 기능을 무료로 경험해보세요.
            </div>
            <ul className="list-none mb-7">
              {FREE_FEATURES.map((f) => (
                <li key={f.text} className="flex items-start gap-2.5 text-[14px] py-1.5 border-b border-sym-border last:border-0">
                  <span className={f.ok ? "text-primary font-extrabold" : "text-slate-300"}>
                    {f.ok ? "✓" : "✗"}
                  </span>
                  <span className={f.ok ? "text-sym-text" : "text-sym-text-light"}>{f.text}</span>
                </li>
              ))}
            </ul>
            <Link href="/login">
              <button className="w-full py-3.5 border-2 border-sym-border rounded-xl text-[15px] font-bold text-dark bg-white hover:border-primary hover:text-primary transition-all cursor-pointer">
                무료로 시작하기
              </button>
            </Link>
          </div>

          {/* Pro */}
          <div
            className="border-2 border-primary rounded-[24px] p-9 text-white relative hover:shadow-2xl transition-all"
            style={{ background: "linear-gradient(160deg, #1e3a5f, #1e293b)" }}
          >
            <div
              className="absolute -top-3.5 left-1/2 -translate-x-1/2 bg-primary text-white text-[12px] font-extrabold px-5 py-1 rounded-full whitespace-nowrap"
            >
              가장 인기 있는 플랜
            </div>
            <div className="text-[14px] font-bold text-[#94a3b8] mb-2 uppercase tracking-widest">PRO</div>
            <div className="mb-1.5">
              <span className="text-[44px] font-black leading-none">{proPrice}</span>
              <span className="text-[14px] text-[#94a3b8]">원 / 월</span>
            </div>
            <div className="text-[13px] text-[#94a3b8] mb-5">{proNote}</div>
            <div className="text-[14px] text-[#94a3b8] mb-6 leading-[1.6]">
              진지하게 창업을 준비하는 분들을 위한 플랜. 무제한 분석과 심층 리포트로 경쟁 우위를 확보하세요.
            </div>
            <ul className="list-none mb-7">
              {PRO_FEATURES.map((f) => (
                <li key={f.text} className="flex items-start gap-2.5 text-[14px] py-1.5 border-b border-white/10 last:border-0">
                  <span style={{ color: "var(--accent)" }} className="font-extrabold">✓</span>
                  <span className="text-[#e2e8f0]">{f.text}</span>
                </li>
              ))}
            </ul>
            <Link href="/login">
              <button className="w-full py-3.5 bg-primary border-2 border-primary rounded-xl text-[15px] font-bold text-white hover:bg-primary-dark transition-colors cursor-pointer">
                PRO 시작하기
              </button>
            </Link>
          </div>
        </div>

        {/* Compare table */}
        <h2 className="text-[22px] font-extrabold text-dark mb-6 text-center">플랜 상세 비교</h2>
        <table className="w-full border-collapse bg-white border border-sym-border rounded-2xl overflow-hidden mb-16">
          <thead>
            <tr>
              <th className="bg-sym-bg text-[13px] font-bold text-sym-text-light p-3.5 px-5 text-left border-b border-sym-border">기능</th>
              <th className="bg-sym-bg text-[13px] font-bold text-sym-text-light p-3.5 text-center border-b border-sym-border">FREE</th>
              <th className="bg-sym-bg text-[13px] font-bold text-primary p-3.5 text-center border-b border-sym-border">PRO</th>
            </tr>
          </thead>
          <tbody>
            {COMPARE_ROWS.map(([feat, free, pro]) => (
              <tr key={feat} className="hover:bg-sym-bg transition-colors">
                <td className="p-3.5 px-5 text-[14px] font-semibold text-sym-text border-b border-sym-border">{feat}</td>
                <td className={`p-3.5 text-center text-[14px] border-b border-sym-border ${free === "✓" ? "text-primary font-extrabold text-[16px]" : free === "✗" ? "text-slate-300" : "text-sym-text-light"}`}>
                  {free}
                </td>
                <td className={`p-3.5 text-center text-[14px] border-b border-sym-border font-bold ${pro === "✓" ? "text-primary text-[16px] font-extrabold" : pro === "✗" ? "text-slate-300" : "text-primary"}`}>
                  {pro}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* FAQ */}
        <h2 className="text-[22px] font-extrabold text-dark mb-6 text-center">자주 묻는 질문</h2>
        <div className="flex flex-col gap-2.5">
          {FAQ_ITEMS.map((item, i) => (
            <div key={i} className="bg-white border border-sym-border rounded-xl overflow-hidden">
              <button
                onClick={() => setOpenFaq(openFaq === i ? null : i)}
                className="w-full flex justify-between items-center px-5 py-4 text-[14px] font-bold text-dark bg-transparent border-0 cursor-pointer hover:bg-sym-bg transition-colors"
              >
                <span>{item.q}</span>
                <span>{openFaq === i ? "−" : "+"}</span>
              </button>
              {openFaq === i && (
                <div className="px-5 pb-4 text-[14px] text-sym-text-light leading-[1.7]">{item.a}</div>
              )}
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
