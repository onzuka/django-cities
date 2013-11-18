from django.contrib import admin
from models import *
from types import MethodType

class AltNamesSearchAdmin(admin.ModelAdmin):

    """
    Add name translations to `search_fields` and `list_display`.
    """

    def __init__(self, model, admin_site):
        super(AltNamesSearchAdmin, self).__init__(model, admin_site)
        # Append `search_fields` with translation fields.
        for rel in model._meta.get_all_related_objects():
            rel_name = rel.field.rel.related_name    # Related name of field in translation model.
            if (rel_name is not None) and rel_name.startswith(ALT_NAMES_PREFIX):
                # Add to `search_fields`.  Below assumed that
                # related model has field `name`.
                field_name = rel_name + '__name'
                self.search_fields += type(self.search_fields)((field_name,))
                # Create method to get alternative name
                # from related models and add it to `list_display`.
                method_name = self.alt_name_display(rel)
                self.list_display += type(self.list_display)((method_name,))

    def alt_name_display(self, rel):
        """
        Create method for displaying of alternative place name
        in this class and return its name.

        Arguments:
        rel - Related manager in model, which suppose to have
        attribute `name`.
        """
        rel_name = rel.field.rel.related_name
        def display(self, obj):
            rel_manager = getattr(obj, rel_name)
            return u', '.join(rel_manager.values_list('name', flat=True))
        display.short_description = rel.field.model._meta.verbose_name
        method_name =  rel_name + '_display'
        setattr(self, method_name, MethodType(display, self, AltNamesSearchAdmin))
        return method_name


class CountryAdmin(AltNamesSearchAdmin):
    list_display = ('name', 'code', 'tld', 'population')
    search_fields = ('name', 'code', 'tld')

admin.site.register(Country, CountryAdmin)

class RegionBaseAdmin(AltNamesSearchAdmin):
    ordering = ('name_std',)
    list_display = ('name_std', 'parent', 'code')
    search_fields = ('name', 'name_std', 'code')

class RegionAdmin(RegionBaseAdmin): pass

admin.site.register(Region, RegionAdmin)

class SubregionAdmin(RegionBaseAdmin):
    raw_id_fields = ('region',)

admin.site.register(Subregion, SubregionAdmin)

class CityBaseAdmin(AltNamesSearchAdmin):
    ordering = ('name_std',)
    list_display = ('name_std', 'parent', 'population')
    search_fields = ('name', 'name_std')

class CityAdmin(CityBaseAdmin):
    raw_id_fields = Region.levels

admin.site.register(City, CityAdmin)

class TownshipAdmin(CityBaseAdmin):
    raw_id_fields = ('city',)

admin.site.register(Township, TownshipAdmin)

class DistrictAdmin(CityBaseAdmin):
    raw_id_fields = ('city', 'township')

admin.site.register(District, DistrictAdmin)

class GeoAltNameAdmin(admin.ModelAdmin):
    ordering = ('name',)
    list_display = ('name', 'geo', 'is_preferred', 'is_short')
    list_filter = ('is_preferred', 'is_short')
    search_fields = ('name',)
    raw_id_fields = ('geo',)

[admin.site.register(geo_alt_name, GeoAltNameAdmin) for locales in geo_alt_names.values() for geo_alt_name in locales.values()]

class PostalCodeAdmin(admin.ModelAdmin):
    ordering = ('code',)
    list_display = ('code', 'country', 'region_name')
    search_fields = ('code', 'country__name', 'region_name', 'subregion_name')

admin.site.register(PostalCode, PostalCodeAdmin)
