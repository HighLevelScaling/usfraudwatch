import type { Metadata } from 'next';
import { Inter, Merriweather } from 'next/font/google';
import './globals.css';
import { Header } from '@/components/header';
import { Footer } from '@/components/footer';

const inter = Inter({
  variable: '--font-inter',
  subsets: ['latin'],
});

const merriweather = Merriweather({
  variable: '--font-merriweather',
  subsets: ['latin'],
  weight: ['400', '700', '900'],
});

export const metadata: Metadata = {
  title: {
    default: 'US Fraud Watch - Tracking Fraud, Waste & Corruption',
    template: '%s | US Fraud Watch',
  },
  metadataBase: new URL('https://usfraudwatch.com'),
  description:
    'Data-driven tracking of fraud, waste, and corruption across America. DOJ indictments, SEC actions, state fraud cases. Source-verified. Updated hourly.',
  keywords: [
    'fraud',
    'corruption',
    'DOJ',
    'FBI',
    'SEC',
    'government waste',
    'public corruption',
    'financial fraud',
    'healthcare fraud',
  ],
  authors: [{ name: 'US Fraud Watch' }],
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://usfraudwatch.com',
    siteName: 'US Fraud Watch',
    title: 'US Fraud Watch - Tracking Fraud, Waste & Corruption',
    description:
      'Data-driven tracking of fraud, waste, and corruption across America.',
    images: [
      {
        url: '/og.png',
        width: 1200,
        height: 630,
        alt: 'US Fraud Watch',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'US Fraud Watch',
    description:
      'Data-driven tracking of fraud, waste, and corruption across America.',
    images: ['/og.png'],
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${inter.variable} ${merriweather.variable} font-sans antialiased bg-slate-50 text-slate-900`}
      >
        <div className="min-h-screen flex flex-col">
          <Header />
          <main className="flex-1">{children}</main>
          <Footer />
        </div>
      </body>
    </html>
  );
}
