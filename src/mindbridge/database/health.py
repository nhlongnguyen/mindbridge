"""Database health checking functionality."""

from datetime import datetime
from typing import Any

from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError

from .connection import DatabaseEngine


class DatabaseHealthChecker:
    """Database health checker for monitoring connection and vector operations."""

    def __init__(self, database_engine: DatabaseEngine) -> None:
        """Initialize health checker with database engine.

        Args:
            database_engine: Database engine instance
        """
        self._database_engine = database_engine

    async def check_basic_connectivity(self) -> dict[str, Any]:
        """Check basic database connectivity.

        Returns:
            Dict containing health check results
        """
        result: dict[str, Any] = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {}
        }

        try:
            async with self._database_engine.get_session() as session:
                # Simple connectivity test
                await session.execute(select(1))
                result["checks"]["connectivity"] = {
                    "status": "healthy",
                    "message": "Database connection successful"
                }
        except SQLAlchemyError as e:
            result["status"] = "unhealthy"
            result["checks"]["connectivity"] = {
                "status": "unhealthy",
                "message": f"Database connection failed: {str(e)}"
            }
        except Exception as e:
            result["status"] = "unhealthy"
            result["checks"]["connectivity"] = {
                "status": "unhealthy",
                "message": f"Unexpected error: {str(e)}"
            }

        return result

    async def check_pgvector_extension(self) -> dict[str, Any]:
        """Check if pgvector extension is available and working.

        Returns:
            Dict containing pgvector extension check results
        """
        result: dict[str, Any] = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {}
        }

        try:
            async with self._database_engine.get_session() as session:
                # Check if pgvector extension exists
                extension_query = text("""
                    SELECT extname, extversion
                    FROM pg_extension
                    WHERE extname = 'vector'
                """)
                extension_result = await session.execute(extension_query)
                extension_row = extension_result.fetchone()

                if extension_row:
                    result["checks"]["pgvector_extension"] = {
                        "status": "healthy",
                        "message": f"pgvector extension version {extension_row.extversion} is installed"
                    }

                    # Test vector operations
                    vector_test_query = text("""
                        SELECT '[1,2,3]'::vector <-> '[4,5,6]'::vector as distance
                    """)
                    vector_result = await session.execute(vector_test_query)
                    distance = vector_result.scalar()

                    result["checks"]["vector_operations"] = {
                        "status": "healthy",
                        "message": f"Vector distance calculation successful: {distance}"
                    }
                else:
                    result["status"] = "unhealthy"
                    result["checks"]["pgvector_extension"] = {
                        "status": "unhealthy",
                        "message": "pgvector extension is not installed"
                    }

        except SQLAlchemyError as e:
            result["status"] = "unhealthy"
            result["checks"]["pgvector_extension"] = {
                "status": "unhealthy",
                "message": f"pgvector check failed: {str(e)}"
            }
        except Exception as e:
            result["status"] = "unhealthy"
            result["checks"]["pgvector_extension"] = {
                "status": "unhealthy",
                "message": f"Unexpected error: {str(e)}"
            }

        return result

    async def check_pool_status(self) -> dict[str, Any]:
        """Check connection pool status.

        Returns:
            Dict containing pool status information
        """
        result: dict[str, Any] = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {}
        }

        try:
            pool = self._database_engine.engine.pool

            # Get pool statistics using getattr for safer access
            pool_size = getattr(pool, 'size', lambda: 0)()
            checked_in = getattr(pool, 'checkedin', lambda: 0)()
            checked_out = getattr(pool, 'checkedout', lambda: 0)()
            overflow = getattr(pool, 'overflow', lambda: 0)()

            result["checks"]["connection_pool"] = {
                "status": "healthy",
                "pool_size": pool_size,
                "checked_in": checked_in,
                "checked_out": checked_out,
                "overflow": overflow,
                "total_connections": pool_size + overflow
            }

        except Exception as e:
            result["status"] = "unhealthy"
            result["checks"]["connection_pool"] = {
                "status": "unhealthy",
                "message": f"Pool status check failed: {str(e)}"
            }

        return result

    async def comprehensive_health_check(self) -> dict[str, Any]:
        """Run comprehensive health check including all components.

        Returns:
            Dict containing comprehensive health check results
        """
        # Run all health checks
        connectivity_check = await self.check_basic_connectivity()
        pgvector_check = await self.check_pgvector_extension()
        pool_check = await self.check_pool_status()

        # Combine results
        overall_status = "healthy"
        if (connectivity_check["status"] != "healthy" or
            pgvector_check["status"] != "healthy" or
            pool_check["status"] != "healthy"):
            overall_status = "unhealthy"

        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                **connectivity_check["checks"],
                **pgvector_check["checks"],
                **pool_check["checks"]
            }
        }

