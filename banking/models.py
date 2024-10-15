from datetime import datetime
from django.db import models
from django.contrib.auth.hashers import make_password, check_password

# Create your models here.
class ApplicationStatus(models.Model):
    id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=10, unique=True)

    def __name__(self):
        return self.status

class Role(models.Model):
    id = models.AutoField(primary_key=True)
    role = models.CharField(max_length=25, unique=True)

    admin_permission = models.BooleanField(default=False)
    banker_permission = models.BooleanField(default=False)
    client_permission = models.BooleanField(default=False)

    def __name__(self):
        return self.role

class Currency(models.Model):
    id = models.AutoField(primary_key=True)
    currency = models.CharField(max_length=10, unique=True)
    sign = models.CharField(max_length=1)

    def __name__(self):
        return self.currency

class TransactionType(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=10, unique=True)

    def __name__(self):
        return self.type

class CardType(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=10, unique=True)

    def __name__(self):
        return self.type


class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=90)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    date = models.DateField(auto_now=True)

    # Add fields required for django authentication 
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Check if the password is already hashed
        if not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super(User, self).save(*args, **kwargs)

    def __name__(self):
        return self.username

class BankAccount(models.Model):
    id = models.AutoField(primary_key=True)
    bank_account_id = models.IntegerField(unique=True)
    IBAN = models.CharField(max_length=34, unique=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now=True)
    bankApplication = models.ForeignKey('BankAccountApplication', on_delete=models.CASCADE, blank=True, null=True)

    def __name__(self):
        return self.bank_account_id

class Card(models.Model):
    id = models.AutoField(primary_key=True)
    card_number = models.CharField(max_length=16, unique=True)
    expiry_date = models.DateField()
    cvv = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    type = models.ForeignKey(CardType, on_delete=models.CASCADE)
    date = models.DateField(auto_now=True)
    cardApplication = models.ForeignKey('CardApplication', on_delete=models.CASCADE, blank=True, null=True)

    def __name__(self):
        return self.card_number

class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    transaction_id = models.CharField(max_length=30, unique=True)
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    type = models.ForeignKey(TransactionType, on_delete=models.CASCADE)
    date = models.DateField()

    def __name__(self):
        return self.transaction_id

class BankAccountApplication(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    status = models.ForeignKey(ApplicationStatus, on_delete=models.CASCADE)

    date = models.DateField(auto_now=True)

    def __name__(self):
        return self.id

class CardApplication(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    type = models.ForeignKey(CardType, on_delete=models.CASCADE)
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.ForeignKey(ApplicationStatus, on_delete=models.CASCADE)
    date = models.DateField(auto_now=True)
    reason = models.CharField(max_length=100, blank=True, null=True)

    def __name__(self):
        return self.id