from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

class CustomPasswordValidator():
    """
        Die Klasse des eigenen Passwort-Validierers.
        """


    def __init__(self, min_length=1):
        self.min_length = min_length

    def validate(self, password, user=None):
        """
            Funktion für das Validieren von Passwörtern
                Jeder String einer Fehlenden Eigenschaft wird, wenn 
                zutreffend, einer Liste zugefügt und am Ende als ValidationError zurückgegeben.
            """
        mind_Laenge           = 8  # Mindest Länge eines Passworts
        vorkommenAnzahl       = 1  # Mindest Anzahl der vorkommenden Eigenschaften
        fehlendeEigenschaften = [] # Liste mit allen fehlenden Eigenschaften
        sonderzeichen         = "[~\!@#\$%\^&\*\(\)_\+{}\":;'\[\]]"
        

        if (len(password) < 8):
            fehlendeEigenschaften.append('Passwort muss  mind. %d Zeichen enthalten.' % mind_Laenge)

        if not any(zeichen.isdigit() for zeichen in password):
            fehlendeEigenschaften.append('Passwort muss mind. %d Zahlen enthalten.' % vorkommenAnzahl)

        if not any(zeichen.isalpha() for zeichen in password):
            fehlendeEigenschaften.append('Passwort muss mind. %d Buchstaben enthalten.' % vorkommenAnzahl)

        if not any(zeichen in sonderzeichen for zeichen in password):
            fehlendeEigenschaften.append('Passwort muss mind. %d Sonderzeichen enthalten.' % vorkommenAnzahl)
            
        if(len(fehlendeEigenschaften) > 0):
            raise ValidationError(fehlendeEigenschaften)

    def get_help_text(self):
        # Muss überschrieben werden
        return ""      