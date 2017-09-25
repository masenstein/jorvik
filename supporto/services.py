import base64
import datetime
import hashlib
import hmac
import random
import xml.etree.ElementTree as ET
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from supporto.models import KbArticle, Ticket, TicketPost, Attachment, RestCache
from supporto.costanti import *
import requests
from jorvik.settings import KAYAKO_SECRET_KEY, KAYAKO_API_KEY, KAYAKO_ENDPOINT, KAYAKO_CACHE_TTL, KAYAKO_CACHE_ENABLED


class KayakoRESTService:
    salt = None
    encodedSignature = None
    params = None
    email = None

    def __init__(self, user_email=None):
        try:
            self.salt = str(random.getrandbits(32))
            signature = hmac.new(bytes(KAYAKO_SECRET_KEY, 'utf-8'), msg=self.salt.encode(),
                                 digestmod=hashlib.sha256).digest()
            self.encodedSignature = base64.encodebytes(signature)
            self.params = {'salt': self.salt, 'apikey': KAYAKO_API_KEY, 'signature': self.encodedSignature}
            self.email = user_email
        except Exception as e:
            pass

    def _getXMLResponse(self, url, params, method):
        if method == 'GET':
            r = requests.get(url, params=params)
            xml_string = r.text
        elif method == 'POST':
            r = Request(url, urlencode(params).encode())
            xml_string = urlopen(r).read().decode()
        else:
            xml_string = None

        return xml_string

    def _getresponse(self, url, params, method='GET'):

        if KAYAKO_CACHE_ENABLED == '0':
            return ET.fromstring(self._getXMLResponse(url, params, method))
        else:
            request_key = url[len(KAYAKO_ENDPOINT) : ]
            arr_sorted_keys = sorted(params.keys())
            for key in arr_sorted_keys:
                # elimino dalla request i params costanti: salt, apikey, signature
                if  key not in {'salt', 'apikey', 'signature'} :
                    request_key += "/" + str(key) + "/" + str(params[key])

            qs = RestCache.objects.filter(pk=request_key)
            if len(qs) == 0 or (len(qs) == 1 and ((datetime.datetime.now() - qs[0].creazione).total_seconds()) > int(KAYAKO_CACHE_TTL)):
                xml_string = self._getXMLResponse(url, params, method)

                entry = RestCache(request=request_key, response=xml_string, email=self.email)
                entry.save()
            else:
                # otteniamo una hit dal db (response recuperata e non scaduta)
                entry = qs[0]
                xml_string = entry.response

            return ET.fromstring(xml_string)

    def _clean_user_cache(self):

        try:
            RestCache.objects.filter(email=self.email).delete()
        except Exception as e:
            import logging
            logger = logging.getLogger('supporto')
            logger.warning('MSG %s: ' % e)
            pass

        return

    def get_departments(self):
        """
        Questo metodo recupera l'elenco completo dei dipartimenti configurati su kayako.
        :return: una lista di tuple: (id, title)
        """
        dept_list = []
        url = KAYAKO_ENDPOINT + '/Base/Department'
        try:

            departments = self._getresponse(url, self.params)
            for department in departments:
                id = department.find('./id').text
                title = department.find('./title').text
                dept_list.append((id, title))
        except Exception as e:
            pass

        return dept_list

    def get_departments_ids(self):
        """
        Questo metodo recupera gli id dei dipartimenti configurati su kayako
        :return: una lista di interi
        """
        dept_list = []
        url = KAYAKO_ENDPOINT + '/Base/Department'

        departments = self._getresponse(url, self.params)
        for department in departments:
            id = department.find('./id').text
            dept_list.append(int(id))

        return dept_list

    def _get_listOfIdTitle(self, api_path):
        """
        Questo metodo effettua una chiamata all'endpoint apiPATH recuperando la lista di tuple: (id, title).
        :return: uuna lista di tuple: (id, title)
        """
        item_list = []
        url = KAYAKO_ENDPOINT + api_path
        try:
            items = self._getresponse(url, self.params)
            for item in items:
                id = item.find('./id').text
                title = item.find('./title').text
                item_list.append((id, title))
        except Exception as e:
            pass

        return item_list

    def get_ticketStatus(self):
        """
        Questo metodo recupera la lista degli stati dei ticket definiti su kayako.
        :return: una lista di tuple: (id, title)
        """
        return self._get_listOfIdTitle('/Tickets/TicketStatus')

    def get_ticketPriority(self):
        """
        Questo metodo recupera la lista delle priority dei ticket definite su kayako.
        :return: una lista di tuple: (id, title)
        """
        return self._get_listOfIdTitle('/Tickets/TicketPriority')

    def get_ticketType(self):
        """
        Questo metodo recupera la lista dei type di ticket definiti su kayako.
        :return: una lista di tuple: (id, title)
        """
        return self._get_listOfIdTitle('/Tickets/TicketType')

    def get_knowledgebase_categories(self):
        """
        Questo metodo recupera l'elenco completo delle categorie della KB.
        :return: una lista di id
        """
        category_id_list = []
        url = KAYAKO_ENDPOINT + '/Knowledgebase/Category/ListAll/'
        try:

            r = requests.get(url, params=self.params)
            categories = ET.fromstring(r.text)
            for category in categories:
                id = category.find('./id').text
                category_id_list.append(id)

        except Exception as e:
            pass

        return category_id_list

    def get_knowledgebase_articles_by_category(self, category_id, start, count):
        """
        Questo metodo recupera la lista degli articoli della knowledge base che contengono la stringa keyword.
        :return: una lista di articoli
        """
        kb_articles_list = []
        url = KAYAKO_ENDPOINT + '/Knowledgebase/Article/ListAll/' + str(category_id) + '/' + str(count) + '/' + str(start) + '/'

        r = requests.get(url, params=self.params)

        kb_articles = ET.fromstring(r.text)
        for kb_article in kb_articles:
            kb_article_item = KbArticle()
            kb_article_item.kb_article_id = kb_article.find('./kbarticleid').text
            kb_article_item.dateline = datetime.datetime.fromtimestamp(
                int(kb_article.find('./dateline').text)).strftime("%Y-%m-%d %H:%M")
            kb_article_item.contents = kb_article.find('./contents').text
            kb_article_item.subject = kb_article.find('./subject').text
            if kb_article.find('./hasattachments').text == '1':
                kb_article_item.attachments_xml_string = ET.tostring(kb_article.find('./attachments'), encoding='utf8', method='xml')

            kb_article_item.contents_text = kb_article.find('./contentstext').text
            kb_articles_list.append(kb_article_item)

        return kb_articles_list


    def get_knowledgebase_results(self, keyword=None):
        """
        Questo metodo recupera la lista degli articoli della knowledge base che contengono la stringa keyword.
        :return: una lista di articoli
        """
        kb_articles_list = []
        url = KAYAKO_ENDPOINT + '/Knowledgebase/Article/'
        r = requests.get(url, params=self.params)

        kb_articles = ET.fromstring(r.text)
        for kb_article in kb_articles:
            kb_article_item = KbArticle()
            kb_article_item.kb_article_id = kb_article.find('./kbarticleid').text
            kb_article_item.dateline = datetime.datetime.fromtimestamp(
                int(kb_article.find('./dateline').text)).strftime("%d/%m/%Y %H:%M")
            kb_article_item.contents = kb_article.find('./contents').text
            kb_article_item.subject = kb_article.find('./subject').text
            kb_article_item.author = kb_article.find('./author').text
            kb_article_item.contents_text = kb_article.find('./contentstext').text
            if keyword in kb_article_item.contents_text:
                kb_articles_list.append(kb_article_item)

        return kb_articles_list

    def get_knowledgebase_article(self, article_id):
        """
        Questo metodo recupera un articolo della knowledge base.
        :return: un articolo compresi gli eventuali attachment
        """
        url = KAYAKO_ENDPOINT + '/Knowledgebase/Article/'+ article_id

        r = requests.get(url, params=self.params)

        kb_article_item = KbArticle()
        kb_articles = ET.fromstring(r.text)
        for kb_article in kb_articles:
            kb_article_item.kb_article_id = kb_article.find('./kbarticleid').text
            kb_article_item.dateline = datetime.datetime.fromtimestamp(
                int(kb_article.find('./dateline').text)).strftime("%d/%m/%Y %H:%M")
            kb_article_item.contents = kb_article.find('./contents').text
            kb_article_item.subject = kb_article.find('./subject').text
            kb_article_item.author = kb_article.find('./author').text
            kb_article_item.contents_text = kb_article.find('./contentstext').text
            kb_article_item.attachmentList = self.get_knowledgebase_attachments(kb_article_item.kb_article_id)

        return kb_article_item

    def get_knowledgebase_attachments(self, article_id):
        """
        Questo metodo recupera gli attachment di un articolo della knowledge base.
        :return: una lista di attachment
        """
        url = KAYAKO_ENDPOINT + '/Knowledgebase/Attachment/ListAll/' + article_id

        r = requests.get(url, params=self.params)

        article_attachment_list = []
        article_attachment_item = Attachment()
        article_attachments = ET.fromstring(r.text)
        for article_attachment in article_attachments:
            article_attachment_item.id = article_attachment.find('./id').text
            article_attachment_item.filename = article_attachment.find('./filename').text
            article_attachment_item.filesize = article_attachment.find('./filesize').text
            article_attachment_item.filetype = article_attachment.find('./filetype').text
            article_attachment_list.append(article_attachment_item)

        return article_attachment_list


    def get_ticketCounts(self, departments_id_list, status_id_list, user_id):
        """
        Questo metodo effettua un conteggio dei ticket raggruppandoli per stato
        :return: il numero di ticket: in_attesa_di_risposta, in_lavorazione, chiusi
        """
        if user_id is None:
            return 0, 0, 0

        str_departments = ''
        for departmentId in departments_id_list:
            str_departments = str_departments + str(departmentId) + ','

        str_status = ''
        for status_id in status_id_list:
            str_status = str_status + str(status_id) + ','

        in_attesa_di_risposta = 0
        in_lavorazione = 0
        chiusi = 0

        url = KAYAKO_ENDPOINT + '/Tickets/Ticket/ListAll/' + str_departments + '/' + str_status + '/-1/' + str(
            user_id) + '/-1/-1/-1/-1'

        tickets = self._getresponse(url, self.params)
        for ticket in tickets:
            status_id = ticket.find('./statusid').text
            if status_id == str(TICKET_ATTESA_RISPOSTA):
                in_attesa_di_risposta += 1
            if status_id == str(TICKET_APERTO) or status_id == str(TICKET_IN_LAVORAZIONE):
                in_lavorazione += 1
            if status_id == str(TICKET_CHIUSO):
                chiusi += 1
        # todo generalizzare questo metodo riportando in output la lista delle occorrenze per ciascuno stato definito in input. Al momento per ticket in lavorazione si conteggiano anche quelli in stato Aperto

        return in_attesa_di_risposta, in_lavorazione, chiusi

    def get_ticketBadgeCount(self, user_email):
        """
        Questo metodo effettua il conteggio dei ticket in attesa di risposta
        :return: il numero di ticket in_attesa_di_risposta
        """
        in_attesa_di_risposta = 0
        try:
            user_id = KayakoRESTService(self.email).get_userIdByEmail(user_email)
            if user_id is None:
                return 0

            departments_id_list = KayakoRESTService(self.email).get_departments_ids()
            str_departments = ''
            for departmentId in departments_id_list:
                str_departments = str_departments + str(departmentId) + ','

            url = KAYAKO_ENDPOINT + '/Tickets/Ticket/ListAll/' + str_departments + '/' + str(TICKET_ATTESA_RISPOSTA)\
                  + '/-1/' + str(user_id) + '/-1/-1/-1/-1'

            tickets = self._getresponse(url, self.params)
            for ticket in tickets:
                status_id = ticket.find('./statusid').text
                if status_id == str(TICKET_ATTESA_RISPOSTA): in_attesa_di_risposta += 1
            # todo generalizzare questo metodo riportando in output la lista delle occorrenze per ciascuno stato definito in input
        except Exception as e:
            pass

        return in_attesa_di_risposta

    def get_ticketListByStatus(self, departments_id_list, status_id_list, user_id):
        """
        Questo metodo recupera la lista dei ticket di un utente, che appartengono a un elenco di dipartimenti con degli stati specificati
        :return: una lista di ticket
        """
        if user_id is None:
            return None

        str_departments = ''
        for departmentId in departments_id_list:
            str_departments = str_departments + str(departmentId) + ','

        str_status = ''
        for status_id in status_id_list:
            str_status = str_status + str(status_id) + ','

        url = KAYAKO_ENDPOINT + '/Tickets/Ticket/ListAll/' + str_departments + '/' + str_status + '/-1/' + str(
            user_id) + '/-1/-1/-1/-1'

        ticket_list = []

        tickets = self._getresponse(url, self.params)
        for ticket in tickets:
            ticket_item = Ticket()
            status_id = ticket.find('./statusid').text

            if int(status_id) in status_id_list:
                ticket_item.id = ticket.attrib['id']
                ticket_item.displayid = ticket.find('./displayid').text
                ticket_item.statusid = status_id
                ticket_item.lastactivity = datetime.datetime.fromtimestamp(
                    int(ticket.find('./lastactivity').text)).strftime("%d/%m/%Y %H:%M")
                ticket_item.subject = ticket.find('./subject').text
                ticket_list.append(ticket_item)

        ticket_list.sort(key=lambda x: datetime.datetime.strptime(x.lastactivity, "%d/%m/%Y %H:%M"), reverse=True)

        return ticket_list

    def get_ticketLightByDisplayID(self, ticket_display_id):
        """
        Questo metodo preleva i dati di un ticket, partendo dal codice del ticket
        :return: un ticket, di cui sono valorizzate le sole proprietà id ed email
        """

        url = KAYAKO_ENDPOINT + '/Tickets/Ticket/' + ticket_display_id

        ticket_item = Ticket()
        tickets = self._getresponse(url, self.params)
        for ticket in tickets:
            ticket_item.id = ticket.attrib['id']
            ticket_item.email = ticket.find('./email').text


        return ticket_item

    def getTicketAttachments(self, ticket_id):
        """
        Questo metodo recupera i metadati degli attachment di un ticket
        :return: una lista di attachment in cui non è valorizzato il contents
        """

        url = KAYAKO_ENDPOINT + '/Tickets/TicketAttachment/ListAll/' + ticket_id

        r = requests.get(url, params=self.params)

        post_attachment_list = []

        post_attachments = ET.fromstring(r.text)
        for postAttachment in post_attachments:
            post_attachment_item = Attachment()
            post_attachment_item.id = postAttachment.find('./id').text
            post_attachment_item.filename = postAttachment.find('./filename').text
            post_attachment_item.filesize = postAttachment.find('./filesize').text
            post_attachment_item.filetype = postAttachment.find('./filetype').text
            post_attachment_list.append(post_attachment_item)

        return post_attachment_list

    def get_attachment(self, endpoint, parent_id, attachment_id):
        """
        Questo metodo recupera un entità attachment da un endpoint che sia del tipo /$endpoint$/$parendID$/$attachmentID$/
        :return: un attachment, compreso di metadati e di contenuto
        """

        url = KAYAKO_ENDPOINT + endpoint + parent_id + '/' + attachment_id

        r = requests.get(url, params=self.params)

        attachment_item = Attachment()
        attachments = ET.fromstring(r.text)
        for attachment in attachments:
            attachment_item.id = attachment.find('./id').text
            attachment_item.filename = attachment.find('./filename').text
            attachment_item.filetype = attachment.find('./filetype').text
            attachment_item.filesize = attachment.find('./filesize').text
            attachment_item.contents = attachment.find('./contents').text

        return attachment_item

    def get_ticketByDisplayID(self, ticket_display_id):
        """
        Questo metodo recupera tutti in dati di un ticket (metadati, post ed allegati) ricevendo in input il codice del ticket
        :return: il ticket con la lista di post e la lista di attachment
        """

        url = KAYAKO_ENDPOINT + '/Tickets/Ticket/'+ ticket_display_id

        ticket_item = Ticket()
        tickets = self._getresponse(url, self.params)
        for ticket in tickets:
            status_id = ticket.find('./statusid').text
            ticket_item.id = ticket.attrib['id']
            ticket_item.displayid = ticket.find('./displayid').text
            ticket_item.priorityid = ticket.find('./priorityid').text
            ticket_item.statusid = status_id
            ticket_item.lastactivity = datetime.datetime.fromtimestamp(
                int(ticket.find('./lastactivity').text)).strftime("%d/%m/%Y %H:%M")
            ticket_item.subject = ticket.find('./subject').text
            ticket_item.lastreplier = ticket.find('./lastreplier').text
            ticket_item.email = ticket.find('./email').text

            ticket_post_item_list = []


            posts = ticket.find('./posts')
            for post in posts:
                ticket_post_item = TicketPost()
                ticket_post_item.id = post.find('./id').text
                ticket_post_item.dateline =  datetime.datetime.fromtimestamp(
                    int(post.find('./dateline').text)).strftime("%d/%m/%Y %H:%M:%S")
                ticket_post_item.fullname = post.find('./fullname').text
                ticket_post_item.hasattachments = post.find('./hasattachments').text
                # Elimino la parte del messaggio che deve essere visibile solo allo staff
                ticket_post_item.contents = post.find('./contents').text.split(TEXT_BREAK_STAFF, 1)[0]
                ticket_post_item_list.append(ticket_post_item)

            ticket_post_item_list.sort(key=lambda x: datetime.datetime.strptime(x.dateline, "%d/%m/%Y %H:%M:%S"), reverse=True)
            ticket_item.ticketPostItemList = ticket_post_item_list
            ticket_item.attachmentList = self.getTicketAttachments(ticket_item.id)

        return ticket_item

    def get_userIdByEmail(self, user_email=None):
        """
        Questo metodo recupera l'id dell'utente kayako partendo dal suo indirizzo email
        :return: un intero con l'identificativo utente
        """
        self.params.update({'query': user_email, 'email': '1'})

        url = KAYAKO_ENDPOINT + '/Base/UserSearch'

        xml = self._getresponse(url, self.params, 'POST')
        user_id_elem = xml.find('./user/id', None)
        user_id = None if user_id_elem is None else user_id_elem.text

        return user_id

    def listeTicket(self, email):
        """
        Questo metodo ottiene la lista dei ticket suddivisi in: in_attesa_di_risposta, in_lavorazione, chiusi
        :return: una lista di tuple (descrizione, numero, codifica)
        """

        attesa_risposta, in_lavorazione, chiusi = self.get_ticketCounts(KayakoRESTService(self.email).get_departments_ids(),[TICKET_APERTO,TICKET_IN_LAVORAZIONE,TICKET_CHIUSO,TICKET_ATTESA_RISPOSTA], self.get_userIdByEmail(email))

        liste = [('In attesa di una tua risposta', attesa_risposta, 'attesa_risposta'),
                 ('In carico allo staff', in_lavorazione, 'in_lavorazione'),
                 ('Chiusi', chiusi, 'chiusi')
                 ]

        return liste

    def createTicket(self, mittente, subject, fullname, email, contents, department_id, persona=None, ticket_status_id=None, ticket_priority_id=None, ticket_type_id=DEFAULT_TICKET_TYPE_ID, autouser_id=DEFAULT_AUTO_USER_ID):
        """
        Questo metodo crea un ticket su kayako
        :return: la terna di valori ticketID, ticketPostID, ticketDisplayID
        """

        from django.template.loader import get_template

        corpo={
            "testo": contents,
            "mittente": mittente,
            "persona": persona,
            "text_break_staff": TEXT_BREAK_STAFF
        }
        ticket_contents = get_template("supporto_modello_testo_ticket.html").render(corpo)

        params = {'subject': subject,
                  'fullname': fullname,
                  'email': email,
                  'contents': ticket_contents,
                  'departmentid': department_id,
                  'ticketstatusid': ticket_status_id,
                  'ticketpriorityid': ticket_priority_id,
                  'tickettypeid': ticket_type_id,
                  'autouserid': autouser_id,
                  }

        self.params.update(params)
        url = KAYAKO_ENDPOINT + '/Tickets/Ticket'
        r = Request(url, urlencode(self.params).encode())
        xml = urlopen(r).read().decode()

        tickets = ET.fromstring(xml)

        ticket_id = tickets.find('./ticket').attrib['id']
        ticket_post_id = tickets.find('./ticket/posts/post/id', None).text
        ticket_display_id = tickets.find('./ticket/displayid', None).text

        self._clean_user_cache()

        return ticket_id, ticket_post_id, ticket_display_id


    def createTicketPost(self, email, ticket_id, contents, file_name, file_content = None):
        """
        Questo metodo aggiunge un post con eventualmente un allegato, ad un ticket già presente
        :return:
        """
        params = {'ticketid': ticket_id,
                  'contents': contents,
                  'userid': KayakoRESTService(email).get_userIdByEmail(email),
                  'filename': file_name,
                  'isprivate': 0
                  }

        if file_content:
            self.params.update({'filecontent': file_content})

        self.params.update(params)
        url = KAYAKO_ENDPOINT + '/Tickets/TicketPost'
        r = Request(url, urlencode(self.params).encode())
        xml = urlopen(r).read().decode()
        posts = ET.fromstring(xml)
        ticket_post_id = posts.find('./post/id', None).text

        self._clean_user_cache()

        return ticket_post_id

    def addTicketAttachment(self, ticket_id, ticket_post_id, file_name, file_content):
        """
        Questo metodo aggiunge un attachment ad un ticket
        :return:
        """
        params = {
            'ticketid' : ticket_id,
            'ticketpostid': ticket_post_id,
            'filename':file_name,
            'contents': file_content
        }

        self.params.update(params)
        url = KAYAKO_ENDPOINT + '/Tickets/TicketAttachment'

        r = Request(url, urlencode(self.params).encode())
        urlopen(r).read().decode()

        return

    def chiudiTicket(self, ticketId):
        """
        Questo metodo aggiorna lo stato di un ticket impostandolo a Chiuso
        :return:
        """

        params = {
            'ticketstatusid': TICKET_CHIUSO
        }
        self.params.update(params)

        url = KAYAKO_ENDPOINT + '/Tickets/Ticket/' + str(ticketId)
        r = Request(url, urlencode(self.params).encode(), method='PUT')
        urlopen(r).read().decode()
        self._clean_user_cache()

        return
