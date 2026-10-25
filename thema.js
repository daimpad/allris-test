// Themenseiten (pipeline/prozessbild.py): breite Zeitleisten auf schmalen Bildschirmen zum Datenstand schieben,
// damit zuerst die kommenden Sitzungen sichtbar sind. Ohne Skript bleibt die Zeitleiste links verschiebbar.
document.querySelectorAll(".pb-rahmen[data-start]").forEach((el) => {
  const start = Number(el.dataset.start);
  if (el.scrollWidth > el.clientWidth && start > 0) {
    el.scrollLeft = Math.max(0, start * el.scrollWidth - el.clientWidth / 3);
  }
});
