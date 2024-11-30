export async function loadArticleContent(articleId, updateSEO) {
  const articlePaths = {
    zh: `./${articleId}/content-zh.html`,
    en: `./${articleId}/content-en.html`,
    fall_back: `../components/under_construction.html`
  };

  async function safeFetch(url) {
    try {
      const response = await fetch(url);
      const notFound = await fetch(articlePaths.fall_back);
      return response.ok ? response : notFound;
    } catch {
      return null;
    }
  }

  try {
    // Fetch each language file independently
    const zhResponse = await safeFetch(articlePaths.zh);
    const enResponse = await safeFetch(articlePaths.en);

    // Extract contents only if response is OK
    const zhContent = zhResponse && zhResponse.ok ? await zhResponse.text() : null;
    const enContent = enResponse && enResponse.ok ? await enResponse.text() : null;

    // Handle cases where no content is available
    if (!zhContent && !enContent) {
      console.warn(`No valid content found for article_id: ${articleId}`);
      document.querySelector("#dynamic-content").innerHTML = `<p>Unable to load the requested article.</p>`;
      return;
    }

    // Dynamically build content
    const contentHTML = `
      ${zhContent ? `<div lang="zh" class="language-content row">${zhContent}</div>` : ""}
      ${enContent ? `<div lang="en" class="language-content row">${enContent}</div>` : ""}
    `;

    // Insert into the dynamic-content container
    document.querySelector("#dynamic-content").innerHTML = contentHTML;

    // Optionally update SEO metadata
    if (updateSEO) updateSEO();

  } catch (error) {
    console.error(`Unexpected error loading article content: ${error}`);
    document.querySelector("#dynamic-content").innerHTML = `<p>Unable to load the requested article.</p>`;
  }
}