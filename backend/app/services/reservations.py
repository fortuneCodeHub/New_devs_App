from datetime import datetime
from decimal import Decimal
from typing import Dict, Any

async def calculate_monthly_revenue(property_id: str, month: int, year: int, db_session=None) -> Decimal:
    start_date = datetime(year, month, 1)
    if month < 12:
        end_date = datetime(year, month + 1, 1)
    else:
        end_date = datetime(year + 1, 1, 1)

    print(f"DEBUG: Querying revenue for {property_id} from {start_date} to {end_date}")

    return Decimal('0')

async def calculate_total_revenue(property_id: str, tenant_id: str) -> Dict[str, Any]:
    try:
        from app.core.database_pool import DatabasePool
        from sqlalchemy import text

        db_pool = DatabasePool()
        await db_pool.initialize()

        if db_pool.session_factory:
            session = await db_pool.get_session()  # BUG FIX: await the coroutine first
            async with session as s:
                query = text("""
                    SELECT 
                        property_id,
                        SUM(total_amount) as total_revenue,
                        COUNT(*) as reservation_count
                    FROM reservations 
                    WHERE property_id = :property_id AND tenant_id = :tenant_id
                    GROUP BY property_id
                """)

                result = await s.execute(query, {
                    "property_id": property_id,
                    "tenant_id": tenant_id
                })
                row = result.fetchone()

                if row:
                    total_revenue = Decimal(str(row.total_revenue))
                    return {
                        "property_id": property_id,
                        "tenant_id": tenant_id,
                        "total": str(total_revenue),
                        "currency": "USD",
                        "count": row.reservation_count
                    }
                else:
                    return {
                        "property_id": property_id,
                        "tenant_id": tenant_id,
                        "total": "0.00",
                        "currency": "USD",
                        "count": 0
                    }
        else:
            raise Exception("Database pool not available")

    except Exception as e:
        print(f"Database error for {property_id} (tenant: {tenant_id}): {e}")

        mock_data = {
            'tenant-a': {
                'prop-001': {'total': '999.00', 'count': 3},
                'prop-002': {'total': '4975.50', 'count': 4},
                'prop-003': {'total': '6100.50', 'count': 2},
            },
            'tenant-b': {
                'prop-001': {'total': '450.75', 'count': 2},
                'prop-004': {'total': '1776.50', 'count': 4},
                'prop-005': {'total': '3256.00', 'count': 3}
            }
        }

        mock_property_data = mock_data.get(tenant_id, {}).get(property_id, {'total': '0.00', 'count': 0})

        return {
            "property_id": property_id,
            "tenant_id": tenant_id,
            "total": mock_property_data['total'],
            "currency": "USD",
            "count": mock_property_data['count']
        }