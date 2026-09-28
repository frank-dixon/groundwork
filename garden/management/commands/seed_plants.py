"""Seed the plant bible with common vegetables from open citable sources."""
from django.core.management.base import BaseCommand

from garden.models import Plant

def load_media_extras():
    """Merge image / varieties fields from docs/data/plants.json when present."""
    from pathlib import Path
    import json
    path = Path(__file__).resolve().parents[3] / 'docs' / 'data' / 'plants.json'
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    out = {}
    for row in data:
        out[row['slug']] = {
            'image': row.get('image') or '',
            'image_credit': row.get('image_credit') or {},
            'varieties': row.get('varieties') or [],
            'varieties_source': row.get('varieties_source') or {},
        }
    return out



# Citations reused across plants (extension / public-domain guidance).
CITE_ALMANAC = {
    'title': 'Vegetable Growing Guides',
    'url': 'https://www.almanac.com/gardening/growing-guides',
    'org': 'Old Farmer’s Almanac',
}
CITE_RHS = {
    'title': 'Grow Your Own',
    'url': 'https://www.rhs.org.uk/vegetables',
    'org': 'Royal Horticultural Society',
}
CITE_CORNELL = {
    'title': 'Home Gardening — Vegetables',
    'url': 'https://horticulture.cals.cornell.edu/',
    'org': 'Cornell University Horticulture',
}
CITE_UMN = {
    'title': 'Vegetables — Growing guides',
    'url': 'https://extension.umn.edu/vegetables',
    'org': 'University of Minnesota Extension',
}
CITE_USDA = {
    'title': 'USDA Plant Hardiness & crop profiles',
    'url': 'https://planthardiness.ars.usda.gov/',
    'org': 'USDA ARS',
}

# Companion edges: slug -> list of companion slugs / antagonist slugs
COMPANIONS = {
    'tomato': ['basil', 'carrot', 'onion', 'lettuce', 'parsley'],
    'basil': ['tomato', 'pepper', 'oregano'],
    'pepper': ['basil', 'onion', 'carrot', 'tomato'],
    'carrot': ['onion', 'lettuce', 'radish', 'tomato', 'pea'],
    'onion': ['carrot', 'lettuce', 'tomato', 'beet'],
    'lettuce': ['carrot', 'radish', 'onion', 'strawberry'],
    'cucumber': ['bean', 'pea', 'radish', 'sunflower'],
    'bean': ['carrot', 'cucumber', 'cabbage', 'corn'],
    'pea': ['carrot', 'radish', 'cucumber', 'corn'],
    'squash': ['corn', 'bean', 'radish'],
    'corn': ['bean', 'squash', 'cucumber', 'pea'],
    'kale': ['beet', 'onion', 'celery'],
    'spinach': ['strawberry', 'pea', 'cabbage'],
    'broccoli': ['onion', 'celery', 'beet'],
    'cabbage': ['onion', 'celery', 'bean', 'dill'],
    'radish': ['carrot', 'lettuce', 'pea', 'cucumber', 'squash'],
    'beet': ['onion', 'cabbage', 'kale', 'lettuce'],
    'potato': ['bean', 'corn'],
    'eggplant': ['bean', 'pepper', 'spinach'],
    'garlic': ['tomato', 'carrot', 'beet'],
    'chard': ['onion', 'cabbage', 'lettuce'],
    'cilantro': ['spinach', 'lettuce', 'tomato'],
}

ANTAGONISTS = {
    'tomato': ['potato', 'corn', 'fennel'],
    'potato': ['tomato', 'squash', 'cucumber'],
    'onion': ['bean', 'pea'],
    'bean': ['onion', 'garlic'],
    'pea': ['onion', 'garlic'],
    'cabbage': ['strawberry', 'tomato'],
    'carrot': ['dill'],  # dill not seeded; harmless empty
    'cucumber': ['potato'],
    'squash': ['potato'],
}


