  
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from account.models import Account

# Hier wird das Account model für den Admin Panel verfügbar. Zusätzlich werden hier noch die Felder für das Admin Panel angepasst.

class AccountAdmin(UserAdmin):
	list_display    = ('email', 'username', 'date_joined', 'last_login', 'is_admin', 'is_staff')
	search_fields   = ('email', 'username',)
	readonly_fields = ('date_joined', 'last_login')

	filter_horizontal = ()
	list_filter 	  = ()
	fieldsets 		  = ()

admin.site.register(Account, AccountAdmin)