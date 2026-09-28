from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Bed, Layout, Plant, PlantPlacement, Plot


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'input'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'input'})
        self.fields['password2'].widget.attrs.update({'class': 'input'})


class PlotForm(forms.ModelForm):
    class Meta:
        model = Plot
        fields = ('name', 'width_ft', 'length_ft')
        labels = {
            'name': 'Plot name',
            'width_ft': 'Width (ft)',
            'length_ft': 'Length (ft)',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Backyard beds'}),
            'width_ft': forms.NumberInput(attrs={'class': 'input', 'step': '0.5', 'min': '1'}),
            'length_ft': forms.NumberInput(attrs={'class': 'input', 'step': '0.5', 'min': '1'}),
        }


class LayoutForm(forms.ModelForm):
    class Meta:
        model = Layout
        fields = ('name', 'plot', 'notes')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Spring 2026'}),
            'plot': forms.Select(attrs={'class': 'input'}),
            'notes': forms.Textarea(attrs={'class': 'input', 'rows': 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['plot'].queryset = Plot.objects.filter(user=user)
            self.fields['plot'].required = False


class BedForm(forms.ModelForm):
    class Meta:
        model = Bed
        fields = ('name', 'width_ft', 'length_ft', 'x_ft', 'y_ft')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input', 'placeholder': 'North bed'}),
            'width_ft': forms.NumberInput(attrs={'class': 'input', 'step': '0.5', 'min': '1'}),
            'length_ft': forms.NumberInput(attrs={'class': 'input', 'step': '0.5', 'min': '1'}),
            'x_ft': forms.NumberInput(attrs={'class': 'input', 'step': '0.5', 'min': '0'}),
            'y_ft': forms.NumberInput(attrs={'class': 'input', 'step': '0.5', 'min': '0'}),
        }


class PlacementForm(forms.ModelForm):
    class Meta:
        model = PlantPlacement
        fields = ('plant', 'quantity', 'x_ft', 'y_ft')
        widgets = {
            'plant': forms.Select(attrs={'class': 'input'}),
            'quantity': forms.NumberInput(attrs={'class': 'input', 'min': '1'}),
            'x_ft': forms.NumberInput(attrs={'class': 'input', 'step': '0.25', 'min': '0'}),
            'y_ft': forms.NumberInput(attrs={'class': 'input', 'step': '0.25', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['plant'].queryset = Plant.objects.all()


class SuggestForm(forms.Form):
    plants = forms.ModelMultipleChoiceField(
        queryset=Plant.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        help_text='Pick crops to place. Suggestions respect spacing and companions.',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['plants'].queryset = Plant.objects.all()
