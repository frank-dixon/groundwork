"""Intentional bed/plot layout suggestions: curated guilds + per-crop spacing."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Any

from .models import Bed, Plant, PlantPlacement

_SOURCES_PATH = Path(__file__).resolve().parents[1] / 'docs' / 'data' / 'layout_sources.json'
_SOURCES_CACHE: dict[str, Any] | None = None


def load_layout_sources() -> dict[str, Any]:
    global _SOURCES_CACHE
    if _SOURCES_CACHE is None:
        _SOURCES_CACHE = json.loads(_SOURCES_PATH.read_text(encoding='utf-8'))
    return _SOURCES_CACHE


def citations_by_id() -> dict[str, dict]:
    return {c['id']: c for c in load_layout_sources()['citations']}


def all_layout_citations() -> list[dict]:
    """Public citation list for UI (static + Django)."""
    return list(load_layout_sources()['citations'])


@dataclass
class SuggestPlan:
    templates_used: list[dict] = field(default_factory=list)
    succession_notes: list[str] = field(default_factory=list)
    citations: list[dict] = field(default_factory=list)
    summary: str = ''
    blocks: list[dict] = field(default_factory=list)


@dataclass
class SuggestResult:
    placements: list[PlantPlacement]
    plan: SuggestPlan


def _plant_dict(plant: Plant) -> dict:
    return {
        'slug': plant.slug,
        'name': plant.name,
        'spacing_inches': int(plant.spacing_inches),
        'row_spacing_inches': int(plant.row_spacing_inches or plant.spacing_inches),
        'sun_needs': plant.sun_needs or 'full',
        'companions': list(plant.companions.values_list('slug', flat=True)),
        'antagonists': list(plant.antagonists.values_list('slug', flat=True)),
        '_obj': plant,
    }


def _spacing_ft(plant: dict) -> float:
    return max(plant['spacing_inches'] / 12.0, 0.25)


def _row_ft(plant: dict) -> float:
    return max(plant.get('row_spacing_inches', plant['spacing_inches']) / 12.0, 0.5)


def _are_antagonists(a: dict, b: dict) -> bool:
    return a['slug'] in b.get('antagonists', []) or b['slug'] in a.get('antagonists', [])


def _resolve_citations(ids: list[str]) -> list[dict]:
    by_id = citations_by_id()
    out = []
    seen = set()
    for cid in ids:
        c = by_id.get(cid)
        if c and c['id'] not in seen:
            out.append({k: c[k] for k in ('title', 'url', 'org') if k in c})
            seen.add(c['id'])
    return out


def _match_templates(selected_slugs: set[str]) -> list[tuple[dict, list[str]]]:
    """Greedy match curated templates covering the selection."""
    templates = sorted(
        load_layout_sources()['templates'],
        key=lambda t: (-t.get('priority', 0), t['name']),
    )
    remaining = set(selected_slugs)
    matched: list[tuple[dict, list[str]]] = []

    for tmpl in templates:
        crops = list(tmpl['crops'])
        require_any = tmpl.get('require_any')
        if require_any and not any(r in remaining for r in require_any):
            continue
        hit = [c for c in crops if c in remaining]
        min_match = int(tmpl.get('min_match', 2))
        if len(hit) < min_match:
            continue
        # Prefer covering required core when listed
        matched.append((tmpl, hit))
        for c in hit:
            remaining.discard(c)

    return matched


def _order_crops_sun_companions(crops: list[dict]) -> list[dict]:
    """Full-sun together first; within group prefer companion-linked crops."""
    sun_rank = {'full': 0, 'partial': 1, 'shade': 2}
    slugs = {c['slug'] for c in crops}

    def score(p: dict) -> tuple:
        comps = sum(1 for s in p.get('companions', []) if s in slugs and s != p['slug'])
        return (sun_rank.get(p.get('sun_needs', 'full'), 9), -comps, p['name'])

    return sorted(crops, key=score)


def _split_antagonists(crops: list[dict]) -> list[list[dict]]:
    """Partition into groups with no hard antagonist pairs adjacent in same group."""
    groups: list[list[dict]] = []
    for crop in _order_crops_sun_companions(crops):
        placed = False
        for g in groups:
            if any(_are_antagonists(crop, other) for other in g):
                continue
            g.append(crop)
            placed = True
            break
        if not placed:
            groups.append([crop])
    return groups


def _fill_rect(
    plant: dict,
    x0: float,
    y0: float,
    width: float,
    length: float,
    max_plants: int = 48,
) -> list[dict]:
    """Fill a rectangle using this crop's own in-row + row spacing."""
    sx = _spacing_ft(plant)
    sy = _row_ft(plant)
    # If the strip is narrow, swap axes so plants still fit
    if width < sx and length >= sx:
        sx, sy = sy, sx
    if width < sx * 0.5 or length < sy * 0.5:
        # Single plant centered if any room
        if width > 0.2 and length > 0.2:
            return [{
                'plant': plant,
                'x_ft': round(x0 + width / 2, 2),
                'y_ft': round(y0 + length / 2, 2),
                'quantity': 1,
            }]
        return []

    placements: list[dict] = []
    y = y0 + sy / 2
    while y <= y0 + length - sy / 2 + 0.01 and len(placements) < max_plants:
        x = x0 + sx / 2
        while x <= x0 + width - sx / 2 + 0.01 and len(placements) < max_plants:
            placements.append({
                'plant': plant,
                'x_ft': round(x, 2),
                'y_ft': round(y, 2),
                'quantity': 1,
            })
            x += sx
        y += sy
    if not placements and width > 0.3 and length > 0.3:
        placements.append({
            'plant': plant,
            'x_ft': round(x0 + width / 2, 2),
            'y_ft': round(y0 + length / 2, 2),
            'quantity': 1,
        })
    return placements


