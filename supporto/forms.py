from django import forms
from django.forms import Textarea
from autocomplete_light import shortcuts as autocomplete_light

from supporto.costanti import *
from supporto.validators import valida_dimensione_file_2mb


class ModuloSceltaDipartimentoTicket(forms.Form):
    dipartimento = forms.ChoiceField(widget=forms.RadioSelect, initial=None,
                                     help_text="Seleziona un dipartimento per aiutarci a smistare la richiesta rapidamente.")


class ModuloRicercaInKnowledgeBase(forms.Form):
    cerca = forms.CharField(min_length=3, label='', widget=forms.TextInput(
        attrs={'placeholder': 'Es: reset password, richiesta trasferimento...'}))


class ModuloRichiestaTicket(forms.Form):
    tipo = forms.ChoiceField(TIPO_RICHIESTA, required=True, initial=None,
                             help_text="Seleziona una delle tipologie di richiesta "
                                       "per aiutarci a smistarla rapidamente.")
    oggetto = forms.CharField(help_text="Una breve descrizione del problema.", min_length=3, max_length=150)
    descrizione = forms.CharField(widget=Textarea, min_length=3)
    allegato = forms.FileField(required=False, validators=[valida_dimensione_file_2mb])

    field_order = ('tipo', 'oggetto', 'descrizione', 'allegato')


class ModuloPostTicket(forms.Form):
    descrizione = forms.CharField(
        widget=Textarea(attrs={'rows': 3, 'cols': 15, 'placeholder': 'Scrivi un commento...'}), min_length=3, label='')
    allegato = forms.FileField(required=False, validators=[valida_dimensione_file_2mb])


class ModuloRichiestaTicketPersone(ModuloRichiestaTicket):
    persona = autocomplete_light.ModelChoiceField(
        "PersonaAutocompletamento", help_text="Seleziona la persona per cui si richiede assistenza."
                                              "Nel caso la problematica impattasse più persone è necessario "
                                              "aprire una segnalazione per ogni persona ",
        required=False
    )

    field_order = ('tipo', 'dipartimentoID', 'oggetto', 'persona', 'descrizione', 'allegato')
