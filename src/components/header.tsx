'use client';

import Link from 'next/link';
import { useState } from 'react';

export function Header() {
  const [isOpen, setIsOpen] = useState(false);

  const navLinks = [
    {
      href: '/stories',
      label: 'All Stories',
      className: 'text-slate-300 hover:text-white transition-colors',
    },
    {
      href: '/states/minnesota',
      label: 'Minnesota',
      className: 'text-slate-300 hover:text-white transition-colors',
    },
    {
      href: '/states/california',
      label: 'California',
      className: 'text-slate-300 hover:text-white transition-colors',
    },
    {
      href: '/subscribe',
      label: 'Subscribe Free',
      className:
        'bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-medium transition-colors',
    },
  ];

  return (
    <header className="bg-slate-900 text-white">
      {/* Top bar */}
      <div className="bg-red-700 text-white text-sm py-1">
        <div className="max-w-6xl mx-auto px-4 flex items-center justify-between">
          <span className="flex items-center gap-2">
            <span className="w-2 h-2 bg-white rounded-full animate-pulse"></span>
            Live: Monitoring DOJ, FBI, SEC, State AGs
          </span>
          <span className="hidden sm:block">Updated hourly from official sources</span>
        </div>
      </div>

      {/* Main header */}
      <div className="max-w-6xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-600 rounded-lg flex items-center justify-center">
              <span className="text-xl font-bold">🔍</span>
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight">US FRAUD WATCH</h1>
              <p className="text-xs text-slate-400">Tracking Fraud Across America</p>
            </div>
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex items-center gap-6">
            {navLinks.map((link) => (
              <Link key={link.href} href={link.href} className={link.className}>
                {link.label}
              </Link>
            ))}
          </nav>

          {/* Mobile menu button */}
          <button
            type="button"
            className="md:hidden p-2 text-slate-300 hover:text-white"
            aria-label="Toggle navigation menu"
            aria-controls="mobile-menu"
            aria-expanded={isOpen}
            onClick={() => setIsOpen((open) => !open)}
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>
        </div>
      </div>

      {isOpen && (
        <div id="mobile-menu" className="md:hidden border-t border-slate-800 bg-slate-900">
          <div className="max-w-6xl mx-auto px-4 py-4 flex flex-col gap-3">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={`block ${link.className}`}
                onClick={() => setIsOpen(false)}
              >
                {link.label}
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Category bar */}
      <div className="border-t border-slate-700">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex items-center gap-4 py-2 overflow-x-auto text-sm">
            <Link
              href="/stories?type=healthcare"
              className="text-slate-400 hover:text-white whitespace-nowrap"
            >
              🏥 Healthcare
            </Link>
            <Link
              href="/stories?type=financial"
              className="text-slate-400 hover:text-white whitespace-nowrap"
            >
              💰 Financial
            </Link>
            <Link
              href="/stories?type=government"
              className="text-slate-400 hover:text-white whitespace-nowrap"
            >
              🏛️ Government
            </Link>
            <Link
              href="/stories?type=corruption"
              className="text-slate-400 hover:text-white whitespace-nowrap"
            >
              ⚖️ Corruption
            </Link>
            <Link
              href="/stories?type=securities"
              className="text-slate-400 hover:text-white whitespace-nowrap"
            >
              📈 Securities
            </Link>
            <Link
              href="/stories?type=tax"
              className="text-slate-400 hover:text-white whitespace-nowrap"
            >
              📋 Tax
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}
