TICKET_APERTO=1
TICKET_IN_LAVORAZIONE=2
TICKET_CHIUSO=3
TICKET_ATTESA_RISPOSTA=4
DEFAULT_TICKET_PRIORITY_ID=1
DEFAULT_TICKET_TYPE_ID=1
DEFAULT_AUTO_USER_ID=1

#MAPPA STATUS_TICKET: codice stato - decrizione stato
STATUS_TICKET = {str(TICKET_APERTO):"Aperto",
                 str(TICKET_IN_LAVORAZIONE):"In lavorazione",
                 str(TICKET_CHIUSO):"Chiuso",
                 str(TICKET_ATTESA_RISPOSTA):"In attesa di risposta"}

#ID SEZIONI FORM SUPPORTO
SEZ_INF = "INF" #PRIMO LIVELLO
SEZ_REQ = "REQ" #SECONDO LIVELLO
SEZ_INC = "INC" #TERZO LIVELLO
SEZ_FEE = "FEE" #FEEDBACK
SEZ_BLO = "BLO" #SANGUE
SEZ_SVI = "SVI" #AREA SVILUPPO

#TABELLA DI MAPPING ID SEZIONE - DESCRIZIONE SEZIONE
TIPO_RICHIESTA = (
    (None, "-- Seleziona una opzione --"),
    (SEZ_INF, "Informazione: Aiuto con l'utilizzo di Gaia"),
    (SEZ_REQ, "Richiesta: Modifica informazioni o correzioni"),
    (SEZ_INC, "Incidente: Errori o segnalazioni di sicurezza"),
    (SEZ_SVI, "Area VI: Ripristino password e richieste e-mail istituzionali (@cri.it, PEC)"),
    (SEZ_BLO, "Feedback in merito alla donazione sangue"),
    (SEZ_FEE, "Feedback GAIA (suggerimenti, critiche, idee)")
)

#TODO gestire il mapping corretto tra sezione e dipartimento
#TABELLA DI MAPPING ID SEZIONE - CODICE DIPARTIMENTO
TIPO_RICHIESTA_DIPARTIMENTO = {SEZ_INF: "137", #TEST API
                               SEZ_REQ: "137", #TEST API
                               SEZ_INC: "137", #TEST API
                               SEZ_FEE: "137", #TEST API
                               SEZ_BLO: "137", #TEST API
                               SEZ_SVI: "137"} #TEST API

#usato in supporto_modello_testo_ticket.html per determinare il testo
#da mostrare solo allo staff e non all'utente
TEXT_BREAK_STAFF = "<strong>Informazioni tecniche associate:</strong>"

