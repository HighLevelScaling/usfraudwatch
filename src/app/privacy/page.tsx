import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Privacy Policy',
  description: 'How US Fraud Watch collects, stores, and protects your data.',
};

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-slate-50">
      <section className="bg-gradient-to-b from-slate-900 to-slate-800 text-white py-14">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">Privacy Policy</h1>
          <p className="text-lg text-slate-300">
            We respect your privacy and keep data collection minimal.
          </p>
        </div>
      </section>

      <div className="max-w-4xl mx-auto px-4 py-12 space-y-8">
        <section className="bg-white rounded-xl border p-6 shadow-sm">
          <h2 className="text-2xl font-bold text-slate-900 mb-3">Information We Collect</h2>
          <ul className="space-y-3 text-slate-600 list-disc list-inside">
            <li>Email address when you subscribe to the newsletter.</li>
            <li>Optional state preferences for personalized alerts.</li>
            <li>Basic analytics data to improve performance and usability.</li>
          </ul>
        </section>

        <section className="bg-white rounded-xl border p-6 shadow-sm">
          <h2 className="text-2xl font-bold text-slate-900 mb-3">How We Use Data</h2>
          <p className="text-slate-600">
            We use your email only to send newsletters and service updates. We do not sell
            or share subscriber data with third parties.
          </p>
        </section>

        <section className="bg-white rounded-xl border p-6 shadow-sm">
          <h2 className="text-2xl font-bold text-slate-900 mb-3">Data Security</h2>
          <p className="text-slate-600">
            Subscriber information is stored in secure infrastructure with restricted access.
            You can unsubscribe at any time via links in every email.
          </p>
        </section>

        <section className="bg-white rounded-xl border p-6 shadow-sm">
          <h2 className="text-2xl font-bold text-slate-900 mb-3">Contact</h2>
          <p className="text-slate-600">
            Questions? Email{' '}
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
