from django import forms

from qaddress.models import Address


class AddressForm(forms.ModelForm):
   
    class Meta:
        model = Address
        fields = ['cp4','cp3','postal_code','district','county','locality','street','number','more_info']
        required = ['cp4','cp3','postal_code','district','county','locality','street','number']
