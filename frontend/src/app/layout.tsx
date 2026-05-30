import type { Metadata } from "next";
import type { ReactNode } from "react";
import Link from "next/link";
import { History, Home, Library, LogIn, ShieldCheck } from "lucide-react";

import "./globals.css";

export const metadata: Metadata = {
  title: "SignCast AI",
  description: "Accessible news transformed into simple English, ASL gloss, and sign clip sequences."
};

const navItems = [
  { href: "/", label: "Home", icon: Home },
  { href: "/dashboard", label: "Dashboard", icon: History },
  { href: "/admin", label: "Dictionary", icon: Library },
  { href: "/login", label: "Login", icon: LogIn }
];

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen">
          <header className="border-b border-ink/10 bg-canvas/90 backdrop-blur">
            <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
              <Link href="/" className="flex items-center gap-2 font-semibold">
                <span className="flex h-9 w-9 items-center justify-center rounded bg-ink text-canvas">
                  <ShieldCheck size={20} aria-hidden="true" />
                </span>
                <span>SignCast AI</span>
              </Link>
              <nav className="flex items-center gap-1">
                {navItems.map((item) => {
                  const Icon = item.icon;
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className="flex items-center gap-2 rounded px-3 py-2 text-sm text-ink/70 transition hover:bg-ink/5 hover:text-ink"
                    >
                      <Icon size={17} aria-hidden="true" />
                      <span className="hidden sm:inline">{item.label}</span>
                    </Link>
                  );
                })}
              </nav>
            </div>
          </header>
          {children}
          <footer className="border-t border-ink/10 bg-white">
            <div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-6 text-sm text-ink/60 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
              <p>SignCast AI makes news easier to read, review, and watch through accessibility-first translation.</p>
              <nav className="flex flex-wrap gap-3">
                <Link href="/about" className="hover:text-ink">About</Link>
                <Link href="/accessibility" className="hover:text-ink">Accessibility</Link>
                <Link href="/privacy" className="hover:text-ink">Privacy</Link>
                <Link href="/terms" className="hover:text-ink">Terms</Link>
                <Link href="/contact" className="hover:text-ink">Contact</Link>
                <Link href="/faq" className="hover:text-ink">FAQ</Link>
              </nav>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
