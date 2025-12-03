"""
Entry point for running the FastAPI application.
"""

if __name__ == "__main__":
    import uvicorn
    from app.main import app
    
    # Run the application
    uvicorn.run(
        app,
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )