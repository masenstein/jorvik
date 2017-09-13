from anagrafica.permessi.applicazioni import PRESIDENTE, UFFICIO_SOCI, UFFICIO_SOCI_TEMPORANEO, UFFICIO_SOCI_UNITA
from autenticazione.funzioni import pagina_privata
from base.errori import messaggio_generico, errore_generico
from supporto.costanti import *
from django.shortcuts import redirect
from supporto.utils import download_attachment, supporto_get_lista_ticket
from supporto.services import KayakoRESTService


@pagina_privata
def supporto_nuova_richiesta(request, me=None):
    """
    Carica la pagina di inserimento di un nuovo ticket in cui vengono inserite le informazioni relative alla segnalazione
    ed eventuali allegati.
    :param request:
    :param me:
    :return:
    """
    from supporto.forms import ModuloRichiestaTicket,ModuloRichiestaTicketPersone
    modulo = None


    if me:
        from base.utils import rimuovi_scelte

        deleghe = set([d.tipo for d in me.deleghe_attuali()])
        tipi = set((UFFICIO_SOCI, UFFICIO_SOCI_TEMPORANEO, UFFICIO_SOCI_UNITA, PRESIDENTE))
        if deleghe.intersection(tipi):
            modulo = ModuloRichiestaTicketPersone(request.POST or None)
        else:
            modulo = ModuloRichiestaTicket(request.POST or None)

        lista_sezioni = modulo.fields['tipo'].choices

        # Rimuovo delle scelte dalla lista delle sezioni
        if not me.deleghe_attuali().exists():
            lista_sezioni = rimuovi_scelte([SEZ_REQ, SEZ_INC], lista_sezioni)

        modulo.fields['tipo'].choices = lista_sezioni

    if modulo and modulo.is_valid():
        import base64

        oggetto = modulo.cleaned_data['oggetto']
        descrizione = modulo.cleaned_data['descrizione']
        persona = modulo.cleaned_data.get('persona', None)
        id_dipartimento = TIPO_RICHIESTA_DIPARTIMENTO.get(modulo.cleaned_data['tipo'])

        ticketID, ticketPostID, ticketDisplayID = KayakoRESTService(me.email).createTicket(mittente=me, subject=oggetto, fullname=me.nome_completo, email=me.email, contents=descrizione, department_id=id_dipartimento, persona=persona)

        if len(request.FILES) != 0:
            nome_allegato = request.FILES['allegato'].name
            contenuto_allegato = request.FILES['allegato'].read()
            KayakoRESTService(me.email).addTicketAttachment(ticketID, ticketPostID, nome_allegato, base64.encodebytes(contenuto_allegato))

        return messaggio_generico(request, me, titolo="Richiesta inoltrata",
                                  messaggio="Grazie per aver contattato il supporto. La tua richiesta con "
                                            "oggetto '%s' è stata correttamente inoltrata. Riceverai a minuti "
                                            "un messaggio di conferma del codice ticket <a href='/ticket/dettaglio/%s/'>'%s'</a> assegnato alla "
                                            "tua richiesta." % (oggetto,ticketDisplayID, ticketDisplayID, ))

    contesto = {
        "modulo": modulo,
        'sezioni': KayakoRESTService(me.email).listeTicket(me.email)
    }
    return 'supporto_nuova_richiesta.html', contesto


@pagina_privata
def supporto_ricerca_kb(request, me=None):

    """
    Effettua la ricerca di articoli all'interno della knowledgebase e mostra una lista di articoli
    :param request:
    :param me:
    :return:
    """
    from supporto.forms import ModuloRicercaInKnowledgeBase
    from supporto.models import KBCache
    from django.db.models import Q
    articoliRisultatoRicerca = []
    articoliInEvidenza = []
    result_count = None

    moduloRicercaInKnowledgeBase = ModuloRicercaInKnowledgeBase(request.POST or None)

    if moduloRicercaInKnowledgeBase and moduloRicercaInKnowledgeBase.is_valid():
        keyword = moduloRicercaInKnowledgeBase.cleaned_data['cerca']

        articoliRisultatoRicerca = []
        qs_articles = KBCache.objects.filter(Q(contents__icontains=keyword) | Q(subject__icontains=keyword))
        if(qs_articles):
            for kbcache in qs_articles:
                articoliRisultatoRicerca.append(kbcache.to_KBArticle())

        if(len(articoliRisultatoRicerca) == 0):
             result_count = True
    else:

        qs_articles = KBCache.objects.filter().order_by('-viewcount')[:3]
        if(qs_articles):
            for kbcache in qs_articles:
                articoliInEvidenza.append(kbcache.to_KBArticle())

    contesto = {
            "moduloRicercaInKnowledgeBase" : moduloRicercaInKnowledgeBase,
            "articoliRisultatoRicerca": articoliRisultatoRicerca,
            "articoliInEvidenza": articoliInEvidenza,
            "result_count" : result_count,
            "sezioni": KayakoRESTService(me.email).listeTicket(me.email),
        }

    return 'supporto_home.html', contesto

