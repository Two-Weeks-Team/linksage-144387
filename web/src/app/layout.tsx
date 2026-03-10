import "./globals.css";

export const metadata = {
  title: "LinkSage",
  description: "AI-Powered Organization for the Curious Mind",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="antialiased">
      <body className="bg-background text-foreground">{children}</body>
    </html>
  );
}