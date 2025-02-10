from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import CakDobe
from django.db.models import Sum
from django.db.models.functions import Coalesce

def home(request):
    return render(request, "home.html")

def databasetest(request):
    items = CakDobe.objects.all()
    return render(request, 'databasetest.html', {"CakDobe": items})

def executors(request):
    items = CakDobe.objects.all()
    return render(request, 'executors.html', {"CakDobe": items})

def primerjava_tipov_pregleda(request):
    items = CakDobe.objects.all()
    return render(request, 'primerjava_tipov_pregleda.html', {"CakDobe": items})

def get_chart_data(request):
    if request.method == "POST":
        body = json.loads(request.body)
        vzs_naziv = body.get("vzs_naziv")
        print(vzs_naziv)
        record = CakDobe.objects.filter(vzs_naziv=vzs_naziv).order_by('-recorded_date').first()
        print(record.recorded_date)
        if record:
            data = {
                "povprecna_cd_zelo_h": record.povprecna_cd_zelo_h,
                "povprecna_cd_hitro": record.povprecna_cd_hitro,
                "povprecna_cd_redno": record.povprecna_cd_redno,
            }
            return JsonResponse(data)
        else:
            return JsonResponse({"error": "No data found"}, status=404)
        
def search_vzs(request):
    query = request.GET.get('query', '')
    results = CakDobe.objects.filter(vzs_naziv__icontains=query).values('vzs_naziv')[:500]  
    return JsonResponse({
        'results': [{'vzs_naziv': item['vzs_naziv']} for item in results]
    })

def search_date(request):
    query = request.GET.get('query', '')
    if query:
        results = CakDobe.objects.filter(recorded_date__icontains=query).values('recorded_date').distinct()[:500]
    else:
        results = CakDobe.objects.values('recorded_date').distinct()[:500]

    return JsonResponse({
        'results': [{'id': item['recorded_date'], 'text': item['recorded_date'].strftime('%Y-%m-%d')} for item in results]
    })

from django.http import JsonResponse
import json
from .models import CakDobe

def get_data_by_date(request):
    try:
        data = (
            CakDobe.objects.values("recorded_date", "tip_vzs")
            .annotate(st_cakajocih_vsota=Sum("st_cakajocih_vsota"))
            .order_by("recorded_date")  # Razvrstitev po datumu
        )

        
        return JsonResponse(list(data), safe=False)
    except Exception as e:
        return JsonResponse({"error": f"Napaka na strežniku: {str(e)}"}, status=500)

def prestej_tipe(request):
    # Preštej število različnih tipov pregledov
    kurativni_count = Pregled.objects.filter(tip_vzs__icontains='Kurativni').count()
    diagnostični_count = Pregled.objects.filter(tip_vzs__icontains='Diagnostični').count()
    terapevtski_count = Pregled.objects.filter(tip_vzs__icontains='Terapevtski').count()

    return JsonResponse({
        'kurativni_count': kurativni_count,
        'diagnostični_count': diagnostični_count,
        'terapevtski_count': terapevtski_count
    })

   
def zacetna_storitev_graf2(request):
    if request.method == "POST":
        try:
            data = (
                CakDobe.objects
                .values("recorded_date")  # Združuje po recorded_date
                .annotate(total_nad_dop_cd_vsota=Sum("nad_dop_cd_vsota"))  # Izračuna vsoto
            )
            
            return JsonResponse(list(data), safe=False)
        except Exception as e:
            return JsonResponse({"error": f"Napaka na strežniku: {str(e)}"}, status=500)
    else:
        return JsonResponse({"error": "Neveljavna HTTP metoda. Uporabite POST."}, status=405)


