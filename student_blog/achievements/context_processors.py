def global_context(request):
    """Global context available to all templates"""
    return {
        'app_name': 'CSE Achievers Portal',
        'app_description': 'Celebrating Student Excellence in Computer Science & Engineering',
        'college_name': 'Mailam Engineering College',
        'department_name': 'Computer Science & Engineering',
    }