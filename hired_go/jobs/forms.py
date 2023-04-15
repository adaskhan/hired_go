from django import forms
from .models import Vacancy, VacancyType, TechStack


class VacancyForm(forms.ModelForm):
    vacancy_type = forms.ChoiceField(choices=[(e.value, e.name) for e in VacancyType])
    tech_stack = forms.ChoiceField(choices=[(e.value, e.name) for e in TechStack])
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(VacancyForm, self).__init__(*args, **kwargs)

        if self.user and not self.user.is_superuser:
            self.fields['company_name'].disabled = True

    class Meta:
        model = Vacancy
        fields = ['title', 'vacancy_type', 'company_name', 'salary', 'company_logo', 'description',
                  'experience', 'location', 'skills', 'tech_stack', 'start_date', 'end_date']
        widgets = {
            'company_logo': forms.ClearableFileInput(attrs={'multiple': False}),
        }
