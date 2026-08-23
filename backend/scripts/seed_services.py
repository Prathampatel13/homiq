import os
import sys
from pathlib import Path

# Add the backend directory to python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.database.session import SessionLocal
from app.models.services import Category, Service

MOCK_CATEGORIES = [
    {"id": 1, "name": "Plumbing", "description": "Expert plumbing solutions"},
    {"id": 2, "name": "Electrical", "description": "Certified electrical repairs"},
    {"id": 3, "name": "AC & Cooling", "description": "Cooling system maintenance"},
    {"id": 4, "name": "Appliances", "description": "Home appliance repair"},
    {"id": 5, "name": "Carpentry", "description": "Woodwork and carpentry"},
    {"id": 6, "name": "Cleaning", "description": "Deep home sanitization"},
    {"id": 7, "name": "Painting", "description": "Interior & exterior painting"},
    {"id": 8, "name": "Bathroom", "description": "Bathroom repair & cleaning"},
    {"id": 9, "name": "Home Maintenance", "description": "General house upkeep"},
    {"id": 10, "name": "Security & Smart Home", "description": "Smart devices & security"},
    {"id": 11, "name": "Outdoor & Garden", "description": "Lawn and outdoor care"},
    {"id": 12, "name": "Windows & Doors", "description": "Window and door fixes"},
]