PLANTS = [
    {
        'slug': 'tomato',
        'name': 'Tomato',
        'scientific_name': 'Solanum lycopersicum',
        'family': 'Solanaceae',
        'spacing_inches': 24,
        'row_spacing_inches': 36,
        'days_to_maturity_min': 60,
        'days_to_maturity_max': 85,
        'sun_needs': 'full',
        'how_to': (
            'Tomato thrives in full sun and warm soil after all frost danger has passed. '
            'Set transplants deep, burying part of the stem so extra roots form along the buried portion. '
            'Space plants about 24 inches apart in rows 36 inches apart, and provide sturdy stakes or cages. '
            'Water consistently at the base to reduce leaf disease, and mulch to keep moisture even. '
            'Harvest when fruits are fully colored and slightly soft to the touch.'
        ),
        'citations': [CITE_UMN, CITE_ALMANAC, CITE_CORNELL],
    },
    {
        'slug': 'pepper',
        'name': 'Pepper',
        'scientific_name': 'Capsicum annuum',
        'family': 'Solanaceae',
        'spacing_inches': 18,
        'row_spacing_inches': 24,
        'days_to_maturity_min': 60,
        'days_to_maturity_max': 90,
        'sun_needs': 'full',
        'how_to': (
            'Peppers need full sun and consistently warm temperatures; transplant only after nights stay above about 50°F. '
            'Space plants 18 inches apart so air can move between canopies and reduce fungal pressure. '
            'Keep soil evenly moist but never waterlogged, and side-dress lightly once fruits set. '
            'Harvest sweet peppers when fully sized and colored, or pick hot peppers as they mature to the desired heat.'
        ),
        'citations': [CITE_UMN, CITE_ALMANAC],
    },
    {
        'slug': 'cucumber',
        'name': 'Cucumber',
        'scientific_name': 'Cucumis sativus',
        'family': 'Cucurbitaceae',
        'spacing_inches': 12,
        'row_spacing_inches': 36,
        'days_to_maturity_min': 50,
        'days_to_maturity_max': 70,
        'sun_needs': 'full',
        'how_to': (
            'Cucumbers grow quickly in warm, fertile soil with full sun. '
            'Sow or transplant after frost, spacing hills or plants about 12 inches apart along a trellis, or farther apart if vines sprawl. '
            'Provide steady moisture; uneven watering often causes bitter fruit. '
            'Pick fruits young and often so the plant keeps producing through the season.'
        ),
        'citations': [CITE_UMN, CITE_RHS],
    },
    {
        'slug': 'lettuce',
        'name': 'Lettuce',
        'scientific_name': 'Lactuca sativa',
        'family': 'Asteraceae',
        'spacing_inches': 8,
        'row_spacing_inches': 12,
        'days_to_maturity_min': 30,
        'days_to_maturity_max': 60,
        'sun_needs': 'partial',
        'how_to': (
            'Lettuce prefers cool weather and can take partial sun in hot climates. '
            'Sow succession plantings every two weeks in spring and again in fall for a continuous harvest. '
            'Thin to about 8 inches for head types, or harvest baby leaves earlier at tighter spacing. '
            'Keep soil moist and provide afternoon shade when temperatures climb to delay bolting.'
        ),
        'citations': [CITE_UMN, CITE_ALMANAC],
    },
    {
        'slug': 'carrot',
        'name': 'Carrot',
        'scientific_name': 'Daucus carota',
        'family': 'Apiaceae',
        'spacing_inches': 3,
        'row_spacing_inches': 12,
        'days_to_maturity_min': 55,
        'days_to_maturity_max': 80,
        'sun_needs': 'full',
        'how_to': (
            'Carrots need loose, stone-free soil so roots can grow straight. '
            'Sow seed thinly about ¼ inch deep, then thin seedlings to roughly 3 inches apart once they are a few inches tall. '
            'Keep the seedbed evenly moist until germination, which can take up to three weeks. '
            'Harvest when shoulders reach the expected diameter for the variety, usually after 55–80 days.'
        ),
        'citations': [CITE_UMN, CITE_RHS],
    },
    {
        'slug': 'bean',
        'name': 'Bush Bean',
        'scientific_name': 'Phaseolus vulgaris',
        'family': 'Fabaceae',
        'spacing_inches': 4,
        'row_spacing_inches': 18,
        'days_to_maturity_min': 50,
        'days_to_maturity_max': 60,
        'sun_needs': 'full',
        'how_to': (
            'Bush beans fix some of their own nitrogen and grow well in ordinary garden soil with full sun. '
            'Sow after the last frost when soil has warmed, placing seeds about 4 inches apart in rows 18 inches apart. '
            'Avoid working among wet plants to limit disease spread. '
            'Pick pods while they are still slender and tender; frequent harvest encourages more flowers.'
        ),
        'citations': [CITE_UMN, CITE_ALMANAC],
    },
    {
        'slug': 'pea',
        'name': 'Pea',
        'scientific_name': 'Pisum sativum',
        'family': 'Fabaceae',
        'spacing_inches': 3,
        'row_spacing_inches': 18,
        'days_to_maturity_min': 55,
        'days_to_maturity_max': 70,
        'sun_needs': 'full',
        'how_to': (
            'Peas are a cool-season crop best sown as soon as the soil can be worked in spring. '
            'Plant seeds about 3 inches apart along a low trellis or fence for easier picking. '
            'Provide even moisture during flowering and pod fill. '
            'Harvest snap and shell peas when pods are plump but before seeds become starchy.'
        ),
        'citations': [CITE_UMN, CITE_CORNELL],
    },
    {
        'slug': 'squash',
        'name': 'Zucchini',
        'scientific_name': 'Cucurbita pepo',
        'family': 'Cucurbitaceae',
        'spacing_inches': 36,
        'row_spacing_inches': 48,
        'days_to_maturity_min': 45,
        'days_to_maturity_max': 55,
        'sun_needs': 'full',
        'how_to': (
            'Zucchini and other summer squash need space, heat, and rich soil. '
            'Plant hills or transplants about 36 inches apart after frost, in full sun. '
            'Water deeply at the base and watch for squash vine borer and powdery mildew. '
            'Harvest fruits at 6–8 inches long for best flavor; oversized fruit slows production.'
        ),
        'citations': [CITE_UMN, CITE_ALMANAC],
    },
    {
        'slug': 'kale',
        'name': 'Kale',
        'scientific_name': 'Brassica oleracea var. acephala',
        'family': 'Brassicaceae',
        'spacing_inches': 12,
        'row_spacing_inches': 18,
        'days_to_maturity_min': 50,
        'days_to_maturity_max': 70,
        'sun_needs': 'full',
        'how_to': (
            'Kale is hardy and productive in cool weather, with flavor that often sweetens after light frost. '
            'Transplant or thin seedlings to about 12 inches apart so leaves can expand. '
            'Provide fertile soil and steady moisture; harvest outer leaves while leaving the growing tip intact. '
            'Use row cover early to reduce flea beetle damage on young plants.'
        ),
        'citations': [CITE_UMN, CITE_RHS],
    },
    {
        'slug': 'spinach',
        'name': 'Spinach',
        'scientific_name': 'Spinacia oleracea',
        'family': 'Amaranthaceae',
        'spacing_inches': 4,
        'row_spacing_inches': 12,
        'days_to_maturity_min': 35,
        'days_to_maturity_max': 45,
        'sun_needs': 'partial',
        'how_to': (
            'Spinach bolts quickly in heat, so grow it in spring and fall or give it afternoon shade in warmer zones. '
            'Sow thickly and thin to about 4 inches for full leaves, or cut baby greens sooner. '
            'Keep soil cool and moist with mulch. '
            'Harvest whole plants or pick outer leaves as needed before flower stalks form.'
        ),
        'citations': [CITE_UMN, CITE_ALMANAC],
    },
    {
        'slug': 'broccoli',
        'name': 'Broccoli',
        'scientific_name': 'Brassica oleracea var. italica',
        'family': 'Brassicaceae',
        'spacing_inches': 18,
        'row_spacing_inches': 24,
        'days_to_maturity_min': 60,
        'days_to_maturity_max': 90,
        'sun_needs': 'full',
        'how_to': (
            'Broccoli prefers cool temperatures and rich, well-drained soil in full sun. '
            'Set transplants 18 inches apart and keep them evenly watered through head formation. '
            'Cut the central head when buds are tight and green, before florets begin to open. '
            'Many varieties then produce smaller side shoots for a longer harvest window.'
        ),
        'citations': [CITE_UMN, CITE_CORNELL],
    },
    {
        'slug': 'onion',
        'name': 'Onion',
        'scientific_name': 'Allium cepa',
        'family': 'Amaryllidaceae',
        'spacing_inches': 4,
        'row_spacing_inches': 12,
        'days_to_maturity_min': 90,
        'days_to_maturity_max': 120,
        'sun_needs': 'full',
        'how_to': (
            'Onions need full sun and fertile, well-drained soil; choose day-length varieties suited to your latitude. '
            'Set sets or transplants about 4 inches apart in rows a foot apart. '
            'Water regularly while bulbs are sizing, then ease off as tops begin to yellow and fall. '
            'Cure harvested bulbs in a warm, airy place before storage.'
        ),
        'citations': [CITE_UMN, CITE_ALMANAC],
    },
    {
        'slug': 'radish',
        'name': 'Radish',
        'scientific_name': 'Raphanus sativus',
        'family': 'Brassicaceae',
        'spacing_inches': 2,
        'row_spacing_inches': 6,
        'days_to_maturity_min': 21,
        'days_to_maturity_max': 30,
        'sun_needs': 'full',
        'how_to': (
            'Radishes are one of the fastest garden crops and shine in cool spring and fall beds. '
            'Sow seed directly, then thin to about 2 inches so roots can swell cleanly. '
            'Provide consistent moisture; dry spells make roots woody and pungent. '
            'Pull as soon as they reach eating size—often in three to four weeks.'
        ),
        'citations': [CITE_UMN, CITE_ALMANAC],
    },
    {
        'slug': 'basil',
        'name': 'Basil',
        'scientific_name': 'Ocimum basilicum',
        'family': 'Lamiaceae',
        'spacing_inches': 10,
        'row_spacing_inches': 12,
        'days_to_maturity_min': 50,
        'days_to_maturity_max': 75,
        'sun_needs': 'full',
        'how_to': (
            'Basil loves heat and full sun; wait until nights are reliably warm before transplanting outdoors. '
            'Space plants about 10 inches apart and pinch growing tips early to encourage bushy growth. '
            'Water at the soil line and harvest leaves regularly before flowering for the best flavor. '
            'Protect from cold snaps—basil is frost tender.'
        ),
        'citations': [CITE_RHS, CITE_ALMANAC],
    },
    {
        'slug': 'corn',
        'name': 'Sweet Corn',
        'scientific_name': 'Zea mays',
        'family': 'Poaceae',
        'spacing_inches': 12,
        'row_spacing_inches': 30,
        'days_to_maturity_min': 70,
        'days_to_maturity_max': 90,
        'sun_needs': 'full',
        'how_to': (
            'Sweet corn is wind-pollinated, so plant in blocks of at least three to four short rows rather than a single line. '
            'Sow after soil warms, spacing seeds about 12 inches apart in rows 30 inches apart. '
            'Keep moist during tassel and silk stages. '
            'Harvest when silks brown and kernels release a milky juice when pierced.'
        ),
        'citations': [CITE_UMN, CITE_CORNELL],
    },
    {
        'slug': 'potato',
        'name': 'Potato',
        'scientific_name': 'Solanum tuberosum',
        'family': 'Solanaceae',
        'spacing_inches': 12,
        'row_spacing_inches': 30,
        'days_to_maturity_min': 70,
        'days_to_maturity_max': 120,
        'sun_needs': 'full',
        'how_to': (
            'Plant certified seed potatoes in loose soil once it can be worked and severe frost risk has eased. '
            'Space pieces about 12 inches apart and hill soil or mulch around stems as plants grow to protect developing tubers from light. '
            'Water evenly, especially during tuber set. '
            'Harvest new potatoes when plants flower, or wait until tops die back for storage crops.'
        ),
        'citations': [CITE_UMN, CITE_RHS],
    },
    {
        'slug': 'beet',
        'name': 'Beet',
        'scientific_name': 'Beta vulgaris',
        'family': 'Amaranthaceae',
        'spacing_inches': 4,
        'row_spacing_inches': 12,
        'days_to_maturity_min': 50,
        'days_to_maturity_max': 70,
        'sun_needs': 'full',
        'how_to': (
            'Beets grow best in cool weather with even moisture and moderately fertile soil. '
            'Sow directly and thin clusters to about 4 inches so roots can size up; use thinnings as greens. '
            'Keep soil from crusting over germinating seed. '
            'Harvest roots at golf-ball to tennis-ball size for tender texture.'
        ),
        'citations': [CITE_UMN, CITE_ALMANAC],
    },
    {
        'slug': 'cabbage',
        'name': 'Cabbage',
        'scientific_name': 'Brassica oleracea var. capitata',
        'family': 'Brassicaceae',
        'spacing_inches': 18,
        'row_spacing_inches': 24,
        'days_to_maturity_min': 65,
        'days_to_maturity_max': 100,
        'sun_needs': 'full',
        'how_to': (
            'Cabbage prefers cool seasons and steady fertility in full sun. '
            'Transplant 18 inches apart and use floating row cover to exclude cabbage worms. '
            'Water regularly so heads form evenly without splitting after rains. '
            'Cut heads when they are firm and fully sized for the variety.'
        ),
        'citations': [CITE_UMN, CITE_CORNELL],
    },
    {
        'slug': 'eggplant',
        'name': 'Eggplant',
        'scientific_name': 'Solanum melongena',
        'family': 'Solanaceae',
        'spacing_inches': 18,
        'row_spacing_inches': 30,
        'days_to_maturity_min': 65,
        'days_to_maturity_max': 90,
        'sun_needs': 'full',
        'how_to': (
            'Eggplant demands heat; transplant only after soil and nights are warm. '
            'Space plants about 18 inches apart in full sun and consider black mulch to warm the root zone. '
            'Stake taller varieties and keep soil evenly moist. '
            'Harvest fruits when the skin is glossy; dull skin often means seeds have hardened.'
        ),
        'citations': [CITE_UMN, CITE_ALMANAC],
    },
    {
        'slug': 'garlic',
        'name': 'Garlic',
        'scientific_name': 'Allium sativum',
        'family': 'Amaryllidaceae',
        'spacing_inches': 6,
        'row_spacing_inches': 12,
        'days_to_maturity_min': 240,
        'days_to_maturity_max': 270,
        'sun_needs': 'full',
        'how_to': (
            'Plant garlic cloves in fall in most temperate regions so roots establish before winter. '
            'Set cloves point-up about 6 inches apart and 2 inches deep, then mulch heavily. '
            'Water in spring as bulbs size; stop watering when leaves yellow. '
            'Cure harvested bulbs in shade with good airflow before storing.'
        ),
        'citations': [CITE_UMN, CITE_RHS],
    },
    {
        'slug': 'chard',
        'name': 'Swiss Chard',
        'scientific_name': 'Beta vulgaris var. cicla',
        'family': 'Amaranthaceae',
        'spacing_inches': 8,
        'row_spacing_inches': 12,
        'days_to_maturity_min': 50,
        'days_to_maturity_max': 60,
        'sun_needs': 'full',
        'how_to': (
            'Swiss chard tolerates more heat than spinach and produces over a long season. '
            'Thin seedlings to about 8 inches apart and harvest outer leaves while leaving the crown growing. '
            'Provide fertile soil and regular water for tender leaves. '
            'In mild climates it can overwinter and resume growth in spring.'
        ),
        'citations': [CITE_UMN, CITE_ALMANAC],
    },
    {
        'slug': 'cilantro',
        'name': 'Cilantro',
        'scientific_name': 'Coriandrum sativum',
        'family': 'Apiaceae',
        'spacing_inches': 4,
        'row_spacing_inches': 8,
        'days_to_maturity_min': 30,
        'days_to_maturity_max': 45,
        'sun_needs': 'partial',
        'how_to': (
            'Cilantro prefers cool weather and will bolt quickly in summer heat. '
            'Sow successive small plantings every few weeks in spring and fall, thinning to about 4 inches. '
            'Provide afternoon shade in warmer months and keep soil moist. '
            'Harvest leaves young; allow some plants to flower if you also want coriander seed.'
        ),
        'citations': [CITE_RHS, CITE_ALMANAC],
    },
]


