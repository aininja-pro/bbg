"""Seed script to populate database with current supplier override rules."""
import asyncio
from datetime import datetime

from app.database import AsyncSessionLocal, init_db
from app.models.rule import Rule


async def seed_supplier_rules():
    """Populate database with current supplier mapping rules."""
    print("🌱 Seeding supplier override rules...")

    await init_db()

    rules = [
        Rule(
            name="Day & Night is Carrier",
            rule_type="supplier_override",
            priority=1,
            enabled=True,
            config={
                "condition": {"supplier_name_equals": "Day & Night Heating & Cooling"},
                "set_supplier": "Carrier"
            }
        ),
        Rule(
            name="Product 5534 → Air Vent",
            rule_type="supplier_override",
            priority=2,
            enabled=True,
            config={
                "condition": {"product_id_contains": "5534"},
                "set_supplier": "Air Vent"
            }
        ),
        Rule(
            name="Product 5531 → CertainTeed",
            rule_type="supplier_override",
            priority=3,
            enabled=True,
            config={
                "condition": {"product_id_contains": "5531"},
                "set_supplier": "CertainTeed"
            }
        ),
        Rule(
            name="Product 5406 → Air Vent",
            rule_type="supplier_override",
            priority=4,
            enabled=True,
            config={
                "condition": {"product_id_contains": "5406"},
                "set_supplier": "Air Vent"
            }
        ),
        Rule(
            name="Product 5407 → CertainTeed",
            rule_type="supplier_override",
            priority=5,
            enabled=True,
            config={
                "condition": {"product_id_contains": "5407"},
                "set_supplier": "CertainTeed"
            }
        ),
        Rule(
            name="Product 5255 → Heatilator",
            rule_type="supplier_override",
            priority=6,
            enabled=True,
            config={
                "condition": {"product_id_contains": "5255"},
                "set_supplier": "Heatilator (Hearth & Home)"
            }
        ),
        Rule(
            name="Product 5270 → Leading Edge",
            rule_type="supplier_override",
            priority=7,
            enabled=True,
            config={
                "condition": {"product_id_contains": "5270"},
                "set_supplier": "Leading Edge"
            }
        ),
        Rule(
            name="Product 5350 → Leading Edge",
            rule_type="supplier_override",
            priority=8,
            enabled=True,
            config={
                "condition": {"product_id_contains": "5350"},
                "set_supplier": "Leading Edge"
            }
        ),
    ]

    async with AsyncSessionLocal() as db:
        try:
            print(f"💾 Inserting {len(rules)} supplier override rules...")
            db.add_all(rules)
            await db.commit()

            print(f"\n✅ Successfully seeded {len(rules)} rules")
            for rule in rules:
                print(f"   - {rule.name} (Priority: {rule.priority})")

            print("\n🎉 Rules seeding complete!")

        except Exception as e:
            await db.rollback()
            print(f"❌ Error seeding rules: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed_supplier_rules())
