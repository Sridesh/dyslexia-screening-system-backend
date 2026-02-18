from fastapi import APIRouter
from app.api.v1 import child, item, test, test_item_log, test_module_sum, test_features, test_xai

api_router = APIRouter()

api_router.include_router(child.router, prefix="/children", tags=["children"])
api_router.include_router(item.router, prefix="/items", tags=["items"])
api_router.include_router(test.router, prefix="/tests", tags=["tests"])
api_router.include_router(test_item_log.router, prefix="/logs", tags=["test-logs"])
api_router.include_router(test_module_sum.router, prefix="/module-summaries", tags=["test-summaries"])
api_router.include_router(test_features.router, prefix="/features", tags=["test-features"])
api_router.include_router(test_xai.router, prefix="/xai", tags=["test-xai"])

# Lazy import to avoid circular dependencies if any, though standard import is fine
from app.api.v1 import adaptive
api_router.include_router(adaptive.router, prefix="/adaptive", tags=["adaptive"])
