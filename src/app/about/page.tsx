import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'About',
  description:
    'Learn how US Fraud Watch sources and verifies fraud, waste, and corruption coverage.',
};

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-slate-50">
      <section className="bg-gradient-to-b from-slate-900 to-slate-800 text-white py-14">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">About US Fraud Watch</h1>
          <p className="text-lg text-slate-300">
            We track fraud, waste, and corruption across America using official government
            sources and verified court records.
          </p>
        </div>
      </section>

      <div className="max-w-4xl mx-auto px-4 py-12 space-y-10">
        <section className="bg-white rounded-xl border p-6 shadow-sm">
          <h2 className="text-2xl font-bold text-slate-900 mb-3">Our Mission</h2>
          <p className="text-slate-600">
            US Fraud Watch helps the public monitor fraud and corruption with a focus on
            transparency. We surface verified cases, link to original documents, and highlight
            patterns that matter.
          </p>
        </section>

        <section className="bg-white rounded-xl border p-6 shadow-sm">
          <h2 className="text-2xl font-bold text-slate-900 mb-3">How We Source Data</h2>
          <ul className="space-y-3 text-slate-600 list-disc list-inside">
            <li>Federal agencies: DOJ, FBI, SEC, FTC, and HHS press releases.</li>
            <li>State attorneys general and auditor offices, with priority focus on MN and CA.</li>
            <li>Federal and state court records via CourtListener and PACER references.</li>
            <li>Automated ingestion that is reviewed for relevance and accuracy.</li>
          </ul>
        </section>

        <section className="bg-white rounded-xl border p-6 shadow-sm">
          <h2 className="text-2xl font-bold text-slate-900 mb-3">Editorial Standards</h2>
          <p className="text-slate-600">
            We do not make legal determinations of guilt or innocence. Every story links to
            primary sources and highlights verified details only.
          </p>
        </section>

        <section className="bg-white rounded-xl border p-6 shadow-sm">
          <h2 className="text-2xl font-bold text-slate-900 mb-3">Contact</h2>
          <p className="text-slate-600">
            Reach us at{' '}
            <a
              href="mailto:contact@usfraudwatch.com"
              className="text-red-600 hover:text-red-700 font-medium"
            >
              contact@usfraudwatch.com
            </a>
            .
          </p>
        </section>
      </div>
    </div>
  );
}
