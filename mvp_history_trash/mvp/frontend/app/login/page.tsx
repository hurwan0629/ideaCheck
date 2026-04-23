"use client";

import { useState } from "react";
import Link from "next/link";
import { signIn } from "@/lib/auth";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const err = await signIn(email, password);
    if (err) setError(err);
  }

  return (
    <main className="max-w-sm mx-auto px-6 py-24">
      <h1 className="text-2xl font-bold mb-8">로그인</h1>
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
          placeholder="비밀번호"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="px-4 py-3 rounded-lg bg-gray-900 border border-gray-700 focus:outline-none focus:border-indigo-500"
          required
        />
        {error && <p className="text-red-400 text-sm">{error}</p>}
        <button
          type="submit"
          className="py-3 rounded-lg bg-indigo-600 hover:bg-indigo-500 font-semibold transition-colors"
        >
          로그인
        </button>
      </form>
      <p className="text-gray-500 text-sm mt-6 text-center">
        계정이 없으신가요?{" "}
        <Link href="/signup" className="text-indigo-400 hover:underline">
          회원가입
        </Link>
      </p>
    </main>
  );
}
