// ============================================================
// store/wizard.ts — 아이디어 입력 위저드 전역 상태
//
// Zustand를 사용한 전역 상태 저장소.
//
// 왜 전역 상태가 필요한가?
//   위저드는 StepForm → StepIndicator → analyze/page.tsx 등
//   여러 컴포넌트에 걸쳐 있다.
//   1단계에서 입력한 topic을 3단계에서도 써야 하는데,
//   props로 계속 전달하면 복잡해진다.
//   → Zustand 저장소에 저장하면 어디서든 꺼내 쓸 수 있다.
//
// 사용 방법:
//   const { form, setField, nextStep } = useWizardStore()
// ============================================================

import { create } from "zustand";

/** 위저드 폼 데이터 타입 */
interface WizardForm {
  topic: string;          // 아이디어 주제
  target: string;         // 타겟 유저
  revenue_model: string;  // 수익 모델
  description: string;    // 추가 설명
}

/** 저장소 전체 타입 (데이터 + 액션) */
interface WizardStore {
  form: WizardForm;                               // 현재 폼 데이터
  step: number;                                    // 현재 단계 (0, 1, 2)
  setField: (key: keyof WizardForm, value: string) => void; // 특정 필드 값 변경
  nextStep: () => void;  // 다음 단계로 이동
  prevStep: () => void;  // 이전 단계로 이동 (0 미만으로 내려가지 않음)
  reset: () => void;     // 초기 상태로 리셋 (분석 완료 후 호출)
}

const DEFAULT_FORM: WizardForm = {
  topic: "",
  target: "",
  revenue_model: "",
  description: "",
};

/**
 * create(): Zustand 저장소를 만든다.
 * set()을 호출하면 상태가 변경되고 구독 중인 컴포넌트가 리렌더된다.
 */
export const useWizardStore = create<WizardStore>((set) => ({
  form: DEFAULT_FORM,
  step: 0,

  // 특정 필드만 업데이트 (스프레드로 나머지는 유지)
  setField: (key, value) =>
    set((s) => ({ form: { ...s.form, [key]: value } })),

  nextStep: () => set((s) => ({ step: s.step + 1 })),

  // Math.max로 0 미만으로 내려가지 않게 보호
  prevStep: () => set((s) => ({ step: Math.max(0, s.step - 1) })),

  // 분석 완료 후 다시 쓸 수 있도록 초기화
  reset: () => set({ form: DEFAULT_FORM, step: 0 }),
}));
