// ============================================================
// components/wizard/StepForm.tsx — 단계별 입력 폼
//
// 역할:
//   현재 step 값에 따라 다른 폼을 보여준다.
//   step=0: 아이디어 주제 입력 (필수)
//   step=1: 타겟 유저 + 수익 모델 입력 (선택)
//   step=2: 입력 내용 최종 확인 후 분석 시작
//
// 사용 위치: app/analyze/page.tsx
// ============================================================

interface Form {
  topic: string;
  target: string;
  revenue_model: string;
}

interface Props {
  step: number;
  form: Form;
  onChange: (key: keyof Form, val: string) => void; // 폼 값 변경 시 호출
  onNext: () => void;    // "다음" 버튼 클릭 시
  onBack: () => void;    // "이전" 버튼 클릭 시
  onSubmit: () => void;  // "분석 시작" 버튼 클릭 시
}

export default function StepForm({ step, form, onChange, onNext, onBack, onSubmit }: Props) {
  // 공통 인풋 스타일 (모든 입력창에 동일하게 적용)
  const inputCls =
    "w-full px-4 py-3 rounded-lg bg-gray-900 border border-gray-700 focus:outline-none focus:border-indigo-500 text-white placeholder-gray-500";

  return (
    <div className="flex flex-col gap-6">
      {/* ── 단계 0: 아이디어 주제 입력 ── */}
      {step === 0 && (
        <>
          <h2 className="text-xl font-semibold">어떤 서비스를 만들고 싶으신가요?</h2>
          <textarea
            className={`${inputCls} min-h-[120px] resize-none`}
            placeholder="예: AI 기반 스타트업 아이디어 검증 SaaS"
            value={form.topic}
            onChange={(e) => onChange("topic", e.target.value)}
          />
        </>
      )}

      {/* ── 단계 1: 타겟 & 수익 모델 입력 ── */}
      {step === 1 && (
        <>
          <h2 className="text-xl font-semibold">타겟과 수익 모델을 알려주세요</h2>
          <input
            className={inputCls}
            placeholder="타겟 (예: 사이드 프로젝트 개발자, 초기 창업자)"
            value={form.target}
            onChange={(e) => onChange("target", e.target.value)}
          />
          <input
            className={inputCls}
            placeholder="수익 모델 (예: Freemium SaaS, 월 $19/$49)"
            value={form.revenue_model}
            onChange={(e) => onChange("revenue_model", e.target.value)}
          />
        </>
      )}

      {/* ── 단계 2: 입력 내용 확인 ── */}
      {step === 2 && (
        <>
          <h2 className="text-xl font-semibold">분석을 시작할까요?</h2>
          {/* 지금까지 입력한 내용을 요약해서 보여준다 */}
          <div className="rounded-lg border border-gray-800 p-4 text-sm text-gray-400 flex flex-col gap-2">
            <p><span className="text-gray-300 font-medium">주제:</span> {form.topic}</p>
            <p><span className="text-gray-300 font-medium">타겟:</span> {form.target || "미입력"}</p>
            <p><span className="text-gray-300 font-medium">수익 모델:</span> {form.revenue_model || "미입력"}</p>
          </div>
        </>
      )}

      {/* ── 하단 버튼 ── */}
      <div className="flex gap-3 justify-end mt-2">
        {/* 이전 버튼: step 0에서는 숨김 */}
        {step > 0 && (
          <button
            onClick={onBack}
            className="px-6 py-2 rounded-lg border border-gray-700 hover:border-gray-500 text-sm transition-colors"
          >
            이전
          </button>
        )}

        {/* 마지막 단계가 아니면 "다음", 마지막 단계면 "분석 시작" */}
        {step < 2 ? (
          <button
            onClick={onNext}
            disabled={step === 0 && !form.topic.trim()} // 주제 미입력 시 비활성화
            className="px-6 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-sm font-semibold transition-colors disabled:opacity-40"
          >
            다음
          </button>
        ) : (
          <button
            onClick={onSubmit}
            className="px-6 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-sm font-semibold transition-colors"
          >
            분석 시작
          </button>
        )}
      </div>
    </div>
  );
}
