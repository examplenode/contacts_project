import re
from django import forms
from .models import Contact
    
class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label="Имя")
    phone = forms.CharField(max_length=20, label="Телефон")
    email = forms.EmailField(label="Email")
    category = forms.ChoiceField(
        choices=[("Работа", "Работа"), ("Дом", "Дом"), ("Друзья", "Друзья")],
        label="Категория",
    )

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if not re.match(r"^\+?[\d\s\-()]{7,20}$", phone):
            raise forms.ValidationError("Некорректный номер телефона")
        return phone

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if len(name) < 2:
            raise forms.ValidationError("Имя слишком короткое")
        return name
class ContactModelForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ["name", "phone", "email", "category"]

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if not re.match(r"^\+?[\d\s\-()]{7,20}$", phone):
            raise forms.ValidationError("Некорректный номер телефона")
        return phone

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if len(name) < 2:
            raise forms.ValidationError("Имя слишком короткое")
        return name