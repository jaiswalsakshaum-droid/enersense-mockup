from .machines import router as machines_router
from .dashboard import router as dashboard_router
from .alerts import router as alerts_router
from .recommendations import router as recommendations_router
from .simulate import router as simulate_router
from .schemes import router as schemes_router
from .stream import router as stream_router

__all__ = [
    "machines_router",
    "dashboard_router",
    "alerts_router",
    "recommendations_router",
    "simulate_router",
    "schemes_router",
    "stream_router",
]
