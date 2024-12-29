from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.chat_router import router as chat_router
import uvicorn

def create_app():
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="RAG Chat API",
        description="A multi-model RAG chat application with real-time capabilities",
        version="1.0.0"
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, replace with specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(chat_router, prefix="/api", tags=["chat"])
    
    return app

def main():
    """Run the application"""
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()