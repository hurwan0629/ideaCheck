// ============================================================
// components/report/CompetitorTable.tsx — 경쟁사 비교 표
//
// 역할:
//   AI가 분석한 경쟁사 목록을 표(table)로 보여준다.
//   이름을 클릭하면 해당 경쟁사 URL로 이동할 수 있다.
//
// 사용 위치: components/report/ReportView.tsx
// ============================================================

interface Competitor {
  name: string;         // 경쟁사 이름
  description: string;  // 한 줄 설명
  url?: string;         // 웹사이트 URL (없을 수도 있음)
  strength?: string;    // 주요 강점
  weakness?: string;    // 주요 약점
}

interface Props {
  competitors: Competitor[];
}

export default function CompetitorTable({ competitors }: Props) {
  // 경쟁사가 없으면 메시지 표시
  if (!competitors.length) return <p className="text-gray-500 text-sm">경쟁사 데이터 없음</p>;

  return (
    <div className="overflow-x-auto"> {/* 모바일에서 가로 스크롤 허용 */}
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-800 text-gray-400">
            <th className="text-left py-2 pr-4">이름</th>
            <th className="text-left py-2 pr-4">설명</th>
            <th className="text-left py-2 pr-4">강점</th>
            <th className="text-left py-2">약점</th>
          </tr>
        </thead>
        <tbody>
          {competitors.map((c) => (
            <tr key={c.name} className="border-b border-gray-900">
              {/* URL이 있으면 링크로, 없으면 텍스트로 */}
              <td className="py-3 pr-4 font-medium">
                {c.url ? (
                  <a href={c.url} target="_blank" rel="noopener noreferrer" className="text-indigo-400 hover:underline">
                    {c.name}
                  </a>
                ) : (
                  c.name
                )}
              </td>
              <td className="py-3 pr-4 text-gray-400">{c.description}</td>
              <td className="py-3 pr-4 text-green-400">{c.strength ?? "-"}</td>
              <td className="py-3 text-red-400">{c.weakness ?? "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
