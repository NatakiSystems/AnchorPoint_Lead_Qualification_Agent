import sqlite3

# Connect to AnchorPoint database
conn = sqlite3.connect("anchorpoint_leads.db")
cursor = conn.cursor()

# Retrieve all records from the leads table
cursor.execute("SELECT * FROM leads")
rows = cursor.fetchall()

print("\n" + "="*60)
print("📊 ANCHORPOINT DATABASE RECORDS:")
print("="*60)

if not rows:
    print("No records found in the database yet.")
else:
    for row in rows:
        print(f"ID: {row[0]} | Name: {row[1]} | Company: {row[2]} | Industry: {row[3]}")
        print(f"    Service: {row[4]} | Budget: ${row[5]} | Timeline: {row[6]} days | Status: {row[7]}")
        print("-" * 60)

conn.close()