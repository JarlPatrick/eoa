import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  async redirects() {
    return [{ source: "/index.php", destination: "/", permanent: true }];
  },
};

export default nextConfig;
