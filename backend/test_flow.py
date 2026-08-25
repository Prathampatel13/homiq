import requests

BASE = 'http://127.0.0.1:8003'
s = requests.Session()

def p(msg, res):
    print(f'{msg:30} | {res.status_code}')
    if res.status_code >= 400:
        print(res.text)

# 1. Login Customer
print('--- Customer ---')
r = s.post(f'{BASE}/auth/login', json={'email':'patelpratham3040@gmail.com', 'password':'password123'})
p('Login Customer', r)
c_token = r.json()['access_token']
c_headers = {'Authorization': f'Bearer {c_token}'}
customer_id = r.json()['user']['id']

# 2. Get services
r = s.get(f'{BASE}/services/?limit=10')
p('Get Services', r)
service_id = r.json()['items'][0]['id']

# 3. Create Booking
r = s.post(f'{BASE}/bookings/', json={
    'service_id': service_id, 'address_id': 1, 'booking_date': '2026-08-29', 'preferred_time': '09:00:00'
}, headers=c_headers)
p('Create Booking', r)
booking_id = r.json()['id']

# 4. Create Tech
print('--- Technician ---')
r = s.post(f'{BASE}/auth/register', json={
    'email': 'tech@homiq.com', 'password': 'password123', 'full_name': 'Tech', 'role': 'technician'
})
if r.status_code == 201:
    print('Tech Registered')
r = s.post(f'{BASE}/auth/login', json={'email':'tech@homiq.com', 'password':'password123'})
p('Login Tech', r)
t_token = r.json()['access_token']
t_headers = {'Authorization': f'Bearer {t_token}'}
tech_user_id = r.json()['user']['id']

# Get technician profile ID
r = s.get(f'{BASE}/technician/profile', headers=t_headers)
if r.status_code == 200:
    tech_id = r.json()['id']
else:
    tech_id = tech_user_id

# Admin
print('--- Admin ---')
r = s.post(f'{BASE}/auth/login', json={'email':'smoke_admin@homiq.com', 'password':'password123'})
p('Login Admin', r)
a_token = r.json()['access_token']
a_headers = {'Authorization': f'Bearer {a_token}'}

# Assign booking to tech (Admin action)
r = s.put(f'{BASE}/bookings/{booking_id}/assign', json={'technician_id': tech_id}, headers=a_headers)
p('Assign Booking', r)

# Tech Accept
r = s.post(f'{BASE}/bookings/{booking_id}/accept', headers=t_headers)
p('Accept Booking', r)

# Tech Start Trip
r = s.post(f'{BASE}/bookings/{booking_id}/start-trip', headers=t_headers)
p('Start Trip', r)

# Tech Arrived
r = s.post(f'{BASE}/bookings/{booking_id}/arrived', headers=t_headers)
p('Arrived', r)

# Tech Generate QR/OTP
r = s.post(f'{BASE}/bookings/{booking_id}/generate-otp', headers=t_headers)
p('Generate OTP', r)
if r.status_code == 200:
    otp = r.json()['otp_code']
    # Verify OTP (Customer does this)
    r = s.post(f'{BASE}/bookings/{booking_id}/verify-otp', json={'otp_code': otp}, headers=c_headers)
    p('Verify OTP (Start)', r)

# Complete
r = s.post(f'{BASE}/bookings/{booking_id}/complete', headers=t_headers)
p('Complete Booking', r)

