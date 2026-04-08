"use client"; // 브라우저에서만 동작 (애니메이션 때문에 필요)

// ============================================================
// components/report/StreamingText.tsx — 스트리밍 텍스트 표시
//
// 역할:
//   AI가 분석 결과를 생성하는 동안 글자가 타이핑되듯 나타나는
//   컴포넌트. content가 업데이트될 때마다 자동으로 리렌더된다.
//
//   커서 깜박임 효과: animate-pulse로 인디고 사각형이 깜박임
//
// 사용 위치: app/analyze/page.tsx (streaming=true일 때)
// ============================================================

interface Props {
  content: string; // AI가 생성한 텍스트 (조각이 추가될 때마다 업데이트됨)
}

export default function StreamingText({ content }: Props) {
  return (
    <div className="rounded-xl border border-gray-800 p-6 font-mono text-sm text-gray-300 whitespace-pre-wrap min-h-[200px]">
      {content}
      {/* 커서 깜박임 효과: AI가 타이핑 중임을 시각적으로 표현 */}
      <span className="inline-block w-2 h-4 bg-indigo-400 animate-pulse ml-0.5" />
    </div>
  );
}
