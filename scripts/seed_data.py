#!/usr/bin/env python
"""
Django management command to seed the database with initial data.
Run: python manage.py seed_data
"""

import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()

def create_admin():
    if not User.objects.filter(is_superuser=True).exists():
        User.objects.create_superuser(
            email="admin@jobcare.voice",
            phone="9999999999",
            password="admin123",
            user_type="admin",
            is_active=True,
            is_staff=True,
        )
        print("  [OK] Admin user created")
    else:
        print("  [SKIP] Admin user already exists")


def create_categories():
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

    created_count = 0
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data["name"],
            defaults=cat_data,
        )
        if created:
            created_count += 1
    print(f"  [OK] {created_count} categories created ({len(categories_data)} total)")


def create_skills():
    from jobs.models import Category, Skill

    skills_data = {
        "Electrician": [
            "Electrical Wiring", "Circuit Installation", "Lighting Setup", "Panel Board Repair",
            "Home Automation", "Industrial Wiring", "Generator Maintenance", "Solar Panel Installation",
            "Security System Installation", "Electrical Safety Inspection",
        ],
        "Plumber": [
            "Pipe Fitting", "Drain Cleaning", "Water Heater Installation", "Tap Repair",
            "Toilet Installation", "Pipeline Repair", "Water Purifier Installation", "Drainage System",
            "Bathroom Fitting", "Gas Line Installation",
        ],
        "Painter": [
            "Wall Painting", "Texture Painting", "Waterproofing", "Wood Polishing",
            "Spray Painting", "Wallpaper Installation", "Interior Design", "Exterior Painting",
            "Furniture Painting", "Metal Painting",
        ],
        "Carpenter": [
            "Furniture Making", "Cabinet Installation", "Door Repair", "Window Fitting",
            "Wood Polishing", "Modular Kitchen", "Carpet Installation", "Deck Building",
            "Furniture Assembly", "Custom Woodwork",
        ],
        "Welder": [
            "Arc Welding", "MIG Welding", "TIG Welding", "Metal Fabrication",
            "Pipe Welding", "Structural Welding", "Aluminum Welding", "Stainless Steel Welding",
            "Auto Body Repair", "Industrial Welding",
        ],
        "Driver": [
            "Car Driving", "Bus Driving", "Truck Driving", "Auto Rickshaw Driving",
            "Heavy Vehicle Operation", "Long Distance Driving", "Delivery Driving", "Chauffeur Service",
            "School Transport", "Tourist Vehicle Operation",
        ],
        "Delivery Partner": [
            "Food Delivery", "Package Delivery", "E-commerce Delivery", "Same Day Delivery",
            "Route Planning", "Customer Service", "Cash Collection", "Temperature Controlled Delivery",
            "Bulk Delivery", "Time Slot Delivery",
        ],
        "Warehouse Worker": [
            "Inventory Management", "Order Picking", "Packing", "Loading/Unloading",
            "Forklift Operation", "Stock Replenishment", "Quality Check", "Barcode Scanning",
            "Warehouse Organization", "Shipment Preparation",
        ],
        "Construction Worker": [
            "Masonry", "Concrete Work", "Rebar Binding", "Formwork",
            "Tiling", "Plastering", "Demolition", "Site Cleanup",
            "Scaffolding", "Excavation",
        ],
        "Security Guard": [
            "Gate Control", "Patrol", "CCTV Monitoring", "Access Control",
            "Emergency Response", "Fire Safety", "Visitor Management", "Report Writing",
            "Conflict Resolution", "First Aid",
        ],
        "Housekeeping": [
            "Room Cleaning", "Bathroom Cleaning", "Floor Mopping", "Dusting",
            "Window Cleaning", "Trash Removal", "Deep Cleaning", "Laundry",
            "Kitchen Cleaning", "Office Cleaning",
        ],
        "Hotel Staff": [
            "Front Desk Operation", "Room Service", "Guest Handling", "Check-in/Check-out",
            "Reservation Management", "Bell Desk Service", "Concierge", "Event Coordination",
            "Housekeeping Supervision", "Restaurant Service",
        ],
        "Factory Worker": [
            "Assembly Line Work", "Machine Operation", "Quality Control", "Packing",
            "Material Handling", "Production Support", "Maintenance", "Safety Compliance",
            "Batch Processing", "Inventory Tracking",
        ],
        "Office Boy": [
            "Photocopying", "Filing", "Mail Distribution", "Tea/Coffee Service",
            "Cleaning", "Errand Running", "Office Supply Management", "Courier Management",
            "Meeting Room Setup", "Visitor Assistance",
        ],
        "Cook": [
            "Indian Cuisine", "Continental Cooking", "Baking", "Meal Planning",
            "Menu Preparation", "Kitchen Hygiene", "Inventory Management", "Special Diet Cooking",
            "Street Food", "Confectionery",
        ],
        "Maid": [
            "House Cleaning", "Dish Washing", "Laundry", "Ironing",
            "Cooking Assistance", "Child Care", "Elder Care", "Pet Care",
            "Groceries Shopping", "Home Organization",
        ],
        "Gardener": [
            "Planting", "Pruning", "Lawn Mowing", "Irrigation",
            "Fertilization", "Pest Control", "Landscape Design", "Tree Trimming",
            "Garden Cleanup", "Indoor Plant Care",
        ],
        "Nurse Assistant": [
            "Patient Monitoring", "Medication Assistance", "Vital Signs Check", "Wound Care",
            "Mobility Support", "Personal Hygiene", "Feeding Assistance", "Bedside Care",
            "Medical Record Keeping", "Elderly Care",
        ],
        "Helper": [
            "Loading/Unloading", "Cleaning", "Material Moving", "Basic Repair",
            "Site Assistance", "Event Setup", "Painting Assistance", "Gardening Help",
            "Packing", "General Labor",
        ],
        "Technician": [
            "AC Repair", "Refrigerator Repair", "Washing Machine Repair", "Microwave Repair",
            "TV Repair", "Water Purifier Repair", "Geyser Repair", "Chimney Repair",
            "Electrical Appliance Repair", "Home Appliance Installation",
        ],
    }

    created_count = 0
    for category_name, skills in skills_data.items():
        try:
            category = Category.objects.get(name=category_name)
            for skill_name in skills:
                skill, created = Skill.objects.get_or_create(
                    name=skill_name,
                    defaults={"category": category},
                )
                if created:
                    created_count += 1
        except Category.DoesNotExist:
            print(f"  [WARN] Category '{category_name}' not found, skipping skills")

    print(f"  [OK] {created_count} skills created")


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

    created_count = 0
    for city_data in cities:
        city, created = City.objects.get_or_create(
            name=city_data["name"],
            defaults=city_data,
        )
        if created:
            created_count += 1
    print(f"  [OK] {created_count} cities created ({len(cities)} total)")


