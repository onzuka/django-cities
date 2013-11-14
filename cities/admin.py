from django.contrib import admin
from models import *

class AltNamesSearchAdmin(admin.ModelAdmin):

    """
    Add name translations to `search_fields`.
    """

    def __init__(self, model, admin_site):
        super(AltNamesSearchAdmin, self).__init__(model, admin_site)
        # Append `search_fields` with translation fields.
        for rel in model._meta.get_all_related_objects():
            rel_name = rel.field.rel.related_name    # Related name of field in translation model.
            if rel_name is not None and rel_name.startswith(ALT_NAMES_PREFIX):
                field_name = rel_name + '__name'    # Assumed, model has field `name`.
                self.search_fields += type(self.search_fields)((field_name,))

class CountryAdmin(AltNamesSearchAdmin):
    list_display = ['name', 'code', 'tld', 'population']
    search_fields = ['name', 'code', 'tld']

admin.site.register(Country, CountryAdmin)

class RegionBaseAdmin(AltNamesSearchAdmin):
    ordering = ['name_std']
    list_display = ['name_std', 'parent', 'code']
    search_fields = ['name', 'name_std', 'code']

class RegionAdmin(RegionBaseAdmin): pass

admin.site.register(Region, RegionAdmin)

class SubregionAdmin(RegionBaseAdmin):
    raw_id_fields = ['region']

admin.site.register(Subregion, SubregionAdmin)

class CityBaseAdmin(AltNamesSearchAdmin):
    ordering = ['name_std']
    list_display = ['name_std', 'parent', 'population']
    search_fields = ['name', 'name_std']

class CityAdmin(CityBaseAdmin):
    raw_id_fields = Region.levels

admin.site.register(City, CityAdmin)

class TownshipAdmin(CityBaseAdmin):
    raw_id_fields = ['city']

admin.site.register(Township, TownshipAdmin)

class DistrictAdmin(CityBaseAdmin):
    raw_id_fields = ['city', 'township']

admin.site.register(District, DistrictAdmin)

class GeoAltNameAdmin(admin.ModelAdmin):
    ordering = ['name']
    list_display = ['name', 'geo', 'is_preferred', 'is_short']
    list_filter = ['is_preferred', 'is_short']
    search_fields = ['name']
    raw_id_fields = ['geo']

[admin.site.register(geo_alt_name, GeoAltNameAdmin) for locales in geo_alt_names.values() for geo_alt_name in locales.values()]

class PostalCodeAdmin(admin.ModelAdmin):
    ordering = ['code']
    list_display = ['code', 'country', 'region_name']
    search_fields = ['code', 'country__name', 'region_name', 'subregion_name']

admin.site.register(PostalCode, PostalCodeAdmin)
