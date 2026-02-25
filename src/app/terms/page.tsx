import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Terms of Use',
  description: 'Terms and conditions for using US Fraud Watch.',
};

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-slate-50">
      <section className="bg-gradient-to-b from-slate-900 to-slate-800 text-white py-14">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">Terms of Use</h1>
          <p className="text-lg text-slate-300">
            By using US Fraud Watch, you agree to the terms below.
          </p>
        </div>
      </section>

      <div className="max-w-4xl mx-auto px-4 py-12 space-y-8">
        <section className="bg-white rounded-xl border p-6 shadow-sm">
          <h2 className="text-2xl font-bold text-slate-900 mb-3">Use of Content</h2>
          <p className="text-slate-600">
            All information is provided for educational and journalistic purposes. We link to
            original government documents for verification and do not provide legal advice.
          </p>
        </section>

        <section className="bg-white rounded-xl border p-6 shadow-sm">
          <h2 className="text-2xl font-bold text-slate-900 mb-3">No Legal Determinations</h2>
          <p className="text-slate-600">
            US Fraud Watch does not make determinations about guilt or innocence. Users should
            consult original sources and professional counsel if needed.
          </p>
        </section>

        <section className="bg-white rounded-xl border p-6 shadow-sm">
          <h2 className="text-2xl font-bold text-slate-900 mb-3">Availability</h2>
          <p className="text-slate-600">
            We aim for accuracy and uptime, but we cannot guarantee uninterrupted service.
            Data pipelines and third-party sources may change without notice.
          </p>
        </section>

        <section className="bg-white rounded-xl border p-6 shadow-sm">
          <h2 className="text-2xl font-bold text-slate-900 mb-3">Contact</h2>
          <p className="text-slate-600">
            Questions about these terms? Contact{' '}
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
