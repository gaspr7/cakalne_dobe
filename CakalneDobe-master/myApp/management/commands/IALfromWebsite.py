

import os
import requests
import pandas as pd
from datetime import datetime
from django.core.management.base import BaseCommand
from myApp.models import CakDobe, importedFiles 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re


class Command(BaseCommand):
    help = "Download the latest Excel file, process it and store data in the Django database." #Tukej glej smrduh

    def handle(self, *args, **kwargs):
        # Step 1: Setup Selenium WebDriver
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Run Chrome in headless mode

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # URL of the page with download links
        url = "https://nijz.si/cakalne-dobe/tedenska-porocila-o-cakalnih-dobah/"
        driver.get(url)

        # Step 2: Wait for the page content to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "a")))

        # Get the page source
        page_source = driver.page_source

        # Step 3: Parse with BeautifulSoup
        soup = BeautifulSoup(page_source, "html.parser")

        # Step 4: Find all links matching the desired pattern
        links = soup.find_all(
            "a", 
            href=True, 
            text = re.compile(r"^Izpis stanja čakalnih dob in števila čakajočih na ravni VZS na dan \d{1,2}\s*\.\s*\d{1,2}\s*\.\s*\d{4}\s*$", re.IGNORECASE)
        )

        if not links:#ojA NINA TUKEJ!!!!
            self.stdout.write(self.style.ERROR("No relevant download links found."))
            return

        # Step 5: Iterate through each link
        for link in links:
            file_url = link.get("href")
            

            file_name = file_url.split("/")[-1]

            # Check if this file has already been imported
            if importedFiles.objects.filter(naslov=file_name).exists():
                self.stdout.write(self.style.SUCCESS(f"File {file_name} has already been imported."))
                continue

            # Define the local download path
            
            download_path = "C:\\Users\\gasper\\OneDrive\\Namizje\\CakalneDobe-master\\CakalneDobe-master\\myApp\\dataFiles\\{file_name}"

            #spremeni path

            # Download the file
            # Step 6: Download the file if it's not already downloaded
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                file_response = requests.get(file_url, headers=headers, timeout=30)
                file_response.raise_for_status()  # Raise an HTTPError for bad responses

                with open(download_path, "wb") as f:
                    f.write(file_response.content)
                self.stdout.write(self.style.SUCCESS(f"Downloaded file {file_name}."))
            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.WARNING(f"Requests failed: {e}. Trying Selenium..."))
                try:
                    # Use Selenium to download the file
                    self.stdout.write(self.style.WARNING(f"Attempting to download {file_name} using Selenium..."))

                    # Navigate to the download link directly
                    driver.get(file_url)

                    download_dir = "C:\\Users\\gasper\\OneDrive\\Namizje\\CakalneDobe-master\\CakalneDobe-master\\myApp\\dataFiles/"
                    #spremeni download_dir
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

                    # Wait for the file to appear in the download directory
                    downloaded_file_path = os.path.join(download_dir, file_name)
                    WebDriverWait(driver, 30).until(lambda x: os.path.exists(downloaded_file_path))

                    self.stdout.write(self.style.SUCCESS(f"File {file_name} downloaded using Selenium."))
                except Exception as selenium_error:
                    self.stdout.write(self.style.ERROR(f"Selenium failed to download file {file_name}: {selenium_error}"))
                    return


            # Process the file and upload data to the database
            self.import_data_from_excel(download_path, file_name)

            # Record the filename in the importedFiles table
            importedFiles.objects.create(naslov=file_name)
            self.stdout.write(self.style.SUCCESS(f"File {file_name} successfully processed and imported."))

            # Clean up by deleting the file
            os.remove(download_path)
            self.stdout.write(self.style.SUCCESS(f"Deleted local file {file_name}."))

        driver.quit()


    def import_data_from_excel(self, file_path, file_name):
        """Helper method to process Excel file and import data into the database."""
        try:
            data = pd.read_excel(file_path, sheet_name="Tb 01")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error reading Excel file {file_name}: {e}"))
            return

        # Extract the recorded date from the filename
        try:
            date_str = file_name.split("na-dan-")[1].split(".xlsx")[0]
            recorded_date = datetime.strptime(date_str, "%d.%m.%Y").date()
        except (IndexError, ValueError):
            self.stdout.write(self.style.ERROR("Error: Could not extract date from filename."))
            return

        # Step 10: Iterate over rows and add to the database
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
