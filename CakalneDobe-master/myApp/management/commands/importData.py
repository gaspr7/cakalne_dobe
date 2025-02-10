import os
import pandas as pd
from datetime import datetime
from django.core.management.base import BaseCommand
from myApp.models import CakDobe

class Command(BaseCommand):
    help = "Import data from the Tb 01 sheet of an Excel file into the Django database."

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help="Path to the Excel file.")

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        file_name = os.path.basename(file_path)

        # Extract the recorded date from the filename
        try:
            date_str = file_name.split("na-dan-")[1].split(".xlsx")[0]
            recorded_date = datetime.strptime(date_str, "%d.%m.%Y").date()
        except (IndexError, ValueError):
            self.stdout.write(self.style.ERROR("Error: Could not extract date from filename."))
            return

        # Load the "Tb 01" sheet
        try:
            data = pd.read_excel(file_path, sheet_name="Tb 01")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error reading Excel file: {e}"))
            return

        # Iterate over rows and add to the database
        records_created = 0
        for _, row in data.iterrows():
            CakDobe.objects.create(
                vzs_sifra=row['VZS šifra'],
                vzs_naziv=row['VZS naziv'],
                tip_vzs=row['TIP VZS'],
                povprecna_cd_zelo_h=row['Povprečna ČD na prvi prosti termin ZELO HITRO'],
                povprecna_cd_hitro=row['Povprečna ČD na prvi prosti termin HITRO'],
                povprecna_cd_redno=row['Povprečna ČD na prvi prosti termin REDNO'],
                st_izvajalcev_bolnisnica=row['Število izvajalcev s čakajočimi pacienti Bolnišnica'],
                st_izvajalcev_zdravstveni_dom=row['Število izvajalcev s čakajočimi pacienti Zdravstveni dom'],
                st_izvajalcev_zasebnik=row['Število izvajalcev s čakajočimi pacienti Zasebnik s koncesijo'],
                st_cakajocih_zelo_h=row['Število čakajočih Zelo hitro'],
                st_cakajocih_hitro=row['Število čakajočih Hitro'],
                st_cakajocih_redno=row['Število čakajočih Redno'],
                st_cakajocih_vsota=row['Število čakajočih skupna vsota'],
                st_vs_cakajocih_bolnisnica=row['Število vseh čakajočih za tip izvajalca Bolnišnica'],
                st_vs_cakajocih_zdravstveni_dom=row['Število vseh čakajočih za tip izvajalca Zdravstveni dom'],
                st_vs_cakajocih_zasebnik=row['Število vseh čakajočih za tip izvajalca Zasebnik s koncesijo'],
                nad_dop_cd_zelo_h=row['Število čakajočih NAD dop. ČD Zelo hitro'],
                nad_dop_cd_hitro=row['Število čakajočih NAD dop. ČD Hitro'],
                nad_dop_cd_redno=row['Število čakajočih NAD dop. ČD Redno'],
                nad_dop_cd_vsota=row['Število čakajočih NAD dop. ČD skupna vsota'],
                nad_dop_cd_vsota_bolnisnica=row['Število vseh čakajočih NAD dop. ČD za tip izvajalca Bolnišnica'],
                nad_dop_cd_vsota_zdravstveni_dom=row['Število vseh čakajočih NAD dop. ČD za tip izvajalca Zdravstveni dom'],
                nad_dop_cd_vsota_zasebnik=row['Število vseh čakajočih NAD dop. ČD za tip izvajalca Zasebnik s koncesijo'],
                recorded_date=recorded_date
            )
            records_created += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully imported {records_created} records into the database."))
