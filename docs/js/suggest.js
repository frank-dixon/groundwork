/**
 * Intentional bed/plot layout suggestions (templates/guilds + per-crop spacing).
 * Port of garden/suggest.py for the static GitHub Pages demo.
 * Template definitions load from data/layout_sources.json (cached offline).
 */
(function (global) {
  let SOURCES = null;
  let SOURCES_PROMISE = null;

  const FALLBACK_SOURCES = {
    citations: [
      {
        id: 'umn',
        title: 'Vegetables — Growing guides',
        url: 'https://extension.umn.edu/vegetables',
        org: 'University of Minnesota Extension',
      },
      {
        id: 'cornell',
        title: 'Home Gardening — Vegetables',
        url: 'https://horticulture.cals.cornell.edu/',
        org: 'Cornell University Horticulture',
      },
      {
        id: 'almanac',
        title: 'Vegetable Growing Guides',
        url: 'https://www.almanac.com/gardening/growing-guides',
        org: 'Old Farmer’s Almanac',
      },
      {
        id: 'sfg',
        title: 'Square Foot Gardening plant spacing (fair-use citation of public guidance)',
        url: 'https://squarefootgardening.org/',
        org: 'Mel Bartholomew / Square Foot Gardening Foundation',
      },
      {
        id: 'companions',
        title: 'Companion planting overview',
        url: 'https://extension.umn.edu/planting-and-growing-guides/companion-planting-home-gardens',
        org: 'University of Minnesota Extension',
      },
      {
        id: 'three_sisters',
        title: 'Three Sisters garden (corn, bean, squash polyculture)',
        url: 'https://www.almanac.com/content/three-sisters-corn-bean-squash',
        org: 'Old Farmer’s Almanac / traditional Indigenous companion planting',
      },
    ],
    templates: [
      {
        id: 'three_sisters',
        name: 'Three Sisters',
        crops: ['corn', 'bean', 'squash'],
        min_match: 2,
        priority: 100,
        pattern: 'three_sisters',
        rationale:
          'Classic polyculture: corn as a trellis, beans fix nitrogen, squash shades soil and deters pests.',
        citation_ids: ['three_sisters', 'almanac', 'companions'],
        succession: null,
      },
      {
        id: 'tomato_basil',
        name: 'Tomato & basil guild',
        crops: ['tomato', 'basil'],
        min_match: 2,
        priority: 90,
        pattern: 'anchor_companion',
        anchor: 'tomato',
        companions: ['basil'],
        rationale:
          'Basil is a classic tomato companion—shared full-sun bed with aromatic underplanting between tomato stations.',
        citation_ids: ['companions', 'umn', 'almanac'],
        succession:
          'Tuck quick lettuce or radish between young tomatoes until canopy fills (text note only).',
      },
      {
        id: 'nightshade_herbs',
        name: 'Nightshade & herbs',
        crops: ['tomato', 'pepper', 'eggplant', 'basil', 'onion'],
        min_match: 2,
        priority: 80,
        pattern: 'rows_by_spacing',
        rationale:
          'Group heat-loving nightshades with basil/onion companions; keep full-sun crops together.',
        citation_ids: ['umn', 'cornell', 'companions'],
        succession: null,
      },
      {
        id: 'salad_cut_come_again',
        name: 'Salad cut-and-come-again',
        crops: ['lettuce', 'spinach', 'cilantro', 'chard', 'radish'],
        min_match: 2,
        priority: 85,
        pattern: 'dense_blocks',
        rationale:
          'Dense leafy blocks at each crop’s own spacing for repeated harvest; mix radish for quick returns.',
        citation_ids: ['sfg', 'umn', 'almanac'],
        succession:
          'Sow radish every 10–14 days between slower lettuce/chard for succession harvests.',
      },
      {
        id: 'root_bed',
        name: 'Root bed',
        crops: ['carrot', 'radish', 'beet', 'onion', 'garlic'],
        min_match: 2,
        priority: 84,
        pattern: 'rows_by_spacing',
        rationale:
          'Root crops in dedicated rows at catalog spacing; onions/garlic deter some pests among carrots and beets.',
        citation_ids: ['sfg', 'umn', 'cornell'],
        succession:
          'Interseed radish between carrot rows—radish matures and clears before carrots need the space.',
      },
      {
        id: 'brassica_companions',
        name: 'Brassica bed with companions',
        crops: ['cabbage', 'broccoli', 'kale', 'beet', 'onion'],
        min_match: 2,
        priority: 88,
        pattern: 'anchor_companion',
        require_any: ['cabbage', 'broccoli', 'kale'],
        anchor_any: ['cabbage', 'broccoli', 'kale'],
        companions: ['beet', 'onion'],
        rationale:
          'Give brassicas wide spacing; edge with beet/onion companions. Avoid planting tomatoes beside cabbage.',
        citation_ids: ['umn', 'cornell', 'companions'],
        succession: null,
      },
      {
        id: 'cucumber_legume',
        name: 'Cucumber & legumes',
        crops: ['cucumber', 'bean', 'pea', 'radish'],
        min_match: 2,
        priority: 75,
        pattern: 'rows_by_spacing',
        rationale:
          'Cucumbers with pea/bean nitrogen partners and radish as a traditional cucumber companion.',
        citation_ids: ['almanac', 'companions', 'umn'],
        succession: null,
      },
      {
        id: 'potato_patch',
        name: 'Potato patch',
        crops: ['potato', 'bean', 'corn'],
        min_match: 1,
        priority: 70,
        pattern: 'rows_by_spacing',
        require_any: ['potato'],
        rationale:
          'Potatoes in their own block with compatible bean/corn; keep clear of tomato, cucumber, and squash antagonists.',
        citation_ids: ['umn', 'cornell', 'companions'],
        succession: null,
      },
    ],
  };

  function loadSources() {
    if (SOURCES) return Promise.resolve(SOURCES);
    if (SOURCES_PROMISE) return SOURCES_PROMISE;
    SOURCES_PROMISE = fetch('data/layout_sources.json')
      .then((r) => {
        if (!r.ok) throw new Error('sources missing');
        return r.json();
      })
      .then((data) => {
        SOURCES = data;
        return SOURCES;
      })
      .catch(() => {
        SOURCES = FALLBACK_SOURCES;
        return SOURCES;
      });
    return SOURCES_PROMISE;
  }

  function spacingFt(plant) {
    return Math.max(plant.spacing_inches / 12, 0.25);
  }

  function rowFt(plant) {
    const row = plant.row_spacing_inches != null ? plant.row_spacing_inches : plant.spacing_inches;
    return Math.max(row / 12, 0.5);
  }

  function areAntagonists(a, b) {
    const aa = a.antagonists || [];
    const bb = b.antagonists || [];
    return aa.includes(b.slug) || bb.includes(a.slug);
  }

  function resolveCitations(ids, sources) {
    const byId = Object.fromEntries((sources.citations || []).map((c) => [c.id, c]));
    const out = [];
    const seen = new Set();
    for (const id of ids) {
      const c = byId[id];
      if (c && !seen.has(c.id)) {
        out.push({ title: c.title, url: c.url, org: c.org });
        seen.add(c.id);
      }
    }
    return out;
  }

  function matchTemplates(selectedSlugs, sources) {
    const templates = (sources.templates || [])
      .slice()
      .sort((a, b) => (b.priority || 0) - (a.priority || 0) || a.name.localeCompare(b.name));
    const remaining = new Set(selectedSlugs);
    const matched = [];
    for (const tmpl of templates) {
      const requireAny = tmpl.require_any;
      if (requireAny && !requireAny.some((r) => remaining.has(r))) continue;
      const hit = tmpl.crops.filter((c) => remaining.has(c));
      const minMatch = tmpl.min_match != null ? tmpl.min_match : 2;
      if (hit.length < minMatch) continue;
      matched.push({ tmpl, hit });
      hit.forEach((c) => remaining.delete(c));
    }
    return matched;
  }

  function orderCropsSunCompanions(crops) {
    const sunRank = { full: 0, partial: 1, shade: 2 };
    const slugs = new Set(crops.map((c) => c.slug));
    return crops.slice().sort((a, b) => {
      const ca = (a.companions || []).filter((s) => slugs.has(s) && s !== a.slug).length;
      const cb = (b.companions || []).filter((s) => slugs.has(s) && s !== b.slug).length;
      const sa = sunRank[a.sun_needs] != null ? sunRank[a.sun_needs] : 9;
      const sb = sunRank[b.sun_needs] != null ? sunRank[b.sun_needs] : 9;
      if (sa !== sb) return sa - sb;
      if (cb !== ca) return cb - ca;
      return a.name.localeCompare(b.name);
    });
  }

  function splitAntagonists(crops) {
    const groups = [];
    for (const crop of orderCropsSunCompanions(crops)) {
      let placed = false;
      for (const g of groups) {
        if (g.some((other) => areAntagonists(crop, other))) continue;
        g.push(crop);
        placed = true;
        break;
      }
      if (!placed) groups.push([crop]);
    }
    return groups;
  }

  function fillRect(plant, x0, y0, width, length, maxPlants) {
    maxPlants = maxPlants == null ? 48 : maxPlants;
    let sx = spacingFt(plant);
    let sy = rowFt(plant);
    if (width < sx && length >= sx) {
      const tmp = sx;
      sx = sy;
      sy = tmp;
    }
    if (width < sx * 0.5 || length < sy * 0.5) {
      if (width > 0.2 && length > 0.2) {
        return [
          {
            plant,
            x_ft: Math.round((x0 + width / 2) * 100) / 100,
            y_ft: Math.round((y0 + length / 2) * 100) / 100,
            quantity: 1,
          },
        ];
      }
      return [];
    }
    const placements = [];
    for (let y = y0 + sy / 2; y <= y0 + length - sy / 2 + 0.01 && placements.length < maxPlants; y += sy) {
      for (let x = x0 + sx / 2; x <= x0 + width - sx / 2 + 0.01 && placements.length < maxPlants; x += sx) {
        placements.push({
          plant,
          x_ft: Math.round(x * 100) / 100,
          y_ft: Math.round(y * 100) / 100,
          quantity: 1,
        });
      }
    }
    if (!placements.length && width > 0.3 && length > 0.3) {
      placements.push({
        plant,
        x_ft: Math.round((x0 + width / 2) * 100) / 100,
        y_ft: Math.round((y0 + length / 2) * 100) / 100,
        quantity: 1,
      });
    }
    return placements;
  }

  function layoutThreeSisters(bySlug, crops, x0, y0, width, length) {
    const placements = [];
    const blocks = [];
    const present = ['corn', 'bean', 'squash'].filter((c) => crops.includes(c) && bySlug[c]);
    let bands;
    if (present.includes('squash') && length >= 4) {
      const squashBand = Math.min(length * 0.28, 3.0);
      const midY0 = y0 + squashBand;
      const midLen = length - 2 * squashBand;
      bands = [
        ['squash', y0, squashBand],
        ['corn_bean', midY0, midLen],
        ['squash', midY0 + midLen, squashBand],
      ];
    } else {
      bands = [['corn_bean', y0, length]];
    }
    for (const [kind, by, bl] of bands) {
      if (bl < 0.4) continue;
      if (kind === 'squash' && present.includes('squash')) {
        placements.push(...fillRect(bySlug.squash, x0, by, width, bl, 6));
        blocks.push({
          id: `squash-${by}`,
          plant_slug: 'squash',
          x_ft: x0,
          y_ft: by,
          width_ft: width,
          length_ft: bl,
          kind: 'guild',
          label: 'Squash',
        });
      } else if (kind === 'corn_bean') {
        if (present.includes('corn') && present.includes('bean')) {
          const cornW = width * 0.55;
          const beanW = width - cornW;
          placements.push(...fillRect(bySlug.corn, x0, by, cornW, bl, 16));
          placements.push(...fillRect(bySlug.bean, x0 + cornW, by, beanW, bl, 24));
          blocks.push({
            id: `corn-${by}`,
            plant_slug: 'corn',
            x_ft: x0,
            y_ft: by,
            width_ft: cornW,
            length_ft: bl,
            kind: 'guild',
            label: 'Corn',
          });
          blocks.push({
            id: `bean-${by}`,
            plant_slug: 'bean',
            x_ft: x0 + cornW,
            y_ft: by,
            width_ft: beanW,
            length_ft: bl,
            kind: 'guild',
            label: 'Bean',
          });
        } else if (present.includes('corn')) {
          placements.push(...fillRect(bySlug.corn, x0, by, width, bl));
          blocks.push({
            id: `corn-${by}`,
            plant_slug: 'corn',
            x_ft: x0,
            y_ft: by,
            width_ft: width,
            length_ft: bl,
            kind: 'guild',
            label: 'Corn',
          });
        } else if (present.includes('bean')) {
          placements.push(...fillRect(bySlug.bean, x0, by, width, bl));
          blocks.push({
            id: `bean-${by}`,
            plant_slug: 'bean',
            x_ft: x0,
            y_ft: by,
            width_ft: width,
            length_ft: bl,
            kind: 'guild',
            label: 'Bean',
          });
        }
        if (present.includes('squash') && length < 4) {
          placements.push(
            ...fillRect(bySlug.squash, x0, y0 + length * 0.65, width, length * 0.35, 2)
          );
        }
      }
    }
    return { placements, blocks };
  }

  function layoutRowsBySpacing(bySlug, crops, x0, y0, width, length, kind) {
    kind = kind || 'row';
    const plants = crops.map((c) => bySlug[c]).filter(Boolean);
    if (!plants.length) return { placements: [], blocks: [] };
    const weights = plants.map((p) => Math.max(spacingFt(p) * rowFt(p), 0.5));
    const totalW = weights.reduce((a, b) => a + b, 0) || 1;
    const placements = [];
    const blocks = [];
    let cursor = y0;
    for (let i = 0; i < plants.length; i++) {
      const p = plants[i];
      let strip = length * (weights[i] / totalW);
      const remaining = y0 + length - cursor;
      if (remaining <= 0) break;
      strip = Math.min(Math.max(strip, Math.min(0.35, remaining)), remaining);
      placements.push(...fillRect(p, x0, cursor, width, strip));
      blocks.push({
        id: `${p.slug}-${cursor}`,
        plant_slug: p.slug,
        x_ft: Math.round(x0 * 100) / 100,
        y_ft: Math.round(cursor * 100) / 100,
        width_ft: Math.round(width * 100) / 100,
        length_ft: Math.round(strip * 100) / 100,
        kind,
        label: p.name,
      });
      cursor += strip;
    }
    return { placements, blocks };
  }

  function layoutDenseBlocks(bySlug, crops, x0, y0, width, length) {
    const plants = crops.map((c) => bySlug[c]).filter(Boolean);
    if (!plants.length) return { placements: [], blocks: [] };
    if (plants.length === 1) {
      return layoutRowsBySpacing(bySlug, crops, x0, y0, width, length, 'block');
    }
    const cols = width >= 3 && plants.length >= 2 ? 2 : 1;
    const rows = Math.ceil(plants.length / cols);
    const cellW = width / cols;
    const cellL = length / rows;
    const placements = [];
    const blocks = [];
    plants.forEach((p, i) => {
      const col = i % cols;
      const row = Math.floor(i / cols);
      const bx = x0 + col * cellW;
      const by = y0 + row * cellL;
      placements.push(...fillRect(p, bx, by, cellW, cellL));
      blocks.push({
        id: `${p.slug}-${i}`,
        plant_slug: p.slug,
        x_ft: Math.round(bx * 100) / 100,
        y_ft: Math.round(by * 100) / 100,
        width_ft: Math.round(cellW * 100) / 100,
        length_ft: Math.round(cellL * 100) / 100,
        kind: 'block',
        label: p.name,
      });
    });
    return { placements, blocks };
  }

  function layoutAnchorCompanion(bySlug, crops, tmpl, x0, y0, width, length) {
    let anchors = [];
    if (tmpl.anchor && crops.includes(tmpl.anchor)) anchors = [tmpl.anchor];
    else if (tmpl.anchor_any) anchors = tmpl.anchor_any.filter((a) => crops.includes(a));
    const companions = (tmpl.companions || []).filter((c) => crops.includes(c));
    const other = crops.filter((c) => !anchors.includes(c) && !companions.includes(c));
    if (anchors.length && (companions.length || other.length)) {
      const anchorLen = length * 0.65;
      const restLen = length - anchorLen;
      const a = layoutRowsBySpacing(bySlug, anchors, x0, y0, width, anchorLen, 'guild');
      const b = layoutRowsBySpacing(
        bySlug,
        companions.concat(other),
        x0,
        y0 + anchorLen,
        width,
        restLen,
        'guild'
      );
      return { placements: a.placements.concat(b.placements), blocks: a.blocks.concat(b.blocks) };
    }
    return layoutRowsBySpacing(bySlug, anchors.concat(companions, other), x0, y0, width, length, 'guild');
  }

  function applyTemplate(tmpl, cropSlugs, bySlug, x0, y0, width, length) {
    const pattern = tmpl.pattern || 'rows_by_spacing';
    if (pattern === 'three_sisters') return layoutThreeSisters(bySlug, cropSlugs, x0, y0, width, length);
    if (pattern === 'anchor_companion')
      return layoutAnchorCompanion(bySlug, cropSlugs, tmpl, x0, y0, width, length);
    if (pattern === 'dense_blocks') return layoutDenseBlocks(bySlug, cropSlugs, x0, y0, width, length);
    return layoutRowsBySpacing(bySlug, cropSlugs, x0, y0, width, length, 'row');
  }

  function planLayout(widthFt, lengthFt, plants, sources) {
    const width = Number(widthFt);
    const length = Number(lengthFt);
    const empty = {
      placements: [],
      blocks: [],
      templates_used: [],
      succession_notes: [],
      citations: [],
      summary: 'No plants selected.',
    };
    if (width <= 0 || length <= 0 || !plants.length) return empty;

    const bySlug = Object.fromEntries(plants.map((p) => [p.slug, p]));
    const selected = new Set(Object.keys(bySlug));
    const matched = matchTemplates(selected, sources || FALLBACK_SOURCES);
    const used = new Set();
    matched.forEach(({ hit }) => hit.forEach((s) => used.add(s)));
    const leftoverSlugs = [...selected].filter((s) => !used.has(s));

    const zones = [];
    matched.forEach(({ tmpl, hit }) => zones.push({ kind: 'template', tmpl, slugs: hit }));
    if (leftoverSlugs.length) {
      const leftoverPlants = orderCropsSunCompanions(leftoverSlugs.map((s) => bySlug[s]));
      splitAntagonists(leftoverPlants).forEach((group) => {
        zones.push({ kind: 'freeform', tmpl: null, slugs: group.map((p) => p.slug) });
      });
    }
    if (!zones.length) return empty;

    const weights = zones.map(({ slugs }) => {
      const footprint = slugs.reduce((sum, s) => {
        const p = bySlug[s];
        return sum + (p ? Math.max(spacingFt(p) * rowFt(p), 0.5) : 0.5);
      }, 0);
      return Math.max(slugs.length, 1) * 2.0 + Math.sqrt(Math.min(footprint, 8.0));
    });
    const totalWeight = weights.reduce((a, b) => a + b, 0) || 1;

    let placements = [];
    const blocks = [];
    const templatesUsed = [];
    const successionNotes = [];
    let citeIds = ['sfg', 'umn', 'companions'];
    let cursor = 0;

    zones.forEach((zone, zi) => {
      let zoneLen = length * (weights[zi] / totalWeight);
      const remaining = length - cursor;
      if (remaining < 0.3) return;
      zoneLen = Math.min(Math.max(zoneLen, Math.min(1.0, remaining)), remaining);

      if (zone.kind === 'template' && zone.tmpl) {
        const { placements: pl, blocks: bl } = applyTemplate(
          zone.tmpl,
          zone.slugs,
          bySlug,
          0,
          cursor,
          width,
          zoneLen
        );
        placements = placements.concat(pl);
        blocks.push(...bl);
        templatesUsed.push({
          id: zone.tmpl.id,
          name: zone.tmpl.name,
          rationale: zone.tmpl.rationale || '',
          crops: zone.slugs.map((s) => bySlug[s].name),
        });
        if (zone.tmpl.succession) successionNotes.push(zone.tmpl.succession);
        citeIds = citeIds.concat(zone.tmpl.citation_ids || []);
      } else {
        const ordered = orderCropsSunCompanions(zone.slugs.map((s) => bySlug[s]).filter(Boolean));
        const { placements: pl, blocks: bl } = layoutRowsBySpacing(
          bySlug,
          ordered.map((p) => p.slug),
          0,
          cursor,
          width,
          zoneLen,
          'row'
        );
        placements = placements.concat(pl);
        blocks.push(...bl);
        const sun = ordered[0] ? ordered[0].sun_needs || 'full' : 'full';
        const sunLabel = { full: 'full sun', partial: 'partial sun', shade: 'shade' }[sun] || sun;
        templatesUsed.push({
          id: `rows-${zone.slugs[0] || 'x'}`,
          name: `${sunLabel.replace(/\b\w/g, (c) => c.toUpperCase())} row block`,
          rationale: `Remaining crops in ${sunLabel} rows using each plant’s own spacing_inches / row_spacing (Square Foot / extension tables).`,
          crops: ordered.map((p) => p.name),
        });
        citeIds = citeIds.concat(['sfg', 'umn']);
      }
      cursor += zoneLen;
    });

    const maxPlacements = 64;
    if (placements.length > maxPlacements) {
      const byP = {};
      placements.forEach((pl) => {
        (byP[pl.plant.slug] = byP[pl.plant.slug] || []).push(pl);
      });
      const share = Math.max(1, Math.floor(maxPlacements / Math.max(Object.keys(byP).length, 1)));
      const trimmed = [];
      Object.values(byP).forEach((items) => {
        const step = Math.max(1, Math.floor(items.length / share));
        for (let i = 0; i < items.length && trimmed.length < maxPlacements; i += step) {
          if (trimmed.filter((t) => t.plant.slug === items[0].plant.slug).length >= share) break;
          trimmed.push(items[i]);
        }
      });
      placements = trimmed.slice(0, maxPlacements);
    }

    citeIds = [...new Set(citeIds.concat(['sfg', 'umn', 'cornell', 'almanac', 'companions']))];
    let citations = resolveCitations(citeIds, sources || FALLBACK_SOURCES);
    const seenUrls = new Set();
    citations = citations.filter((c) => {
      const u = c.url || c.title;
      if (seenUrls.has(u)) return false;
      seenUrls.add(u);
      return true;
    });
    const tmplNames = templatesUsed.map((t) => t.name);
    const summary = tmplNames.length
      ? `Layout uses ${tmplNames.join(', ')} — intentional beds/blocks at each crop’s own spacing, companions grouped, antagonists separated.`
      : 'Layout filled with per-crop spacing blocks.';

    return {
      placements,
      blocks,
      templates_used: templatesUsed,
      succession_notes: [...new Set(successionNotes)],
      citations,
      summary,
    };
  }

  /**
   * @param {{width_ft:number, length_ft:number}} bed
   * @param {object[]} plants
   * @returns {object[]} placements only (compat)
   */
  function suggestFill(bed, plants) {
    const result = suggestFillWithPlan(bed, plants);
    return result.placements;
  }

  /**
   * @returns {{placements:object[], blocks:object[], templates_used:object[], succession_notes:string[], citations:object[], summary:string}}
   */
  function suggestFillWithPlan(bed, plants, sources) {
    return planLayout(bed.width_ft, bed.length_ft, plants, sources || SOURCES || FALLBACK_SOURCES);
  }

  global.GroundworkSuggest = {
    suggestFill,
    suggestFillWithPlan,
    planLayout,
    loadSources,
    getSources: () => SOURCES || FALLBACK_SOURCES,
  };
})(typeof window !== 'undefined' ? window : globalThis);
