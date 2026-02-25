import { type ClassValue, clsx } from 'clsx';

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

export function extractDollarAmounts(text: string): string[] {
  const regex = /\$[\d,]+(?:\.\d{2})?(?:\s*(?:million|billion|thousand))?/gi;
  return text.match(regex) || [];
}

export function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .trim();
}

export function truncate(text: string, length: number): string {
  if (text.length <= length) return text;
  return text.slice(0, length).trim() + '...';
}

export function getSourceColor(sourceName: string): string {
  const sourceColors: Record<string, string> = {
    DOJ: 'bg-blue-100 text-blue-800',
    FBI: 'bg-slate-100 text-slate-800',
    SEC: 'bg-green-100 text-green-800',
    FTC: 'bg-purple-100 text-purple-800',
    HHS: 'bg-red-100 text-red-800',
    'Attorney General': 'bg-amber-100 text-amber-800',
    AG: 'bg-amber-100 text-amber-800',
  };

  for (const [key, color] of Object.entries(sourceColors)) {
    if (sourceName?.includes(key)) {
      return color;
    }
  }

  return 'bg-gray-100 text-gray-800';
}
