'use client';

import { useId, useState } from 'react';
import { Loader2, CheckCircle, AlertCircle } from 'lucide-react';

interface NewsletterFormProps {
  variant?: 'default' | 'inline' | 'hero';
  states?: string[];
}

export function NewsletterForm({ variant = 'default', states }: NewsletterFormProps) {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');
  const emailId = useId();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus('loading');
    setErrorMessage('');

    try {
      const res = await fetch('/api/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          interested_states: states,
        }),
      });

      const data = await res.json();

      if (res.ok) {
        setStatus('success');
        setEmail('');
      } else {
        setStatus('error');
        setErrorMessage(data.error || 'Something went wrong. Please try again.');
      }
    } catch {
      setStatus('error');
      setErrorMessage('Network error. Please check your connection.');
    }
  };

  if (status === 'success') {
    return (
      <div className="flex items-center gap-2 text-green-600 font-medium py-2">
        <CheckCircle className="w-5 h-5" />
        <span>You are subscribed! Check your email for confirmation.</span>
      </div>
    );
  }

  const inputClasses =
    variant === 'hero'
      ? 'flex-1 px-4 py-3 text-lg border-2 border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent'
      : 'flex-1 px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent';

  const buttonClasses =
    variant === 'hero'
      ? 'px-6 py-3 bg-red-600 text-white text-lg font-semibold rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors'
      : 'px-5 py-2 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors';

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className={variant === 'inline' ? 'flex gap-2' : 'flex flex-col sm:flex-row gap-3'}>
        <label htmlFor={emailId} className="sr-only">
          Email address
        </label>
        <input
          id={emailId}
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="your@email.com"
          required
          disabled={status === 'loading'}
          className={inputClasses}
        />
        <button
          type="submit"
          aria-label="Subscribe to the newsletter"
          disabled={status === 'loading'}
          className={buttonClasses}
        >
          {status === 'loading' ? (
            <span className="flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Subscribing...</span>
            </span>
          ) : (
            'Subscribe Free'
          )}
        </button>
      </div>

      {status === 'error' && (
        <div className="flex items-center gap-2 text-red-600 text-sm mt-2">
          <AlertCircle className="w-4 h-4" />
          <span>{errorMessage}</span>
        </div>
      )}

      <p className="text-xs text-slate-500 mt-2">
        Daily fraud alerts from DOJ, FBI, SEC & state attorneys general. Unsubscribe anytime.
      </p>
    </form>
  );
}
