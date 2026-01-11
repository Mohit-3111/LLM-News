/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable image optimization for external images
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
      {
        protocol: 'http',
        hostname: 'localhost',
      },
    ],
    // Disable image optimization for local files in development
    unoptimized: true,
  },

  // Rewrite requests for generated_images to serve from parent directory
  async rewrites() {
    return [
      {
        source: '/generated_images/:path*',
        destination: '/api/image/:path*',
      },
    ];
  },
};

export default nextConfig;
