import { AuthForm } from "@/components/auth-form";

export default function LoginPage() {
  return (
    <main className="mx-auto grid min-h-[calc(100vh-73px)] max-w-7xl place-items-center px-4 py-8 sm:px-6 lg:px-8">
      <div className="w-full">
        <div className="mx-auto mb-6 max-w-md">
          <h1 className="text-3xl font-semibold">Sign in</h1>
          <p className="mt-2 text-sm text-ink/60">Save articles and keep your sign animation watch history synced.</p>
        </div>
        <AuthForm />
      </div>
    </main>
  );
}
