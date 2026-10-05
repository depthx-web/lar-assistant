"""Check database schema."""
import sqlite3

conn = sqlite3.connect('E:/depthx/lar-assistant/data/lara.db')
cursor = conn.cursor()

print("=== ALL TABLES ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()
for table in tables:
    print(f"  - {table[0]}")

print("\n=== MANUSCRIPTS TABLE ===")
cursor.execute('PRAGMA table_info(manuscripts)')
cols = cursor.fetchall()
for c in cols:
    print(f"  {c[1]}: {c[2]}")

print("\n=== REQUIREMENT_CHECKS TABLE ===")
cursor.execute('PRAGMA table_info(requirement_checks)')
cols = cursor.fetchall()
for c in cols:
    print(f"  {c[1]}: {c[2]}")

conn.close()
print("\nDone!")