"""
Database Initialization and Population Script
Creates and populates all three databases with sample data
"""

import sqlite3
import os
from datetime import datetime

# Database paths
DB_DIR = 'databases'
USERS_DB = os.path.join(DB_DIR, 'users.db')
QUESTIONS_DB = os.path.join(DB_DIR, 'questions.db')
ASSIGNMENTS_DB = os.path.join(DB_DIR, 'assignments.db')

# Ensure database directory exists
os.makedirs(DB_DIR, exist_ok=True)


def init_users_db():
    """Initialize users database with schema"""
    print("Initializing users database...")
    conn = sqlite3.connect(USERS_DB)
    cursor = conn.cursor()
    
    with open(os.path.join(DB_DIR, 'users_schema.sql'), 'r') as f:
        schema = f.read()
        cursor.executescript(schema)
    
    conn.commit()
    conn.close()
    print("✓ Users database initialized")


def init_questions_db():
    """Initialize and populate questions database"""
    print("Initializing questions database...")
    conn = sqlite3.connect(QUESTIONS_DB)
    cursor = conn.cursor()
    
    # Create schema
    with open(os.path.join(DB_DIR, 'questions_schema.sql'), 'r') as f:
        schema = f.read()
        cursor.executescript(schema)
    
    # Insert 100+ sample questions
    questions = get_sample_questions()
    
    for role, difficulty, category, question, keywords in questions:
        cursor.execute('''
            INSERT INTO Questions (role, difficulty, category, question_text, expected_keywords, source)
            VALUES (?, ?, ?, ?, ?, 'database')
        ''', (role, difficulty, category, question, keywords))
    
    conn.commit()
    
    # Verify count
    count = cursor.execute('SELECT COUNT(*) FROM Questions').fetchone()[0]
    conn.close()
    
    print(f"✓ Questions database initialized with {count} questions")


def init_assignments_db():
    """Initialize assignments database with new schema"""
    print("Initializing assignments database...")
    conn = sqlite3.connect(ASSIGNMENTS_DB)
    cursor = conn.cursor()
    
    # Create schema
    with open(os.path.join(DB_DIR, 'assignments_schema.sql'), 'r') as f:
        schema = f.read()
        cursor.executescript(schema)
    
    conn.commit()
    conn.close()
    
    print(f"✓ Assignments database initialized (empty - use AI to generate assignments)")


