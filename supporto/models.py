from django.db import models
import xml.etree.ElementTree as ET


class RestCache(models.Model):

    request = models.TextField(primary_key=True)
    response = models.TextField()
    creazione = models.DateTimeField( auto_now=True, db_index=True)
    email = models.CharField(max_length=300, null=True)

class KBCache(models.Model):

    class Meta:
        verbose_name = "Articolo Knowledge Base di Kayako"
        verbose_name_plural = "Articoli Knowledge Base di Kayako"

    articleid = models.IntegerField(primary_key=True)
    contents = models.TextField()
    contentstext = models.TextField()
    subject = models.TextField()
    dateline = models.DateTimeField()
    attachments = models.TextField(null=True,blank=True) #xml contenente la lista degli allegati all'articolo
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
                    KBCache.objects.update_or_create(articleid=kb_article.kb_article_id, defaults={
                        'contents': kb_article.contents,
                        'contentstext': kb_article.contents_text,
                        'subject': kb_article.subject,
                        'dateline': kb_article.dateline,
                        'attachments': kb_article.attachments_xml_string,
                        'lastupdate': lastupdate}
                                                     )

                start += article_interval

        # elimina da KBCache gli articoli non più presenti nella KB Remota
        KBCache.objects.filter(lastupdate__lt=lastupdate).delete()

    def to_KBArticle(cls):

        article = KbArticle()
        article.kb_article_id = cls.articleid
        article.subject = cls.subject
        article.contents = cls.contents
        article.contents_text = cls.contentstext

        article_attachment_list = []
        article_attachment_item = Attachment()
        if cls.attachments:
            article_attachments = ET.fromstring(cls.attachments)
            for article_attachment in article_attachments:
                article_attachment_item.id = article_attachment.find('./id').text
                article_attachment_item.filename = article_attachment.find('./filename').text
                article_attachment_item.filesize = article_attachment.find('./filesize').text
                article_attachment_list.append(article_attachment_item)

        article.attachmentList = article_attachment_list

        return article


# raccolta di classi con i nomi dei campi reperiti dalle chiamate rest di kayako
class KbArticle(object):
    kb_article_id = None
    subject = None
    contents_text = None
    contents = None
    author = None
    dateline = None
    attachment_list = []
    attachments_xml_string = None

    def __repr__(self):
        return ('kb_article_id={}, subject={}, contents_text={}, contents={}, author={}, dateline={}'
                .format(self.kb_article_id, self.subject, self.contents_text, self.contents, self.author, self.dateline))

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