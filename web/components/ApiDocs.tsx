"use client";

import { useEffect } from "react";

declare global {
  interface Window {
    SwaggerUIBundle?: (options: Record<string, unknown>) => unknown;
  }
}

const assetBase = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5";

export function ApiDocs() {
  useEffect(() => {
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const syncTheme = () => {
      const theme = document.documentElement.dataset.theme;
      document.documentElement.dataset.apiTheme =
        theme === "dark" || (!theme && media.matches) ? "dark" : "light";
    };
    const observer = new MutationObserver(syncTheme);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["data-theme"],
    });
    media.addEventListener("change", syncTheme);
    syncTheme();
    const css = document.createElement("link");
    css.rel = "stylesheet";
    css.href = `${assetBase}/swagger-ui.css`;
    document.head.prepend(css);
    const render = () =>
      window.SwaggerUIBundle?.({
        url: "/api/openapi.json",
        dom_id: "#swagger-ui",
        deepLinking: true,
        layout: "BaseLayout",
        displayRequestDuration: true,
        persistAuthorization: true,
      });
    const script = document.createElement("script");
    script.src = `${assetBase}/swagger-ui-bundle.js`;
    script.onload = render;
    document.body.appendChild(script);
    return () => {
      css.remove();
      script.remove();
      observer.disconnect();
      media.removeEventListener("change", syncTheme);
      delete document.documentElement.dataset.apiTheme;
    };
  }, []);
  return (
    <div
      id="swagger-ui"
      className="api-docs"
      aria-label="API dokumentatsioon"
    />
  );
}
