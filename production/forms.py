from django import forms
from .models import Part, UAV

class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ['uav_type', 'serial_number']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class UAVForm(forms.ModelForm):
    class Meta:
        model = UAV
        fields = ['type', 'serial_number', 'wing', 'body', 'tail', 'avionics']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        
        # Filter only unused parts
        self.fields['wing'].queryset = Part.objects.filter(type='wing', is_used=False)
        self.fields['body'].queryset = Part.objects.filter(type='body', is_used=False)
        self.fields['tail'].queryset = Part.objects.filter(type='tail', is_used=False)
        self.fields['avionics'].queryset = Part.objects.filter(type='avionics', is_used=False)
