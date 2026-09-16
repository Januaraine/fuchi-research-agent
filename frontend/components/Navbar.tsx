"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [term, setTerm] = useState("");

  return (
    <nav className="navbar">
      <Link href="/" className="brand">
        KNOWLEDGE OBSERVATORY
        <span className="sub">知识观测站 · Civilization Knowledge Network</span>
      </Link>
      <div className="nav-links">
        <Link href="/" className={pathname === "/" ? "active" : ""}>
          Dashboard
        </Link>
        <Link href="/graph" className={pathname === "/graph" ? "active" : ""}>
          Graph
        </Link>
      </div>
      <div className="grow" />
      <form
        className="search-box"
        onSubmit={(e) => {
          e.preventDefault();
          const q = term.trim();
          if (!q) return;
          router.push(`/graph?q=${encodeURIComponent(q)}`);
        }}
      >
        <input
          value={term}
          onChange={(e) => setTerm(e.target.value)}
          placeholder="搜索知识节点…"
        />
        <button type="submit">搜索</button>
      </form>
    </nav>
  );
}
