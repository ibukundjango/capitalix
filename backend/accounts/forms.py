from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import AccountProfile, KYCProfile, NextOfKin, IdentityDocument, EmailVerification
import hashlib
from django.contrib.auth import authenticate
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
import re

def validate_file_size(file):
    max_size = 5 * 1024 * 1024  # 5MB
    if file.size > max_size:
        raise ValidationError("File size must be under 5MB.")


# ============================================================
# COUNTRY CHOICES - Full List
# ============================================================

COUNTRIES = [
    ('AF', 'Afghanistan'),
    ('AL', 'Albania'),
    ('DZ', 'Algeria'),
    ('AD', 'Andorra'),
    ('AO', 'Angola'),
    ('AG', 'Antigua and Barbuda'),
    ('AR', 'Argentina'),
    ('AM', 'Armenia'),
    ('AU', 'Australia'),
    ('AT', 'Austria'),
    ('AZ', 'Azerbaijan'),
    ('BS', 'Bahamas'),
    ('BH', 'Bahrain'),
    ('BD', 'Bangladesh'),
    ('BB', 'Barbados'),
    ('BY', 'Belarus'),
    ('BE', 'Belgium'),
    ('BZ', 'Belize'),
    ('BJ', 'Benin'),
    ('BT', 'Bhutan'),
    ('BO', 'Bolivia'),
    ('BA', 'Bosnia and Herzegovina'),
    ('BW', 'Botswana'),
    ('BR', 'Brazil'),
    ('BN', 'Brunei'),
    ('BG', 'Bulgaria'),
    ('BF', 'Burkina Faso'),
    ('BI', 'Burundi'),
    ('KH', 'Cambodia'),
    ('CM', 'Cameroon'),
    ('CA', 'Canada'),
    ('CV', 'Cape Verde'),
    ('CF', 'Central African Republic'),
    ('TD', 'Chad'),
    ('CL', 'Chile'),
    ('CN', 'China'),
    ('CO', 'Colombia'),
    ('KM', 'Comoros'),
    ('CG', 'Congo'),
    ('CD', 'Congo (Democratic Republic)'),
    ('CR', 'Costa Rica'),
    ('HR', 'Croatia'),
    ('CU', 'Cuba'),
    ('CY', 'Cyprus'),
    ('CZ', 'Czech Republic'),
    ('DK', 'Denmark'),
    ('DJ', 'Djibouti'),
    ('DM', 'Dominica'),
    ('DO', 'Dominican Republic'),
    ('EC', 'Ecuador'),
    ('EG', 'Egypt'),
    ('SV', 'El Salvador'),
    ('GQ', 'Equatorial Guinea'),
    ('ER', 'Eritrea'),
    ('EE', 'Estonia'),
    ('SZ', 'Eswatini'),
    ('ET', 'Ethiopia'),
    ('FJ', 'Fiji'),
    ('FI', 'Finland'),
    ('FR', 'France'),
    ('GA', 'Gabon'),
    ('GM', 'Gambia'),
    ('GE', 'Georgia'),
    ('DE', 'Germany'),
    ('GH', 'Ghana'),
    ('GR', 'Greece'),
    ('GD', 'Grenada'),
    ('GT', 'Guatemala'),
    ('GN', 'Guinea'),
    ('GW', 'Guinea-Bissau'),
    ('GY', 'Guyana'),
    ('HT', 'Haiti'),
    ('HN', 'Honduras'),
    ('HU', 'Hungary'),
    ('IS', 'Iceland'),
    ('IN', 'India'),
    ('ID', 'Indonesia'),
    ('IR', 'Iran'),
    ('IQ', 'Iraq'),
    ('IE', 'Ireland'),
    ('IL', 'Israel'),
    ('IT', 'Italy'),
    ('JM', 'Jamaica'),
    ('JP', 'Japan'),
    ('JO', 'Jordan'),
    ('KZ', 'Kazakhstan'),
    ('KE', 'Kenya'),
    ('KI', 'Kiribati'),
    ('KP', 'North Korea'),
    ('KR', 'South Korea'),
    ('KW', 'Kuwait'),
    ('KG', 'Kyrgyzstan'),
    ('LA', 'Laos'),
    ('LV', 'Latvia'),
    ('LB', 'Lebanon'),
    ('LS', 'Lesotho'),
    ('LR', 'Liberia'),
    ('LY', 'Libya'),
    ('LI', 'Liechtenstein'),
    ('LT', 'Lithuania'),
    ('LU', 'Luxembourg'),
    ('MG', 'Madagascar'),
    ('MW', 'Malawi'),
    ('MY', 'Malaysia'),
    ('MV', 'Maldives'),
    ('ML', 'Mali'),
    ('MT', 'Malta'),
    ('MH', 'Marshall Islands'),
    ('MR', 'Mauritania'),
    ('MU', 'Mauritius'),
    ('MX', 'Mexico'),
    ('FM', 'Micronesia'),
    ('MD', 'Moldova'),
    ('MC', 'Monaco'),
    ('MN', 'Mongolia'),
    ('ME', 'Montenegro'),
    ('MA', 'Morocco'),
    ('MZ', 'Mozambique'),
    ('MM', 'Myanmar'),
    ('NA', 'Namibia'),
    ('NR', 'Nauru'),
    ('NP', 'Nepal'),
    ('NL', 'Netherlands'),
    ('NZ', 'New Zealand'),
    ('NI', 'Nicaragua'),
    ('NE', 'Niger'),
    ('NG', 'Nigeria'),
    ('NO', 'Norway'),
    ('OM', 'Oman'),
    ('PK', 'Pakistan'),
    ('PW', 'Palau'),
    ('PA', 'Panama'),
    ('PG', 'Papua New Guinea'),
    ('PY', 'Paraguay'),
    ('PE', 'Peru'),
    ('PH', 'Philippines'),
    ('PL', 'Poland'),
    ('PT', 'Portugal'),
    ('QA', 'Qatar'),
    ('RO', 'Romania'),
    ('RU', 'Russia'),
    ('RW', 'Rwanda'),
    ('KN', 'Saint Kitts and Nevis'),
    ('LC', 'Saint Lucia'),
    ('VC', 'Saint Vincent and the Grenadines'),
    ('WS', 'Samoa'),
    ('SM', 'San Marino'),
    ('ST', 'Sao Tome and Principe'),
    ('SA', 'Saudi Arabia'),
    ('SN', 'Senegal'),
    ('RS', 'Serbia'),
    ('SC', 'Seychelles'),
    ('SL', 'Sierra Leone'),
    ('SG', 'Singapore'),
    ('SK', 'Slovakia'),
    ('SI', 'Slovenia'),
    ('SB', 'Solomon Islands'),
    ('SO', 'Somalia'),
    ('ZA', 'South Africa'),
    ('ES', 'Spain'),
    ('LK', 'Sri Lanka'),
    ('SD', 'Sudan'),
    ('SR', 'Suriname'),
    ('SE', 'Sweden'),
    ('CH', 'Switzerland'),
    ('SY', 'Syria'),
    ('TW', 'Taiwan'),
    ('TJ', 'Tajikistan'),
    ('TZ', 'Tanzania'),
    ('TH', 'Thailand'),
    ('TL', 'Timor-Leste'),
    ('TG', 'Togo'),
    ('TO', 'Tonga'),
    ('TT', 'Trinidad and Tobago'),
    ('TN', 'Tunisia'),
    ('TR', 'Turkey'),
    ('TM', 'Turkmenistan'),
    ('TV', 'Tuvalu'),
    ('UG', 'Uganda'),
    ('UA', 'Ukraine'),
    ('AE', 'United Arab Emirates'),
    ('GB', 'United Kingdom'),
    ('US', 'United States'),
    ('UY', 'Uruguay'),
    ('UZ', 'Uzbekistan'),
    ('VU', 'Vanuatu'),
    ('VA', 'Vatican City'),
    ('VE', 'Venezuela'),
    ('VN', 'Vietnam'),
    ('YE', 'Yemen'),
    ('ZM', 'Zambia'),
    ('ZW', 'Zimbabwe'),
]


