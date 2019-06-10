from django import forms
from classAvailable.models import Reservation, Classroom


class loginForm(forms.Form):
    auto_id=False

    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Kullanıcı Adın',}),max_length=100,required=True,label='')
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Şifren'}),label='')


TYPECHOICES=[('1','Sınav'),('2','Etkinlik')]
SELECTIONTYPE=[('1','Saat Ver'),('2','Zaman Aralığı Ver')]

class resForm(forms.Form):
    auto_id=False

    desc=forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Açıklama', 'class':'inputField form-control','id':'descInput'}),max_length=350,required=True,label='')
    type=forms.ChoiceField(widget=forms.RadioSelect(attrs={'class':'inputField ','id':'typeInput'}),choices=TYPECHOICES,required=True,label='Etkinlik Türü')
    capacity=forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder':'Kişi Sayısı','class':'inputField form-control','id':'capInput'}),min_value=6,label='')
    pref_class=forms.ModelMultipleChoiceField(queryset=Classroom.objects.all().order_by('name'),required=False,widget=forms.SelectMultiple(attrs={'class':'inputField form-control','id':'schoolSelect'}),label='')
    instructor=forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Etkinlik sahibi (Birden çoksa: ad soyad1, ad soyad2 ...) ','class':'inputField form-control','id':'instructorInput'}),
                               max_length=1024, required=False, label='')
    proctor=forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder':'Gözetmen Sayısı','class':'inputField form-control','id':'proctorInput'}),
                               required=False, label='')
    day=forms.DateField(widget=forms.DateInput(attrs={'placeholder':'gg/aa/yyyy','class':'inputField form-control datepicker','id':'dayInput','data-provide':"datepicker"}),input_formats=['%d/%m/%Y'],required=True,label='')
    selection=forms.ChoiceField(widget=forms.RadioSelect(attrs={'class':'inputField selectRadio','id':'selectionInput'}),choices=SELECTIONTYPE,required=True,label='Rezervasyon Tercihiniz')
    start=forms.TimeField(widget=forms.TimeInput(attrs={'placeholder':'ss:dd','class':'inputField form-control timepickerM','id':'startInput'},format='%H:%M'),required=True,label='Başlangıç Saati')
    end=forms.TimeField(widget=forms.TimeInput(attrs={'placeholder':'ss:dd','class':'inputField form-control timepickerM','id':'endInput'},format='%H:%M'),required=True,label='Bitiş Saati')
    duration=forms.TimeField(widget=forms.TimeInput(attrs={'placeholder':'ss:dd','class':'inputField form-control timepicker','id':'durationInput','data-toggle':'timepicker','name':'timepicker'},format='%H:%M'),required=False,label='Etkinlik Süresi')

class resNotPreferredForm(forms.Form):
    auto_id=False
    PREF_CHOICES = [('1', 'Naber'), ('2', 'Nasılsın')]
    OTHER_CHOICES = []

    def changePrefs(self,p):
        self.fields['pr']=forms.MultipleChoiceField(required=False,widget=forms.CheckboxSelectMultiple(attrs={'class':'inputField','id':'prefSelect'}),choices=p,label='')

    def changeOthers(self,o):
        self.fields['ot']=forms.MultipleChoiceField(required=False,widget=forms.CheckboxSelectMultiple(attrs={'class':'inputField','id':'otherSelect'}),choices=o,label='')

    pr=forms.MultipleChoiceField(required=False,widget=forms.CheckboxSelectMultiple(attrs={'class':'inputField','id':'prefSelect'}),choices=PREF_CHOICES,label='')
    ot=forms.MultipleChoiceField(required=False,widget=forms.CheckboxSelectMultiple(attrs={'class':'inputField','id':'otherSelect'}),choices=OTHER_CHOICES,label='')
