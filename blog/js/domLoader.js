export async function loadSections() {
  const sections = [
    { selector: "#navibar", path: "../../navibar/navibar_v2.html" },
    { selector: "#fh5co-header", path: "../components/header.html" },
    { selector: "#fh5co-footer", path: "../components/footer.html" },
  ];

  try {
    await Promise.all(
      sections.map(async ({ selector, path }) => {
        const response = await fetch(path);
        if (!response.ok) throw new Error(`Failed to load ${path}`);
        const html = await response.text();
        document.querySelector(selector).innerHTML = html;
      })
    );

    document.dispatchEvent(new Event("contentLoaded"));
  } catch (err) {
    console.error("Error loading sections:", err);
  }
}