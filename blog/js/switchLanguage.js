document.addEventListener("DOMContentLoaded", () => {
  // Detect language from URL query parameters
  const urlParams = new URLSearchParams(window.location.search);
  const currentLanguage = urlParams.get("lang") === "zh" ? "zh" : "en"; // Default to English if lang is not "zh"

  // Set body class based on detected language
  document.body.className = currentLanguage;

  // Function to update SEO information based on language
  function updateSEO(lang) {
    const seoMeta = document.querySelector(`#seo-${lang}`);
    if (!seoMeta) return;

    // Update document title
    document.title = seoMeta.getAttribute("data-title") || document.title;

    // Update meta description
    const description = seoMeta.getAttribute("data-description");
    if (description) {
      const descriptionMeta = document.querySelector('meta[name="description"]');
      descriptionMeta && descriptionMeta.setAttribute("content", description);
    }

    // Update Open Graph metadata
    const ogTitle = seoMeta.getAttribute("data-og-title");
    const ogDescription = seoMeta.getAttribute("data-og-description");
    ogTitle && document.querySelector('meta[property="og:title"]').setAttribute("content", ogTitle);
    ogDescription && document.querySelector('meta[property="og:description"]').setAttribute("content", ogDescription);

    // Update Twitter metadata
    const twitterTitle = seoMeta.getAttribute("data-twitter-title");
    twitterTitle && document.querySelector('meta[name="twitter:title"]').setAttribute("content", twitterTitle);
  }

  // Add event listeners for language switch buttons
  document.querySelectorAll("[data-lang-switch]").forEach((button) => {
    button.addEventListener("click", () => {
      const newLanguage = button.getAttribute("data-lang-switch");
      if (!newLanguage) return;

      document.body.className = newLanguage;
      updateSEO(newLanguage);

      // Optionally update the URL query parameter
      const newURL = new URL(window.location.href);
      newURL.searchParams.set("lang", newLanguage);
      history.replaceState(null, "", newURL.toString());
    });
  });

  // Initial SEO update
  updateSEO(currentLanguage);
});