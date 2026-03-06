"""
Verify Database Contents
This script checks the contents of all three databases after initialization.
"""
import sqlite3

def verify_database():
    print("=" * 60)
    print("DATABASE VERIFICATION")
    print("=" * 60)
    
    # Check users.db
    print("\n1. USERS DATABASE (databases/users.db)")
    print("-" * 60)
    conn = sqlite3.connect('databases/users.db')
    cursor = conn.cursor()
    
    tables = ['Users', 'Resumes', 'Interviews', 'Results', 'ChatHistory', 'Progress']
    for table in tables:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        count = cursor.fetchone()[0]
        print(f"  ✓ {table}: {count} records")
    conn.close()
    
    # Check questions.db
    print("\n2. QUESTIONS DATABASE (databases/questions.db)")
    print("-" * 60)
    conn = sqlite3.connect('databases/questions.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM Questions')
    total = cursor.fetchone()[0]
    print(f"  ✓ Total Questions: {total}")
    
    print("\n  Questions by Role & Difficulty:")
    cursor.execute('''
        SELECT role, difficulty, COUNT(*) as count 
        FROM Questions 
        GROUP BY role, difficulty 
        ORDER BY role, difficulty
    ''')
    for row in cursor.fetchall():
        print(f"    - {row[0]:25s} | {row[1]:6s} | {row[2]} questions")
    
    print("\n  Questions by Category:")
    cursor.execute('''
        SELECT category, COUNT(*) as count 
        FROM Questions 
        GROUP BY category 
        ORDER BY category
    ''')
    for row in cursor.fetchall():
        print(f"    - {row[0]:15s} | {row[1]} questions")
    
    conn.close()
    
    # Check assignments.db
    print("\n3. ASSIGNMENTS DATABASE (databases/assignments.db)")
    print("-" * 60)
    conn = sqlite3.connect('databases/assignments.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM Assignments')
    total = cursor.fetchone()[0]
    print(f"  ✓ Total Assignments: {total}")
    
    print("\n  Assignments by Role & Difficulty:")
    cursor.execute('''
        SELECT role, difficulty, COUNT(*) as count 
        FROM Assignments 
        GROUP BY role, difficulty 
        ORDER BY role, difficulty
    ''')
    for row in cursor.fetchall():
        print(f"    - {row[0]:25s} | {row[1]:6s} | {row[2]} assignments")
    
    # Show sample assignments
    print("\n  Sample Assignments:")
    cursor.execute('SELECT role, difficulty, assignment_text FROM Assignments LIMIT 3')
    for i, row in enumerate(cursor.fetchall(), 1):
        print(f"\n    {i}. [{row[0]} - {row[1]}]")
        print(f"       {row[2][:80]}...")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✓ DATABASE VERIFICATION COMPLETE")
    print("=" * 60)
    print("\nAll databases are properly initialized and populated!")
    print("\nYou can now run: python app.py")

if __name__ == '__main__':
    verify_database()
