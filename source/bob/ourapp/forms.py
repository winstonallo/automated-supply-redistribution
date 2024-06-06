from django import forms
from django.core.exceptions import ValidationError
from .models import Store  # assuming you have a Store model

class StoreForm(forms.Form):
    store_id = forms.IntegerField(
        label='Enter your store ID', 
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    def clean_store_id(self):
        print(self.cleaned_data['store_id'])
        store_id = self.cleaned_data['store_id']
        print(store_id)
        if not Store.objects.filter(id=store_id).exists():
            raise forms.ValidationError('Store with this ID does not exist')
        return store_id