# ============================================================
# STEP 1 – PERSONAL INFO
# ============================================================

class RegistrationStep1Form(forms.Form):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First name'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last name'})
    )
    middle_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Middle name (optional)'})
    )
    username = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Choose a username'})
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        if len(username) < 3:
            raise forms.ValidationError("Username must be at least 3 characters.")
        return username


# ============================================================
# STEP 2 – CONTACT INFO
# ============================================================

class RegistrationStep2Form(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'email@example.com'})
    )
    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': '+1 (123) 456-7890'})
    )
    country = forms.ChoiceField(
        choices=COUNTRIES,
        required=True,
        widget=forms.Select(attrs={'class': 'select'})
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        # Remove all non-digit characters for validation
        digits = re.sub(r'\D', '', phone)
        if len(digits) < 10:
            raise forms.ValidationError("Please enter a valid phone number.")
        return phone


# ============================================================
# STEP 3 – ACCOUNT SETUP (with PIN validation)
# ============================================================

class RegistrationStep3Form(forms.Form):
    CURRENCY_CHOICES = [
        ('USD', 'USD - US Dollar'),
        ('EUR', 'EUR - Euro'),
        ('GBP', 'GBP - British Pound'),
        ('NGN', 'NGN - Nigerian Naira'),
    ]
    ACCOUNT_TYPE_CHOICES = [
        ('checking', 'Checking Account'),
        ('savings', 'Savings Account'),
        ('money_market', 'Money Market Account'),
        ('certificate', 'Certificate Account'),
        ('business', 'Business Account'),
        ('investment', 'Investment Account'),
    ]

    currency = forms.ChoiceField(
        choices=CURRENCY_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'select'})
    )
    account_type = forms.ChoiceField(
        choices=ACCOUNT_TYPE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'select'})
    )
    transaction_pin = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter a 4-digit PIN', 'inputmode': 'numeric'}),
        min_length=4,
        max_length=4,
        required=True,
        help_text="A 4-digit PIN for transactions."
    )

    def clean_transaction_pin(self):
        pin = self.cleaned_data['transaction_pin']
        
        # Check it's exactly 4 digits
        if not pin.isdigit():
            raise forms.ValidationError("PIN must contain only digits (0-9).")
        
        if len(pin) != 4:
            raise forms.ValidationError("PIN must be exactly 4 digits.")
        
        # Check it's not all the same number (e.g., 1111)
        if len(set(pin)) == 1:
            raise forms.ValidationError("PIN cannot be all the same digit (e.g., 1111).")
        
        # Check it's not sequential (e.g., 1234, 4321)
        if pin in ['1234', '2345', '3456', '4567', '5678', '6789', '7890',
                   '4321', '5432', '6543', '7654', '8765', '9876', '0987']:
            raise forms.ValidationError("PIN cannot be sequential (e.g., 1234).")
        
        # Check it's not a common PIN
        common_pins = ['0000', '1111', '2222', '3333', '4444', '5555', '6666', '7777', '8888', '9999',
                       '1212', '1122', '2211', '1221', '2112', '1234', '4321', '1111']
        if pin in common_pins:
            raise forms.ValidationError("PIN is too common. Please choose a more secure PIN.")
        
        return pin


