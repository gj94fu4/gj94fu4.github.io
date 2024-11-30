import { loadSections } from "./domLoader.js";
import { loadArticleContent } from "./articleLoader.js";
import { loadCategoryIndex } from "./categoryLoader.js";
import { updateSEO } from "./seoUpdater.js";

document.addEventListener("DOMContentLoaded", async () => {
  await loadSections();

  const urlParams = new URLSearchParams(window.location.search);
  const articleId = urlParams.get("article_id");

  if (articleId) {
    await loadArticleContent(articleId, updateSEO);
  } else {
    await loadCategoryIndex(updateSEO);
  }
});