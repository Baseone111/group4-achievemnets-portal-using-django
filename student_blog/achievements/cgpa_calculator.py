

from functools import reduce
from typing import List, Dict, Optional, Union


GRADE_SCALE: Dict[str, float] = {
    
    'E-': 1.0,
    
    'E+': 1.5,
    
    'D': 2.0,
    'D+': 2.5,
    
    'C': 3.0,
    
    'C+': 3.5,
    
    'B': 4.0,
    
    'B+': 4.5,
    
    'A': 5.0,
    
    'A+': 5.0,
    
    'F': 0.0
}

# Type aliases for clarity
SubjectData = Dict[str, Union[str, int, float]]
SemesterData = List[SubjectData]
AllSemestersData = Dict[str, SemesterData]


def get_quality_points(grade: str) -> float:
   
    return GRADE_SCALE.get(grade.upper().strip(), 0.0)


def calculate_gpa(semester_data: SemesterData) -> float:
  
    
   
    weighted_points = list(map(
        lambda subj: get_quality_points(subj['grade']) * subj['credits'],
        semester_data
    ))
    
    # 2. Map: Extract Credits for each subject
    credits_list = list(map(lambda subj: subj['credits'], semester_data))
    
    # 3. Reduce: Sum the total weighted points
    total_weighted_points = reduce(lambda acc, val: acc + val, weighted_points, 0)
    
    # 4. Reduce: Sum the total credits
    total_credits = reduce(lambda acc, val: acc + val, credits_list, 0)
    
    # Calculate GPA
    return total_weighted_points / total_credits if total_credits > 0 else 0.0

def calculate_cgpa(semesters_data: AllSemestersData) -> Dict[str, float]:
  
    
    # Compute GPA for each semester using functional mapping
    gpa_results = {
        sem_name: calculate_gpa(data)
        for sem_name, data in semesters_data.items()
    }

    # Aggregate total weighted points and total credits across all semesters
    
    def semester_aggregator(semester_data: SemesterData) -> Dict[str, float]:
        """Helper to get total points and credits for a single semester."""
        points = reduce(
            lambda acc, subj: acc + (get_quality_points(subj['grade']) * subj['credits']),
            semester_data,
            0.0
        )
        credits = reduce(
            lambda acc, subj: acc + subj['credits'],
            semester_data,
            0.0
        )
        return {'total_points': points, 'total_credits': credits}

    # Use map/reduce-like structure on the semester aggregates
    all_semester_aggregates = list(map(
        lambda data: semester_aggregator(data),
        semesters_data.values()
    ))
    
    # Calculate overall totals
    total_gpa_points = reduce(
        lambda acc, agg: acc + agg['total_points'],
        all_semester_aggregates,
        0.0
    )
    total_credits = reduce(
        lambda acc, agg: acc + agg['total_credits'],
        all_semester_aggregates,
        0.0
    )

    # Calculate CGPA
    cgpa = total_gpa_points / total_credits if total_credits > 0 else 0.0

    return {
        'gpa_results': gpa_results,
        'total_gpa_points': total_gpa_points,
        'total_credits': total_credits,
        'cgpa': round(cgpa, 2)
    }