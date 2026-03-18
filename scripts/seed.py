import asyncio
import os
import sys

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from db.database import SessionLocal, engine, Base
from models.user import User, UserRole
from core.security import get_password_hash

def seed_db():
    print("Creating tables if they don't exist...")
    # NOTE: In production you should use Alembic. 
    # For this demo, we can ensure tables exist if Alembic wasn't run
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    try:
        print("Checking for existing owner...")
        owner = db.query(User).filter(User.email == "owner@demo.com").first()
        if not owner:
            print("Creating demo owner account: owner@demo.com / password123")
            owner = User(
                email="owner@demo.com",
                hashed_password=get_password_hash("password123"),
                full_name="Demo Owner",
                role=UserRole.owner,
                is_active=True
            )
            db.add(owner)
            db.commit()
            print("Owner created successfully.")
        else:
            print("Owner already exists.")
            
        # Add categories
        from models.catalog import Category, Product, ProductVariant
        print("Checking categories...")
        cat = db.query(Category).filter(Category.name == "Remeras").first()
        if not cat:
            cat = Category(name="Remeras", description="Remeras y musculosas")
            db.add(cat)
            db.commit()
            db.refresh(cat)
            
            prod = Product(
                category_id=cat.id,
                name="Remera Oversize Basic",
                description="Remera de algodón peinado 20/1, calce oversize.",
                base_price=15000.0,
                is_active=True
            )
            db.add(prod)
            db.commit()
            db.refresh(prod)
            
            var1 = ProductVariant(
                product_id=prod.id,
                sku="REM-OVS-BLK-M",
                color="Black",
                size="M",
                price_override=None,
                min_stock=5,
                is_active=True
            )
            var2 = ProductVariant(
                product_id=prod.id,
                sku="REM-OVS-BLK-L",
                color="Black",
                size="L",
                price_override=None,
                min_stock=5,
                is_active=True
            )
            db.add_all([var1, var2])
            db.commit()
            
            # Initial inventory
            from models.inventory import InventoryMovement, MovementType
            db.add(InventoryMovement(variant_id=var1.id, quantity=20, movement_type=MovementType.adjustment, notes="Initial stock"))
            db.add(InventoryMovement(variant_id=var2.id, quantity=15, movement_type=MovementType.adjustment, notes="Initial stock"))
            db.commit()
            print("Demo catalog and inventory created.")
            
    except Exception as e:
        print(f"Error seeding DB: {e}")
        db.rollback()
    finally:
        db.close()
        print("Done.")

if __name__ == "__main__":
    seed_db()
