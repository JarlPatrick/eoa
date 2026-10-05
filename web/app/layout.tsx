import type { Metadata } from "next";
import Link from "next/link";
import { ThemeToggle } from "@/components/ThemeToggle";
import { HeaderNavigation } from "@/components/HeaderNavigation";
import { HeaderSearch } from "@/components/HeaderSearch";
import "./globals.css";

export const metadata: Metadata = {
  title: { default: "Eesti Olümpiaadide Andmebaas", template: "%s | EOA" },
  description: "Eesti olümpiaadide tulemused, osalejad ja koolid.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="et" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html:
              "try{var t=localStorage.getItem('eoa-theme');if(t==='light'||t==='dark')document.documentElement.dataset.theme=t}catch(e){}",
          }}
        />
      </head>
      <body>
        <header className="site-header">
          <div className="shell header-inner">
            <Link
              prefetch={false}
              href="/"
              className="brand"
              aria-label="EOA avaleht"
            >
              EOA
            </Link>
            <div className="header-main">
              <HeaderNavigation />
              <HeaderSearch />
              <ThemeToggle />
            </div>
          </div>
        </header>
        <div className="shell site-content">
          <main id="main-content">{children}</main>
        </div>
        <footer className="site-footer">
          <div className="shell">
            Eesti Olümpiaadide Andmebaas ·{" "}
            <a href="mailto:eoakontakt@gmail.com">Kontakt</a>
          </div>
        </footer>
      </body>
    </html>
  );
}
