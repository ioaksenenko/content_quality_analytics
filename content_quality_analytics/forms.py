from django import forms


class UploadFileForm(forms.Form):
    zip_file = forms.FileInput()
    # html_files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))


class Analyze(forms.Form):
    checkbox = forms.CheckboxInput()