# ============================================================
# STEP 4 – SECURITY (with password validation)
# ============================================================

class RegistrationStep4Form(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Create a password'}),
        required=True
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password'}),
        required=True
    )
    terms_accepted = forms.BooleanField(
        required=True,
        error_messages={'required': 'You must accept the Terms and Conditions.'}
    )
    privacy_accepted = forms.BooleanField(
        required=True,
        error_messages={'required': 'You must accept the Privacy Policy.'}
    )

    def clean_password(self):
        password = self.cleaned_data.get('password')
        
        # Check minimum length
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        
        # Check for uppercase letter
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        
        # Check for lowercase letter
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError("Password must contain at least one lowercase letter.")
        
        # Check for digit
        if not re.search(r'\d', password):
            raise forms.ValidationError("Password must contain at least one digit.")
        
        # Check for special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise forms.ValidationError("Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>).")
        
        # Check for common passwords
        common_passwords = ['password', '12345678', 'qwertyuiop', 'admin123', 'letmein', 'welcome']
        if password.lower() in common_passwords:
            raise forms.ValidationError("Password is too common. Please choose a stronger password.")
        
        return password

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get('password')
        cpwd = cleaned_data.get('confirm_password')
        if pwd and cpwd and pwd != cpwd:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data


# ============================================================
# EMAIL VERIFICATION
# ============================================================

class EmailVerificationForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        min_length=6,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. 123456',
            'inputmode': 'numeric',
            'pattern': '[0-9]{6}'
        })
    )

    def clean_code(self):
        code = self.cleaned_data['code']
        if not code.isdigit():
            raise forms.ValidationError("Verification code must contain only digits.")
        if len(code) != 6:
            raise forms.ValidationError("Verification code must be exactly 6 digits.")
        return code


# ============================================================
# KYC FORMS
# ============================================================

class KYCProfileForm(forms.ModelForm):

    TITLE_CHOICES = [
        ('Mr', 'Mr.'),
        ('Mrs', 'Mrs.'),
        ('Ms', 'Ms.'),
        ('Miss', 'Miss'),
        ('Dr', 'Dr.'),
        ('Prof', 'Prof.'),
    ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]

    EMPLOYMENT_CHOICES = [
        ('employed', 'Employed'),
        ('self_employed', 'Self-employed'),
        ('business_owner', 'Business Owner'),
        ('student', 'Student'),
        ('retired', 'Retired'),
        ('unemployed', 'Unemployed'),
        ('other', 'Other'),
    ]

    INCOME_CHOICES = [
        ('below_25000', 'Below $25,000'),
        ('25000_49999', '$25,000 – $49,999'),
        ('50000_74999', '$50,000 – $74,999'),
        ('75000_99999', '$75,000 – $99,999'),
        ('100000_149999', '$100,000 – $149,999'),
        ('150000_249999', '$150,000 – $249,999'),
        ('250000_plus', '$250,000+'),
    ]

    NATIONALITY_CHOICES = [
        ('AF', 'Afghanistan'),
        ('AL', 'Albania'),
        ('DZ', 'Algeria'),
        ('AO', 'Angola'),
        ('AR', 'Argentina'),
        ('AU', 'Australia'),
        ('AT', 'Austria'),
        ('BD', 'Bangladesh'),
        ('BE', 'Belgium'),
        ('BJ', 'Benin'),
        ('BR', 'Brazil'),
        ('CA', 'Canada'),
        ('CM', 'Cameroon'),
        ('CN', 'China'),
        ('CO', 'Colombia'),
        ('CD', 'Democratic Republic of the Congo'),
        ('DK', 'Denmark'),
        ('EG', 'Egypt'),
        ('ET', 'Ethiopia'),
        ('FI', 'Finland'),
        ('FR', 'France'),
        ('DE', 'Germany'),
        ('GH', 'Ghana'),
        ('GR', 'Greece'),
        ('IN', 'India'),
        ('IE', 'Ireland'),
        ('IT', 'Italy'),
        ('JP', 'Japan'),
        ('KE', 'Kenya'),
        ('MY', 'Malaysia'),
        ('MX', 'Mexico'),
        ('MA', 'Morocco'),
        ('MZ', 'Mozambique'),
        ('NL', 'Netherlands'),
        ('NZ', 'New Zealand'),
        ('NG', 'Nigeria'),
        ('NO', 'Norway'),
        ('PK', 'Pakistan'),
        ('PH', 'Philippines'),
        ('PL', 'Poland'),
        ('PT', 'Portugal'),
        ('QA', 'Qatar'),
        ('RU', 'Russia'),
        ('RW', 'Rwanda'),
        ('SA', 'Saudi Arabia'),
        ('SN', 'Senegal'),
        ('SG', 'Singapore'),
        ('ZA', 'South Africa'),
        ('ES', 'Spain'),
        ('LK', 'Sri Lanka'),
        ('SE', 'Sweden'),
        ('CH', 'Switzerland'),
        ('TZ', 'Tanzania'),
        ('TH', 'Thailand'),
        ('TR', 'Turkey'),
        ('UG', 'Uganda'),
        ('UA', 'Ukraine'),
        ('AE', 'United Arab Emirates'),
        ('GB', 'United Kingdom'),
        ('US', 'United States'),
        ('ZM', 'Zambia'),
        ('ZW', 'Zimbabwe'),
    ]

    title = forms.ChoiceField(
        choices=TITLE_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'select'
        })
    )

    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'select'
        })
    )

    employment_type = forms.ChoiceField(
        choices=EMPLOYMENT_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'select'
        })
    )

    annual_income_range = forms.ChoiceField(
        choices=INCOME_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'select'
        })
    )

    nationality = forms.ChoiceField(
        choices=NATIONALITY_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'select'
        })
    )

    class Meta:
        model = KYCProfile

        fields = [
            'title',
            'gender',
            'date_of_birth',
            'government_id',
            'employment_type',
            'annual_income_range',
            'address_line',
            'city',
            'state',
            'postal_code',
            'nationality',
        ]

        widgets = {
            'date_of_birth': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'input'
                }
            ),

            'government_id': forms.TextInput(
                attrs={
                    'class': 'input',
                    'placeholder': 'SSN, NI, SIN, National ID, etc.'
                }
            ),

            'address_line': forms.TextInput(
                attrs={
                    'class': 'input',
                    'placeholder': 'Enter your full address'
                }
            ),

            'city': forms.TextInput(
                attrs={
                    'class': 'input',
                    'placeholder': 'City'
                }
            ),

            'state': forms.TextInput(
                attrs={
                    'class': 'input',
                    'placeholder': 'State / Province'
                }
            ),

            'postal_code': forms.TextInput(
                attrs={
                    'class': 'input',
                    'placeholder': 'Postal / ZIP code'
                }
            ),
        }


