from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('home/databasetest/', views.databasetest, name='databasetest'),
    path('executors/', views.executors, name='executors'),
    path('primerjava_tipov_pregleda/', views.primerjava_tipov_pregleda, name='primerjava_tipov_pregleda'),

    path('search-vzs/', views.search_vzs, name='search_vzs'),
    path('recorded_date/', views.search_date, name='search_date'),

    path('get_data_by_date/', views.get_data_by_date, name='get_data_by_date'),

    path("get-chart-data/", views.get_chart_data, name="get_chart_data"), #funkcija za prvi graf na podstrani 1
    path('get-ena-storitev-graf2/', views.ena_storitev_graf2, name='ena_storitev_graf2'), #funkcija za drugi graf na podstrani 1
    path('get-ena-storitev-graf3/', views.ena_storitev_graf3, name='ena_storitev_graf3') , #funkcija za tretji graf na podstrani 1


    path('prestej-tipe/', views.prestej_tipe, name='prestej_tipe') , 

    path('cakajoce_po_kategorijah_nujnost/', views.cakajoce_po_kategorijah_nujnost, name='cakajoce_po_kategorijah_nujnost'),


    
    # Pot za funkcijo `po_tipih2`, ki vrača JSON podatke
    path('po_tipih2/', views.po_tipih2, name='po_tipih2'), #funkcija za drugi graf na podstrani 3

    path("get_izvajalci/", views.get_izvajalci, name="get_izvajalci"),  #funkcija za prvi graf na podstrani 3
    path('trend_nad_dop_cd_vsota/', views.trend_nad_dop_cd_vsota, name='trend_nad_dop_cd_vsota'),


path('zacetna-storitev-graf2/', views.zacetna_storitev_graf2, name='zacetna_storitev_graf2'), #funkcija za drugi graf na podstrani 1
    
]