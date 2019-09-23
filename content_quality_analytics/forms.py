from django import forms


class UploadFileForm(forms.Form):
    forms.FileInput()


class Join(forms.Form):
    checkbox = forms.CheckboxInput()
    input = forms.TextInput()


class Analyze(forms.Form):
    checkbox = forms.CheckboxInput()
