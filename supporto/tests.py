import datetime
from django.test import TestCase
from anagrafica.models import Delega
from anagrafica.permessi.applicazioni import UFFICIO_SOCI, UFFICIO_SOCI_UNITA
from autenticazione.utils_test import TestFunzionale
from base.utils_tests import crea_appartenenza, crea_persona_sede_appartenenza, crea_persona, crea_utenza, \
    email_fittizzia
from supporto.costanti import *
from supporto.models import KBCache
from supporto.services import KayakoRESTService

class TestSupporto(TestCase):

    def test_create_ticket(self):
        email = email_fittizzia()

        #creo il ticket
        ticketID, ticketPostID, ticketDisplayID = KayakoRESTService(email).createTicket(mittente="Nome Cognome",
                                                                                           subject="Ticket test",
                                                                                           fullname="Nome Cognome",
                                                                                           email=email,
                                                                                           contents="Descrizione test",
                                                                                           department_id="137",
                                                                                           persona=None)

        self.assertTrue(int(ticketID) > 0, "Ticket non creato su Kayako")

        #recupero il dettaglio del ticket
        ticket = KayakoRESTService(email).get_ticketLightByDisplayID(ticketDisplayID)
        self.assertTrue(email ==  ticket.email, "Email nel dettaglio ticket non coincide con il ticket creato")
        self.assertTrue(ticketID ==  ticket.id, "Id nel dettaglio ticket non coincide con il ticket creato")

        #aggiungo un allegato al ticket appena creato
        KayakoRESTService(email).addTicketAttachment(ticketID, ticketPostID,
                                                     "file_test.txt",
                                                     "YWxsZWdhdG8gZGkgdGVzdA==")

        lista_allegati = KayakoRESTService(email).getTicketAttachments(ticketID)

        self.assertTrue(len(lista_allegati) == 1)

        #aggiungo un commento al ticket
        KayakoRESTService(email).createTicketPost(email, ticket.id,
                                                  "commento di test",
                                                  "file_test_2.txt",
                                                  "YWxsZWdhdG8gZGkgdGVzdA==")

        #chiudo il ticket
        KayakoRESTService().chiudiTicket(ticket.id)


        ticket_item = KayakoRESTService(email).get_ticketByDisplayID(ticketDisplayID)

        self.assertTrue(len(ticket_item.ticketPostItemList) == 2, "Commenti non presenti nel ticket creato")



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


        ticket_item_2 = KayakoRESTService(email).get_ticketByDisplayID(ticketDisplayID)
        self.assertTrue(int(ticket_item_2.statusid) == TICKET_CHIUSO, "Ticket non chiuso")

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






class TestFunzionaleSupporto(TestFunzionale):

    def test_crea_ticket_con_commento_e_chiudi(self):
        import time

        presidente = crea_persona()
        persona_normale, sede, app = crea_persona_sede_appartenenza(presidente=presidente)
        persona_us = crea_persona()
        persona_us_territoriale = crea_persona()
        crea_appartenenza(persona_us, sede)
        crea_appartenenza(persona_us_territoriale, sede)
        crea_utenza(presidente, email=email_fittizzia())
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

        # Creazione ticket con Persona
        # seleziona l'option INF
        sessione = self.sessione_utente(persona=persona_us)
        sessione.visit("%s/ticket/nuova_richiesta/" % self.live_server_url)
        sessione.is_text_present('Seleziona la persona per cui si richiede assistenza.')
        sessione.find_option_by_value("INF").first.click()
        sessione.fill('oggetto', 'Oggettoditest')
        sessione.fill('descrizione', 'Descrizione')

        sessione.type('persona-autocomplete', persona_normale.nome)
        time.sleep(1.5)
        sessione.find_by_xpath("//span[@data-value='%d']" % persona_normale.pk).first.click()
        sessione.find_by_xpath("//button[@type='submit']").first.click()
        self.assertTrue(sessione.is_text_present('Richiesta inoltrata'))
        # aggiunta commento al ticket
        sessione.find_by_xpath('//a[@id="ticketDisplayID"]').click()
        sessione.fill('descrizione', 'Descrizione commento')
        sessione.find_by_xpath("//button[@type='submit']").first.click()
        sessione.is_text_present('Descrizione commento')

        # chiudo il ticket
        sessione.find_by_xpath("//div[contains(@class, 'panel-info')]//a[contains(@class, 'btn-primary')]").first.click()
        alert = sessione.driver.switch_to_alert()
        alert.accept()
        self.assertEqual(sessione.find_by_xpath('//td[.="Stato"]/following-sibling::td[1]').value, "Chiuso")

        # Utente normale senza persone
        sessione_normale = self.sessione_utente(persona=persona_normale)
        sessione_normale.visit("%s/ticket/nuova_richiesta/" % self.live_server_url)
        sessione_normale.is_text_not_present('Seleziona la persona per cui si richiede assistenza.')
        # seleziona l'option INF
        sessione_normale.find_option_by_value("INF").first.click()
        sessione_normale.fill('oggetto', 'Oggettoditest')
        sessione_normale.fill('descrizione', 'Descrizione')
        sessione_normale.find_by_xpath('//button[@type="submit"]').click()
        self.assertTrue(sessione_normale.is_text_present('Richiesta inoltrata'))
        # recupero display ID del ticket creato
        sessione_normale.find_by_xpath('//a[@id="ticketDisplayID"]').click()
        self.assertTrue("Oggettoditest" in sessione_normale.find_by_xpath('//td[.="Oggetto:  Oggettoditest"]').value)
        self.assertEqual(sessione_normale.find_by_xpath('//td[.="Stato"]/following-sibling::td[1]').value, "Aperto")        
        

        # Utente US con persone
        sessione = self.sessione_utente(persona=persona_us)
        sessione.visit("%s/ticket/nuova_richiesta/" % self.live_server_url)
        sessione.is_text_present('Seleziona la persona per cui si richiede assistenza.')

        # Utente US con persone
        sessione = self.sessione_utente(persona=persona_us_territoriale)
        sessione.visit("%s/ticket/nuova_richiesta/" % self.live_server_url)
        sessione.is_text_present('Seleziona la persona per cui si richiede assistenza.')

        # Presidente con persone
        sessione = self.sessione_utente(persona=presidente)
        sessione.visit("%s/ticket/nuova_richiesta/" % self.live_server_url)
        sessione.is_text_present('Seleziona la persona per cui si richiede assistenza.')
