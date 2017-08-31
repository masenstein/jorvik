from anagrafica.permessi.applicazioni import PRESIDENTE, UFFICIO_SOCI, UFFICIO_SOCI_TEMPORANEO, UFFICIO_SOCI_UNITA
from autenticazione.funzioni import pagina_privata
from base.errori import messaggio_generico
from supporto.costanti import *
from django.shortcuts import redirect
from supporto.utils import download_attachment, supporto_get_lista_ticket
from supporto.services import KayakoRESTService


@pagina_privata
def supporto_nuova_richiesta_step1(request, me=None):
    """
    Carica la pagina di inserimento di un nuovo ticket in cui viene selezionato il dipartimento.
    Nella pagina e' presente il modulo di ricerca degli articoli nella KB
    :param request:
    :param me:
    :return:
    """
    from supporto.forms import ModuloRicercaInKnowledgeBase
    from supporto.forms import ModuloSceltaDipartimentoTicket
    modulo = None

    moduloRicercaInKnowledgeBase = ModuloRicercaInKnowledgeBase(request.POST or None)

    if moduloRicercaInKnowledgeBase and moduloRicercaInKnowledgeBase.is_valid():

        keyword = moduloRicercaInKnowledgeBase.cleaned_data['cerca']
        articleList = KayakoRESTService().get_knowledgebase_results(keyword)

        contesto = {
            "moduloRicercaInKnowledgeBase": moduloRicercaInKnowledgeBase,
            "articleList": articleList
        }
        return 'lista_articoli_kb.html', contesto


    if me:

        deptList = KayakoRESTService().get_departments()
        modulo = ModuloSceltaDipartimentoTicket(request.POST or None)
        modulo.fields['dipartimento'].choices = deptList

    if modulo and modulo.is_valid():

        request.session['dipartimento'] = modulo.cleaned_data['dipartimento']
        return redirect('/ticket/nuova_richiesta_step2/')

    contesto = {
        "modulo": modulo,
        'moduloRicercaInKnowledgeBase': moduloRicercaInKnowledgeBase,
        'sezioni': KayakoRESTService().listeTicket(me.email)
    }
    return 'nuova_richiesta_step1.html', contesto

@pagina_privata
def supporto_nuova_richiesta_step2(request, me=None):
    """
    Carica la pagina di inserimento di un nuovo ticket in cui vengono inserite le informazioni relative alla segnalazione
    ed eventuali allegati.
    Nella pagina e' presente il modulo di ricerca degli articoli nella KB
    :param request:
    :param me:
    :return:
    """
    from supporto.forms import ModuloRichiestaTicket,ModuloRichiestaTicketPersone
    from supporto.forms import ModuloRicercaInKnowledgeBase
    modulo = None

    moduloRicercaInKnowledgeBase = ModuloRicercaInKnowledgeBase(request.POST or None)

    if moduloRicercaInKnowledgeBase and moduloRicercaInKnowledgeBase.is_valid():

        keyword = moduloRicercaInKnowledgeBase.cleaned_data['cerca']

        articleList = KayakoRESTService().get_knowledgebase_results(keyword)

        contesto = {
            "moduloRicercaInKnowledgeBase": moduloRicercaInKnowledgeBase,
            "articleList": articleList
        }
        return 'lista_articoli_kb.html', contesto

    if me:
        deleghe = set([d.tipo for d in me.deleghe_attuali()])
        tipi = set((UFFICIO_SOCI, UFFICIO_SOCI_TEMPORANEO, UFFICIO_SOCI_UNITA, PRESIDENTE))
        if deleghe.intersection(tipi):
            modulo = ModuloRichiestaTicketPersone(request.POST or None)
        else:
            modulo = ModuloRichiestaTicket(request.POST or None)

    if modulo and modulo.is_valid():
        import base64

        oggetto = modulo.cleaned_data['oggetto']
        descrizione = modulo.cleaned_data['descrizione']
        persona = modulo.cleaned_data.get('persona', None)

        ticketID, ticketPostID, ticketDisplayID = KayakoRESTService().createTicket(mittente=me, subject=oggetto, fullname=me.nome_completo, email=me.email, contents=descrizione, departmentid=request.session.get('dipartimento',None),persona=persona)

        if len(request.FILES) != 0:
            nome_allegato = request.FILES['allegato'].name
            contenuto_allegato = request.FILES['allegato'].read()
            KayakoRESTService().addTicketAttachment(ticketID, ticketPostID, nome_allegato, base64.encodebytes(contenuto_allegato))

        return messaggio_generico(request, me, titolo="Richiesta inoltrata",
                                  messaggio="Grazie per aver contattato il supporto. La tua richiesta con "
                                            "oggetto '%s' è stata correttamente inoltrata. Riceverai a minuti "
                                            "un messaggio di conferma del codice ticket <a href='/ticket/dettaglio/%s/'>'%s'</a> assegnato alla "
                                            "tua richiesta." % (oggetto,ticketDisplayID, ticketDisplayID, ))

    contesto = {
        "modulo": modulo,
        'moduloRicercaInKnowledgeBase': moduloRicercaInKnowledgeBase,
        'sezioni': KayakoRESTService().listeTicket(me.email)
    }
    return 'nuova_richiesta_step2.html', contesto


