from decimal import ROUND_HALF_UP, Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q
from .models import Achievement, StudentProfile, ContactMessage
from .forms import AchievementForm, UserRegistrationForm, ProfileForm
from .admin_auth import staff_required, superuser_required

from .cgpa_calculator import calculate_cgpa

def home(request):
    
    try:
        featured_achievements = Achievement.objects.filter(is_approved=True).order_by('-created_at')[:6]
        total_achievements = Achievement.objects.filter(is_approved=True).count()
        total_students = User.objects.filter(is_staff=False).count()
    except Exception as e:
        featured_achievements = []
        total_achievements = 0
        total_students = 0
    
    context = {
        'featured_achievements': featured_achievements,
        'total_achievements': total_achievements,
        'total_students': total_students,
    }
    return render(request, 'achievements/home.html', context)

def achievements(request):
    """All achievements page"""
    search_query = request.GET.get('search', '')
    
    try:
        all_achievements = Achievement.objects.filter(is_approved=True).order_by('-created_at')
        
        if search_query:
            all_achievements = all_achievements.filter(
                Q(name__icontains=search_query) |
                Q(event__icontains=search_query) |
                Q(competition__icontains=search_query) |
                Q(description__icontains=search_query)
            )
    except Exception as e:
        all_achievements = []
    
    context = {
        'achievements': all_achievements,
        'search_query': search_query,
    }
    return render(request, 'achievements/achievements.html', context)

