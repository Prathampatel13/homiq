import json

static_services = [
    { "id": 101, "category_id": 1, "name": 'Plumbing', "description": 'Tap Repair, Pipe Leakage, Drain Cleaning, Sink Repair, Toilet Repair, Water Tank Repair, Bathroom Plumbing', "price": 299, "duration_minutes": 30 },
    { "id": 102, "category_id": 2, "name": 'Electrical', "description": 'Switch & Socket Repair, Fan Installation, Light Installation, Wiring Repair, MCB Repair, Short-Circuit Repair, Inverter Installation', "price": 199, "duration_minutes": 30 },
    { "id": 103, "category_id": 3, "name": 'AC & Cooling', "description": 'AC Service, AC Repair, AC Installation, AC Gas Refill, AC Cleaning, Cooler Repair', "price": 499, "duration_minutes": 60 },
    { "id": 104, "category_id": 4, "name": 'Appliances', "description": 'Refrigerator Repair, Washing Machine Repair, Microwave Repair, Geyser Repair, Water Purifier Service', "price": 349, "duration_minutes": 45 },
    { "id": 105, "category_id": 5, "name": 'Carpentry', "description": 'Furniture Repair, Door Repair, Lock Installation, Cabinet Repair, Shelf Installation, Bed Repair', "price": 249, "duration_minutes": 60 },
    { "id": 106, "category_id": 6, "name": 'Cleaning', "description": 'Full Home Cleaning, Kitchen Cleaning, Bathroom Cleaning, Sofa Cleaning, Carpet Cleaning, Floor Cleaning', "price": 999, "duration_minutes": 120 },
    { "id": 107, "category_id": 7, "name": 'Painting', "description": 'Room Painting, Full Home Painting, Wall Touch-up, Exterior Painting, Waterproof Painting', "price": 1499, "duration_minutes": 240 },
    { "id": 108, "category_id": 8, "name": 'Bathroom', "description": 'Bathroom Deep Cleaning, Shower Repair, Toilet Repair, Basin Repair, Exhaust Fan Installation', "price": 399, "duration_minutes": 60 },
    { "id": 109, "category_id": 9, "name": 'Home Maintenance', "description": 'General Inspection, Minor Repairs, Wall Repair, Grouting, Waterproofing, Home Inspection', "price": 499, "duration_minutes": 90 },
    { "id": 110, "category_id": 10, "name": 'Security & Smart Home', "description": 'CCTV Installation, Smart Lock Installation, Doorbell Installation, Wi-Fi Camera Setup', "price": 599, "duration_minutes": 90 },
    { "id": 111, "category_id": 11, "name": 'Outdoor & Garden', "description": 'Garden Maintenance, Lawn Cleaning, Plant Maintenance, Balcony Cleaning', "price": 349, "duration_minutes": 60 },
    { "id": 112, "category_id": 12, "name": 'Windows & Doors', "description": 'Door Alignment, Door Handle Repair, Window Repair, Glass Replacement, Mosquito Net Installation', "price": 299, "duration_minutes": 45 },
]

new_services = []
current_id = 1000

for s in static_services:
    sub_services = [x.strip() for x in s["description"].split(",")]
    for i, sub in enumerate(sub_services):
        price_modifier = i * 50
        time_modifier = i * 15
        new_services.append(
            f"{{ id: {current_id}, category_id: {s['category_id']}, name: '{sub}', description: 'Professional {sub.lower()} service by expert technicians.', price: {s['price'] + price_modifier}, duration_minutes: {s['duration_minutes'] + time_modifier} }}"
        )
        current_id += 1

output = "const staticServices = [\n" + ",\n".join(["          " + ns for ns in new_services]) + "\n        ];"
with open("expanded.ts", "w") as f:
    f.write(output)
