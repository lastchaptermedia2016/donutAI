/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    if (process.env.NODE_ENV === "production") {
      return [
        {
          source: "/api/:path*",
          destination: `${process.env.BACKEND_URL || "http://localhost:8000"}/api/:path*`,
        },
      ];
    }
    return [];
  },
  // ESLint and TypeScript errors are now enforced during builds
  // This ensures code quality and prevents broken code from reaching production
};

module.exports = nextConfig;
