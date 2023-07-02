import pandas as pd
from django.core.management.base import BaseCommand
from pathlib import Path

from foodgram.models import Ingredient

dir = Path(__file__).resolve().parent


class Command(BaseCommand):
    help = 'importing data from csv'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        df = pd.read_json(f'{dir}/data/ingredients.json')
        for import_name, import_unit in zip(df.name, df.measurement_unit):
            models = Ingredient(name=import_name, measurement_unit=import_unit)
            models.save()
