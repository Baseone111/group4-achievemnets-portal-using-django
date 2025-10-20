from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import os

def achievement_image_path(instance, filename):
    """
    Generate file path for achievement images
    File will be uploaded to: MEDIA_ROOT/achievements/user_<id>/<filename>
    """
    # Get file extension
    ext = filename.split('.')[-1]
    # Generate filename: achievement_<id>_<timestamp>.<ext>
    filename = f'achievement_{instance.id}_{int(timezone.now().timestamp())}.{ext}'
    return os.path.join('achievements', f'user_{instance.student.id}', filename)

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='studentprofile')
    roll_number = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100, default="Computer Science & Engineering")
    year = models.IntegerField(default=2025)
    phone = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    is_student = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True,
                               help_text="Saved overall CGPA for the student")
    total_credits = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True,
                                        help_text="Total recorded credits used in CGPA calculation")

    
    class Meta:
        verbose_name = "Student Profile"
        verbose_name_plural = "Student Profiles"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.roll_number}"
    
    @property
    def full_name(self):
        return self.user.get_full_name()
    
    @property
    def email(self):
        return self.user.email

class Achievement(models.Model):
    COMPETITION_LEVELS = [
        ('college', 'College Level'),
        ('university', 'University Level'),
        ('state', 'State Level'),
        ('national', 'National Level'),
        ('international', 'International Level'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    name = models.CharField(max_length=200)
    event = models.CharField(max_length=200)
    prize = models.CharField(max_length=100)
    competition = models.CharField(max_length=50, choices=COMPETITION_LEVELS, default='college')
    image = models.ImageField(
        upload_to=achievement_image_path,
        blank=True, 
        null=True, 
        help_text="Upload achievement image or certificate"
    )
    image_url = models.URLField(blank=True, null=True, help_text="Or provide image URL")    
    description = models.TextField(blank=True, null=True)
    date_achieved = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Achievement"
        verbose_name_plural = "Achievements"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_approved', 'created_at']),
            models.Index(fields=['student', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.event}"
    
    @property
    def student_name(self):
        return self.student.get_full_name()
    
    @property
    def student_roll_number(self):
        try:
            return self.student.studentprofile.roll_number
        except StudentProfile.DoesNotExist:
            return "N/A"
    
    @property
    def competition_level_display(self):
        return dict(self.COMPETITION_LEVELS).get(self.competition, self.competition)
    
    def approve(self):
        self.is_approved = True
        self.save()
    
    def disapprove(self):
        self.is_approved = False
        self.save()
    
    def get_image_url(self):
        """Return either uploaded image URL or external image URL"""
        try:
            if self.image and hasattr(self.image, 'url'):
            # Check if file actually exists
                if self.image.storage.exists(self.image.name):
                     return self.image.url
                else:
                    return None
            elif self.image_url:
                return self.image_url
            return None
        except Exception as e:
        # Fallback to image_url if there's any error
            return self.image_url

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        try:
            # Generate a default roll number if not provided during signup
            StudentProfile.objects.create(
                user=instance,
                roll_number=f"STU{instance.id:04d}",
                department="Computer Science & Engineering",
                year=2025
            )
        except Exception as e:
            print(f"Error creating profile for user {instance.username}: {e}")

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'studentprofile'):
        instance.studentprofile.save()

#### grading 


from django.db import models
from django.conf import settings # Use settings.AUTH_USER_MODEL for student



class Semester(models.Model):
    """Represents a student's academic semester."""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='semesters'
    )
    name = models.CharField(
        max_length=50, 
        help_text="e.g., 'Semester 1', 'Year 2 Semester 1'"
    )
    
    def __str__(self):
        return f"{self.student.username} - {self.name}"

class CourseUnit(models.Model):
    
    

    GRADE_CHOICES = [
        ('A+', 'A+ (5.0)'), ('A', 'A (5.0)'), 
        ('B+', 'B+ (4.5)'), ('B', 'B (4.0)'), 
        ('C+', 'C+ (3.5)'), ('C', 'C (3.0)'),
        ('D+', 'D+ (2.5)'), ('D', 'D (2.0)'), ('E+', 'E+ (1.5)'),('E-', 'E- (1.0)'),
        ('F', 'F (0.0)')
    ]
    
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='course_units')
    unit_name = models.CharField(max_length=100)
    credits = models.DecimalField(max_digits=3, decimal_places=1) # e.g., 3.0 or 4.0
    
    # Store the final grade (letter)
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, blank=True, null=True)


    def __str__(self):
        return f"{self.unit_name} ({self.semester.name})"