def get_sample_questions():
    """Returns 100+ sample interview questions"""
    return [
        # Python - Easy (20 questions)
        ('Python Developer', 'easy', 'Python', 'What is Python and why is it popular?', 'interpreted, simple, versatile, readable'),
        ('Python Developer', 'easy', 'Python', 'Explain the difference between list and tuple.', 'mutable, immutable, list, tuple'),
        ('Python Developer', 'easy', 'Python', 'What are Python data types?', 'int, float, string, list, dict, tuple, set'),
        ('Python Developer', 'easy', 'Python', 'How do you write comments in Python?', '# single line, """ multi-line """'),
        ('Python Developer', 'easy', 'Python', 'What is a variable in Python?', 'container, storage, reference, type'),
        ('Python Developer', 'easy', 'Python', 'Explain Python indentation.', 'whitespace, blocks, syntax, mandatory'),
        ('Python Developer', 'easy', 'Python', 'What is the difference between append() and extend()?', 'list, single element, multiple elements'),
        ('Python Developer', 'easy', 'Python', 'How do you create a dictionary in Python?', 'key-value, {}, dict()'),
        ('Python Developer', 'easy', 'Python', 'What is a string in Python?', 'text, immutable, sequence, characters'),
        ('Python Developer', 'easy', 'Python', 'How do you get user input in Python?', 'input(), raw_input, console'),
        ('Python Developer', 'easy', 'Python', 'What is the difference between "==" and "is"?', 'equality, identity, value, object'),
        ('Python Developer', 'easy', 'Python', 'What are Python keywords?', 'reserved, if, for, while, def, class'),
        ('Python Developer', 'easy', 'Python', 'How do you convert a string to integer?', 'int(), type conversion, casting'),
        ('Python Developer', 'easy', 'Python', 'What is a for loop in Python?', 'iteration, range, sequence, loop'),
        ('Python Developer', 'easy', 'Python', 'What is a while loop?', 'condition, iteration, break, continue'),
        ('Python Developer', 'easy', 'Python', 'How do you define a function in Python?', 'def, return, parameters, arguments'),
        ('Python Developer', 'easy', 'Python', 'What is the difference between break and continue?', 'loop control, exit, skip'),
        ('Python Developer', 'easy', 'Python', 'What are Python modules?', 'import, library, reusable code, package'),
        ('Python Developer', 'easy', 'Python', 'How do you handle exceptions in Python?', 'try, except, finally, raise'),
        ('Python Developer', 'easy', 'Python', 'What is None in Python?', 'null, absence of value, NoneType'),
        
        # Python - Medium (20 questions)
        ('Python Developer', 'medium', 'Python', 'What are decorators in Python?', 'wrapper, function modifier, @, closure'),
        ('Python Developer', 'medium', 'Python', 'Explain list comprehension with example.', 'concise, [x for x in], filtering, mapping'),
        ('Python Developer', 'medium', 'Python', 'What is the difference between deep copy and shallow copy?', 'copy module, reference, nested, independent'),
        ('Python Developer', 'medium', 'Python', 'What are lambda functions?', 'anonymous, inline, single expression, functional'),
        ('Python Developer', 'medium', 'Python', 'Explain *args and **kwargs.', 'variable arguments, positional, keyword, unpacking'),
        ('Python Developer', 'medium', 'Python', 'What are Python generators?', 'yield, iterator, lazy evaluation, memory efficient'),
        ('Python Developer', 'medium', 'Python', 'Explain the difference between class method and static method.', '@classmethod, @staticmethod, cls, self'),
        ('Python Developer', 'medium', 'Python', 'What is a closure in Python?', 'nested function, encapsulation, scope, factory'),
        ('Python Developer', 'medium', 'Python', 'How does Python manage memory?', 'garbage collection, reference counting, memory pool'),
        ('Python Developer', 'medium', 'Python', 'What are Python iterators and iterables?', '__iter__, __next__, for loop, protocol'),
        ('Python Developer', 'medium', 'Python', 'Explain the map, filter, and reduce functions.', 'functional programming, lambda, transformation'),
        ('Python Developer', 'medium', 'Python', 'What is the difference between __str__ and __repr__?', 'string representation, debugging, user-friendly'),
        ('Python Developer', 'medium', 'Python', 'How do you handle multiple exceptions?', 'tuple, multiple except, exception hierarchy'),
        ('Python Developer', 'medium', 'Python', 'What are context managers in Python?', 'with statement, __enter__, __exit__, resource management'),
        ('Python Developer', 'medium', 'Python', 'Explain Python\'s duck typing.', 'dynamic typing, protocol, interface, behavior'),
        ('Python Developer', 'medium', 'Python', 'What is a metaclass?', 'class of a class, type, creation, customization'),
        ('Python Developer', 'medium', 'Python', 'How do you create a singleton pattern?', 'design pattern, __new__, instance control'),
        ('Python Developer', 'medium', 'Python', 'What is the purpose of __init__.py?', 'package, module initialization, namespace'),
        ('Python Developer', 'medium', 'Python', 'Explain Python\'s GIL (Global Interpreter Lock).', 'thread safety, CPython, concurrency, limitation'),
        ('Python Developer', 'medium', 'Python', 'What are abstract base classes?', 'ABC, interface, abstract methods, inheritance'),
        
        # Python - Hard (10 questions)
        ('Python Developer', 'hard', 'Python', 'Explain the GIL and its impact on multithreading.', 'CPython, concurrency, performance, multiprocessing'),
        ('Python Developer', 'hard', 'Python', 'How does Python\'s garbage collection work?', 'reference counting, cyclic references, generations, gc module'),
        ('Python Developer', 'hard', 'Python', 'What are descriptors in Python?', '__get__, __set__, property, data descriptor'),
        ('Python Developer', 'hard', 'Python', 'Explain the MRO (Method Resolution Order).', 'C3 linearization, multiple inheritance, super(), diamond problem'),
        ('Python Developer', 'hard', 'Python', 'How do you optimize Python code for performance?', 'profiling, Cython, PyPy, algorithm optimization'),
        ('Python Developer', 'hard', 'Python', 'What is the difference between async and threading?', 'asyncio, coroutines, concurrency, I/O bound'),
        ('Python Developer', 'hard', 'Python', 'Explain Python\'s memory model.', 'heap, stack, PyObject, reference counting'),
        ('Python Developer', 'hard', 'Python', 'How do you implement custom iterators?', '__iter__, __next__, StopIteration, protocol'),
        ('Python Developer', 'hard', 'Python', 'What are weak references and when to use them?', 'weakref, circular reference, cache, memory leak'),
        ('Python Developer', 'hard', 'Python', 'Explain Python\'s import system.', 'sys.modules, PYTHONPATH, __import__, importlib'),
        
        # SQL - Easy (10 questions)
        ('Data Scientist', 'easy', 'SQL', 'What is SQL?', 'structured query language, database, queries'),
        ('Data Scientist', 'easy', 'SQL', 'What is a primary key?', 'unique identifier, not null, constraint'),
        ('Data Scientist', 'easy', 'SQL', 'What is a foreign key?', 'reference, relationship, constraint, integrity'),
        ('Data Scientist', 'easy', 'SQL', 'What is the difference between WHERE and HAVING?', 'filtering, aggregate, GROUP BY'),
        ('Data Scientist', 'easy', 'SQL', 'What are the main SQL commands?', 'SELECT, INSERT, UPDATE, DELETE, CREATE'),
        ('Data Scientist', 'easy', 'SQL', 'What is a database?', 'structured data, tables, DBMS, storage'),
        ('Data Scientist', 'easy', 'SQL', 'What is a table?', 'rows, columns, records, schema'),
        ('Data Scientist', 'easy', 'SQL', 'How do you select all columns from a table?', 'SELECT *, FROM, table name'),
        ('Data Scientist', 'easy', 'SQL', 'What is the ORDER BY clause?', 'sorting, ASC, DESC, results'),
        ('Data Scientist', 'easy', 'SQL', 'What is the DISTINCT keyword?', 'unique values, duplicates, SELECT'),
        
        # SQL - Medium (10 questions)
        ('Data Scientist', 'medium', 'SQL', 'Explain INNER JOIN and LEFT JOIN.', 'join types, matching records, null values'),
        ('Data Scientist', 'medium', 'SQL', 'What is a subquery?', 'nested query, SELECT within SELECT, derived table'),
        ('Data Scientist', 'medium', 'SQL', 'What are aggregate functions?', 'COUNT, SUM, AVG, MAX, MIN, GROUP BY'),
        ('Data Scientist', 'medium', 'SQL', 'What is normalization?', '1NF, 2NF, 3NF, redundancy, design'),
        ('Data Scientist', 'medium', 'SQL', 'What is an index?', 'performance, search optimization, B-tree'),
        ('Data Scientist', 'medium', 'SQL', 'Explain the difference between UNION and UNION ALL.', 'combine results, duplicates, performance'),
        ('Data Scientist', 'medium', 'SQL', 'What is a view?', 'virtual table, query abstraction, security'),
        ('Data Scientist', 'medium', 'SQL', 'What are triggers?', 'automatic execution, events, INSERT, UPDATE, DELETE'),
        ('Data Scientist', 'medium', 'SQL', 'What is a stored procedure?', 'reusable code, parameters, business logic'),
        ('Data Scientist', 'medium', 'SQL', 'How do you find the second highest salary?', 'LIMIT, OFFSET, subquery, ranking'),
        
        # Coding - Easy (10 questions)
        ('Full Stack Developer', 'easy', 'Coding', 'How do you reverse a string?', 'iteration, slicing, recursion'),
        ('Full Stack Developer', 'easy', 'Coding', 'How do you check if a number is even or odd?', 'modulo, %, division'),
        ('Full Stack Developer', 'easy', 'Coding', 'How do you find the factorial of a number?', 'recursion, loop, multiplication'),
        ('Full Stack Developer', 'easy', 'Coding', 'How do you check if a string is a palindrome?', 'reverse, comparison, two pointers'),
        ('Full Stack Developer', 'easy', 'Coding', 'How do you find the maximum element in an array?', 'iteration, comparison, max()'),
        ('Full Stack Developer', 'easy', 'Coding', 'How do you count vowels in a string?', 'iteration, condition, counter'),
        ('Full Stack Developer', 'easy', 'Coding', 'How do you swap two variables?', 'temp variable, tuple unpacking, arithmetic'),
        ('Full Stack Developer', 'easy', 'Coding', 'How do you check if a number is prime?', 'divisibility, loop, optimization'),
        ('Full Stack Developer', 'easy', 'Coding', 'How do you sum all elements in a list?', 'loop, sum(), accumulator'),
        ('Full Stack Developer', 'easy', 'Coding', 'How do you remove duplicates from a list?', 'set, loop, dictionary'),
        
        # Coding - Medium (10 questions)
        ('Full Stack Developer', 'medium', 'Coding', 'Find the second largest number in an array.', 'sorting, iteration, tracking'),
        ('Full Stack Developer', 'medium', 'Coding', 'Implement binary search algorithm.', 'divide and conquer, sorted array, O(log n)'),
        ('Full Stack Developer', 'medium', 'Coding', 'Find all pairs that sum to a target value.', 'hash map, two pointers, O(n)'),
        ('Full Stack Developer', 'medium', 'Coding', 'Implement a stack using arrays.', 'LIFO, push, pop, top'),
        ('Full Stack Developer', 'medium', 'Coding', 'Implement a queue using arrays.', 'FIFO, enqueue, dequeue, front'),
        ('Full Stack Developer', 'medium', 'Coding', 'Find the longest substring without repeating characters.', 'sliding window, hash set, optimization'),
        ('Full Stack Developer', 'medium', 'Coding', 'Check if parentheses are balanced.', 'stack, matching, validation'),
        ('Full Stack Developer', 'medium', 'Coding', 'Merge two sorted arrays.', 'two pointers, comparison, merging'),
        ('Full Stack Developer', 'medium', 'Coding', 'Rotate an array by k positions.', 'slicing, modulo, in-place'),
        ('Full Stack Developer', 'medium', 'Coding', 'Find the missing number in an array.', 'sum formula, XOR, hash set'),
        
        # Backend - Medium (10 questions)
        ('Backend Developer', 'medium', 'Backend', 'What is REST API?', 'HTTP methods, stateless, resources, JSON'),
        ('Backend Developer', 'medium', 'Backend', 'Explain the difference between GET and POST.', 'retrieval, submission, idempotent, body'),
        ('Backend Developer', 'medium', 'Backend', 'What are HTTP status codes?', '200, 404, 500, success, error'),
        ('Backend Developer', 'medium', 'Backend', 'What is CORS?', 'Cross-Origin Resource Sharing, security, headers'),
        ('Backend Developer', 'medium', 'Backend', 'What is authentication vs authorization?', 'identity, permissions, JWT, OAuth'),
        ('Backend Developer', 'medium', 'Backend', 'Explain database transactions.', 'ACID, commit, rollback, consistency'),
        ('Backend Developer', 'medium', 'Backend', 'What is caching?', 'Redis, memory, performance, invalidation'),
        ('Backend Developer', 'medium', 'Backend', 'What is a middleware?', 'request pipeline, processing, Flask, Express'),
        ('Backend Developer', 'medium', 'Backend', 'Explain SQL injection and prevention.', 'security, parameterized queries, sanitization'),
        ('Backend Developer', 'medium', 'Backend', 'What is rate limiting?', 'API protection, throttling, abuse prevention'),
        
        # System Design - Hard (10 questions)
        ('Full Stack Developer', 'hard', 'System Design', 'Design a URL shortener service.', 'hash, database, scaling, redirect'),
        ('Full Stack Developer', 'hard', 'System Design', 'Design a chat application.', 'WebSocket, real-time, message queue, database'),
        ('Full Stack Developer', 'hard', 'System Design', 'Design a rate limiter.', 'token bucket, sliding window, distributed'),
        ('Full Stack Developer', 'hard', 'System Design', 'Design a caching system.', 'LRU, Redis, eviction policy, distributed'),
        ('Full Stack Developer', 'hard', 'System Design', 'Design a file storage system.', 'chunking, replication, metadata, S3'),
        ('Full Stack Developer', 'hard', 'System Design', 'Design a notification service.', 'queue, pub-sub, scalability, delivery'),
        ('Full Stack Developer', 'hard', 'System Design', 'Design a search engine.', 'indexing, ranking, crawling, distributed'),
        ('Full Stack Developer', 'hard', 'System Design', 'Design a recommendation system.', 'collaborative filtering, machine learning, personalization'),
        ('Full Stack Developer', 'hard', 'System Design', 'Design a video streaming service.', 'CDN, adaptive bitrate, storage, encoding'),
        ('Full Stack Developer', 'hard', 'System Design', 'Design a distributed database.', 'sharding, replication, CAP theorem, consistency'),
        
        # HR - Easy (5 questions)
        ('Python Developer', 'easy', 'HR', 'Tell me about yourself.', 'introduction, background, experience, goals'),
        ('Python Developer', 'easy', 'HR', 'Why do you want this job?', 'motivation, company fit, career goals'),
        ('Python Developer', 'easy', 'HR', 'What are your strengths?', 'skills, qualities, examples, relevant'),
        ('Python Developer', 'easy', 'HR', 'What are your weaknesses?', 'self-awareness, improvement, honest'),
        ('Python Developer', 'easy', 'HR', 'Where do you see yourself in 5 years?', 'career goals, ambition, realistic'),
    ]


