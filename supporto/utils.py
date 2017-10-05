from base.errori import errore_generico


def download_attachment(endpoint, parentID, attachmentID):
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

    attachment = KayakoRESTService(None).get_attachment(endpoint, parentID, attachmentID)

    data = base64.b64decode(attachment.contents)

    response = HttpResponse(data, content_type=attachment.filetype)
    response['Content-Disposition'] = "attachment; filename={0}".format(attachment.filename)
    response['Content-Length'] = attachment.filesize
    return response


def supporto_errore_generico(request, me, e):
    import logging
    logger = logging.getLogger('supporto')
    logger.error('MSG %s: ' % e)

    return errore_generico(titolo="Errore", messaggio="Si è verificato un errore durante l'esecuzione dell'operazione.",
                           request=request)
