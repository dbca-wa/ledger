from django import forms
from oscar.apps.dashboard.catalogue.forms import ProductForm as CoreProductForm
from ledger.catalogue.models import Product

class ProductForm(CoreProductForm):
    
    class Meta:
        model = Product
        fields = [
            'title','upc','oracle_code','description','is_discountable','structure'
        ]
        widgets = {
            'structure': forms.HiddenInput()
        }
        