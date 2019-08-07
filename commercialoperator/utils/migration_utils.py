from commercialoperator.components.main.models import Park, Activity, AccessType
import csv

def read_csv(filename):
    pass
    

def create_parks(filename):
    """
    Example csv:
        district_id, park name, park_short_code, park_type, adult_price, child_price, concession_price, oracle_code, allowed_activities, allowed_access_types
        1,'My New Park 2','ABC2', 'land', 10.00, 7.00, 5.00, 'ABC 123 GST', 'ALL', 'ALL' 
        2,'My New Park 3','ABC3', 'land', 10.00, 7.00, 5.00, 'ABC 123 GST', 'ALL', 'ALL' 
    """
    land_activities = Activity.objects.filter(activity_category__activity_type='land')
    marine_activities = Activity.objects.filter(activity_category__activity_type='marine')
    try:
        with open(filename) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                district_id = row[0]
                park name = row[1]
                park_short_code = row[2]
                park_type = row[3]
                adult_price = row[4]
                child_price = row[5]
                concession_price = row[6]
                oracle_code = row[7]
                allowed_activities = row[8]
                allowed_access_types = row[9]

                park = Park.objects.create(
                    district_id=district_id,
                    name=park_name,
                    park_type=park_type, #'land',
                    adult_price=adult_price,
                    child_price=child_price,
                    concession_price=concession_price,
                    oracle_code=oracle_code
                )

                if allowed_access_types=='ALL' and park_type=='land':
                    park.allowed_access.add(*AccessType.objects.all())

                if allowed_activities=='ALL' and park_type=='land':
                    park.allowed_activities.add(*land_activities)
                elif allowed_activities=='ALL' and park_type=='marine':
                    park.allowed_activities.add(*marine_activities)