def create_subscription_plans():
    from payments.models import SubscriptionPlan

    plans = [
        {
            "name": "Free",
            "code": "free",
            "description": "Basic job search and application features",
            "price": 0,
            "currency": "INR",
            "duration_days": 36500,
            "features": {
                "job_search": True,
                "apply_jobs": True,
                "voice_search": False,
                "priority_support": False,
                "resume_builder": False,
                "skill_assessment": False,
                "certificate": False,
                "direct_employer_chat": False,
                "advanced_filters": False,
                "application_tracking": True,
                "job_alerts": True,
                "max_applications_per_month": 20,
            },
            "is_active": True,
            "sort_order": 0,
        },
        {
            "name": "Basic",
            "code": "basic",
            "description": "Enhanced features with voice search support",
            "price": 299,
            "currency": "INR",
            "duration_days": 30,
            "features": {
                "job_search": True,
                "apply_jobs": True,
                "voice_search": True,
                "priority_support": False,
                "resume_builder": True,
                "skill_assessment": False,
                "certificate": False,
                "direct_employer_chat": False,
                "advanced_filters": True,
                "application_tracking": True,
                "job_alerts": True,
                "max_applications_per_month": 50,
            },
            "is_active": True,
            "sort_order": 1,
        },
        {
            "name": "Professional",
            "code": "professional",
            "description": "Complete job search toolkit for serious candidates",
            "price": 799,
            "currency": "INR",
            "duration_days": 30,
            "features": {
                "job_search": True,
                "apply_jobs": True,
                "voice_search": True,
                "priority_support": True,
                "resume_builder": True,
                "skill_assessment": True,
                "certificate": True,
                "direct_employer_chat": True,
                "advanced_filters": True,
                "application_tracking": True,
                "job_alerts": True,
                "max_applications_per_month": 200,
            },
            "is_active": True,
            "sort_order": 2,
        },
        {
            "name": "Enterprise",
            "code": "enterprise",
            "description": "For employers and bulk recruiters",
            "price": 4999,
            "currency": "INR",
            "duration_days": 30,
            "features": {
                "job_search": True,
                "apply_jobs": True,
                "voice_search": True,
                "priority_support": True,
                "resume_builder": True,
                "skill_assessment": True,
                "certificate": True,
                "direct_employer_chat": True,
                "advanced_filters": True,
                "application_tracking": True,
                "job_alerts": True,
                "unlimited_applications": True,
                "bulk_applications": True,
                "api_access": True,
                "dedicated_account_manager": True,
                "custom_integrations": True,
                "max_applications_per_month": 99999,
            },
            "is_active": True,
            "sort_order": 3,
        },
    ]

    created_count = 0
    for plan_data in plans:
        plan, created = SubscriptionPlan.objects.get_or_create(
            code=plan_data["code"],
            defaults=plan_data,
        )
        if created:
            created_count += 1
    print(f"  [OK] {created_count} subscription plans created ({len(plans)} total)")


