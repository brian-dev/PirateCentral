UIL_CONFERENCES = [
    ("", "Please select a division"),
    ("1A Division 1", "1A Division 1"),
    ("1A Division 2", "1A Division 2"),
    ("2A Division 1", "2A Division 1"),
    ("2A Division 2", "2A Division 2"),
    ("3A Division 1", "3A Division 1"),
    ("3A Division 2", "3A Division 2"),
    ("4A Division 1", "4A Division 1"),
    ("4A Division 2", "4A Division 2"),
    ("5A Division 1", "5A Division 1"),
    ("5A Division 2", "5A Division 2"),
    ("6A", "6A"),
]
UIL_DISTRICTS = [("", "Please select a district")] + [(f'District {i}', f'District {i}') for i in range(1, 33)]
UIL_REGIONS = [("", "Please select a region")] + [(f'Region {i}', f'Region {i}') for i in range(1, 5)]
GRADE_LEVELS =[
    ('', 'Please select a grade level'),
    ('Varsity', 'Varsity'),
    ('Junior Varsity', 'Junior Varsity'),
    ('Freshman', 'Freshman'),
    ('8th Grade', '8th Grade'),
    ('7th Grade', '7th Grade')
]