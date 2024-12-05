# test_import.py
try:
    from xprocess.pytest_xprocess import getrootdir
    print("pytest_xprocess imported successfully")
except ImportError as e:
    print(f"ImportError: {e}")