@pagina_privata
def supporto_dettaglio_kb(request, me, articleID):
    from supporto.models import KBCache
    """
    Visualizza il dettaglio di un articolo della knowledgebase e relativi allegati.
    Incrementa il numero di visite all'articolo nella tabella KBCache
    :param request:
    :param me:
    :param articleID: id dell'articolo della KB
    :return:
    """
    kbcache_item = KBCache.objects.get(pk=articleID)
    articolo = kbcache_item.to_KBArticle()

    #verifico che l'articolo non sia gia' stato visualizzato dall'articolo
    if 'lista_articoli_letti' not in request.session:
        request.session['lista_articoli_letti'] = []

    lista_articoli_letti = request.session['lista_articoli_letti']
    if articleID not in lista_articoli_letti:
        lista_articoli_letti.append(articleID)
        request.session['lista_articoli_letti'] = lista_articoli_letti
        kbcache_item.viewcount += 1
        kbcache_item.save()

    contesto = {
        "articolo": articolo,
        'sezioni': KayakoRESTService(me.email).listeTicket(me.email)
    }


    return 'supporto_dettaglio_articolo_kb.html', contesto


@pagina_privata
def supporto_attesa_risposta(request, me=None):

    """
    Visualizza la lista dei ticket in attesa di risposta
    :param request:
    :param me:
    :return:
    """
    return supporto_get_lista_ticket([TICKET_ATTESA_RISPOSTA],'Ticket in attesa di risposta', me)

@pagina_privata
def supporto_in_lavorazione(request, me=None):
    """
    Visualizza la lista dei ticket aperti e in lavorazione
    :param request:
    :param me:
    :return:
    """
    return supporto_get_lista_ticket([TICKET_APERTO, TICKET_IN_LAVORAZIONE], 'Ticket in lavorazione', me)

@pagina_privata
def supporto_chiusi(request, me=None):
    """
    Visualizza la lista dei ticket chiusi
    :param request:
    :param me:
    :return:
    """
    return supporto_get_lista_ticket([TICKET_CHIUSO], 'Ticket chiusi', me)

@pagina_privata
def supporto_dettaglio_ticket(request, me, ticketdisplayID):

    """
    Visualizza la pagina di dettaglio di un ticket con il pulsante "Chiudi  ticket" (se il ticket non e' gia' chiuso)
    una form per l'invio di una risposta e la cronologia delle conversazioni
    :param request:
    :param me:
    :param ticketdisplayID: display ID del ticket
    :return:
    """
    from base.errori import permessi
    from supporto.costanti import TICKET_CHIUSO, STATUS_TICKET
    from supporto.forms import ModuloPostTicket

    ticket = KayakoRESTService(me.email).get_ticketByDisplayID(ticketdisplayID)
    #verifico se l'utente è proprietario del ticket
    if ticket.email != me.email:
        return permessi(request, me)

    postList = ticket.ticketPostItemList
    attachmentList = ticket.attachmentList

    if request.method == 'POST':

        modulo = ModuloPostTicket(request.POST or None)

        if modulo and modulo.is_valid():

            import base64
            contents = modulo.cleaned_data['descrizione']
            nome_allegato = None
            contenuto_allegato = None
            if len(request.FILES) != 0:
                nome_allegato = request.FILES['allegato'].name
                contenuto_allegato = request.FILES['allegato'].read()

            contenuto_allegato_base64 = None
            if contenuto_allegato:
                contenuto_allegato_base64 = base64.encodebytes(contenuto_allegato)

            KayakoRESTService(me.email).createTicketPost(me, ticket.id, contents, nome_allegato, contenuto_allegato_base64 )

            return redirect('/ticket/dettaglio/' + ticketdisplayID)

    else:

        modulo = ModuloPostTicket()

    contesto = {
        'ticket': ticket,
        'STATUS_TICKET': STATUS_TICKET,
        'TICKET_CHIUSO' : str(TICKET_CHIUSO),
        'modulo' : modulo,
        'sezioni': KayakoRESTService(me.email).listeTicket(me.email),
        'postList': postList,
        'attachmentList': attachmentList,
        'hasattachments' : len(attachmentList) > 0
    }

    return 'supporto_dettaglio_ticket.html', contesto

@pagina_privata
def supporto_chiudi_ticket(request, me, ticketdisplayID):
    """
    Cambia lo stato del ticket in "Chiuso"
    :param request:
    :param me:
    :param ticketdisplayID:
    :return:
    """

    ticket = KayakoRESTService(me.email).get_ticketLightByDisplayID(ticketdisplayID)

    if not ticket.email == me.email:
        return redirect('/errore/permessi/')

    KayakoRESTService(me.email).chiudiTicket(ticket.id)

    return redirect('/ticket/dettaglio/' + ticketdisplayID)

@pagina_privata
def supporto_download_post_attachment(request, me, ticketdisplayID, attachmentID):
    """
    Restituisce la response con il contenuto del file allegato a un ticket
    """
    ticket = KayakoRESTService(me.email).get_ticketLightByDisplayID(ticketdisplayID)
    return download_attachment('/Tickets/TicketAttachment/', ticket.id, attachmentID)

@pagina_privata
def supporto_download_kb_attachment(request, me, articleID, attachmentID):
    """
    Restituisce la response con il contenuto del file allegato a un articolo di kb
    """
    return download_attachment('/Knowledgebase/Attachment/', articleID, attachmentID)

