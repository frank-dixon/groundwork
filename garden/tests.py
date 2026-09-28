from django.contrib.auth import get_user_model
from django.test import TestCase

from garden.models import Bed, Layout, Plant, Plot
from garden.suggest import plan_layout, suggest_fill_with_plan


class SuggestLayoutTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.core.management import call_command

        call_command('seed_plants')

    def test_tomato_basil_template(self):
        plants = list(Plant.objects.filter(slug__in=['tomato', 'basil', 'lettuce', 'carrot']))
        dicts = [
            {
                'slug': p.slug,
                'name': p.name,
                'spacing_inches': p.spacing_inches,
                'row_spacing_inches': p.row_spacing_inches,
                'sun_needs': p.sun_needs,
                'companions': list(p.companions.values_list('slug', flat=True)),
                'antagonists': list(p.antagonists.values_list('slug', flat=True)),
            }
            for p in plants
        ]
        result = plan_layout(4, 8, dicts)
        names = [t['name'] for t in result['templates_used']]
        self.assertTrue(any('Tomato' in n for n in names))
        self.assertTrue(result['blocks'])
        self.assertTrue(result['citations'])
        self.assertTrue(any('spacing' in (c.get('title') or '').lower() or 'Square' in (c.get('org') or '') or 'Extension' in (c.get('org') or '') for c in result['citations']))

    def test_three_sisters(self):
        plants = list(Plant.objects.filter(slug__in=['corn', 'bean', 'squash']))
        dicts = [
            {
                'slug': p.slug,
                'name': p.name,
                'spacing_inches': p.spacing_inches,
                'row_spacing_inches': p.row_spacing_inches,
                'sun_needs': p.sun_needs,
                'companions': list(p.companions.values_list('slug', flat=True)),
                'antagonists': list(p.antagonists.values_list('slug', flat=True)),
            }
            for p in plants
        ]
        result = plan_layout(4, 10, dicts)
        self.assertEqual(result['templates_used'][0]['name'], 'Three Sisters')

    def test_suggest_fill_persists(self):
        User = get_user_model()
        user = User.objects.create_user('gardener', password='x')
        plot = Plot.objects.create(user=user, name='P', width_ft=10, length_ft=12)
        layout = Layout.objects.create(user=user, plot=plot, name='L')
        bed = Bed.objects.create(layout=layout, name='Main', width_ft=4, length_ft=8)
        plants = list(Plant.objects.filter(slug__in=['tomato', 'basil'])[:2])
        result = suggest_fill_with_plan(bed, plants, clear=True)
        self.assertGreater(len(result.placements), 0)
        self.assertEqual(bed.placements.count(), len(result.placements))
        self.assertTrue(result.plan.templates_used)
