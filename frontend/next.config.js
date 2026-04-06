/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    // Use NEXT_PUBLIC_BACKEND_URL if set, otherwise default to localhost
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
    
    // In production, proxy API requests to the backend
    if (process.env.NODE_ENV === "production") {
      return [
        {
          source: "/api/:path*",
          destination: `${backendUrl}/api/:path*`,
        },
      ];
    }
    
    // In development, also proxy to backend (useful if backend is on different port)
    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
  // ESLint and TypeScript errors are enforced during builds
  // This ensures code quality and prevents broken code from reaching production
};

module.exports = nextConfig;
