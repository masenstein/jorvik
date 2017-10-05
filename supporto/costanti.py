from jorvik.settings import KAYAKO_DEPARTMENT_MAPPING
import ast


TICKET_APERTO=1
TICKET_IN_LAVORAZIONE=2
TICKET_CHIUSO=3
TICKET_ATTESA_RISPOSTA=4
DEFAULT_TICKET_TYPE_ID=1
DEFAULT_AUTO_USER_ID=1
TICKET_PRIORITY_NORMALE=1
TICKET_PRIORITY_BASSA=7

# MAPPA STATUS_TICKET: codice stato - decrizione stato
STATUS_TICKET = {str(TICKET_APERTO): "Aperto",
                 str(TICKET_IN_LAVORAZIONE): "In carico allo staff",
                 str(TICKET_CHIUSO): "Chiuso",
                 str(TICKET_ATTESA_RISPOSTA): "In attesa di una tua risposta"}

#ID SEZIONI FORM SUPPORTO

SEZ_INF = "INF"  # PRIMO LIVELLO
SEZ_REQ = "REQ"  # SECONDO LIVELLO
SEZ_INC = "INC"  # TERZO LIVELLO
SEZ_FEE = "FEE"  # FEEDBACK
SEZ_BLO = "BLO"  # SANGUE
SEZ_SVI = "SVI"  # AREA SVILUPPO

# TABELLA DI MAPPING ID SEZIONE - DESCRIZIONE SEZIONE
TIPO_RICHIESTA = (
    (None, "-- Seleziona una opzione --"),
    (SEZ_INF, "Informazione: Aiuto con l'utilizzo di Gaia"),
    (SEZ_REQ, "Richiesta: Modifica informazioni o correzioni"),
    (SEZ_INC, "Incidente: Errori o segnalazioni di sicurezza"),
    (SEZ_SVI, "Area VI: Ripristino password e richieste e-mail istituzionali (@cri.it, PEC)"),
    (SEZ_BLO, "Feedback in merito alla donazione sangue"),
    (SEZ_FEE, "Feedback GAIA (suggerimenti, critiche, idee)")
)

# TABELLA DI MAPPING ID SEZIONE - CODICE DIPARTIMENTO
department_mapping = ast.literal_eval(KAYAKO_DEPARTMENT_MAPPING)
TIPO_RICHIESTA_DIPARTIMENTO = {SEZ_INF: department_mapping.get(SEZ_INF),  # Gaia 1° livello
                               SEZ_REQ: department_mapping.get(SEZ_REQ),  # Gaia 2° livello
                               SEZ_INC: department_mapping.get(SEZ_INC),  # Gaia 2° livello
                               SEZ_FEE: department_mapping.get(SEZ_FEE),  # Feedback
                               SEZ_BLO: department_mapping.get(SEZ_BLO),  # Donazioni Sangue
                               SEZ_SVI: department_mapping.get(SEZ_SVI)}  # Informatica

# mapping tra tipo segnalazione e (ticket_priority_id,ticket_status_id)
TIPO_RICHIESTA_PRIORITA_STATO = {SEZ_INF: (TICKET_PRIORITY_BASSA, TICKET_APERTO),
                                 SEZ_REQ: (TICKET_PRIORITY_NORMALE, TICKET_APERTO),
                                 SEZ_INC: (TICKET_PRIORITY_NORMALE, TICKET_APERTO),
                                 SEZ_FEE: (TICKET_PRIORITY_NORMALE, TICKET_CHIUSO),
                                 SEZ_BLO: (TICKET_PRIORITY_NORMALE, TICKET_APERTO),
                                 SEZ_SVI: (TICKET_PRIORITY_NORMALE, TICKET_APERTO)}

# usato in supporto_modello_testo_ticket.html per determinare il testo
# da mostrare solo allo staff e non all'utente
TEXT_BREAK_STAFF = "<strong>Informazioni tecniche associate:</strong>"

PAGINAZIONE_LISTE = 10