def _layout_three_sisters(
    by_slug: dict[str, dict],
    crops: list[str],
    x0: float,
    y0: float,
    width: float,
    length: float,
) -> tuple[list[dict], list[dict]]:
    """Corn spine, beans beside, squash at ends — classic strip layout."""
    placements: list[dict] = []
    blocks: list[dict] = []
    present = [c for c in ('corn', 'bean', 'squash') if c in crops and c in by_slug]

    # Length bands: squash | corn+bean | squash  OR proportional by what's present
    if 'squash' in present and length >= 4:
        squash_band = min(length * 0.28, 3.0)
        mid_y0 = y0 + squash_band
        mid_len = length - 2 * squash_band
        bands = [
            ('squash', y0, squash_band),
            ('corn_bean', mid_y0, mid_len),
            ('squash', mid_y0 + mid_len, squash_band),
        ]
    else:
        bands = [('corn_bean', y0, length)]

    for kind, by, bl in bands:
        if bl < 0.4:
            continue
        if kind == 'squash' and 'squash' in present:
            pl = _fill_rect(by_slug['squash'], x0, by, width, bl, max_plants=6)
            placements.extend(pl)
            blocks.append({
                'id': f'squash-{by}',
                'plant_slug': 'squash',
                'x_ft': x0,
                'y_ft': by,
                'width_ft': width,
                'length_ft': bl,
                'kind': 'guild',
                'label': 'Squash',
            })
        elif kind == 'corn_bean':
            if 'corn' in present and 'bean' in present:
                corn_w = width * 0.55
                bean_w = width - corn_w
                pl_c = _fill_rect(by_slug['corn'], x0, by, corn_w, bl, max_plants=16)
                pl_b = _fill_rect(by_slug['bean'], x0 + corn_w, by, bean_w, bl, max_plants=24)
                placements.extend(pl_c + pl_b)
                blocks.append({
                    'id': f'corn-{by}',
                    'plant_slug': 'corn',
                    'x_ft': x0,
                    'y_ft': by,
                    'width_ft': corn_w,
                    'length_ft': bl,
                    'kind': 'guild',
                    'label': 'Corn',
                })
                blocks.append({
                    'id': f'bean-{by}',
                    'plant_slug': 'bean',
                    'x_ft': x0 + corn_w,
                    'y_ft': by,
                    'width_ft': bean_w,
                    'length_ft': bl,
                    'kind': 'guild',
                    'label': 'Bean',
                })
            elif 'corn' in present:
                pl = _fill_rect(by_slug['corn'], x0, by, width, bl)
                placements.extend(pl)
                blocks.append({
                    'id': f'corn-{by}',
                    'plant_slug': 'corn',
                    'x_ft': x0,
                    'y_ft': by,
                    'width_ft': width,
                    'length_ft': bl,
                    'kind': 'guild',
                    'label': 'Corn',
                })
            elif 'bean' in present:
                pl = _fill_rect(by_slug['bean'], x0, by, width, bl)
                placements.extend(pl)
                blocks.append({
                    'id': f'bean-{by}',
                    'plant_slug': 'bean',
                    'x_ft': x0,
                    'y_ft': by,
                    'width_ft': width,
                    'length_ft': bl,
                    'kind': 'guild',
                    'label': 'Bean',
                })
            if 'squash' in present and length < 4:
                # Small bed: one squash hill at far edge
                pl = _fill_rect(
                    by_slug['squash'],
                    x0,
                    y0 + length * 0.65,
                    width,
                    length * 0.35,
                    max_plants=2,
                )
                placements.extend(pl)

    return placements, blocks