class Command(BaseCommand):
    help = 'Seed ~20 common vegetables into the plant bible (idempotent upsert by slug).'

    def handle(self, *args, **options):
        created = updated = 0
        plants_by_slug = {}
        media = load_media_extras()
        for data in PLANTS:
            citations = data.pop('citations')
            extras = media.get(data['slug'], {})
            defaults = {
                **data,
                'citations': citations,
                'image': extras.get('image', ''),
                'image_credit': extras.get('image_credit', {}),
                'varieties': extras.get('varieties', []),
                'varieties_source': extras.get('varieties_source', {}),
            }
            obj, was_created = Plant.objects.update_or_create(
                slug=data['slug'],
                defaults=defaults,
            )
            # put citations back for safety if re-run in same process
            data['citations'] = citations
            plants_by_slug[obj.slug] = obj
            if was_created:
                created += 1
            else:
                updated += 1

        # Wire companions / antagonists by slug (skip missing)
        for slug, companions in COMPANIONS.items():
            plant = plants_by_slug.get(slug)
            if not plant:
                continue
            ids = [plants_by_slug[c].id for c in companions if c in plants_by_slug]
            plant.companions.set(ids)

        for slug, antagonists in ANTAGONISTS.items():
            plant = plants_by_slug.get(slug)
            if not plant:
                continue
            ids = [plants_by_slug[a].id for a in antagonists if a in plants_by_slug]
            plant.antagonists.set(ids)

        self.stdout.write(
            self.style.SUCCESS(
                f'Seeded plants: {created} created, {updated} updated '
                f'({Plant.objects.count()} total).'
            )
        )
