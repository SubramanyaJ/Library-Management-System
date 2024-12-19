from django import forms
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User,LibraryUser ,Rating
from django.core.exceptions import ValidationError
# Get the custom User model

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating', 'review']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 0, 'max': 5, 'step': 1}),
            'review': forms.Textarea(attrs={'rows': 4, 'cols': 50}),
        }


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = LibraryUser
        fields = ['fav_genre']  # Exclude lib_num from editable fields



class SignUpForm(UserCreationForm):
    gmail = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-3 py-2 border rounded shadow-sm focus:outline-none focus:ring-blue-500',
            'placeholder': 'Enter your Gmail'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'gmail', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        # Add Tailwind styles to help texts
        for field_name, field in self.fields.items():
            if field.help_text:
                field.widget.attrs.update({
                    'aria-describedby': f"{field_name}_help"
                })
                field.help_text = f'<p id="{field_name}_help" class="text-sm text-gray-500 mt-1">{field.help_text}</p>'
                # Explicitly update password help texts

                
        self.fields['password1'].help_text = (
            '<p id="password1_help" class="text-sm text-gray-500 mt-1">'
            'Your password must contain at least 8 characters, including letters and numbers.'
            '</p>'
        )
      

        # Update field attributes
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border rounded shadow-sm focus:outline-none focus:ring-blue-500',
            'placeholder': 'Enter your username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border rounded shadow-sm focus:outline-none focus:ring-blue-500',
            'placeholder': 'Enter your password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border rounded shadow-sm focus:outline-none focus:ring-blue-500',
            'placeholder': 'Confirm your password'
        })


        
class BookRequestForm(forms.Form):
    title = forms.CharField(label="Book Title", max_length=100,required=False)
    author = forms.CharField(label="Author", max_length=100, required=False)
    isbn = forms.CharField(label="ISBN",max_length=13,)



class ResetPasswordForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    lib_num = forms.CharField(max_length=15, required=True)
    new_password1 = forms.CharField(widget=forms.PasswordInput, required=True)
    new_password2 = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")
        
        if password1 != password2:
            raise ValidationError("The two passwords do not match.")
        
        return cleaned_data
    

class SignInForm(forms.Form):
    username = forms.CharField(
        max_length=150, 
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border rounded shadow-sm focus:outline-none focus:ring-blue-500',
            'placeholder': 'Enter your username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border rounded shadow-sm focus:outline-none focus:ring-blue-500',
            'placeholder': 'Enter your password'
        })
    )