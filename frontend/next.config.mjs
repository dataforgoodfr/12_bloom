/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    serverMinification: false
  },
  staticPageGenerationTimeout: 1000 * 60 * 5 // 5 minutes
}

export default nextConfig
