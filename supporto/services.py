import base64
import datetime
import hashlib
import hmac
import random
import xml.etree.ElementTree as ET
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from supporto.models import KbArticle,Ticket, TicketPost, Attachment
from supporto.costanti import *
import requests
from jorvik.settings import KAYAKO_SECRET_KEY, KAYAKO_API_KEY, KAYAKO_ENDPOINT


class KayakoRESTService():
    salt = None
    encodedSignature = None
    params = None

    def __init__(self):
        try:
            self.salt = str(random.getrandbits(32))
            signature = hmac.new(bytes(KAYAKO_SECRET_KEY, 'utf-8'), msg=self.salt.encode(),
                                 digestmod=hashlib.sha256).digest()
            self.encodedSignature = base64.encodebytes(signature)
            self.params = {'salt': self.salt, 'apikey': KAYAKO_API_KEY, 'signature': self.encodedSignature}
        except Exception as e:
            pass

    def get_departments(self):
        """
        Questo metodo recupera l'elenco completo dei dipartimenti configurati su kayako.
        :return: una lista di tuple: (id, title)
        """
        deptList = []
        url = KAYAKO_ENDPOINT + '/Base/Department'
        try:
            r = requests.get(url, params=self.params)

            departments = ET.fromstring(r.text)
            for department in departments:
                id = department.find('./id').text
                title = department.find('./title').text
                deptList.append((id, title))
        except Exception as e:
            pass

        return deptList

    def get_departments_ids(self):
        """
        Questo metodo recupera gli id dei dipartimenti configurati su kayako
        :return: una lista di interi
        """
        deptList = []
        url = KAYAKO_ENDPOINT + '/Base/Department'
        r = requests.get(url, params=self.params)

        departments = ET.fromstring(r.text)
        for department in departments:
            id = department.find('./id').text
            deptList.append(int(id))

        return deptList

    def _get_listOfIdTitle(self, apiPATH):
        """
        Questo metodo effettua una chiamata all'endpoint apiPATH recuperando la lista di tuple: (id, title).
        :return: uuna lista di tuple: (id, title)
        """
        itemList = []
        url = KAYAKO_ENDPOINT + apiPATH
        try:
            r = requests.get(url, params=self.params)
            items = ET.fromstring(r.text)
            for item in items:
                id = item.find('./id').text
                title = item.find('./title').text
                itemList.append((id, title))
        except Exception as e:
            pass

        return itemList

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

    def get_knowledgebase_results(self, keyword=None):
        """
        Questo metodo recupera la lista degli articoli della knowledge base che contengono la stringa keyword.
        :return: una lista di articoli
        """
        kbarticlesList = []
        url = KAYAKO_ENDPOINT + '/Knowledgebase/Article/'
        r = requests.get(url, params=self.params)

        kbarticles = ET.fromstring(r.text)
        for kbarticle in kbarticles:
            kbArticleItem = KbArticle()
            kbArticleItem.kbarticleid = kbarticle.find('./kbarticleid').text
            kbArticleItem.dateline = datetime.datetime.fromtimestamp(
                int(kbarticle.find('./dateline').text)).strftime("%d/%m/%Y %H:%M")
            kbArticleItem.contents = kbarticle.find('./contents').text
            kbArticleItem.subject = kbarticle.find('./subject').text
            kbArticleItem.author = kbarticle.find('./author').text
            kbArticleItem.contentstext = kbarticle.find('./contentstext').text
            if keyword in kbArticleItem.contentstext:
                kbarticlesList.append(kbArticleItem)

        return kbarticlesList

    def get_knowledgebase_article(self, articleID):
        """
        Questo metodo recupera un articolo della knowledge base.
        :return: un articolo compresi gli eventuali attachment
        """
        url = KAYAKO_ENDPOINT + '/Knowledgebase/Article/'+ articleID

        r = requests.get(url, params=self.params)

        kbArticleItem = KbArticle()
        kbarticles = ET.fromstring(r.text)
        for kbarticle in kbarticles:
            kbArticleItem.kbarticleid = kbarticle.find('./kbarticleid').text
            kbArticleItem.dateline = datetime.datetime.fromtimestamp(
                int(kbarticle.find('./dateline').text)).strftime("%d/%m/%Y %H:%M")
            kbArticleItem.contents = kbarticle.find('./contents').text
            kbArticleItem.subject = kbarticle.find('./subject').text
            kbArticleItem.author = kbarticle.find('./author').text
            kbArticleItem.contentstext = kbarticle.find('./contentstext').text
            kbArticleItem.attachmentList = self.get_knowledgebase_attachments(kbArticleItem.kbarticleid)

        return kbArticleItem

    def get_knowledgebase_attachments(self, articleid):
        """
        Questo metodo recupera gli attachment di un articolo della knowledge base.
        :return: una lista di attachment
        """
        url = KAYAKO_ENDPOINT + '/Knowledgebase/Attachment/ListAll/'+ articleid

        r = requests.get(url, params=self.params)

        articleAttachmentList = []
        articleAttachmentItem = Attachment()
        articleAttachments = ET.fromstring(r.text)
        for articleAttachment in articleAttachments:
            articleAttachmentItem.id = articleAttachment.find('./id').text
            articleAttachmentItem.filename = articleAttachment.find('./filename').text
            articleAttachmentItem.filesize = articleAttachment.find('./filesize').text
            articleAttachmentItem.filetype = articleAttachment.find('./filetype').text
            articleAttachmentList.append(articleAttachmentItem)

        return articleAttachmentList


    def get_ticketCounts(self, departmentsIdList, statusIdList, userid):
        """
        Questo metodo effettua un conteggio dei ticket raggruppandoli per stato
        :return: il numero di ticket: in_attesa_di_risposta, in_lavorazione, chiusi
        """
        if userid is None:
            return 0, 0, 0

        strDepartments = ''
        for departmentId in departmentsIdList:
            strDepartments = strDepartments + str(departmentId) + ','

        strStatus = ''
        for statusId in statusIdList:
            strStatus = strStatus + str(statusId) + ','

        in_attesa_di_risposta = 0
        in_lavorazione = 0
        chiusi = 0

        url = KAYAKO_ENDPOINT + '/Tickets/Ticket/ListAll/' + strDepartments + '/' + strStatus + '/-1/' + str(
            userid) + '/-1/-1/-1/-1'

        r = requests.get(url, params=self.params)

        tickets = ET.fromstring(r.text)
        for ticket in tickets:
            statusId = ticket.find('./statusid').text
            if statusId == str(TICKET_ATTESA_RISPOSTA): in_attesa_di_risposta += 1
            if statusId == str(TICKET_APERTO) or statusId == str(TICKET_IN_LAVORAZIONE) : in_lavorazione += 1
            if statusId == str(TICKET_CHIUSO): chiusi += 1
        # todo generalizzare questo metodo riportando in output la lista delle occorrenze per ciascuno stato definito in input. Al momento per ticket in lavorazione si conteggiano anche quelli in stato Aperto

        return in_attesa_di_risposta, in_lavorazione, chiusi

    def get_ticketBadgeCount(self, userEmail):
        """
        Questo metodo effettua il conteggio dei ticket in attesa di risposta
        :return: il numero di ticket in_attesa_di_risposta
        """
        in_attesa_di_risposta = 0
        try:
            userid = KayakoRESTService().get_userIdByEmail(userEmail)
            if userid is None:
                return 0

            departmentsIdList = KayakoRESTService().get_departments_ids()
            strDepartments = ''
            for departmentId in departmentsIdList:
                strDepartments = strDepartments + str(departmentId) + ','


            url = KAYAKO_ENDPOINT + '/Tickets/Ticket/ListAll/' + strDepartments + '/' + str(TICKET_ATTESA_RISPOSTA) + '/-1/' + str(userid) + '/-1/-1/-1/-1'

            r = requests.get(url, params=self.params)

            tickets = ET.fromstring(r.text)
            for ticket in tickets:
                statusId = ticket.find('./statusid').text
                if statusId == str(TICKET_ATTESA_RISPOSTA): in_attesa_di_risposta += 1
            # todo generalizzare questo metodo riportando in output la lista delle occorrenze per ciascuno stato definito in input
        except Exception as e:
            pass

        return in_attesa_di_risposta

    def get_ticketListByStatus(self, departmentsIdList, statusIdList, userid):
        """
        Questo metodo recupera la lista dei ticket di un utente, che appartengono a un elenco di dipartimenti con degli stati specificati
        :return: una lista di ticket
        """
        if userid is None:
            return None

        strDepartments = ''
        for departmentId in departmentsIdList:
            strDepartments = strDepartments + str(departmentId) + ','

        strStatus = ''
        for statusId in statusIdList:
            strStatus = strStatus + str(statusId) + ','

        url = KAYAKO_ENDPOINT + '/Tickets/Ticket/ListAll/' + strDepartments + '/' + strStatus + '/-1/' + str(
            userid) + '/-1/-1/-1/-1'

        r = requests.get(url, params=self.params)

        ticketList = []

        tickets = ET.fromstring(r.text)
        for ticket in tickets:
            ticketItem = Ticket()
            statusId = ticket.find('./statusid').text

            if int(statusId) in statusIdList:
                ticketItem.id = ticket.attrib['id']
                ticketItem.displayid = ticket.find('./displayid').text
                ticketItem.statusid = statusId
                ticketItem.lastactivity = datetime.datetime.fromtimestamp(
                    int(ticket.find('./lastactivity').text)).strftime("%d/%m/%Y %H:%M")
                ticketItem.subject = ticket.find('./subject').text
                ticketList.append(ticketItem)

        return ticketList

    def get_ticketLightByDisplayID(self, ticketDisplayID):
        """
        Questo metodo preleva i dati di un ticket, partendo dal codice del ticket
        :return: un ticket, di cui sono valorizzate le sole proprietà id ed email
        """

        url = KAYAKO_ENDPOINT + '/Tickets/Ticket/'+ ticketDisplayID

        r = requests.get(url, params=self.params)

        ticketItem = Ticket()
        tickets = ET.fromstring(r.text)
        for ticket in tickets:
            ticketItem.id = ticket.attrib['id']
            ticketItem.email = ticket.find('./email').text


        return ticketItem

    def getTicketAttachments(self, ticketid):
        """
        Questo metodo recupera i metadati degli attachment di un ticket
        :return: una lista di attachment in cui non è valorizzato il contents
        """

        url = KAYAKO_ENDPOINT + '/Tickets/TicketAttachment/ListAll/'+ ticketid

        r = requests.get(url, params=self.params)

        postAttachmentList = []
        postAttachmentItem = Attachment()
        postAttachments = ET.fromstring(r.text)
        for postAttachment in postAttachments:
            postAttachmentItem.id = postAttachment.find('./id').text
            postAttachmentItem.filename = postAttachment.find('./filename').text
            postAttachmentItem.filesize = postAttachment.find('./filesize').text
            postAttachmentItem.filetype = postAttachment.find('./filetype').text
            postAttachmentList.append(postAttachmentItem)

        return postAttachmentList

    def get_attachment(self, endpoint, parentID, attachmentID):
        """
        Questo metodo recupera un entità attachment da un endpoint che sia del tipo /$endpoint$/$parendID$/$attachmentID$/
        :return: un attachment, compreso di metadati e di contenuto
        """

        url = KAYAKO_ENDPOINT + endpoint + parentID + '/' + attachmentID

        r = requests.get(url, params=self.params)

        attachmentItem = Attachment()
        attachments = ET.fromstring(r.text)
        for attachment in attachments:
            attachmentItem.id = attachment.find('./id').text
            attachmentItem.filename = attachment.find('./filename').text
            attachmentItem.filetype = attachment.find('./filetype').text
            attachmentItem.filesize = attachment.find('./filesize').text
            attachmentItem.contents = attachment.find('./contents').text

        return attachmentItem

    def get_ticketByDisplayID(self, ticketDisplayID):
        """
        Questo metodo recupera tutti in dati di un ticket (metadati, post ed allegati) ricevendo in input il codice del ticket
        :return: il ticket con la lista di post e la lista di attachment
        """

        url = KAYAKO_ENDPOINT + '/Tickets/Ticket/'+ ticketDisplayID

        r = requests.get(url, params=self.params)

        ticketItem = Ticket()
        tickets = ET.fromstring(r.text)
        for ticket in tickets:
            statusId = ticket.find('./statusid').text
            ticketItem.id = ticket.attrib['id']
            ticketItem.displayid = ticket.find('./displayid').text
            ticketItem.statusid = statusId
            ticketItem.lastactivity = datetime.datetime.fromtimestamp(
                int(ticket.find('./lastactivity').text)).strftime("%d/%m/%Y %H:%M")
            ticketItem.subject = ticket.find('./subject').text
            ticketItem.lastreplier = ticket.find('./lastreplier').text
            ticketItem.email = ticket.find('./email').text

            ticketPostItemList = []


            posts = ticket.find('./posts')
            for post in posts:
                ticketPostItem = TicketPost()
                ticketPostItem.id = post.find('./id').text
                ticketPostItem.dateline =  datetime.datetime.fromtimestamp(
                    int(post.find('./dateline').text)).strftime("%d/%m/%Y %H:%M")
                ticketPostItem.fullname = post.find('./fullname').text
                ticketPostItem.hasattachments = post.find('./hasattachments').text
                ticketPostItem.contents = post.find('./contents').text
                ticketPostItemList.append(ticketPostItem)

            ticketItem.ticketPostItemList = ticketPostItemList
            ticketItem.attachmentList = self.getTicketAttachments(ticketItem.id)

        return ticketItem

    def get_userIdByEmail(self, userEmail=None):
        """
        Questo metodo recupera l'id dell'utente kayako partendo dal suo indirizzo email
        :return: un intero con l'identificativo utente
        """
        self.params.update( { 'query': userEmail, 'email': '1'} )

        url = KAYAKO_ENDPOINT + '/Base/UserSearch'

        r = Request(url, urlencode(self.params).encode())
        xml = ET.fromstring(urlopen(r).read().decode())
        useridElem = xml.find('./user/id', None)
        userid = None if useridElem is None else useridElem.text

        return userid

    def listeTicket(self,email):
        """
        Questo metodo ottiene la lista dei ticket suddivisi in: in_attesa_di_risposta, in_lavorazione, chiusi
        :return: una lista di tuple (descrizione, numero, codifica)
        """

        attesa_risposta, in_lavorazione, chiusi = self.get_ticketCounts(KayakoRESTService().get_departments_ids(),[TICKET_APERTO,TICKET_IN_LAVORAZIONE,TICKET_CHIUSO,TICKET_ATTESA_RISPOSTA], self.get_userIdByEmail(email))

        liste = [('In attesa di risposta', attesa_risposta, 'attesa_risposta'),
                 ('In lavorazione', in_lavorazione, 'in_lavorazione'),
                 ('Chiusi', chiusi, 'chiusi')
                 ]

        return liste

    def createTicket(self, mittente, subject, fullname, email, contents, departmentid, persona=None, ticketstatusid=TICKET_APERTO, ticketpriorityid=DEFAULT_TICKET_PRIORITY_ID, tickettypeid=DEFAULT_TICKET_TYPE_ID, autouserid=DEFAULT_AUTO_USER_ID):
        """
        Questo metodo crea un ticket su kayako
        :return: la terna di valori ticketID, ticketPostID, ticketDisplayID
        """

        from django.template.loader import get_template

        corpo={
            "testo": contents,
            "mittente": mittente,
            "persona": persona
        }
        m = get_template("modello_testo_ticket.html").render(corpo)

        params = {'subject': subject,
                  'fullname': fullname,
                  'email': email,
                  'contents': m,
                  'departmentid': departmentid,
                  'ticketstatusid': ticketstatusid,
                  'ticketpriorityid': ticketpriorityid,
                  'tickettypeid': tickettypeid,
                  'autouserid': autouserid
                  }

        self.params.update(params)
        url = KAYAKO_ENDPOINT + '/Tickets/Ticket'
        r = Request(url, urlencode(self.params).encode())
        xml = urlopen(r).read().decode()

        tickets = ET.fromstring(xml)

        ticketID = tickets.find('./ticket').attrib['id']
        ticketPostID = tickets.find('./ticket/posts/post/id', None).text
        ticketDisplayID = tickets.find('./ticket/displayid', None).text

        return ticketID, ticketPostID, ticketDisplayID


    def createTicketPost(self, me, ticketId, contents, filename, filecontent = None):
        """
        Questo metodo aggiunge un post con eventualmente un allegato, ad un ticket già presente
        :return:
        """
        params = {'ticketid': ticketId,
                  'contents': contents,
                  'userid': KayakoRESTService().get_userIdByEmail(me.email),
                  'filename': filename,
                  'isprivate': 0
                  }

        if filecontent:
            self.params.update({ 'filecontent': filecontent })

        self.params.update(params)
        url = KAYAKO_ENDPOINT + '/Tickets/TicketPost'
        r = Request(url, urlencode(self.params).encode())
        xml = urlopen(r).read().decode()

        return

    def addTicketAttachment(self, ticketId, ticketPostId, filename, filecontent):
        """
        Questo metodo aggiunge un attachment ad un ticket
        :return:
        """
        params = {

            'ticketid' : ticketId,
            'ticketpostid': ticketPostId,
            'filename':filename,
            'contents': filecontent
        }

        self.params.update(params)
        url = KAYAKO_ENDPOINT + '/Tickets/TicketAttachment'

        r = Request(url, urlencode(self.params).encode())
        xml = urlopen(r).read().decode()

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
        xml = urlopen(r).read().decode()

        return