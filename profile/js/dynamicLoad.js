document.addEventListener("DOMContentLoaded", async () => {
  try {
    // Dynamic loading of Navibar
    const navibar = await fetch("../navibar/navibar_v2.html");
    const navibarHTML = await navibar.text();
    document.querySelector("#navibar").innerHTML = navibarHTML;

    // Dynamic loading of Footer
    const footer = await fetch("components/footer.html");
    const footerHTML = await footer.text();
    document.querySelector("#footer").innerHTML = footerHTML;

    // Dynamic loading of About section
    const about = await fetch("components/about.html");
    const aboutHTML = await about.text();
    document.querySelector("#about").innerHTML = aboutHTML;

    // Dynamic loading of Resume sections
    await loadResumeSections();

    // Trigger collapsible functionality after all sections are loaded
    document.dispatchEvent(new Event("contentLoaded"));

  } catch (err) {
    console.error("Error loading sections:", err);
  }
});

// Function: Load individual sections of Resume in sequence
async function loadResumeSections() {
  try {
    const resumeSections = [
      { url: "components/education.html", id: "education" },
      { url: "components/business.html", id: "business" },
      { url: "components/academia.html", id: "academia" },
      { url: "components/student_club.html", id: "student-club" },
      { url: "components/volunteer.html", id: "volunteer" },
    ];

    for (const section of resumeSections) {
      const response = await fetch(section.url);
      const html = await response.text();
      const sectionDiv = document.createElement("div");
      sectionDiv.id = section.id;
      sectionDiv.innerHTML = html;
      document.querySelector("#resume").appendChild(sectionDiv);
    }
  } catch (err) {
    console.error("Error loading resume sections:", err);
  }
}