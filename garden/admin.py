from django.contrib import admin

from .models import Bed, Layout, Plant, PlantPlacement, Plot


class BedInline(admin.TabularInline):
    model = Bed
    extra = 0


class PlacementInline(admin.TabularInline):
    model = PlantPlacement
    extra = 0


@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ('name', 'spacing_inches', 'sun_needs', 'days_to_maturity_min')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('companions', 'antagonists')
    search_fields = ('name', 'scientific_name')


@admin.register(Plot)
class PlotAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'width_ft', 'length_ft', 'created_at')
    list_filter = ('user',)


@admin.register(Layout)
class LayoutAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'plot', 'updated_at')
    list_filter = ('user',)
    inlines = [BedInline]


@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ('name', 'layout', 'width_ft', 'length_ft')
    inlines = [PlacementInline]


@admin.register(PlantPlacement)
class PlantPlacementAdmin(admin.ModelAdmin):
    list_display = ('plant', 'bed', 'quantity', 'x_ft', 'y_ft')
