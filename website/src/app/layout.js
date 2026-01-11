import { Inter } from 'next/font/google';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import './globals.css';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

export const metadata = {
  title: {
    default: 'LLM Daily - Your Daily AI & LLM News',
    template: '%s | LLM Daily',
  },
  description: 'Stay ahead of the curve with curated news about artificial intelligence, large language models, and the future of technology. Updated every 15 minutes.',
  keywords: ['AI news', 'LLM', 'artificial intelligence', 'machine learning', 'GPT', 'large language models', 'tech news'],
  authors: [{ name: 'LLM Daily' }],
  creator: 'LLM Daily',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://llmdaily.com',
    siteName: 'LLM Daily',
    title: 'LLM Daily - Your Daily AI & LLM News',
    description: 'Stay ahead of the curve with curated news about artificial intelligence, large language models, and the future of technology.',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'LLM Daily - Your Daily AI & LLM News',
    description: 'Stay ahead of the curve with curated news about AI and LLMs.',
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={inter.variable}>
      <body>
        <Header />
        <main>{children}</main>
        <Footer />
      </body>
    </html>
  );
}
