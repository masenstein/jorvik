from django.db import models

class RestCache(models.Model):

    request = models.TextField(primary_key=True)
    response = models.TextField()
    creazione = models.DateTimeField( auto_now=True, db_index=True)
    email = models.CharField(max_length=300, null=True)

class KBCache(models.Model):
    articleid = models.IntegerField(primary_key=True)
    contents = models.TextField()
    contentstext = models.TextField()
    subject = models.TextField()
    dateline = models.DateTimeField()
    attachments = models.TextField(null=True) #xml contenente la lista degli allegati all'articolo
    viewcount = models.IntegerField(default=0) #numero di visualizzazioni dell'articolo da parte di un utente
    lastupdate = models.DateTimeField(db_index=True) #timestamp di inserimento/aggiornamento della riga in tabella

    @classmethod
    def aggiorna_kb_cache(cls, article_interval=10):
        from datetime import datetime
        from supporto.services import KayakoRESTService
        lastupdate = datetime.now()
        # prelevo la lista delle categorie della KB
        category_ids = KayakoRESTService(None).get_knowledgebase_categories()
        for category_id in category_ids:
            # per ogni categoria prelevo n articoli finchè ne trovo
            start = 0
            trovato = True
            while (trovato):
                kb_articles = KayakoRESTService(None).get_knowledgebase_articles_by_category(category_id, start, article_interval)

                trovato = len(kb_articles) > 0
                # per ogni articolo salvo/aggiorno l'articolo sulla tabella KBCache
                for kb_article in kb_articles:
                    # salvo/aggiorno
                    KBCache.objects.update_or_create(articleid=kb_article.kbarticleid, defaults={
                        'contents': kb_article.contents,
                        'contentstext': kb_article.contentstext,
                        'subject': kb_article.subject,
                        'dateline': kb_article.dateline,
                        'attachments': kb_article.attachments_xml_string,
                        'lastupdate': lastupdate}
                                                     )

                start += article_interval

        # elimina da KBCache gli articoli non più presenti nella KB Remota
        KBCache.objects.filter(lastupdate__lt=lastupdate).delete()


# raccolta di classi con i nomi dei campi reperiti dalle chiamate rest di kayako
class KbArticle(object):
    kbarticleid = None
    subject = None
    contentstext = None
    contents = None
    author = None
    dateline = None
    attachmentList = []
    attachments_xml_string = None

    def __repr__(self):
        return ('kbarticleid={}, subject={}, contentstext={}, contents={}, author={}, dateline={}'.format(self.kbarticleid, self.subject,
                                                                                  self.contentstext, self.contents, self.author, self.dateline))
class TicketPost(object):
    id = None
    dateline = None
    fullname = None
    hasattachments = None
    contents = None

class Attachment(object):
    id = None
    filename = None
    filetype = None
    filesize = None
    contents = None

class Ticket(object):
    id = None
    displayid = None
    lastactivity = None
    departmentid = None
    statusid = None
    typeid = None
    priorityid = None
    lastreplier = None
    email = None
    subject = None
    ticketPostItemList = []
    attachmentList = []

    def __repr__(self):
        return (
            'id={}, displayid={}, lastactivity={}, departmentid={}, statusid={}, typeid={}, priorityid={}, lastreplier={}, email={}, subject={}, ticketPostItemList={}'.format(
                self.id,
                self.displayid,
                self.lastactivity,
                self.departmentid,
                self.statusid,
                self.typeid,
                self.priorityid,
                self.lastreplier,
                self.email,
                self.subject,
                self.ticketPostItemList))