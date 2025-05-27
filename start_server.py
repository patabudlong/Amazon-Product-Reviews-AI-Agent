import multiprocessing
import sys
import os

def main():
    # Add the current directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Import and run the app
    import uvicorn
    from app.main import app
    
    # Run without reload to avoid multiprocessing issues
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main() 