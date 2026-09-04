import sqlite3

conn = sqlite3.connect('homiq.db')
c = conn.cursor()

c.execute("UPDATE bookings SET status = 'CLOSED' WHERE id IN (1, 8)")
conn.commit()

c.execute("SELECT id, status, customer_id, technician_id FROM bookings WHERE status IN ('COMPLETED', 'completed', 'CLOSED', 'closed')")
print('Bookings:', c.fetchall())
