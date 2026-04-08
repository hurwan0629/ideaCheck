// ============================================================
// components/report/ReportCard.tsx — 리포트 카드 (대시보드용)
//
// 역할:
//   대시보드 페이지에서 리포트 하나를 카드 형태로 표시한다.
//   클릭하면 /report/{id} 상세 페이지로 이동한다.
//
// 사용 위치: app/dashboard/page.tsx
// ============================================================

import Link from "next/link";
import { formatDate } from "@/lib/format";

interface Props {
  report: {
    id: string;
    input: { topic: string };  // 아이디어 주제
    plan: string;              // 생성 시 플랜 ('free', 'lite', 'pro')
    created_at: string;        // 생성 일시
  };
}

export default function ReportCard({ report }: Props) {
  return (
    // Link: Next.js의 클라이언트 사이드 네비게이션 컴포넌트
    // 일반 <a> 태그보다 빠르게 페이지 전환이 가능하다
    <Link
      href={`/report/${report.id}`}
      className="rounded-xl border border-gray-800 p-5 hover:border-indigo-500 transition-colors flex justify-between items-center"
    >
      <div>
        {/* 아이디어 주제 */}
        <p className="font-medium mb-1">{report.input.topic}</p>
        {/* 생성 날짜 (한국어 형식으로 변환) */}
        <p className="text-gray-500 text-sm">{formatDate(report.created_at)}</p>
      </div>

      {/* 플랜 뱃지 (오른쪽 끝에 표시) */}
      <span className="text-xs px-2 py-1 rounded-full border border-gray-700 text-gray-400">
        {report.plan}
      </span>
    </Link>
  );
}
