export function applySEO(metaContent, siteName = "Lucky in the House") {
  const title = metaContent.querySelector(".title")?.textContent.trim();
  const description = metaContent.querySelector(".description")?.textContent.trim();
  const coverImage = metaContent.querySelector(".cover-image img")?.getAttribute("src");
  const currentUrl = window.location.href;

  if (title) {
    document.title = `${title} - ${siteName}`;
    document.querySelector('meta[property="og:title"]')?.setAttribute("content", `${title} - ${siteName}`);
    document.querySelector('meta[name="twitter:title"]')?.setAttribute("content", `${title} - ${siteName}`);
  }

  if (description) {
    document.querySelector('meta[name="description"]')?.setAttribute("content", description);
    document.querySelector('meta[property="og:description"]')?.setAttribute("content", description);
  }

  if (coverImage) {
    const absoluteCoverImage = new URL(coverImage, currentUrl).href;
    document.querySelector('meta[property="og:image"]')?.setAttribute("content", absoluteCoverImage);
    document.querySelector('meta[name="twitter:image"]')?.setAttribute("content", absoluteCoverImage);
  }

  document.querySelector('meta[property="og:url"]')?.setAttribute("content", currentUrl);
  document.querySelector('meta[name="twitter:url"]')?.setAttribute("content", currentUrl);
  document.querySelector('meta[property="og:site_name"]')?.setAttribute("content", siteName);
}

export function updateSEO() {
  const currentLanguage = document.body.className.includes("zh") ? "zh" : "en";
  const dynamicContent = document.querySelector("#dynamic-content");

  if (!dynamicContent) {
    console.warn("Dynamic content container not found.");
    return;
  }

  const activeContent = dynamicContent.querySelector(`[lang="${currentLanguage}"]`);
  if (!activeContent) return;

  // Use applySEO to manage SEO meta updates
  applySEO(activeContent);
}