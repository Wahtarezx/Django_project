from django import forms
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ValidationError


class UserBioForm(forms.Form):
    name = forms.CharField()
    age = forms.IntegerField(label='Your age: ')
    bio = forms.CharField(label='Biography: ', widget=forms.Textarea)


def validate_file_name(file: InMemoryUploadedFile) -> None:
    if file.name and 'virus' in file.name.lower():
        raise ValidationError('File name should not contain word "virus"')


class UploadFileForm(forms.Form):
    file = forms.FileField(
        validators=[validate_file_name]
    )
