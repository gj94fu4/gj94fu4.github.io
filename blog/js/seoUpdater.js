export function updateSEO() {
  const currentLanguage = document.body.className.includes("zh") ? "zh" : "en";
  const dynamicContent = document.querySelector("#dynamic-content");

  if (!dynamicContent) {
    console.warn("Dynamic content container not found.");
    return;
  }

  const activeContent = dynamicContent.querySelector(`[lang="${currentLanguage}"]`);
  if (!activeContent) return;

  const title = activeContent.querySelector(".title")?.textContent.trim();
  const description = activeContent.querySelector(".description")?.textContent.trim();
  const coverImage = activeContent.querySelector(".cover-image img")?.getAttribute("src");

  if (title) {
    document.title = `${title} - Lucky in the House`;
    document.querySelector('meta[property="og:title"]')?.setAttribute("content", `${title} - Lucky in the House`);
    document.querySelector('meta[name="twitter:title"]')?.setAttribute("content", `${title} - Lucky in the House`);
  }

  if (description) {
    document.querySelector('meta[name="description"]')?.setAttribute("content", description);
    document.querySelector('meta[property="og:description"]')?.setAttribute("content", description);
  }

  if (coverImage) {
    document.querySelector('meta[property="og:image"]')?.setAttribute("content", coverImage);
    document.querySelector('meta[name="twitter:image"]')?.setAttribute("content", coverImage);
  }

  const currentUrl = window.location.href;
  document.querySelector('meta[property="og:url"]')?.setAttribute("content", currentUrl);
  document.querySelector('meta[name="twitter:url"]')?.setAttribute("content", currentUrl);
}