import os
import sys
import random
from datetime import timedelta

import django
from django.utils import timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()


def create_admin():
    if not User.objects.filter(is_superuser=True).exists():
        User.objects.create_superuser(
            email="admin@jobcare.voice",
            phone="+919999999999",
            password="admin123",
            role="admin",
        )
        print("  Admin user created")
    else:
        print("  Admin user already exists")


def create_categories():
    from jobs.models import Category
    categories_data = [
        {"name": "Electrician", "description": "Electrical wiring, repair, and installation services", "icon": "⚡"},
        {"name": "Plumber", "description": "Pipe fitting, drainage, and water supply services", "icon": "🔧"},
        {"name": "Painter", "description": "Interior and exterior painting services", "icon": "🎨"},
        {"name": "Carpenter", "description": "Woodwork, furniture making, and repair services", "icon": "🪚"},
        {"name": "Welder", "description": "Metal welding and fabrication services", "icon": "🔥"},
        {"name": "Driver", "description": "Transportation and delivery driving services", "icon": "🚗"},
        {"name": "Delivery Partner", "description": "Package and food delivery services", "icon": "📦"},
        {"name": "Warehouse Worker", "description": "Inventory management and warehouse operations", "icon": "📋"},
        {"name": "Construction Worker", "description": "Building construction and labor services", "icon": "🏗️"},
        {"name": "Security Guard", "description": "Security and surveillance services", "icon": "🛡️"},
        {"name": "Housekeeping", "description": "Cleaning and housekeeping services", "icon": "🧹"},
        {"name": "Hotel Staff", "description": "Front desk, housekeeping, and hospitality services", "icon": "🏨"},
        {"name": "Factory Worker", "description": "Manufacturing and production line work", "icon": "🏭"},
        {"name": "Office Boy", "description": "Office assistance and support services", "icon": "📎"},
        {"name": "Cook", "description": "Food preparation and cooking services", "icon": "👨‍🍳"},
        {"name": "Maid", "description": "Domestic help and cleaning services", "icon": "🧹"},
        {"name": "Gardener", "description": "Gardening and landscaping services", "icon": "🌿"},
        {"name": "Nurse Assistant", "description": "Patient care and medical assistance", "icon": "🏥"},
        {"name": "Helper", "description": "General labor and assistance services", "icon": "🤝"},
        {"name": "Technician", "description": "AC, refrigerator, and appliance repair services", "icon": "🔧"},
    ]
    created = 0
    for cat in categories_data:
        _, is_new = Category.objects.get_or_create(name=cat["name"], defaults=cat)
        if is_new:
            created += 1
    print(f"  {created} categories created ({len(categories_data)} total)")


def create_skills():
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
            print(f"  Category '{cat_name}' not found, skipping")
    print(f"  {created} skills created")


def create_cities():
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
    print(f"  {created} cities created ({len(cities)} total)")


def create_subscription_plans():
    from payments.models import SubscriptionPlan
    plans = [
        {"name": "Free", "plan_type": "employer_subscription", "description": "Basic job search and application features", "price": 0, "billing_cycle": "monthly", "features": ["job_search", "apply_jobs", "application_tracking", "job_alerts"], "is_active": True, "sort_order": 0},
        {"name": "Basic", "plan_type": "employer_subscription", "description": "Enhanced features with voice search support", "price": 299, "billing_cycle": "monthly", "features": ["job_search", "apply_jobs", "voice_search", "resume_builder", "advanced_filters", "application_tracking", "job_alerts"], "is_active": True, "sort_order": 1},
        {"name": "Professional", "plan_type": "employer_subscription", "description": "Complete job search toolkit for serious candidates", "price": 799, "billing_cycle": "monthly", "features": ["job_search", "apply_jobs", "voice_search", "priority_support", "resume_builder", "skill_assessment", "direct_employer_chat", "advanced_filters", "application_tracking", "job_alerts"], "is_active": True, "sort_order": 2},
        {"name": "Enterprise", "plan_type": "employer_subscription", "description": "For employers and bulk recruiters", "price": 4999, "billing_cycle": "monthly", "features": ["job_search", "apply_jobs", "voice_search", "priority_support", "resume_builder", "skill_assessment", "direct_employer_chat", "advanced_filters", "application_tracking", "job_alerts", "api_access"], "is_active": True, "sort_order": 3},
    ]
    created = 0
    for p in plans:
        _, is_new = SubscriptionPlan.objects.get_or_create(name=p["name"], defaults=p)
        if is_new:
            created += 1
    print(f"  {created} subscription plans created ({len(plans)} total)")


def create_employer():
    from employers.models import EmployerProfile
    from companies.models import Company
    employer = EmployerProfile.objects.first()
    if employer:
        return employer
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        admin = User.objects.create_superuser(
            email="employer@jobcare.voice",
            phone="+918888888888",
            password="employer123",
            role="admin",
        )
    company, _ = Company.objects.get_or_create(
        name="JobCare Services",
        defaults={
            "description": "Leading blue-collar recruitment platform",
            "industry": "other",
            "verification_status": "verified",
        },
    )
    employer, _ = EmployerProfile.objects.get_or_create(
        user=admin,
        defaults={
            "full_name": "Admin Employer",
            "company": company,
            "is_verified": True,
            "is_company_admin": True,
        },
    )
    print(f"  Employer '{company.name}' ready")
    return employer


def create_sample_jobs():
    from jobs.models import Category, City, Job
    from employers.models import EmployerProfile
    from companies.models import Company

    employer_profile = create_employer()
    company = Company.objects.first()
    user = User.objects.filter(is_superuser=True).first()
    if not company or not user:
        print("  Cannot create jobs: company or user missing")
        return

    categories = {c.name: c for c in Category.objects.all()}
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
        if not cat:
            continue
        _, is_new = Job.objects.get_or_create(
            title=j["title"],
            company=company,
            defaults={
                "employer": user,
                "company": company,
                "category": cat,
                "city": j["city"],
                "description": f"We are looking for an experienced {j['cat']} to join our team. Immediate joining preferred.",
                "requirements": [f"Minimum 1 year of experience", "Reliable and punctual", "Good communication skills", "Own tools preferred"],
                "responsibilities": [f"Perform {j['cat'].lower()} duties as assigned", "Maintain quality standards", "Follow safety protocols", "Report to supervisor"],
                "job_type": j["type"],
                "salary_min": j["min"],
                "salary_max": j["max"],
                "salary_type": "monthly",
                "is_featured": random.choice([True, False]),
                "openings": random.randint(1, 5),
            },
        )
        if is_new:
            created += 1
    print(f"  {created} sample jobs created ({len(sample_jobs)} total)")


if __name__ == "__main__":
    print("=== Seeding Database ===\n")
    print("[1/6] Creating admin user...")
    create_admin()
    print("[2/6] Creating categories...")
    create_categories()
    print("[3/6] Creating skills...")
    create_skills()
    print("[4/6] Creating cities...")
    create_cities()
    print("[5/6] Creating subscription plans...")
    create_subscription_plans()
    print("[6/6] Creating sample jobs...")
    create_sample_jobs()
    print("\n=== Seeding Complete! ===")
