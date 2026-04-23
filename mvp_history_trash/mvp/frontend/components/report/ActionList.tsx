// ============================================================
// components/report/ActionList.tsx — 액션 플랜 목록
//
// 역할:
//   "지금 당장 해야 할 일" 목록을 번호가 붙은 리스트로 보여준다.
//   번호는 단순한 숫자가 아니라 인디고 원형 뱃지로 스타일링된다.
//
// 사용 위치: components/report/ReportView.tsx
// ============================================================

interface Props {
  items: string[]; // 액션 플랜 문자열 배열 (예: ["랜딩 페이지 만들기", "베타 유저 모집"])
}

export default function ActionList({ items }: Props) {
  return (
    <ol className="flex flex-col gap-3">
      {items.map((item, i) => (
        <li key={i} className="flex gap-3 items-start">
          {/* 번호 뱃지: 인디고 원형 배경 + 번호 */}
          <span className="flex-shrink-0 w-6 h-6 rounded-full bg-indigo-900 text-indigo-300 text-xs font-bold flex items-center justify-center mt-0.5">
            {i + 1}
          </span>
          {/* 액션 항목 텍스트 */}
          <p className="text-gray-300 text-sm leading-relaxed">{item}</p>
        </li>
      ))}
    </ol>
  );
}
