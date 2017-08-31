# raccolta di classi con i nomi dei campi reperiti dalle chiamate rest di kayako
class KbArticle(object):
    kbarticleid = None
    subject = None
    contentstext = None
    contents = None
    author = None
    dateline = None
    attachmentList = []

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
    ticketPostItemList = []
    attachmentList = []

    def __repr__(self):
        return (
            'id={}, displayid={}, lastactivity={}, departmentid={}, statusid={}, typeid={}, priorityid={}, lastreplier={}, email={}, ticketPostItemList={}'.format(
                self.id,
                self.displayid,
                self.lastactivity,
                self.departmentid,
                self.statusid,
                self.typeid,
                self.priorityid,
                self.lastreplier,
                self.email,
                self.ticketPostItemList))


class Tipologiche():

    from supporto.services import KayakoRESTService
    # recuperiamo i dati delle entità tipologiche (che non variano nel tempo)
    STATUS_TICKET = dict(KayakoRESTService().get_ticketStatus())
    PRIORITY_TICKET = dict(KayakoRESTService().get_ticketPriority())
    TYPE_TICKET = dict(KayakoRESTService().get_ticketType())
    DEPARTMENT_TICKET = dict(KayakoRESTService().get_departments())