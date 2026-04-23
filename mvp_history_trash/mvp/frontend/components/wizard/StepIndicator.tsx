// ============================================================
// components/wizard/StepIndicator.tsx — 단계 진행 표시바
//
// 역할:
//   위저드의 "1 → 2 → 3" 진행 표시를 렌더링한다.
//   현재 단계는 인디고 색상, 완료된 단계도 인디고, 미래 단계는 회색.
//
// 사용 위치: app/analyze/page.tsx
//
// 예시 (step=1일 때):
//   ●1 서비스 주제 ─── ●2 타겟 & 수익모델 ─── ○3 분석 시작
//    (완료)                (현재)               (미래)
// ============================================================

interface Props {
  steps: string[]; // 단계 이름 목록 (예: ["서비스 주제", "타겟 & 수익모델", "분석 시작"])
  current: number; // 현재 단계 인덱스 (0부터 시작)
}

export default function StepIndicator({ steps, current }: Props) {
  return (
    <div className="flex items-center gap-2 mb-10">
      {steps.map((label, i) => (
        <div key={label} className="flex items-center gap-2">
          {/* 단계 번호 원형 버튼 */}
          <div
            className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${
              i <= current
                ? "bg-indigo-600 text-white"  // 현재 단계 이하: 인디고
                : "bg-gray-800 text-gray-500"  // 미래 단계: 회색
            }`}
          >
            {i + 1}
          </div>

          {/* 단계 이름 */}
          <span className={`text-sm ${i === current ? "text-white" : "text-gray-500"}`}>
            {label}
          </span>

          {/* 단계 사이 연결선 (마지막 단계에는 없음) */}
          {i < steps.length - 1 && (
            <div className={`w-8 h-px ${i < current ? "bg-indigo-600" : "bg-gray-700"}`} />
          )}
        </div>
      ))}
    </div>
  );
}
