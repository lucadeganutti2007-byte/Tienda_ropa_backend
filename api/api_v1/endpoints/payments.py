from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import mercadopago

from db.database import get_db
from models.sales import Sale, SaleStatus, SaleItem as SaleItemModel
from models.catalog import ProductVariant, Product
from models.user import User
from core.config import settings
from api.deps import get_current_active_user

router = APIRouter()


def get_mp_sdk():
    return mercadopago.SDK(settings.MP_ACCESS_TOKEN)


@router.get("/public-key")
def get_public_key() -> Any:
    """Devuelve la public key de MercadoPago para el frontend."""
    return {"public_key": settings.MP_PUBLIC_KEY}


@router.post("/create-preference/{sale_id}")
def create_preference(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Crea una preferencia de pago en MercadoPago para una orden existente.
    El frontend usa el init_point devuelto para redirigir al usuario a pagar.
    """
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    if sale.status != SaleStatus.pending:
        raise HTTPException(status_code=400, detail="Sale is not pending payment")

    # Construir los items de la preferencia de MP
    items = []
    sale_items = db.query(SaleItemModel).filter(SaleItemModel.sale_id == sale_id).all()

    for item in sale_items:
        variant = db.query(ProductVariant).filter(ProductVariant.id == item.variant_id).first()
        product = db.query(Product).filter(Product.id == variant.product_id).first() if variant else None
        title = f"{product.name} - {variant.color} {variant.size}" if product and variant else f"Producto #{item.variant_id}"

        items.append({
            "id": str(item.variant_id),
            "title": title,
            "quantity": item.quantity,
            "unit_price": float(item.unit_price),
            "currency_id": "ARS",
        })

    sdk = get_mp_sdk()
    preference_data = {
        "items": items,
        "external_reference": str(sale_id),
        "back_urls": {
            "success": f"{settings.FRONTEND_URL}/payment/success",
            "failure": f"{settings.FRONTEND_URL}/payment/failure",
            "pending": f"{settings.FRONTEND_URL}/payment/pending",
        },
    }

    # Solo agregar auto_return y notification_url si es una URL pública (no localhost)
    if "localhost" not in settings.FRONTEND_URL:
        preference_data["auto_return"] = "approved"
        preference_data["notification_url"] = f"{settings.FRONTEND_URL}/api/v1/payments/webhook"

    try:
        result = sdk.preference().create(preference_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to MercadoPago: {str(e)}")

    if result["status"] not in (200, 201):
        raise HTTPException(
            status_code=500,
            detail=f"MercadoPago error {result['status']}: {result.get('response', {})}"
        )

    preference = result["response"]

    # Guardar el preference_id en la orden
    sale.mp_preference_id = preference["id"]
    db.commit()

    return {
        "preference_id": preference["id"],
        "init_point": preference["init_point"],           # URL de producción
        "sandbox_init_point": preference["sandbox_init_point"],  # URL de prueba
    }


@router.post("/webhook")
async def payment_webhook(request: Request, db: Session = Depends(get_db)) -> Any:
    """
    Webhook que llama MercadoPago cuando hay una notificación de pago.
    Actualiza el estado de la orden según el resultado del pago.
    """
    try:
        body = await request.json()
    except Exception:
        return {"status": "ok"}

    # MP envía diferentes tipos de notificaciones
    topic = body.get("type") or request.query_params.get("topic")
    resource_id = body.get("data", {}).get("id") or request.query_params.get("id")

    if topic not in ("payment", "merchant_order"):
        return {"status": "ok"}

    sdk = get_mp_sdk()

    if topic == "payment" and resource_id:
        payment_info = sdk.payment().get(resource_id)
        if payment_info["status"] != 200:
            return {"status": "ok"}

        payment = payment_info["response"]
        sale_id = payment.get("external_reference")
        mp_status = payment.get("status")  # approved, rejected, pending, etc.

        if not sale_id:
            return {"status": "ok"}

        sale = db.query(Sale).filter(Sale.id == int(sale_id)).first()
        if not sale:
            return {"status": "ok"}

        sale.mp_payment_id = str(resource_id)

        if mp_status == "approved":
            sale.status = SaleStatus.paid
        elif mp_status in ("rejected", "cancelled"):
            sale.status = SaleStatus.cancelled

        db.commit()

    return {"status": "ok"}
