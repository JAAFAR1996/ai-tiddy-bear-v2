import sys
import os

# Add Python 3.11 packages to path for compatibility
sys.path.append('C:\\Users\\jaafa\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages')

# Set working directory
os.chdir('c:\\Users\\jaafa\\Desktop\\5555\\ai-teddy\\ai-teddy-backup')
sys.path.append('c:\\Users\\jaafa\\Desktop\\5555\\ai-teddy\\ai-teddy-backup\\src')

# Now try to run main
try:
    from src import main
    print("✅ Main module imported successfully")
    print("Attempting to start application...")

    if hasattr(main, 'app'):
        print("✅ FastAPI app found")
    else:
        print("❌ No FastAPI app found in main module")

except Exception as e:
    print(f"❌ Error importing main: {e}")
    import traceback
    traceback.print_exc()
