"""One-tap layout suggestion using spacing + companion planting."""
from __future__ import annotations

from decimal import Decimal

from .models import Bed, Plant, PlantPlacement


def _spacing_ft(plant: Plant) -> float:
    return max(plant.spacing_inches / 12.0, 0.5)


def _antag_conflict(plant: Plant, placed_ids: set[int]) -> bool:
    if not placed_ids:
        return False
    antag = set(plant.antagonists.values_list('id', flat=True))
    return bool(antag & placed_ids)


def _companion_bonus(plant: Plant, placed_ids: set[int]) -> int:
    if not placed_ids:
        return 0
    comps = set(plant.companions.values_list('id', flat=True))
    return len(comps & placed_ids)


def suggest_fill(bed: Bed, plants: list[Plant], clear: bool = True) -> list[PlantPlacement]:
    """
    Fill a bed with the selected plants on a spacing grid.

    Shares space fairly across crops (round-robin by companion score),
    skips strong antagonist pairs, and caps placements for a usable UI.
    """
    if clear:
        bed.placements.all().delete()

    width = float(bed.width_ft)
    length = float(bed.length_ft)
    if width <= 0 or length <= 0 or not plants:
        return []

    # Grid step = median-ish spacing so mixed plantings share a common lattice.
    spacings = sorted(_spacing_ft(p) for p in plants)
    step = spacings[len(spacings) // 2]
    step = max(0.75, min(step, 3.0))

    # Build candidate cells
    cells: list[tuple[float, float]] = []
    y = step / 2
    while y < length - 0.05:
        x = step / 2
        while x < width - 0.05:
            cells.append((round(x, 2), round(y, 2)))
            x += step
        y += step

    max_placements = max(6, min(36, len(cells)))
    cells = cells[:max_placements]

    # Order plants: prefer those with companions among the selection
    selected_ids = {p.id for p in plants}
    ranked = sorted(
        plants,
        key=lambda p: (
            -_companion_bonus(p, selected_ids - {p.id}),
            p.spacing_inches,
            p.name,
        ),
    )

    placed: list[PlantPlacement] = []
    placed_ids: set[int] = set()
    counts = {p.id: 0 for p in plants}
    # Fair share target per plant
    share = max(1, len(cells) // len(ranked))

    plant_cycle = list(ranked)
    idx = 0
    for cx, cy in cells:
        # Try up to N plants to find one that fits share + no antag
        chosen = None
        for attempt in range(len(plant_cycle)):
            plant = plant_cycle[(idx + attempt) % len(plant_cycle)]
            # Soft fair-share: prefer under-quota plants
            if counts[plant.id] >= share + 2 and any(counts[q.id] < share for q in ranked):
                continue
            # Soft preference: delay antagonists if an under-quota alternative exists
            if (
                _antag_conflict(plant, placed_ids)
                and len(ranked) > 1
                and any(counts[q.id] < share and not _antag_conflict(q, placed_ids) for q in ranked)
            ):
                continue
            chosen = plant
            idx = (idx + attempt + 1) % len(plant_cycle)
            break
        if chosen is None:
            chosen = plant_cycle[idx % len(plant_cycle)]
            idx = (idx + 1) % len(plant_cycle)
        placement = PlantPlacement.objects.create(
            bed=bed,
            plant=chosen,
            x_ft=Decimal(str(cx)),
            y_ft=Decimal(str(cy)),
            quantity=1,
        )
        placed.append(placement)
        placed_ids.add(chosen.id)
        counts[chosen.id] += 1

    return placed
