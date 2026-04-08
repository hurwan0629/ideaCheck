// ============================================================
// components/report/ReportView.tsx — 리포트 전체 뷰
//
// 역할:
//   리포트 결과 페이지의 메인 컴포넌트.
//   format.ts로 데이터를 변환한 뒤 하위 컴포넌트들에 나눠준다.
//
//   구조:
//     ReportView
//       ├── 요약 (summary)
//       ├── CompetitorTable (경쟁사 표)
//       ├── 시장 규모 (TAM/SAM/SOM 카드)
//       ├── ActionList (액션 플랜)
//       └── 출처 링크 목록
//
// 사용 위치: app/report/[id]/page.tsx
// ============================================================

import { formatReport, formatDate } from "@/lib/format";
import CompetitorTable from "./CompetitorTable";
import ActionList from "./ActionList";

interface Props {
  report: {
    id: string;
    input: Record<string, any>;     // 유저가 입력한 데이터 (topic 등)
    result: Record<string, any>;    // AI 분석 결과
    created_at: string;             // 생성 일시
  };
}

export default function ReportView({ report }: Props) {
  // 백엔드 JSON → 렌더링용 구조로 변환
  const data = formatReport(report.result);

  return (
    <article className="flex flex-col gap-8">
      {/* 헤더: 아이디어 제목 + 날짜 */}
      <header>
        <h1 className="text-2xl font-bold mb-1">{report.input.topic}</h1>
        <p className="text-gray-500 text-sm">{formatDate(report.created_at)}</p>
      </header>

      {/* 요약 */}
      <section>
        <h2 className="text-lg font-semibold mb-3">요약</h2>
        <p className="text-gray-300 leading-relaxed">{data.summary}</p>
      </section>

      {/* 경쟁사 분석 표 */}
      <section>
        <h2 className="text-lg font-semibold mb-3">경쟁사 분석</h2>
        <CompetitorTable competitors={data.competitors} />
      </section>

      {/* 시장 규모 카드 3개 (TAM/SAM/SOM) */}
      <section>
        <h2 className="text-lg font-semibold mb-3">시장 규모</h2>
        <div className="grid grid-cols-3 gap-4">
          {["tam", "sam", "som"].map((k) => (
            <div key={k} className="rounded-lg border border-gray-800 p-4 text-center">
              <p className="text-xs text-gray-500 uppercase mb-1">{k}</p>
              {/* 데이터가 없으면 "-"로 표시 */}
              <p className="font-semibold">{data.marketSize[k] ?? "-"}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 액션 플랜 번호 목록 */}
      <section>
        <h2 className="text-lg font-semibold mb-3">액션 플랜</h2>
        <ActionList items={data.actionPlan} />
      </section>

      {/* 출처 링크 (있을 때만 표시) */}
      {data.sources.length > 0 && (
        <section>
          <h2 className="text-lg font-semibold mb-3">출처</h2>
          <ul className="flex flex-col gap-1">
            {data.sources.map((src, i) => (
              <li key={i} className="text-indigo-400 text-sm truncate">
                <a href={src} target="_blank" rel="noopener noreferrer">{src}</a>
              </li>
            ))}
          </ul>
        </section>
      )}
    </article>
  );
}