# ============================================================
# NEXT OF KIN FORM
# ============================================================

class NextOfKinForm(forms.ModelForm):

    class Meta:
        model = NextOfKin

        fields = [
            'full_name',
            'address',
            'relationship',
            'age',
        ]

        widgets = {
            'full_name': forms.TextInput(
                attrs={
                    'class': 'input',
                    'placeholder': 'Enter beneficiary legal name'
                }
            ),

            'address': forms.TextInput(
                attrs={
                    'class': 'input',
                    'placeholder': 'Enter full address'
                }
            ),

            'relationship': forms.TextInput(
                attrs={
                    'class': 'input',
                    'placeholder': 'e.g. Spouse, Parent, Sibling'
                }
            ),

            'age': forms.NumberInput(
                attrs={
                    'class': 'input',
                    'min': 1,
                    'max': 120,
                    'placeholder': 'Age'
                }
            ),
        }

class IdentityDocumentForm(forms.ModelForm):
    class Meta:
        model = IdentityDocument
        fields = ['doc_type', 'front_image', 'back_image', 'passport_photo']

    front_image = forms.ImageField(
        validators=[
            FileExtensionValidator(allowed_extensions=['svg', 'png', 'jpg', 'jpeg', 'gif']),
            validate_file_size,
        ],
        widget=forms.FileInput(attrs={'accept': 'image/*'})
    )
    back_image = forms.ImageField(
        validators=[
            FileExtensionValidator(allowed_extensions=['svg', 'png', 'jpg', 'jpeg', 'gif']),
            validate_file_size,
        ],
        widget=forms.FileInput(attrs={'accept': 'image/*'})
    )
    passport_photo = forms.ImageField(
        validators=[
            FileExtensionValidator(allowed_extensions=['svg', 'png', 'jpg', 'jpeg', 'gif']),
            validate_file_size,
        ],
        widget=forms.FileInput(attrs={'accept': 'image/*'})
    )


class KYCTermsForm(forms.Form):
    accept_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(),
        error_messages={'required': 'You must accept the terms to proceed.'}
    )


# ============================================================
# LOGIN FORM (with rate limiting in view)
# ============================================================

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username / Email",
        max_length=254,
        widget=forms.TextInput(attrs={'placeholder': 'username or email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                try:
                    user = User.objects.get(email=username)
                    self.user_cache = authenticate(self.request, username=user.username, password=password)
                except User.DoesNotExist:
                    pass
            if self.user_cache is None:
                raise forms.ValidationError("Invalid login credentials.")
        return self.cleaned_data


# ============================================================
# PROFILE UPDATE
# ============================================================

class AccountProfileForm(forms.ModelForm):
    country = forms.ChoiceField(
        choices=COUNTRIES,
        required=False,
        widget=forms.Select(attrs={'class': 'select'})
    )

    class Meta:
        model = AccountProfile
        fields = ['phone', 'country', 'currency', 'account_type']
        widgets = {
            'currency': forms.Select(attrs={'class': 'select'}),
            'account_type': forms.Select(attrs={'class': 'select'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            digits = re.sub(r'\D', '', phone)
            if len(digits) < 10:
                raise forms.ValidationError("Please enter a valid phone number.")
        return phone
