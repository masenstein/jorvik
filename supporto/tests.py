import datetime
import os
import tempfile

from unittest import skipIf
from unittest.mock import patch
from zipfile import ZipFile
from django.contrib.auth.tokens import default_token_generator
import django.core.files
from django.core import mail
from django.core.files.temp import NamedTemporaryFile
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.encoding import force_bytes, force_text
from django.utils.timezone import now
from django.utils.http import urlsafe_base64_encode
from splinter.exceptions import ElementDoesNotExist

from anagrafica.permessi.applicazioni import UFFICIO_SOCI, UFFICIO_SOCI_UNITA
from articoli.models import Articolo
from anagrafica.models import Persona, Delega, Appartenenza
from attivita.models import Area, Attivita
from autenticazione.utils_test import TestFunzionale
from base.files import Zip
from base.geo import Locazione
from base.stringhe import normalizza_nome
from base.utils import UpperCaseCharField, poco_fa, TitleCharField, mezzanotte_24, mezzanotte_24_ieri, mezzanotte_00
from base.utils_tests import crea_appartenenza, crea_persona_sede_appartenenza, crea_persona, crea_area_attivita, crea_utenza, \
    email_fittizzia, crea_sede
from curriculum.models import Titolo
from formazione.models import CorsoBase, Aspirante
from gestione_file.models import Documento
from jorvik.settings import GOOGLE_KEY
from filer.models import Folder
from filer.tests import create_image
from supporto.forms import ModuloRichiestaTicket, ModuloRichiestaTicketPersone
from supporto.costanti import *
from supporto.services import KayakoRESTService
from supporto.models import KBCache

class TestSupporto(TestCase):

    def test_ricerca_articoli_kb(self):

        KBCache.objects.update_or_create(articleid=1, defaults={
            'contents': 'contenutopresente di test',
            'contentstext': 'contenutopresente di test',
            'subject': 'oggetto di test',
            'dateline': datetime.datetime.now(),
            'attachments': '',
            'lastupdate': datetime.datetime.now()})

        KBCache.objects.update_or_create(articleid=2, defaults={
            'contents': 'contenuto di test 2',
            'contentstext': 'contenutsastext di test 2',
            'subject': 'contenutopresente di test 2',
            'dateline': datetime.datetime.now(),
            'attachments': '',
            'lastupdate': datetime.datetime.now()})


        lista_articoli_trovato = KBCache.cerca_articoli('contenutopresente')
        lista_articoli_non_trovato = KBCache.cerca_articoli('contenutononpresente')

        self.assertTrue(len(lista_articoli_trovato)==2, 'La KB non recupera correttamente gli articoli specificando una keyword')
        self.assertTrue(len(lista_articoli_non_trovato)==0, 'Ricerca per parola chiave non presente non andata a buon fine')

    def test_verifica_contatori_ticket(self):

        #email = email_fittizzia()
        email = 'massimo.carbone@gmail.com'

        liste = KayakoRESTService(email).listeTicket(email)

        self.assertTrue(3 == len(liste), 'Non sono presenti tutte le liste di ticket: attesa_risposta, in_lavorazione, chiusi')

        attesa_risposta = KayakoRESTService(email).get_ticketListByStatus(KayakoRESTService(email).get_departments_ids(),
                                                                          [TICKET_ATTESA_RISPOSTA],
                                                                                              KayakoRESTService(email).get_userIdByEmail(
                                                                                                  email))

        in_lavorazione = KayakoRESTService(email).get_ticketListByStatus(KayakoRESTService(email).get_departments_ids(),
                                                                          [TICKET_IN_LAVORAZIONE, TICKET_APERTO],
                                                                          KayakoRESTService(email).get_userIdByEmail(
                                                                              email))

        chiusi = KayakoRESTService(email).get_ticketListByStatus(KayakoRESTService(email).get_departments_ids(),
                                                                          [TICKET_CHIUSO],
                                                                          KayakoRESTService(email).get_userIdByEmail(
                                                                              email))

        self.assertTrue(len(attesa_risposta) == liste[0][1], 'Il numero di ticket in attesa_risposta non coincide con i contatori dei ticket')
        self.assertTrue(len(in_lavorazione) == liste[1][1], 'Il numero di ticket in in_lavorazione non coincide con i contatori dei ticket')
        self.assertTrue(len(chiusi) == liste[2][1], 'Il numero di ticket in chiusi non coincide con i contatori dei ticket')




@skipIf(True,'Nessun test funzionale eseguito per la sezione supporto')
class TestFunzionaleSupporto(TestFunzionale):

    def test_richiesta_supporto(self):
        presidente = crea_persona()
        persona_normale, sede, app = crea_persona_sede_appartenenza(presidente=presidente)
        persona_us = crea_persona()
        persona_us_territoriale = crea_persona()
        crea_appartenenza(persona_us, sede)
        crea_appartenenza(persona_us_territoriale, sede)
        crea_utenza(presidente, email='massimo.carbone@gmail.com')
        crea_utenza(persona_normale, email=email_fittizzia())
        crea_utenza(persona_us, email=email_fittizzia())
        crea_utenza(persona_us_territoriale, email=email_fittizzia())

        Delega.objects.create(
            inizio="1980-12-10",
            persona=persona_us,
            tipo=UFFICIO_SOCI,
            oggetto=sede
        )
        Delega.objects.create(
            inizio="1980-12-10",
            persona=persona_us_territoriale,
            tipo=UFFICIO_SOCI_UNITA,
            oggetto=sede
        )

        # Utente normale senza persone
        ##sessione_normale = self.sessione_utente(persona=persona_normale)
        ##sessione_normale.visit("%s/supporto/nuova_richiesta/" % self.live_server_url)
        ##sessione_normale.is_text_not_present('Seleziona le persone per cui si richiede assistenza.')
        # seleziona l'option SANGUE
        # inserisci Oggetto
        # inserisci Descrizione
        # click sul pulsante Crea Ticket
        # recupero display ID del ticket creato
        # recupero via API rest dei dettagli del ticket creato
        # verifica uguaglianza campo oggetto
        # verifica uguaglianza campo descrizione

        # Utente US con persone
        ##sessione = self.sessione_utente(persona=persona_us)
        ##sessione.visit("%s/supporto/nuova_richiesta/" % self.live_server_url)
        ##sessione.is_text_present('Seleziona le persone per cui si richiede assistenza.')

        # Utente US con persone
        ##sessione = self.sessione_utente(persona=persona_us_territoriale)
        ##sessione.visit("%s/supporto/nuova_richiesta/" % self.live_server_url)
        ##sessione.is_text_present('Seleziona le persone per cui si richiede assistenza.')

        # Presidente con persone
        ##sessione = self.sessione_utente(persona=presidente)
        ##sessione.visit("%s/supporto/nuova_richiesta/" % self.live_server_url)
        ##sessione.is_text_present('Seleziona le persone per cui si richiede assistenza.')

        # Invio form persona normale
        self.client.login(username=presidente.utenza.email, password='prova')
        dati = {
            'oggetto': 'Oggetto',
            'descrizione': 'Descrizione',
            'tipo': SEZ_INC,
        }
        self.client.post('/supporto/nuova_richiesta/', data=dati)


        # Invio form con selezione persone
