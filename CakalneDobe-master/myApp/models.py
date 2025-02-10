from django.db import models

# Create your models here.

class CakDobe(models.Model):
    vzs_sifra = models.CharField(max_length=100)
    vzs_naziv = models.TextField()
    tip_vzs = models.CharField(max_length=100)
    povprecna_cd_zelo_h = models.FloatField(null=True, blank=True)
    povprecna_cd_hitro = models.FloatField(null=True, blank=True)
    povprecna_cd_redno = models.FloatField(null=True, blank=True)
    st_izvajalcev_bolnisnica = models.FloatField(null=True, blank=True)
    st_izvajalcev_zdravstveni_dom = models.FloatField(null=True, blank=True)
    st_izvajalcev_zasebnik = models.FloatField(null=True, blank=True)
    st_cakajocih_zelo_h = models.FloatField(null=True, blank=True)
    st_cakajocih_hitro = models.FloatField(null=True, blank=True)
    st_cakajocih_redno = models.FloatField(null=True, blank=True)
    st_cakajocih_vsota = models.FloatField(null=True, blank=True)
    st_vs_cakajocih_bolnisnica = models.FloatField(null=True, blank=True)
    st_vs_cakajocih_zdravstveni_dom = models.FloatField(null=True, blank=True)
    st_vs_cakajocih_zasebnik = models.FloatField(null=True, blank=True)
    nad_dop_cd_zelo_h = models.FloatField(null=True, blank=True)
    nad_dop_cd_hitro = models.FloatField(null=True, blank=True)
    nad_dop_cd_redno = models.FloatField(null=True, blank=True)
    nad_dop_cd_vsota = models.FloatField(null=True, blank=True)
    nad_dop_cd_vsota_bolnisnica = models.FloatField(null=True, blank=True)
    nad_dop_cd_vsota_zdravstveni_dom = models.FloatField(null=True, blank=True)
    nad_dop_cd_vsota_zasebnik = models.FloatField(null=True, blank=True)
    recorded_date = models.DateField(editable=True)
    DisplayFields = ['vzs_sifra', 'vzs_naziv', 'recorded_date', 'povprecna_cd_zelo_h', 'povprecna_cd_hitro', 'povprecna_cd_redno', 'st_izvajalcev_bolnisnica', 'st_izvajalcev_zdravstveni_dom', 'st_izvajalcev_zasebnik']
    
    def save(self, *args, **kwargs):
        # Round float fields to one decimal place
        if self.povprecna_cd_zelo_h is not None:
            self.povprecna_cd_zelo_h = round(self.povprecna_cd_zelo_h, 1)
        if self.povprecna_cd_hitro is not None:
            self.povprecna_cd_hitro = round(self.povprecna_cd_hitro, 1)
        if self.povprecna_cd_redno is not None:
            self.povprecna_cd_redno = round(self.povprecna_cd_redno, 1)
        # Add rounding for other float fields as needed

        super().save(*args, **kwargs)



class importedFiles(models.Model):
    naslov = models.TextField()
    dateAdded = models.DateField(auto_now_add=True)