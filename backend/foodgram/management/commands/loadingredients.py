import pandas as pd

from django.core.management.base import BaseCommand

from foodgram.models import Ingredient


class Command(BaseCommand):
    help = 'importing data from csv'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        df = pd.read_json('C:\\Dev\\foodgram-project-react\\data\\ingredients.json')
        for import_name, import_unit in zip(df.name, df.measurement_unit):
            models = Ingredient(name=import_name, measurement_unit=import_unit)
            models.save()
