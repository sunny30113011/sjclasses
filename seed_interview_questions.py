import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')
django.setup()

from courses.models import InterviewQuestion
from accounts.models import User

def seed_questions():
    print("Seeding Top Company Interview Questions & Answers...")
    admin_user = User.objects.filter(is_superuser=True).first()

    questions_data = [
        {
            'company_name': 'TCS',
            'topic': 'Python & Django',
            'category': 'Technical',
            'difficulty': 'Medium',
            'is_featured': True,
            'question_text': 'What is the difference between list and tuple in Python, and when should you use each?',
            'answer_text': 'In Python, both lists and tuples are sequence data structures. Key differences:\n1. Mutability: Lists are mutable (can add, remove, modify elements), while tuples are immutable (read-only after creation).\n2. Syntax: Lists use square brackets [], while tuples use parentheses ().\n3. Memory & Performance: Tuples consume less memory and execute faster than lists because of fixed allocation.\n\nUse Case: Use a list when data needs to be modified dynamically (e.g. shopping cart items). Use a tuple for constant data structures (e.g. DB connection credentials, GPS coordinates).',
            'code_snippet': '# List Example (Mutable)\nmy_list = [1, 2, 3]\nmy_list.append(4)\nprint(my_list) # Output: [1, 2, 3, 4]\n\n# Tuple Example (Immutable)\nmy_tuple = (1, 2, 3)\n# my_tuple[0] = 10  --> Raises TypeError'
        },

        {
            'company_name': 'Infosys',
            'topic': 'Django & Database',
            'category': 'Technical',
            'difficulty': 'Medium',
            'is_featured': True,
            'question_text': 'Explain Django ORM select_related vs prefetch_related and how they prevent N+1 query problems.',
            'answer_text': 'Both select_related and prefetch_related are query optimization techniques in Django to prevent the N+1 database query problem.\n\n1. select_related: Performs an SQL JOIN and fetches related objects in a single database query. Use this for single-valued relationships: ForeignKey and OneToOneField.\n2. prefetch_related: Performs a separate SQL query for each relationship and does the joining in Python. Use this for multi-valued relationships: ManyToManyField and reverse ForeignKey relations.',
            'code_snippet': '# select_related (SQL JOIN for ForeignKey)\nbooks = Book.objects.select_related("author").all()\n\n# prefetch_related (Separate query for ManyToMany)\ncourses = Course.objects.prefetch_related("modules__lessons").all()'
        },

        {
            'company_name': 'Amazon',
            'topic': 'Data Structures & Coding',
            'category': 'Coding',
            'difficulty': 'Hard',
            'is_featured': True,
            'question_text': 'How do you find the first non-repeating character in a string with O(N) time complexity?',
            'answer_text': 'We can use a HashMap / Hash Dictionary or collections.Counter to count the frequency of each character in a single pass O(N). In a second pass through the string, return the first character whose frequency is 1.',
            'code_snippet': 'from collections import Counter\n\ndef first_uniq_char(s: str) -> int:\n    count = Counter(s)\n    for idx, ch in enumerate(s):\n        if count[ch] == 1:\n            return idx\n    return -1\n\n# Test\nprint(first_uniq_char("leetcode")) # Returns 0 ("l")\nprint(first_uniq_char("loveleetcode")) # Returns 2 ("v")'
        },

        {
            'company_name': 'Wipro',
            'topic': 'SQL & Databases',
            'category': 'Technical',
            'difficulty': 'Easy',
            'is_featured': True,
            'question_text': 'What is the difference between WHERE and HAVING clause in SQL?',
            'answer_text': '1. WHERE Clause: Filters individual rows before any grouping or aggregation (GROUP BY) takes place. Cannot be used with aggregate functions like SUM(), COUNT(), AVG().\n2. HAVING Clause: Filters grouped rows after the GROUP BY operation is performed. Used specifically with aggregate functions.',
            'code_snippet': '-- WHERE filters rows before aggregation\nSELECT department, COUNT(*)\nFROM employees\nWHERE salary > 50000\nGROUP BY department\nHAVING COUNT(*) > 5; -- HAVING filters aggregated groups'
        },

        {
            'company_name': 'Google',
            'topic': 'System Architecture',
            'category': 'System Design',
            'difficulty': 'Hard',
            'is_featured': True,
            'question_text': 'How does a Load Balancer work, and what are common algorithms (Round Robin, Least Connections, IP Hash)?',
            'answer_text': 'A Load Balancer distributes incoming network traffic across multiple backend servers to ensure high availability, fault tolerance, and responsiveness.\n\nCommon Algorithms:\n1. Round Robin: Requests are distributed sequentially across servers in a loop.\n2. Least Connections: Directs traffic to the server with the fewest active connections.\n3. IP Hash: Uses the client IP address to determine which server receives the request, ensuring session persistence (sticky sessions).',
            'code_snippet': '# Conceptual Round-Robin Load Balancer Algorithm\nclass RoundRobin:\n    def __init__(self, servers):\n        self.servers = servers\n        self.index = 0\n\n    def get_server(self):\n        server = self.servers[self.index]\n        self.index = (self.index + 1) % len(self.servers)\n        return server'
        },

        {
            'company_name': 'Accenture',
            'topic': 'React & Frontend',
            'category': 'Technical',
            'difficulty': 'Medium',
            'is_featured': True,
            'question_text': 'What is the Virtual DOM in React and how does the reconciliation algorithm work?',
            'answer_text': 'The Virtual DOM (VDOM) is a lightweight in-memory representation of the real DOM. When state changes in React:\n1. A new Virtual DOM tree is created.\n2. React compares the new VDOM with the previous VDOM using a diffing algorithm (Reconciliation).\n3. Only the exact modified nodes are updated in the real DOM, minimizing expensive DOM repaint operations.',
            'code_snippet': '// React Component State Update\nconst [count, setCount] = useState(0);\n\n// Triggering state change updates VDOM diff, not full page reload\n<button onClick={() => setCount(count + 1)}>Increment</button>'
        },

        {
            'company_name': 'Microsoft',
            'topic': 'REST API & Web',
            'category': 'Technical',
            'difficulty': 'Medium',
            'is_featured': False,
            'question_text': 'What are HTTP Status Codes 200, 201, 400, 401, 403, 404, and 500?',
            'answer_text': 'HTTP status codes indicate the result of an HTTP request:\n- 200 OK: Successful request.\n- 201 Created: New resource successfully created (e.g. POST request).\n- 400 Bad Request: Client sent invalid data/payload.\n- 401 Unauthorized: Authentication required / missing token.\n- 403 Forbidden: Client is authenticated but lacks permission.\n- 404 Not Found: Requested URL resource does not exist.\n- 500 Internal Server Error: Server unhandled exception.',
            'code_snippet': '# Django REST Framework Response Examples\nreturn Response(serializer.data, status=status.HTTP_200_OK)\nreturn Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)'
        },

        {
            'company_name': 'TCS',
            'topic': 'HR & Behavioral',
            'category': 'HR / Behavioral',
            'difficulty': 'Easy',
            'is_featured': True,
            'question_text': 'HR Question: "Tell me about a time when you faced a technical bug under tight deadline. How did you resolve it?"',
            'answer_text': 'Use the STAR Technique (Situation, Task, Action, Result):\n- Situation: During our final semester project / production release, we encountered an unhandled 500 server error when 50 simultaneous users registered.\n- Task: I needed to diagnose the bottleneck and fix it within 3 hours before the client demo.\n- Action: I inspected server logs, identified an missing database index on the email column causing lock timeouts, added the index via a Django migration, and tested under load.\n- Result: Request response times dropped from 4.2 seconds to 120ms, and the demo was 100% successful.',
            'code_snippet': None
        }
    ]

    for q in questions_data:
        InterviewQuestion.objects.get_or_create(
            company_name=q['company_name'],
            question_text=q['question_text'],
            defaults={
                'topic': q['topic'],
                'category': q['category'],
                'difficulty': q['difficulty'],
                'answer_text': q['answer_text'],
                'code_snippet': q['code_snippet'],
                'uploaded_by': admin_user,
                'is_featured': q['is_featured']
            }
        )

    print(f"[COMPLETE] Created {InterviewQuestion.objects.count()} Top Company Interview Questions!")

if __name__ == '__main__':
    seed_questions()
