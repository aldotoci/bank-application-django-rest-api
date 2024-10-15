from datetime import datetime

from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError, FieldError


from django.contrib.auth import login, logout, authenticate

from .utils import generate_bank_account_id, generate_albanian_iban, \
                    generate_credit_card_visa, generate_cvv, generate_expiry_date, \
                    generate_transaction_id

from .models import Role, User, Transaction, \
                    Card, Currency, TransactionType, \
                    CardType, BankAccountApplication, \
                    BankAccount, CardApplication, ApplicationStatus

from .serializers import RoleSerializer, UserSerializer, TransactionSerializer, \
                         CardSerializer, CurrencySerializer, TransactionTypeSerializer, \
                         CardTypeSerializer, BankAccountApplicationSerializer, \
                         BankAccountSerializer, CardApplicationSerializer, ApplicationStatusSerializer

from .permissions import IsAdminUser, IsBankerUser, \
                        IsClientUser, IsLoggedIn, \
                        ClientReadOnlyPermission, \
                        ClientApplicationPermission, BankerReadOnlyPermission


@api_view(['POST'])
def loginView(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(request=request, username=username, password=password)
    
    if user:
        login(request, user)
        return Response({'message': 'User logged in', 'user': UserSerializer(user).data}, status=200)
    return Response({'error': 'Invalid credentials'}, status=400)


@api_view(['POST'])
def logoutView(request):
    logout(request)
    return Response({'message': 'User logged out'})


@api_view(['GET'])
@permission_classes([IsLoggedIn])
def get_current_user(request):
    user = request.user
    print('user', user)
    serializer = UserSerializer(user)
    data = serializer.data
    print('data', data)
    return Response(data, status=200)

class ApplicationStatusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ApplicationStatus.objects.all()
    serializer_class = ApplicationStatusSerializer
    permission_classes = [IsLoggedIn]

class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsLoggedIn, IsAdminUser]

class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [IsLoggedIn]

class CardTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CardType.objects.all()
    serializer_class = CardTypeSerializer
    permission_classes = [IsLoggedIn] 

class TransactionTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TransactionType.objects.all()
    serializer_class = TransactionTypeSerializer
    permission_classes = [IsLoggedIn]

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsLoggedIn, IsAdminUser | IsBankerUser | ClientReadOnlyPermission]

    def get_serializer_context(self):
        # Include the request in the serializer context
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def list(self, request, *args, **kwargs):
        authUser = request.user

        # Check the user's role and permissions
        if authUser.role.admin_permission:
            queryset = self.get_queryset().filter(role__banker_permission=True)
        elif authUser.role.banker_permission:
            queryset = self.get_queryset().filter(role__client_permission=True)
        else:
            queryset = self.get_queryset().filter(id=authUser.id)
        
        serializer = self.get_serializer(queryset, many=True)
        
        return Response(serializer.data, status=200)

class BankAccountViewSet(viewsets.ModelViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer
    permission_classes = [IsLoggedIn, IsBankerUser | ClientReadOnlyPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'currency', 'balance']

    def get_serializer_context(self):
        # Include the request in the serializer context
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def list(self, request, *args, **kwargs):
        authUser = request.user

        if authUser.role.banker_permission or authUser.role.admin_permission:
            queryset = self.get_queryset()
        else:
            # queryset = self.get_queryset().filter(user=authUser)
            queryset = self.get_queryset()

        # Apply filters based from the auth user's role
        queryset = self.filter_queryset(queryset)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=200)

class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [IsLoggedIn, IsBankerUser | ClientReadOnlyPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['bank_account', 'type', 'user']

    def get_serializer_context(self):
        # Include the request in the serializer context
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def list(self, request, *args, **kwargs):
        authUser = request.user

        if authUser.role.banker_permission or authUser.role.admin_permission:
            queryset = self.get_queryset()
        else:
            queryset = self.get_queryset().filter(user=authUser)

        # Apply filters based from the auth user's role
        queryset = self.filter_queryset(queryset)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=200)

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsLoggedIn, BankerReadOnlyPermission | ClientReadOnlyPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['bank_account', 'type', 'date', 'currency']

    def get_serializer_context(self):
        # Include the request in the serializer context
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def list(self, request, *args, **kwargs):
        authUser = request.user

        if authUser.role.banker_permission or authUser.role.admin_permission:
            queryset = self.get_queryset()
        else:
            queryset = self.get_queryset().filter(bank_account__user=authUser)

        # Apply filters based from the auth user's role
        queryset = self.filter_queryset(queryset)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=200)
    
class BankAccountApplicationViewSet(viewsets.ModelViewSet):
    queryset = BankAccountApplication.objects.all()
    serializer_class = BankAccountApplicationSerializer
    permission_classes = [IsLoggedIn, BankerReadOnlyPermission | ClientApplicationPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'user', 'currency', 'date']

    def list(self, request, *args, **kwargs):
        authUser = request.user

        if authUser.role.banker_permission or authUser.role.admin_permission:
            queryset = self.get_queryset()
        else:
            queryset = self.get_queryset().filter(user=authUser)

        # Apply filters based from the auth user's role
        queryset = self.filter_queryset(queryset)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=200)

    def get_serializer_context(self):
        # Include the request in the serializer context
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class CardApplicationViewSet(viewsets.ModelViewSet):
    queryset = CardApplication.objects.all()
    serializer_class = CardApplicationSerializer
    permission_classes = [IsLoggedIn, BankerReadOnlyPermission | ClientApplicationPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'user', 'reason', 'date']

    def get_serializer_context(self):
        # Include the request in the serializer context
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def list(self, request, *args, **kwargs):
        authUser = request.user

        if authUser.role.banker_permission or authUser.role.admin_permission:
            queryset = self.get_queryset()
        else:
            queryset = self.get_queryset().filter(user=authUser)

        # Apply filters based from the auth user's role
        queryset = self.filter_queryset(queryset)
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=200)

@api_view(['POST'])
@permission_classes([IsLoggedIn, IsBankerUser])
def bankApplicationBankerAction(request, pk):
    print('pk', pk)
    data = request.data
    applicationApplication = BankAccountApplication.objects.get(pk=pk)

    if 'action' not in data:
        return Response({'error': 'Action is required'}, status=400)
    
    applicationStatus = ApplicationStatus.objects.filter(status=data['action']).exists()

    if not applicationStatus:
        return Response({'error': 'Invalid action'}, status=400)
    
    applicationStatus = ApplicationStatus.objects.get(status=data['action'])
    
    if applicationApplication.status.status != 'pending':
        return Response({'error': 'Application already processed'}, status=400)

    if applicationStatus.status == 'approved':
        # to do
        applicationApplication.status = applicationStatus

        bank_account_id = generate_bank_account_id()
        while BankAccount.objects.filter(bank_account_id=bank_account_id).exists():
            bank_account_id = generate_bank_account_id()

        IBAN = generate_albanian_iban()
        while BankAccount.objects.filter(IBAN=IBAN).exists():
            IBAN = generate_albanian_iban()


        # create bank account
        BankAccount.objects.create(
            bank_account_id=bank_account_id,
            IBAN=IBAN,
            currency=applicationApplication.currency, 
            user=applicationApplication.user,
            balance=0,
            bankApplication=applicationApplication
        )

        applicationApplication.save()
        return Response({'status': 'ok'})
    elif applicationStatus.status == 'rejected':
        applicationApplication.status = applicationStatus
        applicationApplication.save()
        return Response({'status': 'ok'})

    return Response({'error': 'Invalid action'}, status=400)

@api_view(['POST'])
@permission_classes([IsLoggedIn, IsBankerUser])
def cardApplicationBankerAction(request, pk):
    try:
        data = request.data
        cardApplication = CardApplication.objects.get(pk=pk)
        
        if 'action' not in data:
            return Response({'error': 'Action is required'}, status=400)

        if cardApplication.status.status != 'pending':
            return Response({'error': 'Application already processed'}, status=400)
        
        applicationStatus = ApplicationStatus.objects.filter(status=data['action']).exists()

        if not applicationStatus:
            return Response({'error': 'Invalid action'}, status=400)
        
        applicationStatus = ApplicationStatus.objects.get(status=data['action'])

        print('applicationStatus', applicationStatus)        

        if applicationStatus.status == 'approved':
            cardApplication.status = applicationStatus
            
            card_number = generate_credit_card_visa()
            while Card.objects.filter(card_number=card_number).exists():
                card_number = generate_credit_card_visa()

            card = Card.objects.create(
                card_number=card_number,
                expiry_date=generate_expiry_date(),
                cvv=generate_cvv(),
                user=cardApplication.user,
                bank_account=cardApplication.bank_account,
                type=cardApplication.type,
                cardApplication=cardApplication
            )
            
            card.save()
            cardApplication.save()
            return Response({'status': 'ok'})
        elif applicationStatus.status == 'rejected':
            if 'reason' not in data:
                return Response({'error': 'Reason is required'}, status=400)
            if not isinstance(data['reason'], str):
                return Response({'error': 'Reason is required'}, status=400)

            cardApplication.status = applicationStatus
            cardApplication.reason = data['reason']
            cardApplication.save()

            return Response({'status': 'ok'})
        
        return Response({'error': 'Invalid action'}, status=400)
    except (ValidationError, FieldError, ValueError) as e:
        return Response({'error': str(e)}, status=400)

    except Exception as e:
        print(e)
        return Response({'error': 'An error occurred'}, status=500)

@api_view(['POST'])
@permission_classes([IsLoggedIn, IsClientUser])
def transfer_money(request):
    # Create a debit transaction for the sender and a credit transaction for receiver

    data = request.data
    print("data", data)
    required_fields = {
        'amount': int, 
        'currency': int, 
        'bank_account': int, 
        'bank_account_receiver': int
    }

    for field, field_type in required_fields.items():
        if field not in data:
            return Response({'error': f'{field} is required'}, status=400)
        if not isinstance(data[field], field_type):
            return Response({'error': f'{field} must be an integer'}, status=400)

    try:
        amount = data['amount']
        currency = Currency.objects.get(pk=data['currency'])
        

        if not BankAccount.objects.filter(pk=data['bank_account']).exists():
            return Response({'error': 'Invalid bank account'}, status=400)
        
        if not BankAccount.objects.filter(pk=data['bank_account_receiver']).exists():
            return Response({'error': 'Invalid bank account receiver'}, status=400)


        bank_account = BankAccount.objects.get(pk=data['bank_account'])
        bank_account_receiver = BankAccount.objects.get(pk=data['bank_account_receiver'])
        
        if bank_account.user.id != request.user.id:
            return Response({'error': 'Invalid bank account'}, status=400)

        if amount <= 0:
            return Response({'error': 'Amount must be greater than 0'}, status=400)

        if bank_account.balance < amount:
            return Response({'error': 'Insufficient funds'}, status=400)
        
        # Check if the bank accounts have the same currency type
        if bank_account.currency.id != bank_account_receiver.currency.id:
            return Response({'error': 'Bank accounts have different currency types'}, status=400)

        # Check if the bank accounts have a card linked to them
        if not Card.objects.filter(bank_account=bank_account).exists():
            return Response({'error': 'Your bank account does not have a card linked'}, status=400)
        
        if not Card.objects.filter(bank_account=bank_account_receiver).exists():
            return Response({'error': 'Receiver bank account does not have a card linked'}, status=400)

        # Create a debit transaction for the bank account sender
        Transaction.objects.create(
            transaction_id=generate_transaction_id(),
            bank_account=bank_account,
            amount=-amount,
            currency=currency,
            type=TransactionType.objects.get(type='debit'),
            date=datetime.now()
        )

        # Create a credit transaction for the bank account receiver
        Transaction.objects.create(
            transaction_id=generate_transaction_id(),
            bank_account=bank_account_receiver,
            amount=amount,
            currency=currency,
            type=TransactionType.objects.get(type='credit'),
            date=datetime.now()
        )

        bank_account.balance -= amount
        bank_account_receiver.balance += amount

        bank_account.save()
        bank_account_receiver.save()

        return Response({'status': 'ok'})
    except (ValidationError, FieldError, ValueError) as e:
        return Response({'error': str(e)}, status=400)
    except Exception as e:
        print(e)
        return Response({'error': 'An error occurred'}, status=500)



     