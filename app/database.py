import json
import os
from datetime import datetime, timezone
from typing import List, Optional

from app.models import PropertyListing


class ListingRepository:
    """PostgreSQL repository with an explicit in-memory fallback for local demos."""

    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL")
        self._engine = None
        self._table_ready = False

    @property
    def enabled(self) -> bool:
        return bool(self.database_url)

    def _connect(self):
        if not self.enabled:
            return None
        if self._engine is None:
            from sqlalchemy import create_engine
            self._engine = create_engine(self.database_url, pool_pre_ping=True)
        return self._engine.connect()

    def ensure_schema(self) -> None:
        if not self.enabled or self._table_ready:
            return
        from sqlalchemy import text
        with self._connect() as connection:
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS rental_listings (
                    id VARCHAR(255) PRIMARY KEY,
                    rent_monthly INTEGER NOT NULL,
                    area VARCHAR(255) NOT NULL,
                    listing JSONB NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    synced_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """))
            connection.commit()
        self._table_ready = True

    def replace_active(self, listings: List[PropertyListing]) -> None:
        self.ensure_schema()
        if not self.enabled:
            return
        from sqlalchemy import bindparam, text
        with self._connect() as connection:
            seen_ids = []
            for listing in listings:
                seen_ids.append(listing.id)
                connection.execute(text("""
                    INSERT INTO rental_listings (id, rent_monthly, area, listing, is_active, synced_at)
                    VALUES (:id, :rent, :area, CAST(:listing AS JSONB), TRUE, :synced_at)
                    ON CONFLICT (id) DO UPDATE SET
                        rent_monthly = EXCLUDED.rent_monthly,
                        area = EXCLUDED.area,
                        listing = EXCLUDED.listing,
                        is_active = TRUE,
                        synced_at = EXCLUDED.synced_at
                """), {
                    "id": listing.id,
                    "rent": listing.rent_monthly,
                    "area": listing.area,
                    "listing": json.dumps(listing.model_dump()),
                    "synced_at": datetime.now(timezone.utc),
                })
            if seen_ids:
                inactive_query = text("UPDATE rental_listings SET is_active = FALSE WHERE id NOT IN :ids").bindparams(bindparam("ids", expanding=True))
                connection.execute(inactive_query, {"ids": seen_ids})
            connection.commit()

    def get_all(self) -> Optional[List[PropertyListing]]:
        if not self.enabled:
            return None
        self.ensure_schema()
        from sqlalchemy import text
        with self._connect() as connection:
            rows = connection.execute(text("SELECT listing FROM rental_listings WHERE is_active = TRUE ORDER BY rent_monthly ASC"))
            listings = [PropertyListing.model_validate(row[0]) for row in rows]
            return listings or None


repository = ListingRepository()
