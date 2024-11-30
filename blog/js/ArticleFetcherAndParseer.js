async function fetchAndParseArticle(articleId, lang, fallbackPath) {
  const articlePath = `./${articleId}/content-${lang}.html`;
  const safeFetch = async (url) => {
    try {
      const response = await fetch(url);
      return response.ok ? response : await fetch(fallbackPath);
    } catch {
      return null;
    }
  };

  const response = await safeFetch(articlePath);
  if (response) {
    const content = await response.text();
    const parser = new DOMParser();
    return parser.parseFromString(content, "text/html");
  }
  return null;
}