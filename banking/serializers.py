from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Role, User, Transaction, \
                    Card, Currency, TransactionType, \
                    CardType, BankAccountApplication, \
                    BankAccount, CardApplication, ApplicationStatus

class ApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationStatus
        fields = '__all__'

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'

class TransactionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionType
        fields = '__all__'

class CardTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardType
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # Hide the password in response
    role = serializers.CharField(required=False)  # Role is not required in the request
    class Meta:
        model = User
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['role'] = RoleSerializer(instance.role).to_representation(instance.role)
        return data

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)

    def validate(self, data):
        request = self.context.get('request')
        authUser = request.user  

        # Role validation
        if 'role' in data:
            role = Role.objects.get(pk=data['role'])
            data['role'] = role
            if request.method == 'POST':
                if authUser.role.admin_permission and not data['role'].banker_permission:
                    raise serializers.ValidationError('Admin can only create banker')
                elif authUser.role.banker_permission and not data['role'].client_permission:
                    raise serializers.ValidationError('Banker can only create client')
                elif authUser.role.client_permission:
                    raise serializers.ValidationError('Client cannot create a user')
            
            if request.method == 'PUT':
                if authUser.role.admin_permission and not data['role'].banker_permission:
                    raise serializers.ValidationError('Admin can only update banker')
                elif authUser.role.banker_permission and not data['role'].client_permission:
                    raise serializers.ValidationError('Banker can only update client')
                elif authUser.role.client_permission:
                    raise serializers.ValidationError('Client cannot update a user')
                
        # If role is not in data then set the role based on the currently logged-in user
        else:
            if request.method == 'POST':
                if authUser.role.admin_permission:
                    data['role'] = Role.objects.get(banker_permission=True)
                elif authUser.role.banker_permission:
                    data['role'] = Role.objects.get(client_permission=True)
                else:
                    raise serializers.ValidationError('You do not have permission to create a user')

        return super().validate(data)

class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = '__all__'

    def to_representation(self, instance):
        authUser = self.context.get('request').user

        if authUser.role.client_permission and instance.user.id != authUser.id:
            data = {}
            data['id'] = instance.id
            data['IBAN'] = instance.IBAN
            data['user'] = {'id': instance.user.id} 
            data['currency'] = CurrencySerializer(instance.currency).to_representation(instance.currency)
            return data
        
        data = super().to_representation(instance)

        data['currency'] = CurrencySerializer(instance.currency).to_representation(instance.currency)
        data['user'] = {'id': instance.user.id, 'username': instance.user.username} 
        return data
    
class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'        

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['type'] = CardTypeSerializer(instance.type).to_representation(instance.type)
        return data

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class BankAccountApplicationSerializer(serializers.ModelSerializer):
    user = serializers.CharField(required=False)
    status = serializers.CharField(required=False)
    class Meta:
        model = BankAccountApplication
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = instance.user.id
        data['status'] = ApplicationStatusSerializer(instance.status).to_representation(instance.status)
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        authUser = request.user

        data = {
            'user': authUser,
            'status': ApplicationStatus.objects.get(status='pending'),
            'currency': validated_data['currency'],
        }

        return super().create(data)

class CardApplicationSerializer(serializers.ModelSerializer):
    user = serializers.CharField(required=False)
    status = serializers.CharField(required=False)

    class Meta:
        model = CardApplication
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = instance.user.id
        data['bank_account'] = instance.bank_account.id
        data['type'] = instance.type.id
        data['status'] = ApplicationStatusSerializer(instance.status).to_representation(instance.status)
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        authUser = request.user

        data = {
            'user': authUser,
            'bank_account': validated_data['bank_account'],
            'type': validated_data['type'],
            'monthly_salary': validated_data['monthly_salary'],
            'status': ApplicationStatus.objects.get(status='pending')
        }

        return super().create(data)
    
    def validate(self, data):
        request = self.context.get('request')
        authUser = request.user
        
        if data['monthly_salary'] < 500:
            raise serializers.ValidationError('Monthly limit should be at least 500')

        if data['bank_account'].user.id != authUser.id:
            raise serializers.ValidationError('Bank account does not belong to the user')

                
        return super().validate(data)




