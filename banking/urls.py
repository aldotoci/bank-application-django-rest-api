from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RoleViewSet, TransactionViewSet, \
                    CardViewSet, CurrencyViewSet, TransactionTypeViewSet, \
                    CardTypeViewSet, BankAccountApplicationViewSet, \
                    BankAccountViewSet,  CardApplicationViewSet, \
                    ApplicationStatusViewSet, \
                    loginView, logoutView, bankApplicationBankerAction, \
                    cardApplicationBankerAction, transfer_money, get_current_user

router = DefaultRouter()

router.register(r'roles', RoleViewSet)
router.register(r'application-statuses', ApplicationStatusViewSet)
router.register(r'currencies', CurrencyViewSet)
router.register(r'card-types', CardTypeViewSet)
router.register(r'transaction-types', TransactionTypeViewSet)
router.register(r'users', UserViewSet)
router.register(r'bank-accounts', BankAccountViewSet)
router.register(r'cards', CardViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'bank-account-applications', BankAccountApplicationViewSet)
router.register(r'card-applications', CardApplicationViewSet)


urlpatterns = [
    path('login/', loginView),
    path('logout/', logoutView),
    path('bank-account-applications/<int:pk>/banker-action/', bankApplicationBankerAction),
    path('card-applications/<int:pk>/banker-action/', cardApplicationBankerAction),
    path('transfer-money/', transfer_money),
    path('get-current-user/', get_current_user),
    path('', include(router.urls)),
]




