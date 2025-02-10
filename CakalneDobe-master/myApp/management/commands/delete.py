from myApp.models import CakDobe, importedFiles

deleted_count, _ = CakDobe.objects.all().delete()
print(f"All records deleted. {deleted_count} records were removed.")

deleted_count, _ = importedFiles.objects.all().delete()
print(f"All records deleted. {deleted_count} records were removed.")