import Link from 'next/link';

export function Footer() {
  return (
    <footer className="bg-slate-900 text-slate-400 py-12">
      <div className="max-w-6xl mx-auto px-4">
        <div className="grid md:grid-cols-4 gap-8">
          {/* About */}
          <div className="md:col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 bg-red-600 rounded-lg flex items-center justify-center">
                <span className="text-lg">🔍</span>
              </div>
              <span className="text-white font-bold">US FRAUD WATCH</span>
            </div>
            <p className="text-sm mb-4">
              We aggregate fraud-related announcements from the Department of Justice,
              FBI, SEC, FTC, state attorneys general, and federal courts. All sources
              are official government records—we link to every original document.
            </p>
            <p className="text-xs">
              This is not legal advice. All information is for educational purposes only.
            </p>
          </div>

          {/* Links */}
          <div>
            <h3 className="text-white font-semibold mb-4">Coverage</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/stories" className="hover:text-white transition-colors">
                  All Stories
                </Link>
              </li>
              <li>
                <Link href="/states/minnesota" className="hover:text-white transition-colors">
                  Minnesota Watch
                </Link>
              </li>
              <li>
                <Link href="/states/california" className="hover:text-white transition-colors">
                  California Watch
                </Link>
              </li>
              <li>
                <Link href="/stories?source=DOJ" className="hover:text-white transition-colors">
                  DOJ Cases
                </Link>
              </li>
              <li>
                <Link href="/stories?source=SEC" className="hover:text-white transition-colors">
                  SEC Actions
                </Link>
              </li>
            </ul>
          </div>

          {/* Sources */}
          <div>
            <h3 className="text-white font-semibold mb-4">Our Sources</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <a
                  href="https://www.justice.gov/news"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-white transition-colors"
                >
                  DOJ Press Office →
                </a>
              </li>
              <li>
                <a
                  href="https://www.fbi.gov/news"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-white transition-colors"
                >
                  FBI News →
                </a>
              </li>
              <li>
                <a
                  href="https://www.sec.gov/litigation"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-white transition-colors"
                >
                  SEC Litigation →
                </a>
              </li>
              <li>
                <a
                  href="https://www.courtlistener.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-white transition-colors"
                >
                  CourtListener →
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom */}
        <div className="border-t border-slate-700 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center gap-4 text-sm">
          <p>© {new Date().getFullYear()} US Fraud Watch. All rights reserved.</p>
          <div className="flex gap-6">
            <Link href="/about" className="hover:text-white transition-colors">
              About
            </Link>
            <Link href="/privacy" className="hover:text-white transition-colors">
              Privacy
            </Link>
            <Link href="/terms" className="hover:text-white transition-colors">
              Terms
            </Link>
            <a
              href="mailto:contact@usfraudwatch.com"
              className="hover:text-white transition-colors"
            >
              Contact
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
