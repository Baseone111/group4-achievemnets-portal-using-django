from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Achievement, StudentProfile

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email address'
    }))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your first name'
    }))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your last name'
    }))
    roll_number = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your roll number'
    }))
    department = forms.CharField(max_length=100, required=True, initial="Computer Science & Engineering", widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your department'
    }))
    year = forms.IntegerField(min_value=2000, max_value=2030, required=True, initial=2025, widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your academic year'
    }))
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your phone number (optional)'
    }))
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Create a strong password'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Confirm your password'
            }),
        }
    
    def clean_roll_number(self):
        roll_number = self.cleaned_data['roll_number']
        if StudentProfile.objects.filter(roll_number=roll_number).exists():
            raise forms.ValidationError("This roll number is already registered.")
        return roll_number
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
    
        if commit:
            user.save()
        
        # Use get_or_create to handle existing profiles
            profile, created = StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    'roll_number': self.cleaned_data['roll_number'],
                    'department': self.cleaned_data['department'],
                    'year': self.cleaned_data['year'],
                    'phone': self.cleaned_data['phone'] or None,
                    'is_student': True
                }
            )
        
        # If profile already existed, update it
            if not created:
                profile.roll_number = self.cleaned_data['roll_number']
                profile.department = self.cleaned_data['department']
                profile.year = self.cleaned_data['year']
                profile.phone = self.cleaned_data['phone'] or None
                profile.is_student = True
                profile.save()
    
        return user

class AchievementForm(forms.ModelForm):
    class Meta:
        model = Achievement
        fields = ['name', 'event', 'prize', 'competition', 'image', 'image_url', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., First Prize in Hackathon'
            }),
            'event': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., Smart India Hackathon 2024'
            }),
            'prize': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 1st Prize, Gold Medal'
            }),
            'competition': forms.Select(attrs={
                'class': 'form-control'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'image_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/achievement-image.jpg'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your achievement in detail...'
            }),
        }
    
    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name) < 5:
            raise forms.ValidationError("Achievement name must be at least 5 characters long.")
        return name
    
    def clean_prize(self):
        prize = self.cleaned_data['prize']
        if len(prize) < 3:
            raise forms.ValidationError("Please provide a valid prize description.")
        return prize

class ProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['roll_number', 'department', 'year', 'phone', 'avatar', 'bio']
        widgets = {
            'roll_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your roll number'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your department'
            }),
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your academic year',
                'min': 2000,
                'max': 2030
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your phone number'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Tell us about yourself, your interests, and career goals...'
            }),
        }
    
    def clean_roll_number(self):
        roll_number = self.cleaned_data['roll_number']
        if StudentProfile.objects.filter(roll_number=roll_number).exclude(user=self.instance.user).exists():
            raise forms.ValidationError("This roll number is already registered by another student.")
        return roll_number
    
    def clean_year(self):
        year = self.cleaned_data['year']
        if year < 2000 or year > 2030:
            raise forms.ValidationError("Please enter a valid academic year.")
        return year
    
    ##grading 
    # achievements/forms.py
from django import forms
from .models import CourseUnit, Semester

class CourseUnitForm(forms.ModelForm):
    
    # Allow the user to select an existing semester or enter a new one
    semester_name = forms.CharField(
        max_length=50, 
        required=True, 
        label="Semester Name (e.g., 'Sem 1', 'Year 2')"
    )

    class Meta:
        model = CourseUnit
        fields = ['unit_name', 'credits', 'grade']
        
        widgets = {
            'unit_name': forms.TextInput(attrs={'placeholder': 'e.g., Data Structures'}),
            'credits': forms.NumberInput(attrs={'placeholder': 'e.g., 3.0', 'step': '0.5'}),
        }
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Populate the semester_name field with suggestions from existing semesters
        if self.user:
            existing_semesters = Semester.objects.filter(student=self.user).values_list('name', flat=True).distinct()
            # You can use a DataList/select field here for better UX, but CharField is simpler.
            # Example using a ChoiceField for selection (uncomment if preferred):
            # self.fields['semester_name'].widget = forms.Select(choices=[(s, s) for s in existing_semesters] + [('', '--- Enter New/Select Existing ---')])
        
    def save(self, commit=True):
        # 1. Get or Create the Semester object
        semester_name = self.cleaned_data.pop('semester_name')
        semester, created = Semester.objects.get_or_create(
            student=self.user,
            name=semester_name
        )
        
        # 2. Assign the semester to the CourseUnit instance
        course_unit = super().save(commit=False)
        course_unit.semester = semester
        
        if commit:
            course_unit.save()
        return course_unit