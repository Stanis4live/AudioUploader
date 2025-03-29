import uvicorn
from app.core.config import main_app
from app.core.logging_config import setup_logging

setup_logging()

async def start_fastapi():
    config = uvicorn.Config(
        main_app,
        log_level="info",
    )
    server = uvicorn.Server(config)
    await server.serve()
