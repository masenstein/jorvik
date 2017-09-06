def download_attachment( endpoint, parentID, attachmentID):

    """
    Questo metodo recupera un attachment richiamando /$endpoint$/$parendID$/$attachmentID$/
    :param endpoint: il relative path dell'endpoint da richiamare per ottenere l'xml con i metadati ed il contenuto dell'allegato
    :param parentID: il primo identificativo da concatenare all'endpoint
    :param attachmentID: il secondo identificativo da concatenare all'endpoint
    :return: una response con l'attachment pronto per il download
    """
    from django.http import HttpResponse
    import base64
    from supporto.services import KayakoRESTService

    attachment = KayakoRESTService(email=None).get_attachment(endpoint, parentID, attachmentID)

    data = base64.b64decode(attachment.contents)

    response = HttpResponse(data, content_type=attachment.filetype)
    response['Content-Disposition'] = "attachment; filename={0}".format(attachment.filename)
    response['Content-Length'] = attachment.filesize
    return response

def supporto_get_lista_ticket(statusIdList, titoloPagina, me=None):
    """
    Questo metodo recupera i ticket che si trovano in uno stato della lista statusIdList e li mostra in un template supporto_lista_ticket
    :param statusIdList: lista di identificativi degli stati dei ticket da recuperare
    :param titoloPagina: il title html della pagina che sarà mostrata
    :return: il template html ed il contesto per la sua valorizzazione
    """
    from supporto.costanti import STATUS_TICKET
    from supporto.services import KayakoRESTService

    ticketList = KayakoRESTService(me.email).get_ticketListByStatus(KayakoRESTService(me.email).get_departments_ids(),statusIdList, KayakoRESTService(me.email).get_userIdByEmail(me.email))

    contesto = {
        'STATUS_TICKET': STATUS_TICKET,
        'sezioni': KayakoRESTService(me.email).listeTicket(me.email),
        'lista_ticket': ticketList,
        'titolo_pagina': titoloPagina
    }

    return 'supporto_lista_ticket.html', contesto