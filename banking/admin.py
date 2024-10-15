from django.contrib import admin
from .models import Role, User, Transaction, \
                    Card, Currency, TransactionType, \
                    CardType, BankAccountApplication, \
                    BankAccount, ApplicationStatus, CardApplication

# Register your models here.
admin.site.register(ApplicationStatus )
admin.site.register(Role )
admin.site.register(User)
admin.site.register(BankAccount)
admin.site.register(Transaction)
admin.site.register(Card)
admin.site.register(Currency)
admin.site.register(TransactionType)
admin.site.register(CardType)
admin.site.register(BankAccountApplication)
admin.site.register(CardApplication)