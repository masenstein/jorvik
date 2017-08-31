from django import forms
from django.forms import Textarea
from autocomplete_light import shortcuts as autocomplete_light
from anagrafica.validators import valida_dimensione_file_5mb

class ModuloSceltaDipartimentoTicket(forms.Form):

    dipartimento = forms.ChoiceField(widget=forms.RadioSelect, initial=None,help_text="Seleziona un dipartimento per aiutarci a smistare la richiesta rapidamente.")

class ModuloRicercaInKnowledgeBase(forms.Form):

    cerca = forms.CharField(min_length=3,label='Cerca nella knowledge base', widget= forms.TextInput(attrs={'placeholder':'Come possiamo aiutarti?'}))


class ModuloRichiestaTicket(forms.Form):
    oggetto = forms.CharField(help_text="Una breve descrizione del problema.", min_length=3, max_length=150)
    descrizione = forms.CharField(widget=Textarea, min_length=3)
    #fixme verificare il controllo sulla dimensione massima del file
    allegato = forms.FileField(required=False, validators=[valida_dimensione_file_5mb])


class ModuloPostTicket(forms.Form):

    descrizione = forms.CharField(widget=Textarea, min_length=3)
    #fixme verificare il controllo sulla dimensione massima del file
    allegato = forms.FileField(required=False, validators=[valida_dimensione_file_5mb])


class ModuloRichiestaTicketPersone(ModuloRichiestaTicket):
    persona = autocomplete_light.ModelChoiceField(
        "PersonaAutocompletamento", help_text="Seleziona la persona per cui si richiede assistenza."
                                              "Nel caso la problematica impattasse più persone è necessario "
                                              "aprire una segnalazione per ogni persona ",
        required=False
    )

    field_order = ('dipartimentoID', 'oggetto', 'persona', 'descrizione','allegato')