export async function loadCategoryIndex(updateSEO) {
  const urlParams = new URLSearchParams(window.location.search);
  const lang = urlParams.get("lang") === "zh" || urlParams.get("lang") === "en" ? urlParams.get("lang") : "en";

  const categoryFilesDiv = document.querySelector("#category-files");

  if (!categoryFilesDiv) {
    console.error("Category files container not found.");
    return;
  }

  let categoryFiles = [];
  try {
    const filesData = categoryFilesDiv.getAttribute("data-files");
    if (!filesData) throw new Error("No data-files attribute found.");
    categoryFiles = JSON.parse(filesData).map((file) => `cat-${file}.html`);
  } catch (error) {
    console.error("Error parsing category files:", error);
    return;
  }

  try {
    const dynamicContentContainer = document.querySelector("#dynamic-content");
    const parser = new DOMParser();

    for (const file of categoryFiles) {
      const response = await fetch(`../components/${file}`);
      if (!response.ok) {
        console.warn(`Failed to load ${file}`);
        continue;
      }

      const content = await response.text();
      const doc = parser.parseFromString(content, "text/html");

      const board = doc.querySelector("#fh5co-board");
      if (!board) continue;

      const articleIds = JSON.parse(board.getAttribute("data-article-ids") || "[]");

      articleIds.forEach((articleId) => {
        const item = document.createElement("div");
        item.className = "item";
        item.setAttribute("data-article-id", articleId);
        item.innerHTML = "<!-- Dynamic content will be injected here -->";
        board.appendChild(item);
      });

      for (const articleId of articleIds) {
        try {
          const articlePaths = {
            zh: `./${articleId}/content-zh.html`,
            en: `./${articleId}/content-en.html`,
          };

          // Fetch language contents individually and handle missing files
          const zhResponse = await fetch(articlePaths.zh).catch(() => null);
          const enResponse = await fetch(articlePaths.en).catch(() => null);

          const zhContent = zhResponse && zhResponse.ok ? await zhResponse.text() : null;
          const enContent = enResponse && enResponse.ok ? await enResponse.text() : null;

          if (!zhContent && !enContent) {
            console.warn(`No valid content found for article_id: ${articleId}`);
            continue;
          }

          const zhDoc = zhContent ? parser.parseFromString(zhContent, "text/html") : null;
          const enDoc = enContent ? parser.parseFromString(enContent, "text/html") : null;

          const zhTitle = zhDoc?.querySelector(".title")?.textContent.trim() || "無標題";
          const enTitle = enDoc?.querySelector(".title")?.textContent.trim() || "Untitled";
          const zhDescription = zhDoc?.querySelector(".description")?.textContent.trim() || "";
          const enDescription = enDoc?.querySelector(".description")?.textContent.trim() || "";
          const zhCoverImage = zhDoc?.querySelector(".cover-image img")?.getAttribute("src") || "";
          const enCoverImage = enDoc?.querySelector(".cover-image img")?.getAttribute("src") || "";

          const item = board.querySelector(`[data-article-id="${articleId}"]`);
          if (item && zhDoc && enDoc) {
            item.innerHTML = `
              <div>
                <a class="fh5co-board-img">
                  <img src="${lang === "zh" ? zhCoverImage : enCoverImage}" alt="${lang === "zh" ? zhTitle : enTitle}">
                </a>
              </div>
              <div class="fh5co-desc">
                <div align="justify" lang="en">
                  <strong>${enTitle}</strong><br>${enDescription}
                  <a href="./?article_id=${articleId}">(Read more...)</a>
                </div>
                <div align="justify" lang="zh">
                  <strong>${zhTitle}</strong><br>${zhDescription}
                  <a href="./?article_id=${articleId}&lang=zh">（繼續閱讀）</a>
                </div>
              </div>
            `;
          }
          else if (item && zhDoc && !enDoc) {
            item.innerHTML = `
              <div lang="zh">
                <a class="fh5co-board-img">
                  <img src="${zhCoverImage}" alt="${zhTitle}">
                </a>
              </div>
              <div class="fh5co-desc" lang="zh">
                <div align="justify" lang="zh">
                  <strong>${zhTitle}</strong><br>${zhDescription}
                  <a href="./?article_id=${articleId}&lang=zh">（繼續閱讀）</a>
                </div>
              </div>
            `;
          }
          else if (item && !zhDoc && enDoc) {
            item.innerHTML = `
              <div lang="en">
                <a class="fh5co-board-img">
                  <img src="${enCoverImage}" alt="${enTitle}">
                </a>
              </div>
              <div class="fh5co-desc" lang="en">
                <div align="justify" lang="en">
                  <strong>${enTitle}</strong><br>${enDescription}
                  <a href="./?article_id=${articleId}">(Read more...)</a>
                </div>
              </div>
            `;
          }
        } catch (articleError) {
          console.error(`Error processing article_id ${articleId}:`, articleError);
        }
      }

      dynamicContentContainer.innerHTML += doc.body.innerHTML;
    }

    const grids = document.querySelectorAll("[data-columns]");
    grids.forEach((grid) => salvattore.registerGrid(grid));

    // Fetch SEO metadata
    const seoResponse = await fetch("../components/escapade-meta.html");
    if (!seoResponse.ok) throw new Error("Failed to load SEO metadata.");
    const seoHTML = await seoResponse.text();

    // Parse SEO content
    const seoDoc = parser.parseFromString(seoHTML, "text/html");
    const seoMeta = seoDoc.querySelector(`.seo-meta[lang="${lang}"]`);

    // Update SEO dynamically
    if (seoMeta) {
      const siteName = "Lucky in the House";
      const title = seoMeta.querySelector(".title")?.textContent.trim();
      const description = seoMeta.querySelector(".description")?.textContent.trim();
      const coverImage = seoMeta.querySelector(".cover-image img")?.getAttribute("src");
      const currentUrl = window.location.href;

      if (title) {
        document.title = `${title} - ${siteName}`;
        document.querySelector('meta[property="og:title"]').setAttribute("content", `${title} - ${siteName}`);
        document.querySelector('meta[name="twitter:title"]').setAttribute("content", `${title} - ${siteName}`);
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

    if (updateSEO) updateSEO();
  } catch (error) {
    console.error("Error loading category index:", error);
    document.querySelector("#dynamic-content").innerHTML = `<p>Unable to load the category index.</p>`;
  }
}