/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  allowedDevOrigins: [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'https://*.trycloudflare.com',
  ],
  env: {
    NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8001/backend',
    NEXT_PUBLIC_RISK_SERVICE_URL: process.env.NEXT_PUBLIC_RISK_SERVICE_URL || 'http://localhost:8000',
  },
}

module.exports = nextConfig