def get_sample_assignments():
    """Returns 30+ sample coding assignments"""
    return [
        # Python - Easy (8 assignments)
        ('Python Developer', 'easy', 'Write a function to reverse a string without using built-in reverse methods.', 
         'Use slicing [::-1] or iterate backwards building a new string.'),
        ('Python Developer', 'easy', 'Create a function to check if a string is a palindrome.', 
         'Compare the string with its reverse.'),
        ('Python Developer', 'easy', 'Write a program to find the factorial of a number using recursion.', 
         'Base case: factorial(0) = 1, Recursive: n * factorial(n-1)'),
        ('Python Developer', 'easy', 'Create a function to count vowels in a given string.', 
         'Iterate through string and check if each character is in "aeiouAEIOU"'),
        ('Python Developer', 'easy', 'Write a program to check if a number is prime.', 
         'Check divisibility from 2 to sqrt(n)'),
        ('Python Developer', 'easy', 'Create a function to find the sum of digits in a number.', 
         'Convert to string and sum int(digit) for each digit, or use modulo.'),
        ('Python Developer', 'easy', 'Write a program to remove duplicates from a list.', 
         'Convert to set and back to list, or use dict.fromkeys()'),
        ('Python Developer', 'easy', 'Create a function to merge two dictionaries.', 
         'Use {**dict1, **dict2} or dict1.update(dict2)'),
        
        # Python - Medium (7 assignments)
        ('Python Developer', 'medium', 'Write a program to find the second largest number in a list.', 
         'Remove max element and find max again, or sort and get second last.'),
        ('Python Developer', 'medium', 'Implement a function to find all duplicates in a list.', 
         'Use Counter from collections or iterate with a set to track seen elements.'),
        ('Python Developer', 'medium', 'Create a decorator to measure function execution time.', 
         'Use time.time() before and after function call in wrapper function.'),
        ('Python Developer', 'medium', 'Write a function to flatten a nested list.', 
         'Use recursion or itertools.chain.from_iterable()'),
        ('Python Developer', 'medium', 'Implement a simple LRU cache using OrderedDict.', 
         'Use OrderedDict with move_to_end() and popitem(last=False)'),
        ('Python Developer', 'medium', 'Create a function to find the longest common substring.', 
         'Use dynamic programming with 2D matrix.'),
        ('Python Developer', 'medium', 'Write a program to implement binary search.', 
         'Divide array in half, compare middle element with target.'),
        
        # SQL - Easy (5 assignments)
        ('Data Scientist', 'easy', 'Write a SQL query to find the second highest salary.', 
         'Use LIMIT with OFFSET or subquery with MAX().'),
        ('Data Scientist', 'easy', 'Write a query to remove duplicates from a table.', 
         'Use DELETE with ROW_NUMBER() or DISTINCT with INSERT INTO.'),
        ('Data Scientist', 'easy', 'Create a query to find employees with salary above average.', 
         'Use subquery: WHERE salary > (SELECT AVG(salary) FROM employees)'),
        ('Data Scientist', 'easy', 'Write a JOIN query between employees and departments tables.', 
         'SELECT * FROM employees e INNER JOIN departments d ON e.dept_id = d.id'),
        ('Data Scientist', 'easy', 'Create a query to count employees in each department.', 
         'Use GROUP BY: SELECT dept_id, COUNT(*) FROM employees GROUP BY dept_id'),
        
        # SQL - Medium (3 assignments)
        ('Data Scientist', 'medium', 'Write a query to find employees who earn more than their managers.', 
         'Self join: SELECT e.name FROM emp e JOIN emp m ON e.manager_id = m.id WHERE e.salary > m.salary'),
        ('Data Scientist', 'medium', 'Create a query to find the Nth highest salary.', 
         'Use LIMIT with OFFSET or DENSE_RANK() window function.'),
        ('Data Scientist', 'medium', 'Write a query to find duplicates in a table.', 
         'Use GROUP BY with HAVING COUNT(*) > 1'),
        
        # Backend/Full Stack - Easy (4 assignments)
        ('Full Stack Developer', 'easy', 'Build a simple REST API endpoint for user registration using Flask.', 
         'Use @app.route with POST method, validate input, hash password, save to database.'),
        ('Full Stack Developer', 'easy', 'Create an API endpoint to fetch all users from database.', 
         'Use @app.route with GET method, query database, return JSON.'),
        ('Full Stack Developer', 'easy', 'Implement basic form validation for email and password.', 
         'Use regex for email, check password length and requirements.'),
        ('Full Stack Developer', 'easy', 'Create a simple login authentication system.', 
         'Check credentials, create session, return success/error.'),
        
        # Backend/Full Stack - Medium (5 assignments)
        ('Backend Developer', 'medium', 'Design and implement a RESTful API for a blog system with CRUD operations.', 
         'Create endpoints for Create, Read, Update, Delete posts with authentication.'),
        ('Backend Developer', 'medium', 'Implement JWT-based authentication in Flask.', 
         'Use PyJWT library, create token on login, verify token on protected routes.'),
        ('Backend Developer', 'medium', 'Create an API with rate limiting to prevent abuse.', 
         'Use Flask-Limiter or implement custom middleware with Redis.'),
        ('Backend Developer', 'medium', 'Build a file upload API with validation.', 
         'Check file type, size, save securely, return file URL.'),
        ('Backend Developer', 'medium', 'Implement pagination for API responses.', 
         'Use LIMIT and OFFSET in queries, return page metadata with results.'),
    ]


if __name__ == '__main__':
    print("=" * 50)
    print("Database Initialization Started")
    print("=" * 50)
    
    try:
        init_users_db()
        init_questions_db()
        init_assignments_db()
        
        print("\n" + "=" * 50)
        print("✓ All databases initialized successfully!")
        print("=" * 50)
        print(f"\nDatabase files created:")
        print(f"  - {USERS_DB}")
        print(f"  - {QUESTIONS_DB}")
        print(f"  - {ASSIGNMENTS_DB}")
        
    except Exception as e:
        print(f"\n✗ Error during initialization: {e}")
        import traceback
        traceback.print_exc()