def signup(request):
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                
                # Auto login after signup
                login(request, user)
                messages.success(request, ' Registration successful! Welcome to Base_One Achievers!')
                return redirect('dashboard')
                
            except Exception as e:
                messages.error(request, f' Error creating account: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'achievements/signup.html', {'form': form})

def login_view(request):
    """User login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            
            # Redirect based on user type
            next_page = request.GET.get('next', 'dashboard')
            return redirect(next_page)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'achievements/login.html')

@login_required
def logout_view(request):
   
    logout(request)
    messages.success(request, '👋 You have been logged out successfully.')
    return redirect('home')

@login_required
def dashboard(request):
   
    # Initialize variables
    student_achievements = []
    profile = None
    approved_count = 0
    form = AchievementForm()
    
    try:
        # Get user achievements and profile
        student_achievements = Achievement.objects.filter(student=request.user).order_by('-created_at')
        profile = getattr(request.user, 'studentprofile', None)
        approved_count = Achievement.objects.filter(student=request.user, is_approved=True).count()
    except Exception as e:
        print(f"Error loading dashboard data: {e}")
    
    # Handle form submission
    if request.method == 'POST':
        form = AchievementForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                achievement = form.save(commit=False)
                achievement.student = request.user
                achievement.save()
                messages.success(request, ' Achievement submitted for approval!')
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f' Error submitting achievement: {str(e)}')
        else:
            messages.error(request, ' Please correct the errors below.')
    
    context = {
        'achievements': student_achievements,
        'form': form,
        'profile': profile,
        'approved_count': approved_count
    }
    return render(request, 'achievements/dashboard.html', context)

@login_required
def profile(request):
    
    try:
        profile = get_object_or_404(StudentProfile, user=request.user)
        total_achievements = Achievement.objects.filter(student=request.user).count()
        approved_achievements = Achievement.objects.filter(student=request.user, is_approved=True).count()
    except Exception as e:
        profile = None
        total_achievements = 0
        approved_achievements = 0
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, ' Profile updated successfully!')
                return redirect('profile')
            except Exception as e:
                messages.error(request, f'Error updating profile: {str(e)}')
        else:
            messages.error(request, ' Please correct the errors below.')
    else:
        form = ProfileForm(instance=profile)
    
    context = {
        'profile': profile,
        'form': form,
        'total_achievements': total_achievements,
        'approved_achievements': approved_achievements
    }
    return render(request, 'achievements/profile.html', context)

@login_required
def delete_achievement(request, achievement_id):
   
    try:
        achievement = get_object_or_404(Achievement, id=achievement_id, student=request.user)
        achievement.delete()
        messages.success(request, ' Achievement deleted successfully!')
    except Exception as e:
        messages.error(request, 'Error deleting achievement.')
    
    return redirect('dashboard')

@staff_required
def admin_dashboard(request):
    """Staff-only dashboard"""
    try:
        student_count = User.objects.filter(is_staff=False).count()
        staff_count = User.objects.filter(is_staff=True).count()
        achievement_count = Achievement.objects.count()
        pending_approvals = Achievement.objects.filter(is_approved=False).count()
        approved_achievements = Achievement.objects.filter(is_approved=True).count()
    except Exception as e:
        student_count = staff_count = achievement_count = pending_approvals = approved_achievements = 0
    
    context = {
        'student_count': student_count,
        'staff_count': staff_count,
        'achievement_count': achievement_count,
        'pending_approvals': pending_approvals,
        'approved_achievements': approved_achievements,
    }
    return render(request, 'achievements/admin_dashboard.html', context)

@superuser_required
def register_staff(request):
 
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                # Make user staff
                user.is_staff = True
                user.save()
                
                # Update profile to mark as staff
                profile = user.studentprofile
                profile.is_student = False
                profile.save()
                
                messages.success(request, f' Staff member {user.username} created successfully!')
                return redirect('admin_dashboard')
            except Exception as e:
                messages.error(request, f' Error creating staff member: {str(e)}')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'achievements/register_staff.html', {'form': form})

def admin_site_permission(request):
    """
    Custom permission check for admin site access
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    if not request.user.is_staff:
        messages.error(request, " Access denied. Only staff members can access the admin panel.")
        return redirect('home')
    
    # Allow access to admin site
    from django.contrib.admin.sites import site
    return site.index(request)

def contact_submit(request):
    """Handle contact form submission"""
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            email = request.POST.get('email')
            subject = request.POST.get('subject')
            message = request.POST.get('message')
            
            # Save to database
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            
            messages.success(request, ' Thank you for your message! We will get back to you soon.')
        except Exception as e:
            messages.error(request, 'Error sending message. Please try again.')
    
    return redirect('home')

def get_achievements_api(request):
    """API endpoint for achievements"""
    try:
        achievements = Achievement.objects.filter(is_approved=True).values(
            'id', 'name', 'event', 'prize', 'competition', 'image', 'description'
        )
        return JsonResponse(list(achievements), safe=False)
    except Exception as e:
        return JsonResponse([], safe=False)

# Error handlers
def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CourseUnit, Semester
from .forms import CourseUnitForm


# ... (other view imports)

@login_required
def dashboard(request):
    
    # --- 1. Handle Form Submission for New Course Unit ---
    course_form = CourseUnitForm(user=request.user)
    if request.method == 'POST':
        if 'add_course' in request.POST: # Check if the course submission button was clicked
            course_form = CourseUnitForm(request.POST, user=request.user)
            if course_form.is_valid():
                course_form.save()
                messages.success(request, "Course unit added successfully! GPA/CGPA re-calculated.")
                return redirect('dashboard') # Redirect to prevent resubmission
        
      
    student_semesters = Semester.objects.filter(student=request.user).prefetch_related('course_units').order_by('id')
    
    # Transform model data into the format required by calculate_cgpa
    student_grades_data = {}
    last_gpa = 0.0
    
    for semester in student_semesters:
        semester_units = []
        for unit in semester.course_units.all():
            if unit.grade:
                semester_units.append({
                    'subject': unit.unit_name,
                    'grade': unit.grade,
                    'credits': float(unit.credits), # Convert Decimal to float for calculation
                })
        
        # Only add semesters that have graded units
        if semester_units:
            student_grades_data[semester.name] = semester_units

    # --- 3. Compute GPA and CGPA ---
    grade_results = {'cgpa': 0.0, 'total_credits': 0.0, 'gpa_results': {}}
    
    if student_grades_data:
        grade_results = calculate_cgpa(student_grades_data)
        
        # Determine the latest semester GPA to display as 'Current GPA'
        if grade_results['gpa_results']:
            # Get the GPA of the last semester processed
            last_semester_name = list(student_grades_data.keys())[-1]
            last_gpa = grade_results['gpa_results'].get(last_semester_name, 0.0)


    # ... (Your existing achievement fetching and counting logic)

    context = {
        # ... your existing context variables (achievements, approved_count, etc.)
        'course_form': course_form,
        'cgpa_results': grade_results,
        'current_gpa': last_gpa,
        'student_semesters': student_semesters, # Pass full data for displaying tables
    }

    return render(request, 'achievements/dashboard.html', context)





def build_grades_data_for_user(user):
   
    student_semesters = Semester.objects.filter(student=user).prefetch_related('course_units').order_by('id')
    student_grades_data = {}
    for semester in student_semesters:
        semester_units = []
        for unit in semester.course_units.all():
            if unit.grade:
                semester_units.append({
                    'subject': unit.unit_name,
                    'grade': unit.grade,
                    'credits': float(unit.credits),
                })
        if semester_units:
            student_grades_data[semester.name] = semester_units
    return student_grades_data

@staff_required
def admin_dashboard(request):
    """
    Staff-only admin dashboard. Includes a list of students (non-staff users).
    """
    try:
        student_count = User.objects.filter(is_staff=False).count()
        staff_count = User.objects.filter(is_staff=True).count()
        achievement_count = Achievement.objects.count()
        pending_approvals = Achievement.objects.filter(is_approved=False).count()
        approved_achievements = Achievement.objects.filter(is_approved=True).count()
    except Exception as e:
        student_count = staff_count = achievement_count = pending_approvals = approved_achievements = 0

    # New: list of students for staff to view and compute CGPA
    students_list = User.objects.filter(is_staff=False).select_related('studentprofile').order_by('username')

    context = {
        'student_count': student_count,
        'staff_count': staff_count,
        'achievement_count': achievement_count,
        'pending_approvals': pending_approvals,
        'approved_achievements': approved_achievements,
        'students_list': students_list,
    }
    return render(request, 'achievements/admin_dashboard.html', context)


@staff_required

def compute_and_store_student_cgpa(request, user_id):

  
    target_user = get_object_or_404(User, id=user_id)
    if target_user.is_staff:
        return JsonResponse({'error': 'Target user is staff; cannot compute.'}, status=400)

    
    student_grades_data = build_grades_data_for_user(target_user)

    if not student_grades_data:
        return JsonResponse({'error': 'No graded units found for this student.'}, status=400)

    
    try:
        result = calculate_cgpa(student_grades_data)
       
    except Exception as e:
        return JsonResponse({'error': f'Error computing CGPA: {str(e)}'}, status=500)

    # Persist to StudentProfile
    try:
        profile = getattr(target_user, 'studentprofile', None)
        if profile is None:
           
            profile = StudentProfile.objects.create(user=target_user, roll_number=f"STU{target_user.id:04d}", is_student=True)
       
        cgpa_val = result.get('cgpa', None)
        if cgpa_val is not None:
            profile.cgpa = Decimal(str(cgpa_val)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        else:
            profile.cgpa = None

        total_credits_val = result.get('total_credits', None)
        if total_credits_val is not None:
            profile.total_credits = Decimal(str(total_credits_val)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        else:
            profile.total_credits = None

        profile.save()
    except Exception as e:
        return JsonResponse({'error': f'Error saving CGPA: {str(e)}'}, status=500)

   
    return JsonResponse({
        'success': True,
        'cgpa': float(profile.cgpa) if profile.cgpa is not None else None,
        'total_credits': float(profile.total_credits) if profile.total_credits is not None else None,
        'gpa_results': result.get('gpa_results', {}),
    })