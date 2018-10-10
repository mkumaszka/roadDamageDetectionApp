from django import forms


class ImageUploadForm(forms.Form):
    """Image upload form."""
    image = forms.ImageField()


class FileUploadForm(forms.Form):
    """File upload form."""
    file = forms.FileField()


