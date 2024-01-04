import json
import uuid
from django.forms import model_to_dict
from django.shortcuts import render
import pandas as pd
from django.http import HttpResponse
from qaddress.forms import AddressForm
from django.contrib.auth.mixins import LoginRequiredMixin
from qaddress.utils import truncate_tables
from .models import Address, DistrictData, CountyData, CPData
from django.db import transaction

# Create your views here.
from django.http import JsonResponse
from django.views import View
from .models import CPData

from django.shortcuts import render
from django.views import View


class AddressJsonView(LoginRequiredMixin, View):
    form_class = AddressForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            new_address = form.save(commit=False)
            new_address.project = kwargs.get('project')
            new_address.app = kwargs.get('app')
            new_address.model = kwargs.get('model')
            new_address.save()
            data = str(new_address.token)
            return HttpResponse(json.dumps( data, ensure_ascii=False), content_type="application/json")
        else:
            return HttpResponse(json.dumps({'error':form.errors}, ensure_ascii=False), content_type="application/json")
        
class AddressView(LoginRequiredMixin, View):
    form_class = AddressForm

    def get_context_data(self, **kwargs):
        context = {'base_template': self.base_template}
        return context
    
    def get_form(self):
        return self.form_class()

    def get_template_name(self):
        return self.template_name

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        context = self.get_context_data()
        context['form'] = form
        return render(request, self.get_template_name(), context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            new_address = form.save(commit=False)
            new_address.project = "QIMOB"
            new_address.app = "crm"
            new_address.model = "client" 
            new_address.save()
            return {'success':str(new_address.token)}
        else:
            return {'error':form.errors}

class PostalCodeView(View):

    def get(self, request, *args, **kwargs):
        return render(request, "postal_code.html")
    
    def post(self, request, *args, **kwargs):
        cp3 = request.POST.get('cp3', None)
        cp4 = request.POST.get('cp4', None)

        cp_data = CPData.objects.filter(CP3=cp3, CP4=cp4)

        if not cp_data.exists():
            return JsonResponse({'error': 'No data found for this postal code'}, status=404)

        cp_data_list = list(cp_data.values('DD__DESIG', 'CC__DESIG', 'LLLL', 'LOCALIDADE', 'ART_COD', 'ART_TIPO', 'PRI_PREP', 'ART_TITULO', 'SEG_PREP', 'ART_DESIG', 'ART_LOCAL', 'TROÇO', 'PORTA', 'CLIENTE', 'CP4', 'CP3', 'CPALF'))

        art_tipo_art_desig = list(f"{d['ART_TIPO']} {d['ART_DESIG']}" for d in cp_data_list)

        data = {key: cp_data_list[0][key] for key in ['CP4', 'CP3', 'DD__DESIG', 'CC__DESIG', 'LOCALIDADE']}

        data["ART_TIPO_ART_DESIG"] = art_tipo_art_desig

        return data
    
class PostalCodeJsonView(View):

    def get(self, request, *args, **kwargs):
        return render(request, "postal_code.html")
    
    def post(self, request, *args, **kwargs):
        cp3 = request.POST.get('cp3', None)
        cp4 = request.POST.get('cp4', None)

        cp_data = CPData.objects.filter(CP3=cp3, CP4=cp4)

        if not cp_data.exists():
            return JsonResponse({'error': {'postal_code': ['No data found for this postal code']}}, status=200)

        cp_data_list = list(cp_data.values('DD__DESIG', 'CC__DESIG', 'LLLL', 'LOCALIDADE', 'ART_COD', 'ART_TIPO', 'PRI_PREP', 'ART_TITULO', 'SEG_PREP', 'ART_DESIG', 'ART_LOCAL', 'TROÇO', 'PORTA', 'CLIENTE', 'CP4', 'CP3', 'CPALF'))

        art_tipo_art_desig = list(f"{d['ART_TIPO']} {d['ART_DESIG']}" for d in cp_data_list)

        data = {key: cp_data_list[0][key] for key in ['CP4', 'CP3', 'DD__DESIG', 'CC__DESIG', 'LOCALIDADE']}

        data["ART_TIPO_ART_DESIG"] = art_tipo_art_desig

        data['success'] = ["Postal code found"]

        return JsonResponse(data, safe=False)

class updateAddressDataByToken(View):
    
    def post(self, request, *args, **kwargs):
        token = request.POST.get('token', None)
        try:
            uuid_token = uuid.UUID(token)
        except ValueError:
            return {'error': 'Invalid token format'}
        address_data = Address.objects.get(token=uuid_token)
        if not address_data:
            return {'error': 'No data found for this token'}
        form = AddressForm(data=request.POST, instance=address_data)
        if form.is_valid():
            new_address = form.save(commit=False)
            new_address.project = "QIMOB"
            new_address.app = "crm"
            new_address.model = "client" 
            new_address.save()
            return JsonResponse({'success': str(new_address.token)}, status=200)
        else:
            return JsonResponse({'error': form.errors}, status=400)
                 
class retrieveAddressDataByToken(View):
    def get(self, request, *args, **kwargs):
        tokens = kwargs.get('tokens', None)
        uuid_tokens = []
        for token in tokens:
            try:
                uuid_token = uuid.UUID(token)
            except ValueError:
                return {'error': 'Invalid token format'}
            uuid_tokens.append(uuid_token)   
        address_data = Address.objects.filter(token__in=uuid_tokens)
        if not address_data.exists():
            return {'error': 'No data found for this token'}
        address_data_list = [model_to_dict(addr) for addr in address_data]
        for addr_dict, addr in zip(address_data_list, address_data):
            addr_dict['token'] = str(addr.token)
        return{'success': address_data_list}

# Data Import Views  
def render_import_data_upload_page(request):
    if request.method == 'POST':
        #return import_data(request)
        return import_data_bulk(request)
    elif request.method == 'GET':
        return render(request, "import.html")

@transaction.atomic
def import_data_bulk(request):

    # Clean tables.
    truncate_tables()

    # Define the columns of the files.
    district_columns = ['DD', 'DESIG']
    county_columns = ['DD', 'CC', 'DESIG']
    cp_columns = ['DD', 'CC', 'LLLL', 'LOCALIDADE', 'ART_COD', 'ART_TIPO', 'PRI_PREP', 'ART_TITULO', 'SEG_PREP', 'ART_DESIG', 'ART_LOCAL', 'TROÇO', 'PORTA', 'CLIENTE', 'CP4', 'CP3', 'CPALF']

    # Get the files from the request.
    district_file = request.FILES['district_data']
    county_file = request.FILES['county_data']
    cp_file = request.FILES['cp_data']

    # Read the files with pandas (https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)
    # Leading and trailing spaces are removed from column names when read_csv is used with sep=';'. (https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)
    # Encoding is set to ISO-8859-1 because the files have special characters. (https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)
    # Low memory is set to False because the files have more than 1000 columns. (https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)
    # DD, CC, LLLL, CP4 and CP3 are set to str because they are not numeric. (https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)
    district_data = pd.read_csv(district_file, sep=';', names=district_columns, encoding='ISO-8859-1', low_memory=False, dtype={'DD': str})
    county_data = pd.read_csv(county_file, sep=';', names=county_columns, encoding='ISO-8859-1', low_memory=False, dtype={'DD': str, 'CC': str})
    cp_data = pd.read_csv(cp_file, sep=';', names=cp_columns, encoding='ISO-8859-1', low_memory=False, dtype={'DD': str, 'CC': str, 'LLLL': str, 'CP4': str, 'CP3': str})
        
    # Import the data into the Django models (Pandas iterrows(https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.iterrows.html))
    # Python list comprehension that creates a list of DistrictData/CountyData objects.
    # Bulk create the objects
    district_objs = [DistrictData(DD=row['DD'], DESIG=row['DESIG']) for index, row in district_data.iterrows()]
    DistrictData.objects.bulk_create(district_objs)

    county_objs = [CountyData(DD=DistrictData.objects.get(DD=row['DD']), CC=row['CC'], DESIG=row['DESIG']) for index, row in county_data.iterrows()]
    CountyData.objects.bulk_create(county_objs)

    # Python Dict with all data of district and county based on their relation. (Faster Approuch)
    district_dict = {obj.DD: obj for obj in DistrictData.objects.all()}
    county_dict = {(obj.DD.DD, obj.CC): obj for obj in CountyData.objects.all()}

    cp_objs = []
    
    # Split the data insertion by batch size (Faster Approuch)
    batch_size = 1000
    
    for index, row in cp_data.iterrows():
        cp_objs.append(CPData(
            DD=district_dict[str(row['DD'])],
            CC=county_dict[(str(row['DD']), str(row['CC']))],
            LLLL=row['LLLL'],
            LOCALIDADE=row['LOCALIDADE'],
            ART_COD=row['ART_COD'],
            ART_TIPO=row['ART_TIPO'],
            PRI_PREP=row['PRI_PREP'],
            ART_TITULO=row['ART_TITULO'],
            SEG_PREP=row['SEG_PREP'],
            ART_DESIG=row['ART_DESIG'],
            ART_LOCAL=row['ART_LOCAL'],
            TROÇO=row['TROÇO'],
            PORTA=row['PORTA'],
            CLIENTE=row['CLIENTE'],
            CP4=row['CP4'],
            CP3=row['CP3'],
            CPALF=row['CPALF']
        ))
        if (index + 1) % batch_size == 0:
            CPData.objects.bulk_create(cp_objs)
            cp_objs = []
    if cp_objs: # Check if there is data to be saved.
        CPData.objects.bulk_create(cp_objs) 
    return HttpResponse("Data imported successfully")
    



