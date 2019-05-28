PERMISSION_GROUPS = [
    {
        'name': 'Organisation Access Request Officers',
        'per_activity': False,
        'permissions': ['organisation_access_request']
    },
    {
        'name': 'System Administrators',
        'per_activity': False,
        'permissions': ['system_administrator']
    },
    {
        'name': 'Licensing Officers',
        'per_activity': True,
        'permissions': ['licensing_officer']
    },
    {
        'name': 'Issuing Officers',
        'per_activity': True,
        'permissions': ['issuing_officer']
    },
    {
        'name': 'Assessors',
        'per_activity': True,
        'permissions': ['assessor']
    },
    {
        'name': 'Return Curators',
        'per_activity': True,
        'permissions': ['return_curator']
    },
    {
        'name': 'Payment Officers',
        'per_activity': False,
        'permissions': ['payment_officer']
    },
    {
        'name': 'Triage Call/Email',
        'per_district': True,
        'permissions': ['triage_call_email']
    },
    {
        'name': 'Officer',
        'per_district': True,
        'permissions': ['officer']
    },
    {
        'name': 'Manager',
        'per_district': True,
        'permissions': ['manager']
    },
    {
        'name': 'Volunteer',
        'per_district': False,
        'permissions': ['volunteer']
    },
    
]

CUSTOM_GROUP_PERMISSIONS = {
    'organisation_access_request': {
        'name': 'Organisation Access Request',
        'app_label': 'wildlifecompliance',
        'model': 'activitypermissiongroup',
    },
    'system_administrator': {
        'name': 'System Administrator',
        'app_label': 'wildlifecompliance',
        'model': 'activitypermissiongroup',
    },
    'licensing_officer': {
        'name': 'Licensing Officer',
        'app_label': 'wildlifecompliance',
        'model': 'activitypermissiongroup',
    },
    'issuing_officer': {
        'name': 'Issuing Officer',
        'app_label': 'wildlifecompliance',
        'model': 'activitypermissiongroup',
    },
    'assessor': {
        'name': 'Assessor',
        'app_label': 'wildlifecompliance',
        'model': 'activitypermissiongroup',
    },
    'return_curator': {
        'name': 'Return Curator',
        'app_label': 'wildlifecompliance',
        'model': 'activitypermissiongroup',
    },
    'payment_officer': {
        'name': 'Payment Officer',
        'app_label': 'wildlifecompliance',
        'model': 'activitypermissiongroup',
    },
    'triage_call_email': {
        'name': 'Triage Call/Email',
        'app_label': 'wildlifecompliance',
        'model': 'compliancepermissiongroup',
    },
    'officer': {
        'name': 'Officer',
        'app_label': 'wildlifecompliance',
        'model': 'compliancepermissiongroup',
    },
    'manager': {
        'name': 'Manager',
        'app_label': 'wildlifecompliance',
        'model': 'compliancepermissiongroup',
    },
    'volunteer': {
        'name': 'Volunteer',
        'app_label': 'wildlifecompliance',
        'model': 'compliancepermissiongroup',
    },
    
}

# COMPLIANCE_PERMISSION_GROUPS = [
#     {
#         'name': 'Triage Call/Email',
#         'per_district': True,
#         'permissions': ['triage_call_email']
#     },
#     {
#         'name': 'Officer',
#         'per_district': True,
#         'permissions': ['officer']
#     },
#     {
#         'name': 'Manager',
#         'per_district': True,
#         'permissions': ['manager']
#     },
#     {
#         'name': 'Volunteer',
#         'per_district': False,
#         'permissions': ['volunteer']
#     },
# ]

# COMPLIANCE_GROUP_PERMISSIONS = {
#     'triage_call_email': {
#         'name': 'Triage Call/Email',
#         'app_label': 'wildlifecompliance',
#         'model': 'compliancepermissiongroup',
#     },
#     'officer': {
#         'name': 'Officer',
#         'app_label': 'wildlifecompliance',
#         'model': 'compliancepermissiongroup',
#     },
#     'manager': {
#         'name': 'Manager',
#         'app_label': 'wildlifecompliance',
#         'model': 'compliancepermissiongroup',
#     },
#     'volunteer': {
#         'name': 'Volunteer',
#         'app_label': 'wildlifecompliance',
#         'model': 'compliancepermissiongroup',
#     },
# }
