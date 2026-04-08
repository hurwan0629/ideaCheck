"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import StepIndicator from "@/components/wizard/StepIndicator";
import StepForm from "@/components/wizard/StepForm";
import StreamingText from "@/components/report/StreamingText";
import { readStream } from "@/lib/stream";

const STEPS = ["서비스 주제", "타겟 & 수익모델", "분석 시작"];

export default function AnalyzePage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [form, setForm] = useState({ topic: "", target: "", revenue_model: "" });
  const [streaming, setStreaming] = useState(false);
  const [statusMsg, setStatusMsg] = useState("");
  const [chunks, setChunks] = useState("");

  async function startAnalysis() {
    setStreaming(true);
    const reportId = await readStream("/analyze", form, {
      onStatus: setStatusMsg,
      onChunk: (c) => setChunks((prev) => prev + c),
    });
    if (reportId) router.push(`/report/${reportId}`);
  }

  if (streaming) {
    return (
      <main className="max-w-2xl mx-auto px-6 py-16">
        <p className="text-indigo-400 mb-4">{statusMsg}</p>
        <StreamingText content={chunks} />
      </main>
    );
  }

  return (
    <main className="max-w-2xl mx-auto px-6 py-16">
      <StepIndicator steps={STEPS} current={step} />
      <StepForm
        step={step}
        form={form}
        onChange={(key, val) => setForm((f) => ({ ...f, [key]: val }))}
        onNext={() => setStep((s) => s + 1)}
        onBack={() => setStep((s) => s - 1)}
        onSubmit={startAnalysis}
      />
    </main>
  );
}
