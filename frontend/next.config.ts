import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Emit a self-contained server bundle so the Docker production image stays
  // small (only the files actually needed at runtime are copied).
  output: "standalone",
};

export default nextConfig;