def get_executors_count(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            vzs_naziv = body.get("vzs_naziv")

            if not vzs_naziv:
                return JsonResponse({"error": "Parameter 'vzs_naziv' manjka."}, status=400)

            records = CakDobe.objects.filter(vzs_naziv=vzs_naziv).order_by("recorded_date")

            if not records.exists():
                return JsonResponse({"error": f"Ni podatkov za {vzs_naziv}."}, status=404)

            data = [
                {
                    "recorded_date": record.recorded_date.strftime("%Y-%m-%d"),
                    "st_vs_cakajocih_bolnisnica": record.st_vs_cakajocih_bolnisnica,
                    "st_vs_cakajocih_zdravstveni_dom": record.st_vs_cakajocih_zdravstveni_dom,
                    "st_vs_cakajocih_zasebnik": record.st_vs_cakajocih_zasebnik,
                }
                for record in records
            ]

            return JsonResponse(data, safe=False)  
        except json.JSONDecodeError:
            return JsonResponse({"error": "Neveljaven JSON format."}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Napaka na strežniku: {str(e)}"}, status=500)
    else:
        return JsonResponse({"error": "Neveljavna HTTP metoda. Uporabite POST."}, status=405)




def po_tipih2(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            vzs_naziv = body.get("vzs_naziv")

            if not vzs_naziv:
                return JsonResponse({"error": "Parameter 'vzs_naziv' manjka."}, status=400)

            records = CakDobe.objects.filter(vzs_naziv=vzs_naziv).order_by("recorded_date")

            if not records.exists():
                return JsonResponse({"error": f"Ni podatkov za {vzs_naziv}."}, status=404)

            data = [
                {
                    "recorded_date": record.recorded_date.strftime("%Y-%m-%d"),
                    "nad_dop_cd_vsota_bolnisnica": record.nad_dop_cd_vsota_bolnisnica,
                    "nad_dop_cd_vsota_zdravstveni_dom": record.nad_dop_cd_vsota_zdravstveni_dom,
                    "nad_dop_cd_vsota_zasebnik": record.nad_dop_cd_vsota_zasebnik,
                }
                for record in records
            ]

            return JsonResponse(data, safe=False)  # Return list as JSON
        except json.JSONDecodeError:
            return JsonResponse({"error": "Neveljaven JSON format."}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Napaka na strežniku: {str(e)}"}, status=500)
    else:
        return JsonResponse({"error": "Neveljavna HTTP metoda. Uporabite POST."}, status=405)




def ena_storitev_graf2(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            vzs_naziv = body.get("vzs_naziv")

            if not vzs_naziv:
                return JsonResponse({"error": "Parameter 'vzs_naziv' manjka."}, status=400)

            records = CakDobe.objects.filter(vzs_naziv=vzs_naziv).order_by("recorded_date")

            if not records.exists():
                return JsonResponse({"error": f"Ni podatkov za {vzs_naziv}."}, status=404)

            data = [
                {
                    "recorded_date": record.recorded_date.strftime("%Y-%m-%d"),
                    "povprecna_cd_zelo_h": record.povprecna_cd_zelo_h,
                    "povprecna_cd_hitro": record.povprecna_cd_hitro,
                    "povprecna_cd_redno": record.povprecna_cd_redno
                }
                for record in records
            ]

            return JsonResponse(data, safe=False)  
        except json.JSONDecodeError:
            return JsonResponse({"error": "Neveljaven JSON format."}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Napaka na strežniku: {str(e)}"}, status=500)
    else:
        return JsonResponse({"error": "Neveljavna HTTP metoda. Uporabite POST."}, status=405)




def ena_storitev_graf3(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            vzs_naziv = body.get("vzs_naziv")

            if not vzs_naziv:
                return JsonResponse({"error": "Parameter 'vzs_naziv' manjka."}, status=400)

            records = CakDobe.objects.filter(vzs_naziv=vzs_naziv).order_by("recorded_date")

            if not records.exists():
                return JsonResponse({"error": f"Ni podatkov za {vzs_naziv}."}, status=404)

            data = [
                {
                    "recorded_date": record.recorded_date.strftime("%Y-%m-%d"),
                    "nad_dop_cd_zelo_h": record.nad_dop_cd_zelo_h,
                    "nad_dop_cd_hitro": record.nad_dop_cd_hitro,
                    "nad_dop_cd_redno": record.nad_dop_cd_redno,
                }
                for record in records
            ]

            return JsonResponse(data, safe=False)  
        except json.JSONDecodeError:
            return JsonResponse({"error": "Neveljaven JSON format."}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Napaka na strežniku: {str(e)}"}, status=500)
    else:
        return JsonResponse({"error": "Neveljavna HTTP metoda. Uporabite POST."}, status=405)







def get_izvajalci(request):
    if request.method == "POST":
        body = json.loads(request.body)
        vzs_naziv = body.get("vzs_naziv")
        print(vzs_naziv)
        record = CakDobe.objects.filter(vzs_naziv=vzs_naziv).order_by('-recorded_date').first()
        print(record.recorded_date)
        if record:
            data = {
                "st_izvajalcev_bolnisnica": record.st_izvajalcev_bolnisnica,
                "st_izvajalcev_zdravstveni_dom": record.st_izvajalcev_zdravstveni_dom,
                "st_izvajalcev_zasebnik": record.st_izvajalcev_zasebnik,
            }
            return JsonResponse(data)
        else:
            return JsonResponse({"error": "No data found"}, status=404)


def trend_nad_dop_cd_vsota(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            
            
            records = CakDobe.objects.filter(vzs_naziv=vzs_naziv).order_by("recorded_date")

            if not records.exists():
                return JsonResponse({"error": f"Ni podatkov za {vzs_naziv}."}, status=404)

            data = [
                {
                    "recorded_date": record.recorded_date.strftime("%Y-%m-%d"),  
                    "nad_dop_cd_vsota": record.nad_dop_cd_vsota,
                }
                for record in records
            ]

            return JsonResponse(data, safe=False)  
        except json.JSONDecodeError:
            return JsonResponse({"error": "Neveljaven JSON format."}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Napaka na strežniku: {str(e)}"}, status=500)
    else:
        return JsonResponse({"error": "Neveljavna HTTP metoda. Uporabite POST."}, status=405)



def cakajoce_po_kategorijah_nujnost(request):
    if request.method == "POST":
        try:
            
            cakajoce_bolnisnica = CakDobe.objects.filter(kategorija='bolnisnica').last()
            cakajoce_zdravstveni_dom = CakDobe.objects.filter(kategorija='zdravstveni_dom').last()
            cakajoce_zasebnik = CakDobe.objects.filter(kategorija='zasebnik').last()
            
            st_izvajalcev_bolnisnica = cakajoce_bolnisnica.stevilo_cakajoce if cakajoce_bolnisnica else 0
            st_izvajalcev_zdravstveni_dom = cakajoce_zdravstveni_dom.stevilo_cakajoce if cakajoce_zdravstveni_dom else 0
            st_izvajalcev_zasebnik = cakajoce_zasebnik.stevilo_cakajoce if cakajoce_zasebnik else 0

            st_izvajalcev_bolnisnica_nad_dopustno = cakajoce_bolnisnica.stevilo_cakajoce_nad_dopustno if cakajoce_bolnisnica else 0
            st_izvajalcev_zdravstveni_dom_nad_dopustno = cakajoce_zdravstveni_dom.stevilo_cakajoce_nad_dopustno if cakajoce_zdravstveni_dom else 0
            st_izvajalcev_zasebnik_nad_dopustno = cakajoce_zasebnik.stevilo_cakajoce_nad_dopustno if cakajoce_zasebnik else 0

            return JsonResponse({
                'st_izvajalcev_bolnisnica': st_izvajalcev_bolnisnica,
                'st_izvajalcev_zdravstveni_dom': st_izvajalcev_zdravstveni_dom,
                'st_izvajalcev_zasebnik': st_izvajalcev_zasebnik,
                'st_izvajalcev_bolnisnica_nad_dopustno': st_izvajalcev_bolnisnica_nad_dopustno,
                'st_izvajalcev_zdravstveni_dom_nad_dopustno': st_izvajalcev_zdravstveni_dom_nad_dopustno,
                'st_izvajalcev_zasebnik_nad_dopustno': st_izvajalcev_zasebnik_nad_dopustno,
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Invalid request method"}, status=400)


