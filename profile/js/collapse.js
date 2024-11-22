document.addEventListener("contentLoaded", () => {
  setupCollapse();
});

function setupCollapse() {
  const toggles = document.querySelectorAll("[data-toggle='collapse']");

  toggles.forEach((toggle) => {
    toggle.addEventListener("click", () => {
      const content = toggle.nextElementSibling;

      if (content && content.classList.contains("collapsible-content")) {
        content.classList.toggle("active");

        const arrow = toggle.querySelector(".arrow");
        if (arrow) {
          arrow.style.transform = content.classList.contains("active")
            ? "rotate(90deg)"
            : "rotate(0deg)";
        }
      }
    });
  });
}