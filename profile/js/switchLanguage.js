document.addEventListener("DOMContentLoaded", () => {
  // Detect language from URL query parameters
  const url = location.href;
  let currentLanguage = "en"; // Default to English

  if (url.indexOf("?") !== -1) {
    const queryParams = url.split("?")[1].split("&");
    queryParams.forEach((param) => {
      const [key, value] = param.split("=");
      if (key === "lang" && (value === "zh" || value === "en")) {
        currentLanguage = value;
      }
    });
  }

  // Set body class based on detected language
  document.body.className = currentLanguage;

  // Function to update SEO information based on language
  function updateSEO(lang) {
    const titleElement = document.getElementById("dynamic-title");
    const descriptionElement = document.getElementById("dynamic-description");
    const seoMeta = document.querySelector(`#seo-${lang}`);

    if (seoMeta) {
      const title = seoMeta.getAttribute("data-title");
      const description = seoMeta.getAttribute("data-description");

      if (titleElement) titleElement.textContent = title;
      if (descriptionElement) descriptionElement.setAttribute("content", description);
    }
  }

  // Detect language switch and update SEO
  document.querySelectorAll("[onclick]").forEach((element) => {
    element.addEventListener("click", () => {
      if (element.textContent.includes("EN")) {
        currentLanguage = "en";
      } else if (element.textContent.includes("中")) {
        currentLanguage = "zh";
      }
      document.body.className = currentLanguage;
      updateSEO(currentLanguage);
    });
  });

  // Initial SEO update
  updateSEO(currentLanguage);
});