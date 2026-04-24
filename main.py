import os
import subprocess
import sys

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def run_script(script_name):
    print(f"\n--- Ishga tushirilmoqda: {script_name} ---")
    try:
        # We use the current python executable to run the scripts
        result = subprocess.run([sys.executable, script_name], capture_output=False, text=True)
        if result.returncode != 0:
            print(f"\n[!] Script xato bilan tugadi (kod: {result.returncode})")
    except Exception as e:
        print(f"\n[!] Xatolik yuz berdi: {e}")
    input("\nDavom etish uchun Enter bosing...")

def main():
    scripts = {
        "1": ("Annex 6: Logistics Solver", "solve_Annex6.py"),
        "2": ("Annex 7: Energy Solver", "solve_Annex7.py"),
        "3": ("Virus Detection", "solve_virus_detection.py"),
        "4": ("Youngest Employee Finder", "find_youngest_employee.py"),
        "5": ("Caesar Key Finder (Annex 9)", "find_caesar_key.py"),
        "6": ("Sequence Finder (A26)", "find_a26.py"),
        "7": ("Date Extractor from EXE", "extract_dates_from_exe.py"),
    }

    while True:
        clear_screen()
        print("="*50)
        print("   TURK_MAN LOYIHASI - ASOSIY MENU   ")
        print("="*50)
        for key, (name, _) in scripts.items():
            print(f"{key}. {name}")
        print("0. Chiqish")
        print("-" * 50)
        
        choice = input("Vazifani tanlang (0-7): ")
        
        if choice == "0":
            print("Xayr!")
            break
        elif choice in scripts:
            name, filename = scripts[choice]
            if os.path.exists(filename):
                run_script(filename)
            else:
                print(f"\n[!] Fayl topilmadi: {filename}")
                input("Davom etish uchun Enter bosing...")
        else:
            print("\n[!] Noto'g'ri tanlov!")
            input("Davom etish uchun Enter bosing...")

if __name__ == "__main__":
    main()