def _layout_anchor_companion(
    by_slug: dict[str, dict],
    crops: list[str],
    tmpl: dict,
    x0: float,
    y0: float,
    width: float,
    length: float,
) -> tuple[list[dict], list[dict]]:
    anchors = []
    if tmpl.get('anchor') and tmpl['anchor'] in crops:
        anchors = [tmpl['anchor']]
    elif tmpl.get('anchor_any'):
        anchors = [a for a in tmpl['anchor_any'] if a in crops]
    companions = [c for c in tmpl.get('companions', []) if c in crops]
    other = [c for c in crops if c not in anchors and c not in companions]

    placements: list[dict] = []
    blocks: list[dict] = []

    # Anchors get ~65% of length; companions/others share the rest (usable strips).
    if anchors and (companions or other):
        anchor_len = length * 0.65
        rest_len = length - anchor_len
        pl, bl = _layout_rows_by_spacing(
            by_slug, anchors, x0, y0, width, anchor_len, kind='guild'
        )
        placements.extend(pl)
        blocks.extend(bl)
        pl2, bl2 = _layout_rows_by_spacing(
            by_slug, companions + other, x0, y0 + anchor_len, width, rest_len, kind='guild'
        )
        placements.extend(pl2)
        blocks.extend(bl2)
        return placements, blocks

    ordered = anchors + companions + other
    return _layout_rows_by_spacing(by_slug, ordered, x0, y0, width, length, kind='guild')


def _layout_rows_by_spacing(
    by_slug: dict[str, dict],
    crops: list[str],
    x0: float,
    y0: float,
    width: float,
    length: float,
    kind: str = 'row',
) -> tuple[list[dict], list[dict]]:
    """Allocate length strips proportional to each crop's footprint need."""
    plants = [by_slug[c] for c in crops if c in by_slug]
    if not plants:
        return [], []

    weights = []
    for p in plants:
        # Larger spacing crops get more strip length
        weights.append(max(_spacing_ft(p) * _row_ft(p), 0.5))
    total_w = sum(weights) or 1.0

    placements: list[dict] = []
    blocks: list[dict] = []
    cursor = y0
    for p, w in zip(plants, weights):
        strip = length * (w / total_w)
        if strip < 0.35:
            strip = max(strip, 0.35)
        # Clamp last strip to remaining
        remaining = y0 + length - cursor
        if remaining <= 0:
            break
        strip = min(strip, remaining)
        pl = _fill_rect(p, x0, cursor, width, strip)
        placements.extend(pl)
        blocks.append({
            'id': f'{p["slug"]}-{cursor}',
            'plant_slug': p['slug'],
            'x_ft': round(x0, 2),
            'y_ft': round(cursor, 2),
            'width_ft': round(width, 2),
            'length_ft': round(strip, 2),
            'kind': kind,
            'label': p['name'],
        })
        cursor += strip

    return placements, blocks


def _layout_dense_blocks(
    by_slug: dict[str, dict],
    crops: list[str],
    x0: float,
    y0: float,
    width: float,
    length: float,
) -> tuple[list[dict], list[dict]]:
    """Side-by-side square-foot style blocks across the bed width when possible."""
    plants = [by_slug[c] for c in crops if c in by_slug]
    if not plants:
        return [], []

    placements: list[dict] = []
    blocks: list[dict] = []

    # Prefer a grid of blocks: if many crops, tile along length in pairs across width
    n = len(plants)
    if n == 1:
        return _layout_rows_by_spacing(by_slug, crops, x0, y0, width, length, kind='block')

    cols = 2 if width >= 3 and n >= 2 else 1
    rows = (n + cols - 1) // cols
    cell_w = width / cols
    cell_l = length / rows

    for i, p in enumerate(plants):
        col = i % cols
        row = i // cols
        bx = x0 + col * cell_w
        by = y0 + row * cell_l
        pl = _fill_rect(p, bx, by, cell_w, cell_l)
        placements.extend(pl)
        blocks.append({
            'id': f'{p["slug"]}-{i}',
            'plant_slug': p['slug'],
            'x_ft': round(bx, 2),
            'y_ft': round(by, 2),
            'width_ft': round(cell_w, 2),
            'length_ft': round(cell_l, 2),
            'kind': 'block',
            'label': p['name'],
        })

    return placements, blocks


