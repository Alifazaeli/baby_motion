import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/studio/api/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL}/studio/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
