from django.urls import include, path
from qaddress import views

app_name = "qaddress"

urlpatterns = [
    path('file/import/', views.render_import_data_upload_page, name='import-data'),
    path('postal_code/json/', views.PostalCodeJsonView.as_view(), name='postal_code_json'),
    path('address/json/', views.AddressJsonView.as_view(), name='address_json'),
    path('postal_code/', views.PostalCodeView.as_view(), name='postal_code'),
    path('address/', views.AddressJsonView.as_view(), name='address'),
    path('address/<str:token>/', views.retrieveAddressDataByToken.as_view(), name='address_by_token'),
    path('address/update/<int:pk>/', views.updateAddressDataByToken.as_view(), name='address_update_by_token'),
]