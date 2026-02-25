import { Metadata } from 'next';
import { NewsletterForm } from '@/components/newsletter-form';
import { CheckCircle } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Subscribe',
  description:
    'Get daily fraud alerts from DOJ, FBI, SEC, and state attorneys general delivered to your inbox.',
};

export default function SubscribePage() {
  const benefits = [
    'Daily fraud alerts from DOJ, FBI, and SEC',
    'Priority coverage of Minnesota and California',
    'Links to original government documents',
    'Curated by importance and relevance',
    'Unsubscribe anytime with one click',
  ];

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Hero */}
      <section className="bg-gradient-to-b from-slate-900 to-slate-800 text-white py-16">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Stay Ahead of Fraud
          </h1>
          <p className="text-xl text-slate-300 max-w-2xl mx-auto">
            Get daily updates on fraud, waste, and corruption from official
            government sources. Free forever.
          </p>
        </div>
      </section>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 -mt-8">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <div className="grid md:grid-cols-2 gap-8">
            {/* Form */}
            <div>
              <h2 className="text-2xl font-bold text-slate-900 mb-4">
                Subscribe Free
              </h2>
              <NewsletterForm variant="default" />

              <div className="mt-8">
                <h3 className="font-semibold text-slate-900 mb-3">
                  What you will get:
                </h3>
                <ul className="space-y-2">
                  {benefits.map((benefit, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-slate-600">
                      <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                      <span>{benefit}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Preview */}
            <div className="bg-slate-50 rounded-lg p-6">
              <h3 className="font-semibold text-slate-900 mb-4">
                Sample Newsletter Preview
              </h3>
              <div className="bg-white border rounded-lg p-4 text-sm">
                <div className="border-b pb-3 mb-3">
                  <div className="text-xs text-slate-500 mb-1">
                    From: US Fraud Watch
                  </div>
                  <div className="font-semibold">
                    Daily Fraud Briefing - Jan 17, 2025
                  </div>
                </div>
                <div className="space-y-3">
                  <div>
                    <div className="text-xs text-blue-600 font-medium">DOJ</div>
                    <div className="font-medium text-slate-900">
                      Minnesota Man Sentenced for $5.2M COVID Relief Fraud
                    </div>
                    <div className="text-xs text-slate-500 mt-1">
                      A Minnesota man was sentenced to 120 months for fraudulently
                      obtaining COVID-19 relief funds...
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-green-600 font-medium">SEC</div>
                    <div className="font-medium text-slate-900">
                      SEC Charges Investment Adviser in $25M Ponzi Scheme
                    </div>
                    <div className="text-xs text-slate-500 mt-1">
                      The SEC charged an investment adviser with running a Ponzi
                      scheme defrauding investors...
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-600 font-medium">FBI</div>
                    <div className="font-medium text-slate-900">
                      FBI Arrests Public Official in Corruption Probe
                    </div>
                    <div className="text-xs text-slate-500 mt-1">
                      FBI agents arrested a county official on charges of accepting
                      bribes...
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Trust indicators */}
        <div className="mt-12 text-center">
          <h3 className="text-sm font-semibold text-slate-500 mb-4">
            OUR DATA SOURCES
          </h3>
          <div className="flex flex-wrap justify-center gap-8 text-slate-400">
            <span>Department of Justice</span>
            <span>FBI</span>
            <span>SEC</span>
            <span>FTC</span>
            <span>State Attorneys General</span>
          </div>
        </div>
      </div>

      {/* FAQ */}
      <section className="max-w-4xl mx-auto px-4 py-16">
        <h2 className="text-2xl font-bold text-slate-900 mb-8 text-center">
          Frequently Asked Questions
        </h2>
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg p-6">
            <h3 className="font-semibold text-slate-900 mb-2">
              Is it really free?
            </h3>
            <p className="text-sm text-slate-600">
              Yes, the daily newsletter is completely free. We may offer premium
              features in the future, but the core newsletter will always be free.
            </p>
          </div>
          <div className="bg-white rounded-lg p-6">
            <h3 className="font-semibold text-slate-900 mb-2">
              Where does the data come from?
            </h3>
            <p className="text-sm text-slate-600">
              All stories come from official government sources: DOJ press
              releases, FBI news, SEC litigation releases, and state attorney
              general offices.
            </p>
          </div>
          <div className="bg-white rounded-lg p-6">
            <h3 className="font-semibold text-slate-900 mb-2">
              How often will I get emails?
            </h3>
            <p className="text-sm text-slate-600">
              By default, you will receive one daily email each morning with the
              previous day&apos;s top fraud stories. You can change this to weekly in
              your preferences.
            </p>
          </div>
          <div className="bg-white rounded-lg p-6">
            <h3 className="font-semibold text-slate-900 mb-2">
              Can I unsubscribe?
            </h3>
            <p className="text-sm text-slate-600">
              Yes, every email includes an unsubscribe link at the bottom. One
              click and you are removed immediately. No questions asked.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