MOCK_SERVICES = [
    # Plumbing
    {"id": 101, "category_id": 1, "name": "Tap Repair", "description": "Fixing leaky taps and faucets.", "base_price": 199, "duration_minutes": 30},
    {"id": 102, "category_id": 1, "name": "Pipe Leakage", "description": "Sealing and repairing pipe leaks.", "base_price": 349, "duration_minutes": 45},
    {"id": 103, "category_id": 1, "name": "Drain Cleaning", "description": "Unclogging blocked drains.", "base_price": 499, "duration_minutes": 60},
    {"id": 104, "category_id": 1, "name": "Sink Repair", "description": "Kitchen and bathroom sink repairs.", "base_price": 299, "duration_minutes": 45},
    {"id": 105, "category_id": 1, "name": "Toilet Repair", "description": "Fixing flush and toilet issues.", "base_price": 399, "duration_minutes": 45},
    {"id": 106, "category_id": 1, "name": "Water Tank Repair", "description": "Water tank cleaning and repair.", "base_price": 899, "duration_minutes": 90},
    {"id": 107, "category_id": 1, "name": "Bathroom Plumbing", "description": "Complete bathroom plumbing check.", "base_price": 599, "duration_minutes": 60},

    # Electrical
    {"id": 201, "category_id": 2, "name": "Switch & Socket Repair", "description": "Fixing faulty switches and sockets.", "base_price": 149, "duration_minutes": 30},
    {"id": 202, "category_id": 2, "name": "Fan Installation", "description": "Ceiling and exhaust fan setup.", "base_price": 249, "duration_minutes": 45},
    {"id": 203, "category_id": 2, "name": "Light Installation", "description": "Hanging lights, LEDs, and tubes.", "base_price": 199, "duration_minutes": 30},
    {"id": 204, "category_id": 2, "name": "Wiring Repair", "description": "Safe electrical wiring repairs.", "base_price": 499, "duration_minutes": 60},
    {"id": 205, "category_id": 2, "name": "MCB Repair", "description": "Fixing tripping MCB and fuse issues.", "base_price": 349, "duration_minutes": 45},
    {"id": 206, "category_id": 2, "name": "Short-Circuit Repair", "description": "Emergency short-circuit resolution.", "base_price": 599, "duration_minutes": 60},
    {"id": 207, "category_id": 2, "name": "Inverter Installation", "description": "Battery and inverter setup.", "base_price": 699, "duration_minutes": 60},

    # AC & Cooling
    {"id": 301, "category_id": 3, "name": "AC Service", "description": "Regular AC servicing and cleaning.", "base_price": 599, "duration_minutes": 60},
    {"id": 302, "category_id": 3, "name": "AC Repair", "description": "Fixing cooling issues and parts.", "base_price": 899, "duration_minutes": 90},
    {"id": 303, "category_id": 3, "name": "AC Installation", "description": "Professional AC mounting.", "base_price": 1499, "duration_minutes": 120},
    {"id": 304, "category_id": 3, "name": "AC Gas Refill", "description": "Coolant refill for optimum cooling.", "base_price": 2499, "duration_minutes": 60},
    {"id": 305, "category_id": 3, "name": "AC Cleaning", "description": "Deep coil and filter cleaning.", "base_price": 499, "duration_minutes": 45},
    {"id": 306, "category_id": 3, "name": "Cooler Repair", "description": "Desert and room cooler fixes.", "base_price": 349, "duration_minutes": 45},

    # Appliances
    {"id": 401, "category_id": 4, "name": "Refrigerator Repair", "description": "Fixing cooling and compressor issues.", "base_price": 599, "duration_minutes": 60},
    {"id": 402, "category_id": 4, "name": "Washing Machine Repair", "description": "Resolving drum and motor problems.", "base_price": 499, "duration_minutes": 60},
    {"id": 403, "category_id": 4, "name": "Microwave Repair", "description": "Heating and circuit board fixes.", "base_price": 399, "duration_minutes": 45},
    {"id": 404, "category_id": 4, "name": "Geyser Repair", "description": "Water heater coil and thermostat.", "base_price": 449, "duration_minutes": 60},
    {"id": 405, "category_id": 4, "name": "Water Purifier Service", "description": "Filter change and RO repair.", "base_price": 549, "duration_minutes": 45},

    # Carpentry
    {"id": 501, "category_id": 5, "name": "Furniture Repair", "description": "Fixing broken chairs, tables, etc.", "base_price": 349, "duration_minutes": 60},
    {"id": 502, "category_id": 5, "name": "Door Repair", "description": "Hinge alignment and wood repair.", "base_price": 299, "duration_minutes": 45},
    {"id": 503, "category_id": 5, "name": "Lock Installation", "description": "Fitting standard and deadbolt locks.", "base_price": 199, "duration_minutes": 30},
    {"id": 504, "category_id": 5, "name": "Cabinet Repair", "description": "Fixing kitchen and wardrobe cabinets.", "base_price": 449, "duration_minutes": 60},
    {"id": 505, "category_id": 5, "name": "Shelf Installation", "description": "Mounting wooden shelves securely.", "base_price": 249, "duration_minutes": 45},
    {"id": 506, "category_id": 5, "name": "Bed Repair", "description": "Frame and joint reinforcement.", "base_price": 499, "duration_minutes": 90},

    # Cleaning
    {"id": 601, "category_id": 6, "name": "Full Home Cleaning", "description": "Complete deep cleaning of the house.", "base_price": 2999, "duration_minutes": 240},
    {"id": 602, "category_id": 6, "name": "Kitchen Cleaning", "description": "Degreasing and sanitizing kitchen.", "base_price": 999, "duration_minutes": 90},
    {"id": 603, "category_id": 6, "name": "Bathroom Cleaning", "description": "Deep stain removal and descaling.", "base_price": 699, "duration_minutes": 60},
    {"id": 604, "category_id": 6, "name": "Sofa Cleaning", "description": "Shampooing and vacuuming sofa.", "base_price": 799, "duration_minutes": 60},
    {"id": 605, "category_id": 6, "name": "Carpet Cleaning", "description": "Dust extraction and wash.", "base_price": 599, "duration_minutes": 45},
    {"id": 606, "category_id": 6, "name": "Floor Cleaning", "description": "Scrubbing and polishing floors.", "base_price": 899, "duration_minutes": 90},

    # Painting
    {"id": 701, "category_id": 7, "name": "Room Painting", "description": "Painting for a single room.", "base_price": 3499, "duration_minutes": 360},
    {"id": 702, "category_id": 7, "name": "Full Home Painting", "description": "Complete house interior painting.", "base_price": 14999, "duration_minutes": 1440},
    {"id": 703, "category_id": 7, "name": "Wall Touch-up", "description": "Fixing patches and minor spots.", "base_price": 899, "duration_minutes": 90},
    {"id": 704, "category_id": 7, "name": "Exterior Painting", "description": "Weatherproof painting for outdoors.", "base_price": 19999, "duration_minutes": 2880},
    {"id": 705, "category_id": 7, "name": "Waterproof Painting", "description": "Sealing walls against moisture.", "base_price": 4599, "duration_minutes": 480},

    # Bathroom
    {"id": 801, "category_id": 8, "name": "Bathroom Deep Cleaning", "description": "Scrubbing tiles and fixtures.", "base_price": 699, "duration_minutes": 60},
    {"id": 802, "category_id": 8, "name": "Shower Repair", "description": "Fixing showerheads and pressure.", "base_price": 299, "duration_minutes": 45},
    {"id": 803, "category_id": 8, "name": "Toilet Repair", "description": "Leak and flush mechanism repair.", "base_price": 399, "duration_minutes": 45},
    {"id": 804, "category_id": 8, "name": "Basin Repair", "description": "Washbasin blockages and leaks.", "base_price": 249, "duration_minutes": 30},
    {"id": 805, "category_id": 8, "name": "Exhaust Fan Installation", "description": "Installing ventilation fans.", "base_price": 199, "duration_minutes": 30},

    # Home Maintenance
    {"id": 901, "category_id": 9, "name": "General Inspection", "description": "Overall home health checkup.", "base_price": 499, "duration_minutes": 60},
    {"id": 902, "category_id": 9, "name": "Minor Repairs", "description": "Quick fixes around the house.", "base_price": 299, "duration_minutes": 45},
    {"id": 903, "category_id": 9, "name": "Wall Repair", "description": "Fixing cracks and holes in walls.", "base_price": 399, "duration_minutes": 60},
    {"id": 904, "category_id": 9, "name": "Grouting", "description": "Tile gap sealing and grouting.", "base_price": 599, "duration_minutes": 90},
    {"id": 905, "category_id": 9, "name": "Waterproofing", "description": "Preventing water seepage.", "base_price": 1299, "duration_minutes": 120},
    {"id": 906, "category_id": 9, "name": "Home Inspection", "description": "Detailed property assessment.", "base_price": 999, "duration_minutes": 90},

    # Security & Smart Home
    {"id": 1001, "category_id": 10, "name": "CCTV Installation", "description": "Setting up security cameras.", "base_price": 899, "duration_minutes": 90},
    {"id": 1002, "category_id": 10, "name": "Smart Lock Installation", "description": "Digital door lock setup.", "base_price": 799, "duration_minutes": 60},
    {"id": 1003, "category_id": 10, "name": "Doorbell Installation", "description": "Video and standard doorbells.", "base_price": 299, "duration_minutes": 45},
    {"id": 1004, "category_id": 10, "name": "Wi-Fi Camera Setup", "description": "Configuring wireless security cams.", "base_price": 499, "duration_minutes": 60},

    # Outdoor & Garden
    {"id": 1101, "category_id": 11, "name": "Garden Maintenance", "description": "Trimming and general care.", "base_price": 599, "duration_minutes": 90},
    {"id": 1102, "category_id": 11, "name": "Lawn Cleaning", "description": "Removing debris and leaves.", "base_price": 399, "duration_minutes": 60},
    {"id": 1103, "category_id": 11, "name": "Plant Maintenance", "description": "Pruning, repotting, and soil care.", "base_price": 499, "duration_minutes": 60},
    {"id": 1104, "category_id": 11, "name": "Balcony Cleaning", "description": "Washing and scrubbing balconies.", "base_price": 349, "duration_minutes": 45},

    # Windows & Doors
    {"id": 1201, "category_id": 12, "name": "Door Alignment", "description": "Fixing sagging or sticking doors.", "base_price": 299, "duration_minutes": 45},
    {"id": 1202, "category_id": 12, "name": "Door Handle Repair", "description": "Replacing or fixing handles.", "base_price": 199, "duration_minutes": 30},
    {"id": 1203, "category_id": 12, "name": "Window Repair", "description": "Fixing sliding and hinge windows.", "base_price": 349, "duration_minutes": 60},
    {"id": 1204, "category_id": 12, "name": "Glass Replacement", "description": "Replacing broken window panes.", "base_price": 599, "duration_minutes": 60},
    {"id": 1205, "category_id": 12, "name": "Mosquito Net Installation", "description": "Fixing insect screens on windows.", "base_price": 499, "duration_minutes": 60},
]

def seed_db():
    db = SessionLocal()
    try:
        print('Seeding categories...')
        for cat_data in MOCK_CATEGORIES:
            existing = db.query(Category).filter_by(id=cat_data['id']).first()
            if not existing:
                cat = Category(**cat_data)
                db.add(cat)
            else:
                existing.name = cat_data['name']
                existing.description = cat_data['description']
                
        db.commit()
        
        print('Seeding services...')
        for srv_data in MOCK_SERVICES:
            existing = db.query(Service).filter_by(id=srv_data['id']).first()
            if not existing:
                srv = Service(**srv_data)
                db.add(srv)
            else:
                for k, v in srv_data.items():
                    setattr(existing, k, v)
                    
        db.commit()
        print('Database seeding complete!')
        
    except Exception as e:
        db.rollback()
        print(f'Error seeding database: {e}')
    finally:
        db.close()

if __name__ == '__main__':
    seed_db()
