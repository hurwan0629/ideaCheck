const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function getTrends() {
  try {
    const res = await fetch(`${API_URL}/trends`, { next: { revalidate: 3600 } });
    if (!res.ok) return [];
    const data = await res.json();
    return data.trends ?? [];
  } catch {
    return [];
  }
}

export default async function TrendsPage() {
  const trends = await getTrends();

  return (
    <main className="max-w-4xl mx-auto px-6 py-12">
      <h1 className="text-2xl font-bold mb-2">시장 트렌드</h1>
      <p className="text-gray-400 text-sm mb-8">아이디어가 없을 때, 요즘 뜨는 시장을 먼저 살펴보세요.</p>

      {trends.length === 0 ? (
        <p className="text-gray-500">트렌드 데이터를 불러오는 중입니다...</p>
      ) : (
        <div className="flex flex-col gap-8">
          {trends.map((t: any) => (
            <section key={t.topic}>
              <h2 className="text-lg font-semibold mb-3 text-indigo-400">{t.topic}</h2>
              <div className="flex flex-col gap-3">
                {t.data.map((item: any, i: number) => (
                  <div key={i} className="rounded-lg border border-gray-800 p-4">
                    <p className="font-medium mb-1">{item.title}</p>
                    <p className="text-gray-400 text-sm line-clamp-2">{item.content}</p>
                  </div>
                ))}
              </div>
            </section>
          ))}
        </div>
      )}
    </main>
  );
}