@pagina_privata
def supporto_ricerca_kb(request, me=None):

    """
    Effettua la ricerca di articoli all'interno della knowledgebase e mostra una lista di articoli
    :param request:
    :param me:
    :return:
    """
    from supporto.forms import ModuloRicercaInKnowledgeBase

    articleList = []

    moduloRicercaInKnowledgeBase = ModuloRicercaInKnowledgeBase(request.POST or None)

    if moduloRicercaInKnowledgeBase and moduloRicercaInKnowledgeBase.is_valid():

        keyword = moduloRicercaInKnowledgeBase.cleaned_data['cerca']

        articleList = KayakoRESTService().get_knowledgebase_results(keyword)


    contesto = {
            "moduloRicercaInKnowledgeBase": moduloRicercaInKnowledgeBase,
            "articleList": articleList,
            'sezioni': KayakoRESTService().listeTicket(me.email)
        }
    return 'lista_articoli_kb.html', contesto

@pagina_privata
def supporto_dettaglio_kb(request, me, articleID):

    """
    Visualizza il dettaglio di un articolo della knowledgebase e relativi allegati.
    :param request:
    :param me:
    :param articleID: id dell'articolo della KB
    :return:
    """
    articolo = KayakoRESTService().get_knowledgebase_article(articleID)

    contesto = {
        "articolo": articolo,
        'sezioni': KayakoRESTService().listeTicket(me.email)
    }
    return 'dettaglio_articolo_kb.html', contesto


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
    from supporto.models import Tipologiche
    from supporto.costanti import TICKET_CHIUSO
    from supporto.forms import ModuloPostTicket

    ticket = KayakoRESTService().get_ticketByDisplayID(ticketdisplayID)
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

            KayakoRESTService().createTicketPost(me, ticket.id, contents, nome_allegato, contenuto_allegato_base64 )

            return redirect('/ticket/dettaglio/' + ticketdisplayID)

    else:

        modulo = ModuloPostTicket()

    contesto = {
        'ticket': ticket,
        'tipologiche': Tipologiche(),
        'TICKET_CHIUSO' : str(TICKET_CHIUSO),
        'modulo' : modulo,
        'sezioni': KayakoRESTService().listeTicket(me.email),
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

    ticket = KayakoRESTService().get_ticketLightByDisplayID(ticketdisplayID)

    if not ticket.email == me.email:
        return redirect('/errore/permessi/')

    KayakoRESTService().chiudiTicket(ticket.id)

    return redirect('/ticket/dettaglio/' + ticketdisplayID)

@pagina_privata
def supporto_download_post_attachment(request, me, ticketdisplayID, attachmentID):
    """
    Restituisce la response con il contenuto del file allegato a un ticket
    """
    ticket = KayakoRESTService().get_ticketLightByDisplayID(ticketdisplayID)
    return download_attachment('/Tickets/TicketAttachment/', ticket.id, attachmentID)

@pagina_privata
def supporto_download_kb_attachment(request, me, articleID, attachmentID):
    """
    Restituisce la response con il contenuto del file allegato a un articolo di kb
    """
    return download_attachment('/Knowledgebase/Attachment/', articleID, attachmentID)

