/** Shared plant-data helpers for the static Pages demo. */
(function (global) {
  const DATA_URL = 'data/plants.json';
  let cache = null;

  async function loadPlants() {
    if (cache) return cache;
    const res = await fetch(DATA_URL);
    if (!res.ok) throw new Error('Failed to load plants.json');
    cache = await res.json();
    return cache;
  }

  function bySlug(plants) {
    const map = {};
    for (const p of plants) map[p.slug] = p;
    return map;
  }

  function sunLabel(p) {
    return p.sun_needs_display || ({ full: 'Full sun', partial: 'Partial sun', shade: 'Shade tolerant' }[p.sun_needs] || p.sun_needs);
  }

  function maturity(p) {
    if (p.maturity_display) return p.maturity_display;
    if (p.days_to_maturity_min && p.days_to_maturity_max) {
      if (p.days_to_maturity_min === p.days_to_maturity_max) return `${p.days_to_maturity_min} days`;
      return `${p.days_to_maturity_min}–${p.days_to_maturity_max} days`;
    }
    if (p.days_to_maturity_min) return `~${p.days_to_maturity_min} days`;
    return '—';
  }

  global.GroundworkPlants = { loadPlants, bySlug, sunLabel, maturity };
})(typeof window !== 'undefined' ? window : globalThis);