def _apply_template(
    tmpl: dict,
    crop_slugs: list[str],
    by_slug: dict[str, dict],
    x0: float,
    y0: float,
    width: float,
    length: float,
) -> tuple[list[dict], list[dict]]:
    pattern = tmpl.get('pattern', 'rows_by_spacing')
    if pattern == 'three_sisters':
        return _layout_three_sisters(by_slug, crop_slugs, x0, y0, width, length)
    if pattern == 'anchor_companion':
        return _layout_anchor_companion(by_slug, crop_slugs, tmpl, x0, y0, width, length)
    if pattern == 'dense_blocks':
        return _layout_dense_blocks(by_slug, crop_slugs, x0, y0, width, length)
    return _layout_rows_by_spacing(by_slug, crop_slugs, x0, y0, width, length)


def plan_layout(width_ft: float, length_ft: float, plants: list[dict]) -> dict:
    """
    Pure planner: returns placements, blocks, and plan metadata.
    Each plant dict needs slug, name, spacing_inches, row_spacing_inches,
    sun_needs, companions, antagonists.
    """
    width = float(width_ft)
    length = float(length_ft)
    empty = {
        'placements': [],
        'blocks': [],
        'templates_used': [],
        'succession_notes': [],
        'citations': [],
        'summary': 'No plants selected.',
    }
    if width <= 0 or length <= 0 or not plants:
        return empty

    by_slug = {p['slug']: p for p in plants}
    selected = set(by_slug)
    matched = _match_templates(selected)
    used_slugs: set[str] = set()
    for _, hits in matched:
        used_slugs.update(hits)
    leftover_slugs = [s for s in selected if s not in used_slugs]

    # Zone allocation along bed length
    zones: list[tuple[str, Any, list[str]]] = []
    for tmpl, hits in matched:
        zones.append(('template', tmpl, hits))
    if leftover_slugs:
        leftover_plants = _order_crops_sun_companions([by_slug[s] for s in leftover_slugs])
        for group in _split_antagonists(leftover_plants):
            zones.append(('freeform', None, [p['slug'] for p in group]))

    if not zones:
        return empty

    # Weight zones: crop count dominates so leftover herbs/roots keep usable strips;
    # footprint is a soft boost for large-spacing guilds.
    weights = []
    for kind, tmpl, slugs in zones:
        footprint = sum(
            max(_spacing_ft(by_slug[s]) * _row_ft(by_slug[s]), 0.5) for s in slugs if s in by_slug
        )
        weights.append(max(len(slugs), 1) * 2.0 + min(footprint, 8.0) ** 0.5)
    total_weight = sum(weights) or 1.0

    placements: list[dict] = []
    blocks: list[dict] = []
    templates_used: list[dict] = []
    succession_notes: list[str] = []
    cite_ids: list[str] = ['sfg', 'umn', 'companions']
    cursor = 0.0

    for (kind, tmpl, slugs), w in zip(zones, weights):
        zone_len = length * (w / total_weight)
        remaining = length - cursor
        if remaining < 0.3:
            break
        zone_len = min(zone_len, remaining)
        # Ensure minimum usable strip
        zone_len = max(zone_len, min(1.0, remaining))

        if kind == 'template' and tmpl:
            pl, bl = _apply_template(tmpl, slugs, by_slug, 0.0, cursor, width, zone_len)
            placements.extend(pl)
            blocks.extend(bl)
            names = [by_slug[s]['name'] for s in slugs if s in by_slug]
            templates_used.append({
                'id': tmpl['id'],
                'name': tmpl['name'],
                'rationale': tmpl.get('rationale', ''),
                'crops': names,
            })
            if tmpl.get('succession'):
                succession_notes.append(tmpl['succession'])
            cite_ids.extend(tmpl.get('citation_ids') or [])
        else:
            # Freeform: sun-grouped row blocks at each crop's spacing
            ordered = _order_crops_sun_companions([by_slug[s] for s in slugs if s in by_slug])
            pl, bl = _layout_rows_by_spacing(
                by_slug, [p['slug'] for p in ordered], 0.0, cursor, width, zone_len, kind='row'
            )
            placements.extend(pl)
            blocks.extend(bl)
            sun = ordered[0].get('sun_needs', 'full') if ordered else 'full'
            sun_label = {'full': 'full sun', 'partial': 'partial sun', 'shade': 'shade'}.get(sun, sun)
            templates_used.append({
                'id': f'rows-{slugs[0] if slugs else "x"}',
                'name': f'{sun_label.title()} row block',
                'rationale': (
                    f"Remaining crops in {sun_label} rows using each plant’s own "
                    f"spacing_inches / row_spacing (Square Foot / extension tables)."
                ),
                'crops': [p['name'] for p in ordered],
            })
            cite_ids.extend(['sfg', 'umn'])

        cursor += zone_len

    # Cap total placements for UI sanity while keeping block structure
    max_placements = 64
    if len(placements) > max_placements:
        # Keep proportional sample per plant
        from collections import defaultdict
        by_p: dict[str, list] = defaultdict(list)
        for pl in placements:
            by_p[pl['plant']['slug']].append(pl)
        trimmed = []
        share = max(1, max_placements // max(len(by_p), 1))
        for slug, items in by_p.items():
            step = max(1, len(items) // share)
            trimmed.extend(items[::step][:share])
        placements = trimmed[:max_placements]

    citations = _resolve_citations(
        list(dict.fromkeys(cite_ids + ['sfg', 'umn', 'cornell', 'almanac', 'companions']))
    )
    # Dedupe by URL (UMN appears as both vegetables + companions pages)
    seen_urls: set[str] = set()
    deduped: list[dict] = []
    for c in citations:
        u = c.get('url') or c.get('title')
        if u in seen_urls:
            continue
        seen_urls.add(u)
        deduped.append(c)
    citations = deduped

    tmpl_names = [t['name'] for t in templates_used]
    summary = (
        f"Layout uses {', '.join(tmpl_names)} — intentional beds/blocks at each crop’s "
        f"own spacing, companions grouped, antagonists separated."
        if tmpl_names
        else 'Layout filled with per-crop spacing blocks.'
    )

    return {
        'placements': placements,
        'blocks': blocks,
        'templates_used': templates_used,
        'succession_notes': list(dict.fromkeys(succession_notes)),
        'citations': citations,
        'summary': summary,
    }


def suggest_fill(bed: Bed, plants: list[Plant], clear: bool = True) -> list[PlantPlacement]:
    """
    Fill a bed with intentional template/guild layouts.

    Returns list[PlantPlacement] for backward compatibility. Use suggest_fill_with_plan
    when rationale / citations are needed.
    """
    result = suggest_fill_with_plan(bed, plants, clear=clear)
    return result.placements


def suggest_fill_with_plan(
    bed: Bed, plants: list[Plant], clear: bool = True
) -> SuggestResult:
    if clear:
        bed.placements.all().delete()

    width = float(bed.width_ft)
    length = float(bed.length_ft)
    if width <= 0 or length <= 0 or not plants:
        return SuggestResult(placements=[], plan=SuggestPlan(summary='Nothing to place.'))

    plant_dicts = [_plant_dict(p) for p in plants]
    planned = plan_layout(width, length, plant_dicts)

    placed: list[PlantPlacement] = []
    for item in planned['placements']:
        plant_obj = item['plant'].get('_obj') or next(
            (p for p in plants if p.slug == item['plant']['slug']), None
        )
        if plant_obj is None:
            continue
        placement = PlantPlacement.objects.create(
            bed=bed,
            plant=plant_obj,
            x_ft=Decimal(str(item['x_ft'])),
            y_ft=Decimal(str(item['y_ft'])),
            quantity=int(item.get('quantity') or 1),
        )
        placed.append(placement)

    plan = SuggestPlan(
        templates_used=planned['templates_used'],
        succession_notes=planned['succession_notes'],
        citations=planned['citations'],
        summary=planned['summary'],
        blocks=planned['blocks'],
    )
    return SuggestResult(placements=placed, plan=plan)
