import { notFound } from "next/navigation";
import ReportView from "@/components/report/ReportView";

async function getReport(id: string) {
  const res = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/report/${id}`,
    { cache: "no-store" }
  );
  if (!res.ok) return null;
  return res.json();
}

export default async function ReportPage(props: PageProps<"/report/[id]">) {
  const { id } = await props.params;
  const report = await getReport(id);
  if (!report) notFound();

  return (
    <main className="max-w-4xl mx-auto px-6 py-12">
      <ReportView report={report} />
    </main>
  );
}
