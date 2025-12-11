"""
Build script to create executables for Telegram Channel API and Frontend
Run this script to build both executables at once.
"""
import subprocess
import sys
import os

def build_executable(script_name, exe_name, console=True):
    """Build an executable using PyInstaller"""
    print(f"\n{'='*60}")
    print(f"Building {exe_name}...")
    print(f"{'='*60}\n")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--name", exe_name,
        "--onefile",  # Single executable file
        "--clean",    # Clean PyInstaller cache
    ]
    
    if console:
        cmd.append("--console")  # Show console window
    else:
        cmd.append("--noconsole")  # Hide console window (GUI mode)
    
    # Add hidden imports that might be needed
    hidden_imports = [
        "uvicorn.lifespan.on",
        "uvicorn.lifespan.off",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.protocols.websockets.websockets_impl",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.http.h11_impl",
        "uvicorn.protocols.http.httptools_impl",
        "uvicorn.loops.auto",
        "uvicorn.loops.asyncio",
        "uvicorn.logging",
        "fastapi",
        "pydantic",
        "telethon",
        "telethon.tl",
        "telethon.tl.types",
        "telethon.errors",
        "deep_translator",
        "langdetect",
        "dotenv",
        "argostranslate",
        "argostranslate.package",
        "argostranslate.translate",
    ]
    
    for imp in hidden_imports:
        cmd.extend(["--hidden-import", imp])
    
    # Add the script
    cmd.append(script_name)
    
    # Run PyInstaller
    try:
        result = subprocess.run(cmd, check=True)
        print(f"\n✓ Successfully built {exe_name}.exe")
        print(f"  Location: dist/{exe_name}.exe\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error building {exe_name}: {e}\n")
        return False
    except FileNotFoundError:
        print(f"\n✗ PyInstaller not found. Please install it first:")
        print(f"  pip install pyinstaller\n")
        return False

def main():
    print("="*60)
    print("Telegram Channel API - Executable Builder")
    print("="*60)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("✓ PyInstaller is installed\n")
    except ImportError:
        print("✗ PyInstaller is not installed")
        print("\nInstalling PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✓ PyInstaller installed\n")
    
    # Build both executables
    success = True
    
    # Build API server (with console)
    success &= build_executable("main.py", "TelegramAPI_Server", console=True)
    
    # Build Frontend server (with console)
    success &= build_executable("frontend.py", "TelegramAPI_Frontend", console=True)
    
    print("\n" + "="*60)
    if success:
        print("✓ All executables built successfully!")
        print("\nExecutables are in the 'dist' folder:")
        print("  - TelegramAPI_Server.exe (API on port 8000)")
        print("  - TelegramAPI_Frontend.exe (Frontend on port 8001)")
        print("\nNote: Make sure to create a .env file with your credentials")
        print("      before running the executables.")
    else:
        print("✗ Some builds failed. Check the errors above.")
    print("="*60)

if __name__ == "__main__":
    main()


