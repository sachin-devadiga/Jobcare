from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = "Seed the database with initial data (categories, skills, cities, plans, jobs)"

    def handle(self, *args, **options):
        self.stdout.write("=== Seeding Database ===\n")

        self.stdout.write("[1/6] Creating admin user...")
        self._create_admin()

        self.stdout.write("[2/6] Creating categories...")
        self._create_categories()

        self.stdout.write("[3/6] Creating skills...")
        self._create_skills()

        self.stdout.write("[4/6] Creating cities...")
        self._create_cities()

        self.stdout.write("[5/6] Creating subscription plans...")
        self._create_subscription_plans()

        self.stdout.write("[6/6] Creating sample jobs...")
        self._create_sample_jobs()

        self.stdout.write(self.style.SUCCESS("=== Seeding Complete! ==="))

    def _create_admin(self):
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                email="admin@jobcare.voice",
                phone="9999999999",
                password="admin123",
                user_type="admin",
                is_active=True,
                is_staff=True,
            )
            self.stdout.write(self.style.SUCCESS("  Admin user created"))
        else:
            self.stdout.write("  Admin user already exists")

    def _create_categories(self):
        from jobs.models import Category

        categories_data = [
            {"name": "Electrician", "description": "Electrical wiring, repair, and installation services", "icon": "⚡", "color": "#FFD700"},
            {"name": "Plumber", "description": "Pipe fitting, drainage, and water supply services", "icon": "🔧", "color": "#1E90FF"},
            {"name": "Painter", "description": "Interior and exterior painting services", "icon": "🎨", "color": "#FF6347"},
            {"name": "Carpenter", "description": "Woodwork, furniture making, and repair services", "icon": "🪚", "color": "#8B4513"},
            {"name": "Welder", "description": "Metal welding and fabrication services", "icon": "🔥", "color": "#FF4500"},
            {"name": "Driver", "description": "Transportation and delivery driving services", "icon": "🚗", "color": "#32CD32"},
            {"name": "Delivery Partner", "description": "Package and food delivery services", "icon": "📦", "color": "#FF69B4"},
            {"name": "Warehouse Worker", "description": "Inventory management and warehouse operations", "icon": "📋", "color": "#A0522D"},
            {"name": "Construction Worker", "description": "Building construction and labor services", "icon": "🏗️", "color": "#D2691E"},
            {"name": "Security Guard", "description": "Security and surveillance services", "icon": "🛡️", "color": "#2F4F4F"},
            {"name": "Housekeeping", "description": "Cleaning and housekeeping services", "icon": "🧹", "color": "#9370DB"},
            {"name": "Hotel Staff", "description": "Front desk, housekeeping, and hospitality services", "icon": "🏨", "color": "#DAA520"},
            {"name": "Factory Worker", "description": "Manufacturing and production line work", "icon": "🏭", "color": "#708090"},
            {"name": "Office Boy", "description": "Office assistance and support services", "icon": "📎", "color": "#4682B4"},
            {"name": "Cook", "description": "Food preparation and cooking services", "icon": "👨‍🍳", "color": "#FF6347"},
            {"name": "Maid", "description": "Domestic help and cleaning services", "icon": "🧹", "color": "#DB7093"},
            {"name": "Gardener", "description": "Gardening and landscaping services", "icon": "🌿", "color": "#228B22"},
            {"name": "Nurse Assistant", "description": "Patient care and medical assistance", "icon": "🏥", "color": "#00CED1"},
            {"name": "Helper", "description": "General labor and assistance services", "icon": "🤝", "color": "#BDB76B"},
            {"name": "Technician", "description": "AC, refrigerator, and appliance repair services", "icon": "🔧", "color": "#4169E1"},
        ]

        created = 0
        for cat in categories_data:
            _, is_new = Category.objects.get_or_create(name=cat["name"], defaults=cat)
            if is_new:
                created += 1
        self.stdout.write(f"  {created} categories created ({len(categories_data)} total)")

    def _create_skills(self):
        from jobs.models import Category, Skill

        skills_map = {
            "Electrician": ["Electrical Wiring", "Circuit Installation", "Lighting Setup", "Panel Board Repair", "Home Automation", "Industrial Wiring", "Generator Maintenance", "Solar Panel Installation", "Security System Installation", "Electrical Safety Inspection"],
            "Plumber": ["Pipe Fitting", "Drain Cleaning", "Water Heater Installation", "Tap Repair", "Toilet Installation", "Pipeline Repair", "Water Purifier Installation", "Drainage System", "Bathroom Fitting", "Gas Line Installation"],
            "Painter": ["Wall Painting", "Texture Painting", "Waterproofing", "Wood Polishing", "Spray Painting", "Wallpaper Installation", "Interior Design", "Exterior Painting", "Furniture Painting", "Metal Painting"],
            "Carpenter": ["Furniture Making", "Cabinet Installation", "Door Repair", "Window Fitting", "Wood Polishing", "Modular Kitchen", "Carpet Installation", "Deck Building", "Furniture Assembly", "Custom Woodwork"],
            "Welder": ["Arc Welding", "MIG Welding", "TIG Welding", "Metal Fabrication", "Pipe Welding", "Structural Welding", "Aluminum Welding", "Stainless Steel Welding", "Auto Body Repair", "Industrial Welding"],
            "Driver": ["Car Driving", "Bus Driving", "Truck Driving", "Auto Rickshaw Driving", "Heavy Vehicle Operation", "Long Distance Driving", "Delivery Driving", "Chauffeur Service", "School Transport", "Tourist Vehicle Operation"],
            "Delivery Partner": ["Food Delivery", "Package Delivery", "E-commerce Delivery", "Same Day Delivery", "Route Planning", "Customer Service", "Cash Collection", "Temperature Controlled Delivery", "Bulk Delivery", "Time Slot Delivery"],
            "Warehouse Worker": ["Inventory Management", "Order Picking", "Packing", "Loading/Unloading", "Forklift Operation", "Stock Replenishment", "Quality Check", "Barcode Scanning", "Warehouse Organization", "Shipment Preparation"],
            "Construction Worker": ["Masonry", "Concrete Work", "Rebar Binding", "Formwork", "Tiling", "Plastering", "Demolition", "Site Cleanup", "Scaffolding", "Excavation"],
            "Security Guard": ["Gate Control", "Patrol", "CCTV Monitoring", "Access Control", "Emergency Response", "Fire Safety", "Visitor Management", "Report Writing", "Conflict Resolution", "First Aid"],
            "Housekeeping": ["Room Cleaning", "Bathroom Cleaning", "Floor Mopping", "Dusting", "Window Cleaning", "Trash Removal", "Deep Cleaning", "Laundry", "Kitchen Cleaning", "Office Cleaning"],
            "Hotel Staff": ["Front Desk Operation", "Room Service", "Guest Handling", "Check-in/Check-out", "Reservation Management", "Bell Desk Service", "Concierge", "Event Coordination", "Housekeeping Supervision", "Restaurant Service"],
            "Factory Worker": ["Assembly Line Work", "Machine Operation", "Quality Control", "Packing", "Material Handling", "Production Support", "Maintenance", "Safety Compliance", "Batch Processing", "Inventory Tracking"],
            "Office Boy": ["Photocopying", "Filing", "Mail Distribution", "Tea/Coffee Service", "Cleaning", "Errand Running", "Office Supply Management", "Courier Management", "Meeting Room Setup", "Visitor Assistance"],
            "Cook": ["Indian Cuisine", "Continental Cooking", "Baking", "Meal Planning", "Menu Preparation", "Kitchen Hygiene", "Inventory Management", "Special Diet Cooking", "Street Food", "Confectionery"],
            "Maid": ["House Cleaning", "Dish Washing", "Laundry", "Ironing", "Cooking Assistance", "Child Care", "Elder Care", "Pet Care", "Groceries Shopping", "Home Organization"],
            "Gardener": ["Planting", "Pruning", "Lawn Mowing", "Irrigation", "Fertilization", "Pest Control", "Landscape Design", "Tree Trimming", "Garden Cleanup", "Indoor Plant Care"],
            "Nurse Assistant": ["Patient Monitoring", "Medication Assistance", "Vital Signs Check", "Wound Care", "Mobility Support", "Personal Hygiene", "Feeding Assistance", "Bedside Care", "Medical Record Keeping", "Elderly Care"],
            "Helper": ["Loading/Unloading", "Cleaning", "Material Moving", "Basic Repair", "Site Assistance", "Event Setup", "Painting Assistance", "Gardening Help", "Packing", "General Labor"],
            "Technician": ["AC Repair", "Refrigerator Repair", "Washing Machine Repair", "Microwave Repair", "TV Repair", "Water Purifier Repair", "Geyser Repair", "Chimney Repair", "Electrical Appliance Repair", "Home Appliance Installation"],
        }

        created = 0
        for cat_name, skill_list in skills_map.items():
            try:
                cat = Category.objects.get(name=cat_name)
                for s in skill_list:
                    _, is_new = Skill.objects.get_or_create(name=s, defaults={"category": cat})
                    if is_new:
                        created += 1
            except Category.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"  Category '{cat_name}' not found, skipping"))
        self.stdout.write(f"  {created} skills created")

    def _create_cities(self):
        from jobs.models import City

        cities = [
            {"name": "Mumbai", "state": "Maharashtra", "is_active": True},
            {"name": "Delhi", "state": "Delhi", "is_active": True},
            {"name": "Bangalore", "state": "Karnataka", "is_active": True},
            {"name": "Hyderabad", "state": "Telangana", "is_active": True},
            {"name": "Ahmedabad", "state": "Gujarat", "is_active": True},
            {"name": "Chennai", "state": "Tamil Nadu", "is_active": True},
            {"name": "Kolkata", "state": "West Bengal", "is_active": True},
            {"name": "Pune", "state": "Maharashtra", "is_active": True},
            {"name": "Jaipur", "state": "Rajasthan", "is_active": True},
            {"name": "Lucknow", "state": "Uttar Pradesh", "is_active": True},
            {"name": "Surat", "state": "Gujarat", "is_active": True},
            {"name": "Nagpur", "state": "Maharashtra", "is_active": True},
            {"name": "Indore", "state": "Madhya Pradesh", "is_active": True},
            {"name": "Bhopal", "state": "Madhya Pradesh", "is_active": True},
            {"name": "Visakhapatnam", "state": "Andhra Pradesh", "is_active": True},
            {"name": "Patna", "state": "Bihar", "is_active": True},
            {"name": "Vadodara", "state": "Gujarat", "is_active": True},
            {"name": "Coimbatore", "state": "Tamil Nadu", "is_active": True},
            {"name": "Guwahati", "state": "Assam", "is_active": True},
            {"name": "Chandigarh", "state": "Chandigarh", "is_active": True},
            {"name": "Mysore", "state": "Karnataka", "is_active": True},
            {"name": "Nashik", "state": "Maharashtra", "is_active": True},
            {"name": "Agra", "state": "Uttar Pradesh", "is_active": True},
            {"name": "Varanasi", "state": "Uttar Pradesh", "is_active": True},
            {"name": "Amritsar", "state": "Punjab", "is_active": True},
            {"name": "Ludhiana", "state": "Punjab", "is_active": True},
            {"name": "Kanpur", "state": "Uttar Pradesh", "is_active": True},
            {"name": "Thane", "state": "Maharashtra", "is_active": True},
            {"name": "Ranchi", "state": "Jharkhand", "is_active": True},
            {"name": "Jodhpur", "state": "Rajasthan", "is_active": True},
            {"name": "Raipur", "state": "Chhattisgarh", "is_active": True},
            {"name": "Kochi", "state": "Kerala", "is_active": True},
        ]

        created = 0
        for c in cities:
            _, is_new = City.objects.get_or_create(name=c["name"], defaults=c)
            if is_new:
                created += 1
        self.stdout.write(f"  {created} cities created ({len(cities)} total)")

    def _create_subscription_plans(self):
        from payments.models import SubscriptionPlan

        plans = [
            {"name": "Free", "code": "free", "description": "Basic job search and application features", "price": 0, "currency": "INR", "duration_days": 36500, "features": {"job_search": True, "apply_jobs": True, "voice_search": False, "priority_support": False, "resume_builder": False, "skill_assessment": False, "certificate": False, "direct_employer_chat": False, "advanced_filters": False, "application_tracking": True, "job_alerts": True, "max_applications_per_month": 20}, "is_active": True, "sort_order": 0},
            {"name": "Basic", "code": "basic", "description": "Enhanced features with voice search support", "price": 299, "currency": "INR", "duration_days": 30, "features": {"job_search": True, "apply_jobs": True, "voice_search": True, "priority_support": False, "resume_builder": True, "skill_assessment": False, "certificate": False, "direct_employer_chat": False, "advanced_filters": True, "application_tracking": True, "job_alerts": True, "max_applications_per_month": 50}, "is_active": True, "sort_order": 1},
            {"name": "Professional", "code": "professional", "description": "Complete job search toolkit for serious candidates", "price": 799, "currency": "INR", "duration_days": 30, "features": {"job_search": True, "apply_jobs": True, "voice_search": True, "priority_support": True, "resume_builder": True, "skill_assessment": True, "certificate": True, "direct_employer_chat": True, "advanced_filters": True, "application_tracking": True, "job_alerts": True, "max_applications_per_month": 200}, "is_active": True, "sort_order": 2},
            {"name": "Enterprise", "code": "enterprise", "description": "For employers and bulk recruiters", "price": 4999, "currency": "INR", "duration_days": 30, "features": {"job_search": True, "apply_jobs": True, "voice_search": True, "priority_support": True, "resume_builder": True, "skill_assessment": True, "certificate": True, "direct_employer_chat": True, "advanced_filters": True, "application_tracking": True, "job_alerts": True, "unlimited_applications": True, "bulk_applications": True, "api_access": True, "dedicated_account_manager": True, "custom_integrations": True, "max_applications_per_month": 99999}, "is_active": True, "sort_order": 3},
        ]

        created = 0
        for p in plans:
            _, is_new = SubscriptionPlan.objects.get_or_create(code=p["code"], defaults=p)
            if is_new:
                created += 1
        self.stdout.write(f"  {created} subscription plans created ({len(plans)} total)")

    def _create_sample_jobs(self):
        from jobs.models import Category, City, Job
        from employers.models import EmployerProfile

        employer = EmployerProfile.objects.first()
        if not employer:
            self.stdout.write(self.style.WARNING("  No employer found. Create an employer first."))
            return

        categories = {c.name: c for c in Category.objects.all()}
        cities = {c.name: c for c in City.objects.all()}

        sample_jobs = [
            {"title": "Experienced Electrician", "cat": "Electrician", "city": "Mumbai", "type": "full_time", "min": 15000, "max": 35000},
            {"title": "Plumber for Residential Projects", "cat": "Plumber", "city": "Delhi", "type": "full_time", "min": 12000, "max": 30000},
            {"title": "House Painter Needed", "cat": "Painter", "city": "Bangalore", "type": "contract", "min": 10000, "max": 25000},
            {"title": "Skilled Carpenter for Furniture", "cat": "Carpenter", "city": "Hyderabad", "type": "full_time", "min": 18000, "max": 40000},
            {"title": "MIG Welder for Factory", "cat": "Welder", "city": "Pune", "type": "full_time", "min": 20000, "max": 45000},
            {"title": "Delivery Driver - Zomato/Swiggy", "cat": "Driver", "city": "Ahmedabad", "type": "part_time", "min": 10000, "max": 25000},
            {"title": "Warehouse Associate", "cat": "Warehouse Worker", "city": "Chennai", "type": "full_time", "min": 12000, "max": 25000},
            {"title": "Security Guard - Mall", "cat": "Security Guard", "city": "Kolkata", "type": "full_time", "min": 10000, "max": 20000},
            {"title": "Hotel Housekeeper", "cat": "Housekeeping", "city": "Jaipur", "type": "full_time", "min": 8000, "max": 18000},
            {"title": "Restaurant Cook", "cat": "Cook", "city": "Lucknow", "type": "full_time", "min": 12000, "max": 28000},
            {"title": "Gardener for Golf Course", "cat": "Gardener", "city": "Surat", "type": "full_time", "min": 10000, "max": 22000},
            {"title": "Patient Care Assistant", "cat": "Nurse Assistant", "city": "Nagpur", "type": "full_time", "min": 14000, "max": 30000},
            {"title": "AC Technician", "cat": "Technician", "city": "Indore", "type": "full_time", "min": 15000, "max": 35000},
            {"title": "Hotel Front Desk Staff", "cat": "Hotel Staff", "city": "Bhopal", "type": "full_time", "min": 10000, "max": 22000},
            {"title": "Factory Assembly Worker", "cat": "Factory Worker", "city": "Surat", "type": "full_time", "min": 8000, "max": 18000},
        ]

        created = 0
        for j in sample_jobs:
            cat = categories.get(j["cat"])
            city = cities.get(j["city"])
            if not cat or not city:
                continue
            _, is_new = Job.objects.get_or_create(
                title=j["title"],
                employer=employer,
                defaults={
                    "category": cat,
                    "city": city,
                    "description": f"We are looking for an experienced {j['cat']} to join our team. Immediate joining preferred.",
                    "requirements": "- Minimum 1 year of experience\n- Reliable and punctual\n- Good communication skills\n- Own tools preferred",
                    "responsibilities": f"- Perform {j['cat'].lower()} duties as assigned\n- Maintain quality standards\n- Follow safety protocols\n- Report to supervisor",
                    "employment_type": j["type"],
                    "min_salary": j["min"],
                    "max_salary": j["max"],
                    "salary_period": "monthly",
                    "currency": "INR",
                    "is_active": True,
                    "is_featured": random.choice([True, False]),
                    "vacancies": random.randint(1, 5),
                    "application_deadline": timezone.now().date() + timedelta(days=random.randint(15, 60)),
                },
            )
            if is_new:
                created += 1
        self.stdout.write(f"  {created} sample jobs created ({len(sample_jobs)} total)")
