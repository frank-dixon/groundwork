/**
 * Offline one-tap layout suggestion (spacing + companions).
 * Port of garden/suggest.py for the static GitHub Pages demo.
 */
(function (global) {
  function spacingFt(plant) {
    return Math.max(plant.spacing_inches / 12, 0.5);
  }

  function antagConflict(plant, placedSlugs, bySlug) {
    if (!placedSlugs.size) return false;
    return (plant.antagonists || []).some((s) => placedSlugs.has(s));
  }

  function companionBonus(plant, otherSlugs) {
    if (!otherSlugs.size) return 0;
    return (plant.companions || []).filter((s) => otherSlugs.has(s)).length;
  }

  /**
   * @param {{width_ft:number, length_ft:number}} bed
   * @param {object[]} plants
   * @returns {{plant:object, x_ft:number, y_ft:number, quantity:number}[]}
   */
  function suggestFill(bed, plants) {
    const width = Number(bed.width_ft);
    const length = Number(bed.length_ft);
    if (width <= 0 || length <= 0 || !plants.length) return [];

    const spacings = plants.map(spacingFt).sort((a, b) => a - b);
    let step = spacings[Math.floor(spacings.length / 2)];
    step = Math.max(0.75, Math.min(step, 3.0));

    const cells = [];
    for (let y = step / 2; y < length - 0.05; y += step) {
      for (let x = step / 2; x < width - 0.05; x += step) {
        cells.push([Math.round(x * 100) / 100, Math.round(y * 100) / 100]);
      }
    }

    const maxPlacements = Math.max(6, Math.min(36, cells.length));
    const grid = cells.slice(0, maxPlacements);

    const selectedSlugs = new Set(plants.map((p) => p.slug));
    const ranked = plants.slice().sort((a, b) => {
      const ba = companionBonus(a, new Set([...selectedSlugs].filter((s) => s !== a.slug)));
      const bb = companionBonus(b, new Set([...selectedSlugs].filter((s) => s !== b.slug)));
      if (bb !== ba) return bb - ba;
      if (a.spacing_inches !== b.spacing_inches) return a.spacing_inches - b.spacing_inches;
      return a.name.localeCompare(b.name);
    });

    const placed = [];
    const placedSlugs = new Set();
    const counts = Object.fromEntries(plants.map((p) => [p.slug, 0]));
    const share = Math.max(1, Math.floor(grid.length / ranked.length));
    const cycle = ranked.slice();
    let idx = 0;

    for (const [cx, cy] of grid) {
      let chosen = null;
      for (let attempt = 0; attempt < cycle.length; attempt++) {
        const plant = cycle[(idx + attempt) % cycle.length];
        const underQuotaExists = ranked.some((q) => counts[q.slug] < share);
        if (counts[plant.slug] >= share + 2 && underQuotaExists) continue;
        if (
          antagConflict(plant, placedSlugs) &&
          ranked.length > 1 &&
          ranked.some(
            (q) => counts[q.slug] < share && !antagConflict(q, placedSlugs)
          )
        ) {
          continue;
        }
        chosen = plant;
        idx = (idx + attempt + 1) % cycle.length;
        break;
      }
      if (!chosen) {
        chosen = cycle[idx % cycle.length];
        idx = (idx + 1) % cycle.length;
      }
      placed.push({ plant: chosen, x_ft: cx, y_ft: cy, quantity: 1 });
      placedSlugs.add(chosen.slug);
      counts[chosen.slug] += 1;
    }
    return placed;
  }

  global.GroundworkSuggest = { suggestFill };
})(typeof window !== 'undefined' ? window : globalThis);
