import type { Metadata } from "next";
import "./globals.css";
import { AppSidebar } from "@/components/AppSidebar";
import { Toaster } from "@/components/ui/sonner";

export const metadata: Metadata = {
  title: "BabyMotion Content Studio",
  description: "Agentic content creation for BabyMotion stories",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen bg-background font-sans antialiased">
        <div className="flex h-screen overflow-hidden">
          <AppSidebar />
          <div className="flex-1 flex flex-col overflow-hidden">
            <main className="flex-1 overflow-y-auto p-6 lg:p-8">
              {children}
            </main>
          </div>
        </div>
        <Toaster richColors />
      </body>
    </html>
  );
}
