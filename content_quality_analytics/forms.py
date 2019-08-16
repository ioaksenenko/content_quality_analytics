from django import forms


class UploadFileForm(forms.Form):
    file = forms.FileInput()


class Analyze(forms.Form):
    checkbox = forms.CheckboxInput()