def create_sample_jobs():
    from jobs.models import Category, City, Job
    from employers.models import EmployerProfile
    from companies.models import Company

    employer = EmployerProfile.objects.first()
    if not employer:
        print("  [SKIP] No employer found. Create an employer first to generate sample jobs.")
        return

    categories = list(Category.objects.all())
    cities = list(City.objects.all())

    if not categories or not cities:
        print("  [SKIP] Categories or cities not found. Seed them first.")
        return

    sample_jobs = [
        {"title": "Experienced Electrician", "category": "Electrician", "city": "Mumbai", "employment_type": "full_time", "min_salary": 15000, "max_salary": 35000},
        {"title": "Plumber for Residential Projects", "category": "Plumber", "city": "Delhi", "employment_type": "full_time", "min_salary": 12000, "max_salary": 30000},
        {"title": "House Painter Needed", "category": "Painter", "city": "Bangalore", "employment_type": "contract", "min_salary": 10000, "max_salary": 25000},
        {"title": "Skilled Carpenter for Furniture", "category": "Carpenter", "city": "Hyderabad", "employment_type": "full_time", "min_salary": 18000, "max_salary": 40000},
        {"title": "MIG Welder for Factory", "category": "Welder", "city": "Pune", "employment_type": "full_time", "min_salary": 20000, "max_salary": 45000},
        {"title": "Delivery Driver - Zomato/Swiggy", "category": "Driver", "city": "Ahmedabad", "employment_type": "part_time", "min_salary": 10000, "max_salary": 25000},
        {"title": "Warehouse Associate", "category": "Warehouse Worker", "city": "Chennai", "employment_type": "full_time", "min_salary": 12000, "max_salary": 25000},
        {"title": "Security Guard - Mall", "category": "Security Guard", "city": "Kolkata", "employment_type": "full_time", "min_salary": 10000, "max_salary": 20000},
        {"title": "Hotel Housekeeper", "category": "Housekeeping", "city": "Jaipur", "employment_type": "full_time", "min_salary": 8000, "max_salary": 18000},
        {"title": "Restaurant Cook", "category": "Cook", "city": "Lucknow", "employment_type": "full_time", "min_salary": 12000, "max_salary": 28000},
        {"title": "Gardener for Golf Course", "category": "Gardener", "city": "Surat", "employment_type": "full_time", "min_salary": 10000, "max_salary": 22000},
        {"title": "Patient Care Assistant", "category": "Nurse Assistant", "city": "Nagpur", "employment_type": "full_time", "min_salary": 14000, "max_salary": 30000},
        {"title": "AC Technician", "category": "Technician", "city": "Indore", "employment_type": "full_time", "min_salary": 15000, "max_salary": 35000},
        {"title": "Hotel Front Desk Staff", "category": "Hotel Staff", "city": "Bhopal", "employment_type": "full_time", "min_salary": 10000, "max_salary": 22000},
        {"title": "Factory Assembly Worker", "category": "Factory Worker", "city": "Surat", "employment_type": "full_time", "min_salary": 8000, "max_salary": 18000},
    ]

    created_count = 0
    for job_data in sample_jobs:
        category = next((c for c in categories if c.name == job_data["category"]), None)
        city = next((c for c in cities if c.name == job_data["city"]), None)
        if not category or not city:
            continue

        job, created = Job.objects.get_or_create(
            title=job_data["title"],
            employer=employer,
            defaults={
                "category": category,
                "city": city,
                "description": f"We are looking for an experienced {job_data['category']} to join our team. Immediate joining preferred.",
                "requirements": f"- Minimum 1 year of experience\n- Reliable and punctual\n- Good communication skills\n- Own tools preferred",
                "responsibilities": f"- Perform {job_data['category'].lower()} duties as assigned\n- Maintain quality standards\n- Follow safety protocols\n- Report to supervisor",
                "employment_type": job_data["employment_type"],
                "min_salary": job_data["min_salary"],
                "max_salary": job_data["max_salary"],
                "salary_period": "monthly",
                "currency": "INR",
                "is_active": True,
                "is_featured": random.choice([True, False]),
                "vacancies": random.randint(1, 5),
                "application_deadline": timezone.now().date() + timedelta(days=random.randint(15, 60)),
            },
        )
        if created:
            created_count += 1
    print(f"  [OK] {created_count} sample jobs created ({len(sample_jobs)} total)")


def main():
    print("\n=== Seeding Database ===\n")

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

    print("\n=== Seeding Complete! ===\n")


if __name__ == "__main__":
    main()
