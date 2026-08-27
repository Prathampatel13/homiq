import asyncio
from app.database.session import SessionLocal
from app.models.bookings import Booking, BookingStatus
from app.models.users import Customer, Technician
from app.models.auth import User
from app.schemas.reviews import ReviewCreate
from app.services.review import ReviewService
from fastapi import HTTPException
from app.crud.review import ReviewCRUD

def test():
    db = SessionLocal()
    try:
        booking = db.query(Booking).first()
        if not booking:
            print("No booking found")
            return
            
        booking.status = BookingStatus.COMPLETED
        # make sure it has a technician_id
        if not booking.technician_id:
            tech = db.query(Technician).first()
            booking.technician_id = tech.id
            
        from app.models.reviews import Review
        db.query(Review).filter(Review.booking_id == booking.id).delete()
        db.commit()
            
        print(f"Testing with booking {booking.id}, status {booking.status}, customer_id {booking.customer_id}, technician_id {booking.technician_id}")
        
        customer = db.query(Customer).filter(Customer.id == booking.customer_id).first()
        user = db.query(User).filter(User.id == customer.user_id).first()
        
        payload = ReviewCreate(
            booking_id=booking.id,
            technician_id=booking.technician_id or 1,
            rating=2,
            comment="kdfuhdshda"
        )
        
        try:
            res = ReviewService(db).create_review(user, payload)
            print("Success:", res)
        except HTTPException as e:
            print(f"HTTPException: {e.status_code} - {e.detail}")
        except Exception as e:
            print(f"Exception: {type(e)} - {e}")
            import traceback
            traceback.print_exc()
            
    finally:
        db.close()

if __name__ == "__main__":
    test()
