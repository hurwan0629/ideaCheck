import Link from "next/link";
import { cookies } from "next/headers";
import { createServerClient } from "@supabase/ssr";
import ReportCard from "@/components/report/ReportCard";
import { apiFetch } from "@/lib/api";

async function getUserReports() {
  const cookieStore = await cookies();
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
      },
    }
  );

  const { data: { session } } = await supabase.auth.getSession();
  if (!session) return [];

  return apiFetch<any[]>("/user/reports", {
    headers: { Authorization: `Bearer ${session.access_token}` },
  });
}

export default async function DashboardPage() {
  const reports = await getUserReports();

  return (
    <main className="max-w-4xl mx-auto px-6 py-12">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold">내 리포트</h1>
        <Link
          href="/analyze"
          className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-sm font-semibold transition-colors"
        >
          + 새 분석
        </Link>
      </div>

      {reports.length === 0 ? (
        <div className="text-center py-24 text-gray-500">
          <p className="mb-4">아직 분석한 아이디어가 없습니다.</p>
          <Link href="/analyze" className="text-indigo-400 hover:underline">
            첫 아이디어를 검증해보세요 →
          </Link>
        </div>
      ) : (
        <div className="grid gap-4">
          {reports.map((r) => (
            <ReportCard key={r.id} report={r} />
          ))}
        </div>
      )}
    </main>
  );
}
