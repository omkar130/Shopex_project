from django import forms
from .models import Account, UserProfile

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Enter Password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Confirm Password'
    }))

    class Meta:
        model = Account
        fields = ['first_name','last_name','phone_number','email','password']

    def __init__(self,*args,**kwrgs):
        super(RegistrationForm,self).__init__(*args,**kwrgs)
        self.fields['first_name'].widget.attrs['placeholder']='Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder']='Enter Last Name'
        self.fields['email'].widget.attrs['placeholder']='Enter Email'
        self.fields['phone_number'].widget.attrs['placeholder']='Enter Phone Number'
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'        #this one to apply to all the fields so that 'form-control' class styling will get apply to all fields in html




    def clean(self):
        cleaned_data = super(RegistrationForm,self).clean()                 # calls the clean method of RegistrationForm parent
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                "Password Does Not Match"
            )



class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number']

    def __init__(self,*args,**kwrgs):
        super(UserForm,self).__init__(*args,**kwrgs)
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['address', 'city', 'country', 'profile_pic']

    def __init__(self,*args,**kwrgs):
        super(UserProfileForm,self).__init__(*args,**kwrgs)
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'
