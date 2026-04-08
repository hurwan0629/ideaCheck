import Link from "next/link";

const PLANS = [
  {
    name: "Free",
    price: "$0",
    features: ["월 2회 리포트", "경쟁사 요약", "워터마크 PDF"],
    cta: "무료로 시작",
    href: "/analyze",
    highlight: false,
  },
  {
    name: "Lite",
    price: "$19/mo",
    features: ["월 10회 리포트", "출처 포함 데이터", "TAM/SAM/SOM 추정", "PDF 다운로드"],
    cta: "Lite 시작",
    href: "/signup?plan=lite",
    highlight: true,
  },
  {
    name: "Pro",
    price: "$49/mo",
    features: ["무제한 리포트", "아키텍처 추천 포함", "API 접근", "모든 Lite 기능"],
    cta: "Pro 시작",
    href: "/signup?plan=pro",
    highlight: false,
  },
];

export default function PricingPage() {
  return (
    <main className="max-w-4xl mx-auto px-6 py-16">
      <h1 className="text-3xl font-bold text-center mb-12">요금제</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {PLANS.map((p) => (
          <div
            key={p.name}
            className={`rounded-xl border p-8 flex flex-col gap-6 ${
              p.highlight ? "border-indigo-500 bg-indigo-950/30" : "border-gray-800"
            }`}
          >
            <div>
              <h2 className="text-xl font-bold mb-1">{p.name}</h2>
              <p className="text-2xl font-semibold text-indigo-400">{p.price}</p>
            </div>
            <ul className="flex flex-col gap-2 text-sm text-gray-300 flex-1">
              {p.features.map((f) => (
                <li key={f}>✓ {f}</li>
              ))}
            </ul>
            <Link
              href={p.href}
              className={`text-center py-2 rounded-lg font-semibold transition-colors ${
                p.highlight
                  ? "bg-indigo-600 hover:bg-indigo-500"
                  : "border border-gray-700 hover:border-gray-500"
              }`}
            >
              {p.cta}
            </Link>
          </div>
        ))}
      </div>
    </main>
  );
}
