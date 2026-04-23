export default function SettingsPage() {
  return (
    <main className="max-w-2xl mx-auto px-6 py-12">
      <h1 className="text-2xl font-bold mb-8">계정 설정</h1>
      <div className="flex flex-col gap-6">
        <section className="rounded-xl border border-gray-800 p-6">
          <h2 className="font-semibold mb-4">프로필</h2>
          <p className="text-gray-400 text-sm">닉네임, 이메일 정보</p>
          {/* TODO: ProfileForm 컴포넌트 */}
        </section>
        <section className="rounded-xl border border-gray-800 p-6">
          <h2 className="font-semibold mb-4">구독 관리</h2>
          <p className="text-gray-400 text-sm">현재 플랜, 결제 정보, 해지</p>
          {/* TODO: SubscriptionPanel 컴포넌트 */}
        </section>
      </div>
    </main>
  );
}
