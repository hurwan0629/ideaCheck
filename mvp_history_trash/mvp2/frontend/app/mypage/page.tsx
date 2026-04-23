"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { analyzeAPI, ideasAPI } from "@/lib/api";
import { getUser, isLoggedIn, type User } from "@/lib/auth";

type Analysis = {
  id: number;
  service_name: string;
  category: string;
  result: { scores?: { market_growth?: number; competition?: number; differentiation?: number } } | null;
  created_at: string;
};

type Idea = {
  id: number;
  title: string;
  body: string;
  status: "idea" | "in_progress" | "analyzed";
  created_at: string;
};

const STATUS_STYLE: Record<string, { cls: string; label: string }> = {
  idea: { cls: "bg-blue-50 text-primary", label: "💡 아이디어" },
  in_progress: { cls: "bg-yellow-50 text-yellow-700", label: "🔄 검토 중" },
  analyzed: { cls: "bg-emerald-50 text-emerald-700", label: "✅ 분석 완료" },
};

export default function MypagePage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [tab, setTab] = useState<"history" | "ideas">("history");
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [ideas, setIdeas] = useState<Idea[]>([]);
  const [newIdeaTitle, setNewIdeaTitle] = useState("");
  const [showAddIdea, setShowAddIdea] = useState(false);

  useEffect(() => {
    if (!isLoggedIn()) { router.push("/login"); return; }
    setUser(getUser());
    analyzeAPI.history().then((r) => setAnalyses(r.data)).catch(() => {});
    ideasAPI.list().then((r) => setIdeas(r.data)).catch(() => {});
  }, [router]);

  const deleteAnalysis = async (id: number) => {
    await analyzeAPI.delete(id);
    setAnalyses((prev) => prev.filter((a) => a.id !== id));
  };

  const deleteIdea = async (id: number) => {
    await ideasAPI.delete(id);
    setIdeas((prev) => prev.filter((i) => i.id !== id));
  };

  const addIdea = async () => {
    if (!newIdeaTitle.trim()) return;
    const res = await ideasAPI.create({ title: newIdeaTitle });
    setIdeas((prev) => [res.data, ...prev]);
    setNewIdeaTitle("");
    setShowAddIdea(false);
  };

  if (!user) return null;

  const FREE_LIMIT = 5;
  const usagePct = Math.min((user.monthly_analysis_count / FREE_LIMIT) * 100, 100);
  const ideaPct = Math.min((ideas.length / 20) * 100, 100);

  return (
    <div className="max-w-[1000px] mx-auto px-10 py-10">
      {/* Profile banner */}
      <div
        className="rounded-[20px] p-7 flex items-center gap-5 mb-7 text-white"
        style={{ background: "linear-gradient(120deg, #1e293b, #1e3a5f)" }}
      >
        <div
          className="w-16 h-16 rounded-full flex items-center justify-center text-[26px] font-extrabold text-white flex-shrink-0"
          style={{ background: "linear-gradient(135deg, #2563eb, #06b6d4)" }}
        >
          {user.name[0].toUpperCase()}
        </div>
        <div>
          <h2 className="text-[20px] font-extrabold mb-1">
            {user.name}님{" "}
            <span
              className="text-[12px] font-bold px-3 py-1 rounded-full ml-2 uppercase"
              style={{ background: "rgba(6,182,212,0.15)", border: "1px solid rgba(6,182,212,0.3)", color: "var(--accent)" }}
            >
              {user.plan}
            </span>
          </h2>
          <p className="text-[#94a3b8] text-[13px]">
            {user.email} · {new Date(user.created_at).toLocaleDateString("ko-KR", { year: "numeric", month: "long" })} 가입
          </p>
        </div>
        <div className="ml-auto flex gap-7">
          {[
            { num: analyses.length, label: "총 분석" },
            { num: ideas.length, label: "저장된 아이디어" },
            { num: user.monthly_analysis_count, label: "이번 달 분석" },
          ].map((s) => (
            <div key={s.label} className="text-center">
              <div className="text-[24px] font-extrabold">{s.num}</div>
              <div className="text-[11px] text-[#94a3b8] mt-0.5">{s.label}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-[1fr_300px] gap-6">
        {/* Main */}
        <div>
          {/* Tabs */}
          <div className="flex border-b-2 border-sym-border mb-6">
            {(["history", "ideas"] as const).map((t) => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={`px-5 py-2.5 text-[14px] font-semibold cursor-pointer border-0 bg-transparent border-b-2 -mb-0.5 transition-all ${
                  tab === t ? "text-primary border-primary" : "text-sym-text-light border-transparent hover:text-dark"
                }`}
              >
                {t === "history" ? "분석 히스토리" : "아이디어 노트"}
              </button>
            ))}
          </div>

          {tab === "history" && (
            <div>
              {analyses.length === 0 ? (
                <div className="text-center py-16 text-sym-text-light">
                  <div className="text-[40px] mb-3">🔍</div>
                  아직 분석 내역이 없습니다.{" "}
                  <Link href="/analyze" className="text-primary font-semibold">지금 분석하러 가기 →</Link>
                </div>
              ) : (
                analyses.map((a) => (
                  <div key={a.id} className="card mb-3.5 hover:border-blue-300 hover:shadow-md transition-all cursor-pointer">
                    <div className="flex justify-between items-start mb-2.5">
                      <div className="text-[16px] font-extrabold text-dark">{a.service_name}</div>
                      <div className="text-[12px] text-sym-text-light">
                        {new Date(a.created_at).toLocaleDateString("ko-KR")}
                      </div>
                    </div>
                    {a.category && (
                      <div className="flex gap-1.5 mb-2.5">
                        <span className="tag">{a.category}</span>
                      </div>
                    )}
                    {a.result?.scores && (
                      <div className="flex gap-4 text-[12px] text-sym-text-light mb-3">
                        <span>시장 성장성 <strong className="text-dark">{a.result.scores.market_growth}점</strong></span>
                        <span>경쟁 강도 <strong className="text-dark">{a.result.scores.competition}점</strong></span>
                        <span>차별화 가능성 <strong className="text-dark">{a.result.scores.differentiation}점</strong></span>
                      </div>
                    )}
                    <div className="flex gap-2">
                      <Link href="/analyze" className="no-underline">
                        <button className="px-3.5 py-1.5 bg-primary text-white rounded-lg text-[12px] font-semibold hover:bg-primary-dark transition-colors cursor-pointer border-0">
                          분석 다시 보기
                        </button>
                      </Link>
                      <button
                        onClick={() => deleteAnalysis(a.id)}
                        className="px-3.5 py-1.5 border border-sym-border rounded-lg text-[12px] font-semibold bg-white text-sym-text hover:bg-sym-bg transition-colors cursor-pointer"
                      >
                        삭제
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {tab === "ideas" && (
            <div>
              {ideas.map((idea) => {
                const st = STATUS_STYLE[idea.status];
                return (
                  <div key={idea.id} className="card mb-3.5">
                    <div className="flex justify-between mb-2">
                      <div className="text-[15px] font-bold text-dark">{idea.title}</div>
                      <div className="text-[12px] text-sym-text-light">
                        {new Date(idea.created_at).toLocaleDateString("ko-KR")}
                      </div>
                    </div>
                    {idea.body && (
                      <div className="text-[13px] text-sym-text-light leading-[1.6] mb-3">{idea.body}</div>
                    )}
                    <div className="flex items-center gap-2">
                      <span className={`text-[11px] font-bold px-2.5 py-1 rounded-full ${st.cls}`}>{st.label}</span>
                      <Link href="/analyze" className="no-underline">
                        <button className="text-[11px] px-2.5 py-1 border border-sym-border rounded-lg bg-white text-sym-text hover:bg-sym-bg transition-colors cursor-pointer ml-2">
                          분석하기
                        </button>
                      </Link>
                      <button
                        onClick={() => deleteIdea(idea.id)}
                        className="text-[11px] px-2.5 py-1 border border-sym-border rounded-lg bg-white text-sym-text hover:bg-sym-bg transition-colors cursor-pointer"
                      >
                        삭제
                      </button>
                    </div>
                  </div>
                );
              })}

              {showAddIdea ? (
                <div className="card mb-3.5">
                  <input
                    className="form-input mb-3"
                    placeholder="아이디어 제목을 입력하세요"
                    value={newIdeaTitle}
                    onChange={(e) => setNewIdeaTitle(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && addIdea()}
                    autoFocus
                  />
                  <div className="flex gap-2">
                    <button onClick={addIdea} className="btn-primary text-[13px] py-2 px-4">저장</button>
                    <button onClick={() => setShowAddIdea(false)} className="btn-secondary text-[13px] py-2 px-4">취소</button>
                  </div>
                </div>
              ) : (
                <button
                  onClick={() => setShowAddIdea(true)}
                  className="w-full py-3 border-2 border-dashed border-sym-border rounded-[14px] bg-transparent text-[14px] font-semibold text-sym-text-light hover:border-primary hover:text-primary hover:bg-blue-50 transition-all cursor-pointer"
                >
                  + 새 아이디어 적어두기
                </button>
              )}
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div>
          <div className="card mb-4">
            <h3 className="text-[14px] font-extrabold text-dark mb-3.5">📊 이번 달 사용량</h3>
            <div className="mb-3.5">
              <div className="flex justify-between text-[13px] mb-1.5">
                <span className="text-sym-text">분석 횟수</span>
                <span className="font-bold text-dark">{user.monthly_analysis_count} / {user.plan === "pro" ? "무제한" : FREE_LIMIT}</span>
              </div>
              <div className="bg-slate-100 rounded-full h-1.5">
                <div className="h-full rounded-full bg-primary" style={{ width: `${user.plan === "pro" ? 30 : usagePct}%` }} />
              </div>
            </div>
            <div className="mb-3.5">
              <div className="flex justify-between text-[13px] mb-1.5">
                <span className="text-sym-text">저장된 아이디어</span>
                <span className="font-bold text-dark">{ideas.length} / {user.plan === "pro" ? "무제한" : 20}</span>
              </div>
              <div className="bg-slate-100 rounded-full h-1.5">
                <div className="h-full rounded-full bg-primary" style={{ width: `${user.plan === "pro" ? 20 : ideaPct}%` }} />
              </div>
            </div>
            {user.plan === "free" && (
              <div className="mt-3.5 p-3 bg-blue-50 rounded-[10px] text-[12px] text-blue-800">
                <strong>FREE 플랜</strong> 사용 중 · 무제한 분석을 원하시면{" "}
                <Link href="/pricing" className="text-primary font-bold no-underline">요금제 업그레이드하기 →</Link>
              </div>
            )}
          </div>

          <div className="card">
            <h3 className="text-[14px] font-extrabold text-dark mb-3.5">⚙️ 계정 설정</h3>
            {[
              { label: "이름", action: "변경" },
              { label: "이메일", action: "변경" },
              { label: "비밀번호", action: "변경" },
              { label: "알림 설정", action: "설정" },
            ].map((item) => (
              <div key={item.label} className="flex justify-between items-center py-2.5 border-b border-sym-border last:border-0 text-[13px]">
                <span className="text-sym-text">{item.label}</span>
                <button className="text-primary text-[12px] font-semibold bg-transparent border-0 cursor-pointer">{item.action}</button>
              </div>
            ))}
            <div className="flex justify-between items-center py-2.5 text-[13px]">
              <span className="text-red-500">계정 탈퇴</span>
              <button className="text-red-500 text-[12px] font-semibold bg-transparent border-0 cursor-pointer">탈퇴</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
