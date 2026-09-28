from django.conf import settings
from django.db import models
from django.urls import reverse


class Plant(models.Model):
    """A vegetable or herb in the plant bible."""

    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    scientific_name = models.CharField(max_length=150, blank=True)
    family = models.CharField(max_length=100, blank=True)
    spacing_inches = models.PositiveSmallIntegerField(
        help_text='In-row spacing between plants (inches).'
    )
    row_spacing_inches = models.PositiveSmallIntegerField(
        default=18, help_text='Spacing between rows (inches).'
    )
    days_to_maturity_min = models.PositiveSmallIntegerField(null=True, blank=True)
    days_to_maturity_max = models.PositiveSmallIntegerField(null=True, blank=True)
    sun_needs = models.CharField(
        max_length=20,
        choices=[
            ('full', 'Full sun'),
            ('partial', 'Partial sun'),
            ('shade', 'Shade tolerant'),
        ],
        default='full',
    )
    how_to = models.TextField(help_text='Full-sentence growing guidance.')
    companions = models.ManyToManyField(
        'self', blank=True, symmetrical=False, related_name='companion_of'
    )
    antagonists = models.ManyToManyField(
        'self', blank=True, symmetrical=False, related_name='antagonist_of'
    )
    citations = models.JSONField(
        default=list,
        help_text='List of {title, url, org} citation dicts.',
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plant_detail', kwargs={'slug': self.slug})

    @property
    def maturity_display(self):
        if self.days_to_maturity_min and self.days_to_maturity_max:
            if self.days_to_maturity_min == self.days_to_maturity_max:
                return f'{self.days_to_maturity_min} days'
            return f'{self.days_to_maturity_min}–{self.days_to_maturity_max} days'
        if self.days_to_maturity_min:
            return f'~{self.days_to_maturity_min} days'
        return '—'


class Plot(models.Model):
    """User's garden plot dimensions (onboarding)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='plots'
    )
    name = models.CharField(max_length=120)
    width_ft = models.DecimalField(max_digits=6, decimal_places=1)
    length_ft = models.DecimalField(max_digits=6, decimal_places=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.width_ft}×{self.length_ft} ft)'


class Layout(models.Model):
    """A named garden layout belonging to a user."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='layouts'
    )
    plot = models.ForeignKey(
        Plot, on_delete=models.SET_NULL, null=True, blank=True, related_name='layouts'
    )
    name = models.CharField(max_length=120)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('layout_detail', kwargs={'pk': self.pk})


class Bed(models.Model):
    """A rectangular bed within a layout."""

    layout = models.ForeignKey(Layout, on_delete=models.CASCADE, related_name='beds')
    name = models.CharField(max_length=80)
    x_ft = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    y_ft = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    width_ft = models.DecimalField(max_digits=6, decimal_places=1)
    length_ft = models.DecimalField(max_digits=6, decimal_places=1)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.width_ft}×{self.length_ft} ft)'

    @property
    def area_sqft(self):
        return float(self.width_ft) * float(self.length_ft)


class PlantPlacement(models.Model):
    """A plant placed in a bed."""

    bed = models.ForeignKey(Bed, on_delete=models.CASCADE, related_name='placements')
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='placements')
    x_ft = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    y_ft = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    quantity = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ['plant__name']

    def __str__(self):
        return f'{self.quantity}× {self.plant.name} in {self.bed.name}'
