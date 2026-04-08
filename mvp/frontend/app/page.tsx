import Link from "next/link";

export default function LandingPage() {
  return (
    <main className="flex flex-col items-center">
      {/* Hero */}
      <section className="w-full max-w-4xl mx-auto px-6 pt-24 pb-16 text-center">
        <h1 className="text-5xl font-bold mb-6 bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
          아이디어, 하루 만에 검증하세요
        </h1>
        <p className="text-lg text-gray-400 mb-10">
          바이브코딩 시대의 창업자를 위한 AI 시장조사 & 스타트업 아이디어 검증 플랫폼
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/analyze"
            className="px-8 py-3 rounded-lg bg-indigo-600 hover:bg-indigo-500 font-semibold transition-colors"
          >
            무료로 시작하기
          </Link>
          <Link
            href="/trends"
            className="px-8 py-3 rounded-lg border border-gray-700 hover:border-gray-500 font-semibold transition-colors"
          >
            시장 트렌드 보기
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="w-full max-w-4xl mx-auto px-6 py-16 grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          { title: "경쟁사 분석", desc: "실시간 웹 검색으로 경쟁사 3~5개를 자동 탐색" },
          { title: "시장 규모 추정", desc: "TAM/SAM/SOM을 데이터 기반으로 추정" },
          { title: "액션 플랜", desc: "지금 당장 해야 할 다음 단계를 구체적으로 제시" },
        ].map((f) => (
          <div key={f.title} className="rounded-xl border border-gray-800 p-6">
            <h3 className="font-semibold text-lg mb-2">{f.title}</h3>
            <p className="text-gray-400 text-sm">{f.desc}</p>
          </div>
        ))}
      </section>

      <section className="w-full max-w-4xl mx-auto px-6 py-8 text-center">
        <Link href="/pricing" className="text-indigo-400 hover:text-indigo-300 text-sm underline">
          요금제 보기 →
        </Link>
      </section>
    </main>
  );
}
