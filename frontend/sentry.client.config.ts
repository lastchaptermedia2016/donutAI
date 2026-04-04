import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  
  // Performance Monitoring
  tracesSampleRate: 0.1, // Capture 10% of transactions
  
  // Error Sampling
  sampleRate: 1.0, // Capture 100% of errors
  
  // Environment
  environment: process.env.NODE_ENV,
  
  // Release tracking
  release: process.env.NEXT_PUBLIC_APP_VERSION || "0.1.0",
  
  // Integrations
  integrations: [
    new Sentry.BrowserTracing(),
    new Sentry.Replay({
      maskAllText: true,
      blockAllMedia: true,
    }),
  ],
  
  // Session Replay
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
  
  // Before sending event
  beforeSend(event, hint) {
    // Filter out known benign errors
    const error = hint.originalException;
    if (error instanceof Error && error.message.includes("Network request failed")) {
      return null;
    }
    return event;
  },
});