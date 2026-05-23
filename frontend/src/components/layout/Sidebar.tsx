"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { clsx } from "clsx";

const navItems = [
  { href: "/practice", label: "Practice", icon: "+" },
  { href: "/history", label: "History", icon: "~" },
  { href: "/library", label: "Library", icon: "#" },
  { href: "/settings", label: "Settings", icon: "*" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-56 border-r border-warm-100 bg-white p-4 flex flex-col gap-1">
      <div className="mb-6 px-3">
        <div className="text-2xl font-serif text-sage-700">SA</div>
      </div>
      {navItems.map((item) => (
        <Link
          key={item.href}
          href={item.href}
          className={clsx(
            "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
            pathname === item.href
              ? "bg-sage-50 text-sage-700"
              : "text-warm-600 hover:bg-warm-50 hover:text-warm-800"
          )}
        >
          <span className="text-lg w-5 text-center font-mono">{item.icon}</span>
          {item.label}
        </Link>
      ))}
    </aside>
  );
}
