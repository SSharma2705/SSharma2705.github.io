(() => {
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const progress = document.createElement("div");
  progress.className = "site-progress";
  progress.setAttribute("aria-hidden", "true");
  document.body.prepend(progress);

  function updateProgress() {
    const total = document.documentElement.scrollHeight - window.innerHeight;
    const value = total > 0 ? window.scrollY / total : 0;
    progress.style.transform = "scaleX(" + Math.max(0, Math.min(value, 1)) + ")";
  }
  window.addEventListener("scroll", updateProgress, { passive: true });
  updateProgress();

  if (!reduceMotion && "IntersectionObserver" in window) {
    const targets = [...document.querySelectorAll("main section, .pub-group, .compact-feature")];
    targets.forEach((target) => target.setAttribute("data-reveal", ""));
    document.body.classList.add("motion-ready");
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.12 });
    targets.forEach((target) => observer.observe(target));
  }

  const canTilt = !reduceMotion && window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  if (canTilt) {
    document.querySelectorAll("[data-tilt], .portrait-wrap, .compact-feature").forEach((element) => {
      element.addEventListener("pointermove", (event) => {
        const box = element.getBoundingClientRect();
        const x = (event.clientX - box.left) / box.width - 0.5;
        const y = (event.clientY - box.top) / box.height - 0.5;
        element.classList.add("is-tilting");
        element.style.transform = "perspective(900px) rotateX(" + (-y * 2) + "deg) rotateY(" + (x * 2) + "deg) translateY(-2px)";
      });
      element.addEventListener("pointerleave", () => {
        element.classList.remove("is-tilting");
        element.style.transform = "";
      });
    });
  }
})();
