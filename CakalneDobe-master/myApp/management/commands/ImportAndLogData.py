import os
import pandas as pd
from datetime import datetime
from django.core.management.base import BaseCommand
from myApp.models import CakDobe, importedFiles


class Command(BaseCommand):
    help = "Automatically imports data from Excel files in a directory into the Django database."

    def handle(self, *args, **kwargs):
        # Directory to monitor for files
        directory_path = "C:\\Users\\gasper\\OneDrive\\Namizje\\CakalneDobe-master\\CakalneDobe-master\\myApp\\dataFiles"

        
        if not os.path.exists(directory_path):
            self.stdout.write(self.style.ERROR(f"Error: Directory {directory_path} does not exist."))
            return

        # Get a list of all files in the directory
        files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]

        if not files:
            self.stdout.write(self.style.WARNING("No files found in the directory."))
            return

        for file_name in files:
            file_path = os.path.join(directory_path, file_name)

            # Check if the file has already been imported
            if importedFiles.objects.filter(naslov=file_name).exists():
                self.stdout.write(self.style.WARNING(f"Skipping already imported file: {file_name}"))
                continue

            # Extract the recorded date from the filename
            try:
                date_str = file_name.split("na-dan-")[1].split(".xlsx")[0]
                recorded_date = datetime.strptime(date_str, "%d.%m.%Y").date()
            except (IndexError, ValueError):
                self.stdout.write(self.style.ERROR(f"Error: Could not extract date from filename {file_name}."))
                continue

            # Load the "Tb 01" sheet
            try:
                data = pd.read_excel(file_path, sheet_name="Tb 01")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error reading Excel file {file_name}: {e}"))
                continue

            # Add records to the database
            records_created = 0
            for _, row in data.iterrows():
                try:
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
                except KeyError as e:
                    self.stdout.write(self.style.ERROR(f"Missing column in file {file_name}: {e}"))
                    continue

            # Add file to importedFiles table
            importedFiles.objects.create(naslov=file_name)

            # Delete the processed file
            os.remove(file_path)
            self.stdout.write(self.style.SUCCESS(f"Successfully processed {records_created} records from {file_name}."))
