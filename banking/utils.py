import random
import string
from datetime import datetime, timedelta

def generate_bank_account_id(length=10):
    """
    Generate a random bank account number of specified length.
    
    Args:
        length (int): The length of the account number. Default is 10.
    
    Returns:
        str: A random bank account number as a string.
    """
    account_number = ''.join([str(random.randint(0, 9)) for _ in range(length)])
    return account_number

def generate_albanian_iban():
    """
    Generate a random IBAN for Albania.
    
    IBAN format for Albania:
    - Starts with 'AL'
    - 2-digit checksum (random)
    - 4-character bank identifier (random letters)
    - 20 alphanumeric characters for the account number (digits and uppercase letters)
    
    Returns:
        str: A random Albanian IBAN.
    """
    # Generate random 2-digit checksum
    checksum = ''.join([str(random.randint(0, 9)) for _ in range(2)])
    
    # Generate random 4-character bank identifier (only uppercase letters)
    bank_identifier = ''.join(random.choices(string.ascii_uppercase, k=4))
    
    # Generate random 20-character account number (digits and uppercase letters)
    account_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
    
    # Construct the IBAN
    iban = f"AL{checksum}{bank_identifier}{account_number}"
    return iban

def luhn_checksum(card_number):
    """
    Calculate the Luhn checksum of a credit card number.
    
    Args:
        card_number (list of int): The card number as a list of digits.
    
    Returns:
        int: The Luhn checksum.
    """
    def digits_of(n):
        return [int(d) for d in str(n)]
    
    digits = card_number
    checksum = 0
    
    # Start from the rightmost digit, and double every second digit
    for i, digit in enumerate(reversed(digits)):
        if i % 2 == 1:
            doubled = digit * 2
            if doubled > 9:
                doubled -= 9
            checksum += doubled
        else:
            checksum += digit
    
    return checksum % 10

def generate_credit_card(prefix, length=16):
    """
    Generate a valid random credit card number using the Luhn algorithm.
    
    Args:
        prefix (list of int): The starting digits of the card (e.g., [4] for Visa).
        length (int): Total length of the card number. Default is 16.
    
    Returns:
        str: A valid credit card number as a string.
    """
    # Create an empty list for the card number, starting with the prefix
    card_number = prefix
    
    # Randomly generate the remaining digits (except the last one, which is the check digit)
    while len(card_number) < (length - 1):
        card_number.append(random.randint(0, 9))
    
    # Calculate the Luhn check digit
    check_digit = luhn_checksum(card_number)
    check_digit = 0 if check_digit == 0 else 10 - check_digit
    
    # Append the check digit to the card number
    card_number.append(check_digit)
    
    # Return the card number as a string
    return ''.join(map(str, card_number))


def generate_credit_card_visa():
    """
    Generate a random Visa credit card number.
    
    Returns:
        str: A random Visa credit card number.
    """
    return generate_credit_card([4])

def generate_cvv():
    """
    Generate a random 3-digit CVV.
    
    Returns:
        str: A random 3-digit CVV.
    """
    return str(random.randint(100, 999))

def generate_expiry_date(years_valid=5):
    """
    Generate a random expiration date for a credit card.
    The expiration date is set between 1 and `years_valid` years from the current date.
    
    Args:
        years_valid (int): The maximum number of years the card can be valid for. Default is 5 years.
    
    Returns:
        str: A random expiration date in the format MM/YY.
    """
    # Current date
    now = datetime.now()
    
    # Generate a random number of months from now, ensuring it's at least 1 month and within `years_valid` years
    expiry_months = random.randint(1, years_valid * 12)
    expiry_date = now + timedelta(days=expiry_months * 30)  # Approximation of months

    # Format the expiration date as MM/YY
    return expiry_date.strftime("%Y-%m-%d")

def generate_transaction_id(prefix='TXN'):
    """
    Generate a unique transaction ID.
    
    Args:
        prefix (str): A prefix for the transaction ID. Default is 'TXN'.
    
    Returns:
        str: A unique transaction ID.
    """
    # Generate a random 8-character alphanumeric string
    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    # Get the current timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Combine prefix, timestamp, and random string to create a unique transaction ID
    transaction_id = f"{prefix}-{timestamp}-{random_string}"
    
    return transaction_id


