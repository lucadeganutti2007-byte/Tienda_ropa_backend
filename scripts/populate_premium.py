import os
import sys
import random
from datetime import datetime, timedelta

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from db.database import SessionLocal, engine
from models.catalog import Category, Product, ProductVariant
from models.inventory import InventoryMovement, MovementType
from models.sales import Sale, SaleItem, SaleStatus
from core.security import get_password_hash

def populate():
    db: Session = SessionLocal()
    try:
        print("Cleaning up catalog (keeping categories but replacing products)...")
        # For simplicity, we'll just add new products
        
        # 1. Ensure Categories
        categories_data = [
            {"name": "REMERAS", "description": "Remeras premium de algodón peinado"},
            {"name": "HOODIES", "description": "Hoodies oversize y canguro"},
            {"name": "PANTALONES", "description": "Cargo, joggers y jeans techwear"},
            {"name": "ABRIGOS", "description": "Camperas y bombers premium"}
        ]
        
        categories = {}
        for cat_data in categories_data:
            cat = db.query(Category).filter(Category.name == cat_data["name"]).first()
            if not cat:
                cat = Category(**cat_data)
                db.add(cat)
                db.commit()
                db.refresh(cat)
            categories[cat_data["name"]] = cat

        # 2. Products Data
        products_data = [
            {
                "name": "HOODIE OVERSIZE 'NIGHTWALKER'",
                "category": "HOODIES",
                "price": 45000.0,
                "desc": "Hoodie de frisa premium, calce extra oversize. Color negro profundo.",
                "image": "/products/hoodie-black.png"
            },
            {
                "name": "REMERA BOX FITTED 'CYBERPUNK'",
                "category": "REMERAS",
                "price": 22000.0,
                "desc": "Remera de algodón 20/1 con estampa minimalista reflectiva.",
                "image": "/products/tshirt-white.png"
            },
            {
                "name": "PANTALÓN CARGO 'TACTICAL-X'",
                "category": "PANTALONES",
                "price": 55000.0,
                "desc": "Pantalón cargo de gabardina reforzada con 6 bolsillos funcionales.",
                "image": "/products/cargo-black.png"
            },
            {
                "name": "BOMBER JACKET 'VALKYRIA'",
                "category": "ABRIGOS",
                "price": 95000.0,
                "desc": "Campera bomber impermeable con forrería de raso y detalles en puño.",
                "image": "/products/bomber-olive.png"
            }
        ]

        sizes = ["S", "M", "L", "XL"]
        colors = ["BLACK", "WHITE", "OLIVE"]

        for prod_data in products_data:
            # Check if product exists
            existing_prod = db.query(Product).filter(Product.name == prod_data["name"]).first()
            if existing_prod:
                print(f"Product {prod_data['name']} already exists, skipping...")
                continue
            
            prod = Product(
                name=prod_data["name"],
                category_id=categories[prod_data["category"]].id,
                description=prod_data["desc"],
                base_price=prod_data["price"],
                image_url=prod_data["image"],
                is_active=True
            )
            db.add(prod)
            db.commit()
            db.refresh(prod)
            
            # Create variants for each size
            for size in sizes:
                variant = ProductVariant(
                    product_id=prod.id,
                    sku=f"{prod.name[:3].upper()}-{size}-{random.randint(100,999)}",
                    color=prod_data.get("color", "PROMO"),
                    size=size,
                    min_stock=5
                )
                db.add(variant)
                db.commit()
                db.refresh(variant)
                
                # Add initial stock
                movement = InventoryMovement(
                    variant_id=variant.id,
                    quantity=random.randint(20, 50),
                    movement_type=MovementType.adjustment,
                    notes="Stock inicial - Carga masiva"
                )
                db.add(movement)
            
            db.commit()
            print(f"Added product: {prod.name}")

        # 3. Add some sample sales
        print("Generating sample sales for reports...")
        variants = db.query(ProductVariant).all()
        if variants:
            for i in range(20):
                sale_date = datetime.now() - timedelta(days=random.randint(0, 90))
                sale = Sale(
                    sale_type="online",
                    status="completed",
                    total_amount=0,
                    created_at=sale_date,
                    shipping_address="Calle Falsa 123, Buenos Aires"
                )
                db.add(sale)
                db.commit()
                db.refresh(sale)
                
                total = 0
                for _ in range(random.randint(1, 3)):
                    v = random.choice(variants)
                    qty = random.randint(1, 2)
                    price = v.price
                    item = SaleItem(
                        sale_id=sale.id,
                        variant_id=v.id,
                        quantity=qty,
                        unit_price=price
                    )
                    db.add(item)
                    total += price * qty
                    
                    db.add(InventoryMovement(
                        variant_id=v.id,
                        quantity=-qty,
                        movement_type=MovementType.out_sale_online,
                        notes=f"Venta #{sale.id}"
                    ))
                
                sale.total_amount = total
                db.add(sale)
                db.commit()

        print("Successfully populated database with premium products and sales history.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate()
