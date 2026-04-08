"use client";

import { Suspense, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { signUp } from "@/lib/auth";

function SignupForm() {
  const searchParams = useSearchParams();
  const plan = searchParams.get("plan") ?? "free";
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const err = await signUp(email, password);
    if (err) setError(err);
    else setDone(true);
  }

  if (done) {
    return (
      <main className="max-w-sm mx-auto px-6 py-24 text-center">
        <h1 className="text-2xl font-bold mb-4">이메일을 확인하세요</h1>
        <p className="text-gray-400">인증 링크를 보내드렸습니다.</p>
      </main>
    );
  }

  return (
    <main className="max-w-sm mx-auto px-6 py-24">
      <h1 className="text-2xl font-bold mb-2">회원가입</h1>
      {plan !== "free" && (
        <p className="text-indigo-400 text-sm mb-6">{plan.toUpperCase()} 플랜으로 시작</p>
      )}
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <input
          type="email"
          placeholder="이메일"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="px-4 py-3 rounded-lg bg-gray-900 border border-gray-700 focus:outline-none focus:border-indigo-500"
          required
        />
        <input
          type="password"
          placeholder="비밀번호 (8자 이상)"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="px-4 py-3 rounded-lg bg-gray-900 border border-gray-700 focus:outline-none focus:border-indigo-500"
          minLength={8}
          required
        />
        {error && <p className="text-red-400 text-sm">{error}</p>}
        <button
          type="submit"
          className="py-3 rounded-lg bg-indigo-600 hover:bg-indigo-500 font-semibold transition-colors"
        >
          회원가입
        </button>
      </form>
      <p className="text-gray-500 text-sm mt-6 text-center">
        이미 계정이 있으신가요?{" "}
        <Link href="/login" className="text-indigo-400 hover:underline">
          로그인
        </Link>
      </p>
    </main>
  );
}

export default function SignupPage() {
  return (
    <Suspense fallback={<div className="py-24 text-center text-gray-500">로딩 중...</div>}>
      <SignupForm />
    </Suspense>
  );
}
