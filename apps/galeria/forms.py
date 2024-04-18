from django import forms

from apps.galeria.models import Fotografia

class NovaImagemForm(forms.ModelForm):
    class Meta:
        model = Fotografia
        exclude = ['publicada',]
        widgets = {
            'nome' : forms.TextInput(attrs={'class' : 'form-control'}),
            'legenda' : forms.TextInput(attrs={'class' : 'form-control'}),
            'categoria' : forms.Select(attrs={'class' : 'form-control'}),
            'descricao' : forms.Textarea(attrs={'class' : 'form-control'}),
            'foto' : forms.FileInput(attrs={'class' : 'form-control'}),
            'data_fotografia' : forms.DateInput(
                attrs={
                    'type' : 'date',
                    'class' : 'form-control',
                },
                format = '%d/%m/%Y',
            ),
            'usuario' : forms.Select(attrs={'class' : 'form-control'}),
        }
