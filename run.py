"""
Entry point for running the FastAPI application.
"""

if __name__ == "__main__":
    import uvicorn
    
    # Run the application using import string to enable reload
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )