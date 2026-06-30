import os
import json
from pathlib import Path
import pandas as pd
from huggingface_hub import InferenceClient
import pdfplumber

# Hugging Face API key
HF_TOKEN = os.getenv("HF_TOKEN")  # Set this environment variable
client = InferenceClient(token=HF_TOKEN)

BASE_DIR = Path(__file__).resolve().parent.parent

def load_datasets():
    """Load questions and answers CSV files."""
    import csv
    
    questions_path = BASE_DIR / "data" / "questions.csv"
    answers_path = BASE_DIR / "data" / "answers.csv"
    kaggle_questions_path = BASE_DIR / "data" / "Software Questions.csv"
    
    # Load original datasets
    questions_df = pd.read_csv(questions_path, encoding='utf-8') if questions_path.exists() else pd.DataFrame()
    
    # Load answers with proper CSV handling
    answers_data = []
    if answers_path.exists():
        with open(answers_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            for row in reader:
                if len(row) >= 2:
                    # Join all columns after the first as the answer (in case of extra commas)
                    answers_data.append({
                        'question': row[0],
                        'answer': ','.join(row[1:])
                    })
    answers_df = pd.DataFrame(answers_data)
    
    # Load Kaggle dataset with encoding fallback
    kaggle_df = pd.DataFrame()
    if kaggle_questions_path.exists():
        try:
            kaggle_df = pd.read_csv(kaggle_questions_path, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                kaggle_df = pd.read_csv(kaggle_questions_path, encoding='latin-1')
            except Exception as e:
                print(f"Warning: Could not load Kaggle dataset: {e}")
    
    return questions_df, answers_df, kaggle_df

def extract_resume_text(pdf_path: str) -> str:
    """Extract text from PDF resume using pdfplumber."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def call_llm(prompt: str, model: str = "meta-llama/Llama-3.1-8B-Instruct") -> str:
    """Call Hugging Face Inference API."""
    try:
        response = client.text_generation(prompt, model=model, max_new_tokens=500)
        # Response is a string directly
        if isinstance(response, str):
            return response
        return str(response)
    except Exception as e:
        try:
            chat_response = client.chat_completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
            )
            if chat_response and getattr(chat_response, "choices", None):
                content = chat_response.choices[0].message.content
                if isinstance(content, str):
                    return content
            return "{}"
        except Exception as chat_error:
            print(f"LLM Error: {chat_error}")
            return "{}"

def transcribe_audio(audio_path: str) -> str:
    """Legacy function - no longer used with real-time speech recognition."""
    return "Real-time speech recognition is handled by the browser Web Speech API"

def analyze_resume(resume_text: str) -> dict:
    """Analyze resume to extract skills, projects, experience, and map to question categories."""
    if not resume_text or len(resume_text.strip()) == 0:
        return {
            "skills": ["Not provided"], 
            "projects": [], 
            "experience": "Not specified",
            "categories": ["General Programming"]
        }
    
    # First, extract keywords directly from resume text
    resume_lower = resume_text.lower()
    
    # Comprehensive technology keywords
    tech_keywords = {
        # Programming Languages
        'python': ['python', 'django', 'flask', 'fastapi', 'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'jupyter'],
        'javascript': ['javascript', 'js', 'node.js', 'nodejs', 'react', 'vue', 'angular', 'express', 'jquery'],
        'java': ['java', 'spring', 'hibernate', 'maven', 'gradle'],
        'cpp': ['c++', 'cpp', 'qt', 'boost'],
        'csharp': ['c#', 'csharp', '.net', 'asp.net', 'entity framework'],
        'php': ['php', 'laravel', 'symfony', 'wordpress'],
        'ruby': ['ruby', 'rails', 'ruby on rails'],
        'go': ['go', 'golang'],
        'rust': ['rust'],
        'kotlin': ['kotlin', 'android'],
        'swift': ['swift', 'ios'],
        'scala': ['scala', 'spark'],
        
        # Web Technologies
        'html': ['html', 'html5'],
        'css': ['css', 'css3', 'sass', 'scss', 'bootstrap', 'tailwind'],
        'react': ['react', 'react.js', 'redux', 'next.js', 'gatsby'],
        'angular': ['angular', 'angularjs'],
        'vue': ['vue', 'vue.js', 'nuxt'],
        
        # Backend
        'node': ['node.js', 'nodejs', 'express', 'nest.js'],
        'django': ['django', 'django rest framework'],
        'flask': ['flask'],
        'spring': ['spring', 'spring boot', 'spring framework'],
        'laravel': ['laravel'],
        
        # Databases
        'sql': ['sql', 'mysql', 'postgresql', 'postgres', 'sqlite', 'oracle', 'mssql', 'sql server'],
        'nosql': ['mongodb', 'mongo', 'cassandra', 'redis', 'dynamodb', 'couchdb', 'elasticsearch'],
        
        # Cloud & DevOps
        'aws': ['aws', 'amazon web services', 'ec2', 's3', 'lambda', 'rds', 'cloudformation'],
        'azure': ['azure', 'microsoft azure'],
        'gcp': ['gcp', 'google cloud', 'firebase'],
        'docker': ['docker', 'kubernetes', 'k8s', 'container', 'docker-compose'],
        'terraform': ['terraform', 'infrastructure as code'],
        'jenkins': ['jenkins', 'ci/cd', 'continuous integration'],
        'git': ['git', 'github', 'gitlab', 'bitbucket'],
        
        # Data Science & ML
        'machine learning': ['machine learning', 'ml', 'scikit-learn', 'tensorflow', 'pytorch', 'keras'],
        'data science': ['data science', 'pandas', 'numpy', 'matplotlib', 'seaborn', 'jupyter'],
        'deep learning': ['deep learning', 'neural network', 'cnn', 'rnn', 'lstm'],
        'nlp': ['nlp', 'natural language processing', 'spacy', 'nltk'],
        
        # Mobile
        'android': ['android', 'kotlin', 'java'],
        'ios': ['ios', 'swift', 'objective-c'],
        'react native': ['react native', 'expo'],
        'flutter': ['flutter', 'dart'],
        
        # Other
        'linux': ['linux', 'ubuntu', 'centos', 'bash', 'shell scripting'],
        'testing': ['testing', 'unit test', 'integration test', 'selenium', 'jest', 'pytest', 'junit'],
        'security': ['security', 'oauth', 'jwt', 'encryption', 'ssl', 'https'],
        'api': ['api', 'rest', 'graphql', 'soap', 'microservices'],
        'design patterns': ['design patterns', 'solid', 'mvc', 'mvvm']
    }
    
    # Extract skills from keywords
    found_skills = set()
    for category, keywords in tech_keywords.items():
        for keyword in keywords:
            if keyword in resume_lower:
                found_skills.add(category)
    
    # Use LLM for more detailed analysis
    prompt = f"""Extract from this resume:
1. Technical skills (be very specific, list actual technologies/tools used)
2. Projects (list with technologies used)
3. Experience level (Junior/Entry-level: <2 years, Mid-level: 2-5 years, Senior: >5 years)
4. Primary role/domain (e.g., Full Stack Developer, Data Scientist, Backend Engineer, etc.)

Resume: {resume_text[:1000]}

Reply in format: skills: X | projects: Y | experience: Z | domain: W"""
    
    response = call_llm(prompt)
    
    # Default values
    llm_skills = ["General programming"]
    projects = []
    experience = "Mid-level"
    domain = "Software Engineering"
    
    try:
        # Try to parse if JSON
        if response.strip().startswith('{'):
            data = json.loads(response)
            llm_skills = data.get("skills", llm_skills)
            projects = data.get("projects", projects) 
            experience = data.get("experience", experience)
            domain = data.get("domain", domain)
    except:
        # Parse text response
        lines = response.split('|')
        for line in lines:
            line = line.strip()
            if line.startswith('skills:'):
                llm_skills = [s.strip() for s in line[7:].split(',')]
            elif line.startswith('projects:'):
                projects = [p.strip() for p in line[9:].split(',')]
            elif line.startswith('experience:'):
                experience = line[11:].strip()
            elif line.startswith('domain:'):
                domain = line[7:].strip()
    
    # Combine keyword-extracted and LLM-extracted skills
    all_skills = list(set(llm_skills + list(found_skills)))
    
    # Enhanced category mapping
    category_mapping = {
        # Programming Languages
        'python': ['General Programming', 'Data Structures', 'Algorithms', 'Data Science'],
        'javascript': ['General Programming', 'Web Development', 'Frontend'],
        'java': ['General Programming', 'Object-Oriented Programming', 'Data Structures'],
        'cpp': ['General Programming', 'Data Structures', 'Algorithms', 'Low-level Systems'],
        'csharp': ['General Programming', 'Object-Oriented Programming'],
        'php': ['General Programming', 'Web Development', 'Backend'],
        'ruby': ['General Programming', 'Web Development'],
        'go': ['General Programming', 'Backend', 'System Design'],
        'rust': ['General Programming', 'Low-level Systems'],
        'kotlin': ['General Programming', 'Mobile Development'],
        'swift': ['General Programming', 'Mobile Development'],
        'scala': ['General Programming', 'Data Engineering'],
        
        # Web Technologies
        'html': ['Web Development', 'Frontend'],
        'css': ['Web Development', 'Frontend'],
        'react': ['Web Development', 'Frontend', 'JavaScript Frameworks'],
        'angular': ['Web Development', 'Frontend', 'JavaScript Frameworks'],
        'vue': ['Web Development', 'Frontend', 'JavaScript Frameworks'],
        
        # Backend
        'node': ['Backend', 'Web Development', 'Server-side JavaScript'],
        'django': ['Backend', 'Web Development', 'Python Frameworks'],
        'flask': ['Backend', 'Web Development', 'Python Frameworks'],
        'spring': ['Backend', 'Java Frameworks'],
        'laravel': ['Backend', 'Web Development', 'PHP Frameworks'],
        
        # Databases
        'sql': ['Database Systems', 'Data Engineering'],
        'nosql': ['Database Systems', 'Data Engineering', 'System Design'],
        
        # Cloud & DevOps
        'aws': ['Cloud Computing', 'System Design', 'DevOps'],
        'azure': ['Cloud Computing', 'System Design'],
        'gcp': ['Cloud Computing', 'System Design'],
        'docker': ['DevOps', 'System Design', 'Containerization'],
        'terraform': ['DevOps', 'Infrastructure as Code'],
        'jenkins': ['DevOps', 'CI/CD'],
        'git': ['Version Control', 'Software Development'],
        
        # Data Science & ML
        'machine learning': ['Machine Learning', 'Artificial Intelligence', 'Data Science'],
        'data science': ['Data Science', 'Machine Learning', 'Statistics'],
        'deep learning': ['Machine Learning', 'Artificial Intelligence'],
        'nlp': ['Machine Learning', 'Natural Language Processing'],
        
        # Mobile
        'android': ['Mobile Development', 'Android'],
        'ios': ['Mobile Development', 'iOS'],
        'react native': ['Mobile Development', 'Cross-platform'],
        'flutter': ['Mobile Development', 'Cross-platform'],
        
        # Other
        'linux': ['System Administration', 'DevOps'],
        'testing': ['Software Testing', 'Quality Assurance'],
        'security': ['Security', 'Cybersecurity'],
        'api': ['API Design', 'System Design', 'Web Development'],
        'design patterns': ['Software Design', 'Architecture']
    }
    
    categories = set()
    skills_lower = [skill.lower() for skill in all_skills]
    
    for skill in skills_lower:
        for key, cats in category_mapping.items():
            if key in skill or any(keyword in skill for keyword in tech_keywords.get(key, [])):
                categories.update(cats)
    
    # Add domain-specific categories with more precision
    domain_lower = domain.lower()
    if any(word in domain_lower for word in ['data scientist', 'data science', 'machine learning', 'ml', 'ai']):
        categories.update(['Machine Learning', 'Data Science', 'Statistics', 'Data Engineering'])
    elif any(word in domain_lower for word in ['web developer', 'frontend', 'backend', 'full stack', 'fullstack']):
        categories.update(['Web Development', 'System Design', 'API Design'])
    elif 'mobile' in domain_lower or 'ios' in domain_lower or 'android' in domain_lower:
        categories.update(['Mobile Development', 'System Design'])
    elif any(word in domain_lower for word in ['devops', 'infrastructure', 'cloud']):
        categories.update(['DevOps', 'System Design', 'Cloud Computing'])
    elif 'security' in domain_lower:
        categories.update(['Security', 'System Design'])
    
    # Add default categories if none found
    if not categories:
        categories = {'General Programming', 'Algorithms', 'Data Structures'}
    
    return {
        "skills": all_skills,
        "projects": projects,
        "experience": experience,
        "domain": domain,
        "categories": list(categories)
    }

def generate_questions(role: str, resume_analysis: dict, questions_df: pd.DataFrame, kaggle_df: pd.DataFrame) -> list:
    """Generate questions based on role, resume analysis, and Kaggle dataset."""
    
    categories = resume_analysis.get("categories", ["General Programming"])
    experience = resume_analysis.get("experience", "Mid-level")
    skills = resume_analysis.get("skills", [])
    
    # Map experience to difficulty
    difficulty_mapping = {
        "Junior": ["Easy", "Medium"],
        "Mid-level": ["Medium", "Hard"],
        "Senior": ["Medium", "Hard"]
    }
    allowed_difficulties = difficulty_mapping.get(experience, ["Medium", "Hard"])
    
    # Prioritize top categories (limit to most relevant ones)
    # Sort categories by relevance to skills
    skill_category_priority = {
        'python': ['Data Science', 'Machine Learning', 'General Programming'],
        'javascript': ['Web Development', 'Frontend'],
        'react': ['Web Development', 'Frontend'],
        'node': ['Backend', 'Web Development'],
        'java': ['General Programming', 'Object-Oriented Programming'],
        'sql': ['Database Systems'],
        'aws': ['Cloud Computing', 'System Design'],
        'docker': ['DevOps', 'System Design'],
        'machine learning': ['Machine Learning', 'Data Science'],
        'data science': ['Data Science', 'Machine Learning']
    }
    
    # Get top 3 most relevant categories
    prioritized_categories = []
    skills_lower = [skill.lower() for skill in skills]
    
    for skill in skills_lower:
        for key, cats in skill_category_priority.items():
            if key in skill:
                prioritized_categories.extend(cats)
    
    # If we have prioritized categories, use them first, otherwise use all
    if prioritized_categories:
        categories = list(set(prioritized_categories))[:4]  # Limit to 4 categories
    else:
        categories = categories[:4]  # Limit to 4 categories
    
    print(f"Selected categories for question generation: {categories}")
    
    # Filter Kaggle questions with more precise matching
    relevant_questions = []
    question_scores = []  # (question, score) tuples
    
    if not kaggle_df.empty:
        # More precise category mapping
        category_synonyms = {
            "General Programming": ["General Programming"],
            "Data Structures": ["Data Structures"],
            "Algorithms": ["Algorithms"],
            "Web Development": ["Web Development"],
            "Frontend": ["Web Development", "Frontend"],
            "Backend": ["Backend", "Web Development"],
            "Machine Learning": ["Machine Learning", "Artificial Intelligence"],
            "Data Science": ["Data Science", "Machine Learning"],
            "System Design": ["System Design", "Distributed Systems"],
            "Database Systems": ["Database Systems"],
            "DevOps": ["DevOps"],
            "Cloud Computing": ["Cloud Computing"],
            "Security": ["Security"],
            "Mobile Development": ["Mobile Development"],
            "API Design": ["API Design"],
            "Software Testing": ["Software Testing"]
        }
        
        for category in categories:
            # Find exact category matches first
            exact_matches = kaggle_df[
                (kaggle_df['Category'] == category) & 
                (kaggle_df['Difficulty'].isin(allowed_difficulties))
            ]
            
            if not exact_matches.empty:
                for _, row in exact_matches.iterrows():
                    question = row['Question']
                    # Score based on how well it matches the category
                    score = 10 if row['Category'] == category else 5
                    question_scores.append((question, score))
            
            # Then try synonym matches with lower priority
            matching_cats = category_synonyms.get(category, [category])
            synonym_matches = kaggle_df[
                (kaggle_df['Category'].isin(matching_cats)) & 
                (kaggle_df['Difficulty'].isin(allowed_difficulties)) &
                (~kaggle_df['Question'].isin([q for q, _ in question_scores]))  # Avoid duplicates
            ]
            
            if not synonym_matches.empty:
                for _, row in synonym_matches.iterrows():
                    question = row['Question']
                    score = 7  # Lower score for synonym matches
                    question_scores.append((question, score))
    
    # Sort by score and get top questions
    question_scores.sort(key=lambda x: x[1], reverse=True)
    relevant_questions = [q for q, _ in question_scores]
    
    # Remove duplicates while preserving order
    seen = set()
    relevant_questions = [q for q in relevant_questions if not (q in seen or seen.add(q))]
    
    print(f"Found {len(relevant_questions)} relevant questions from Kaggle dataset")
    
    # If not enough questions from Kaggle, supplement with original dataset
    if len(relevant_questions) < 5 and not questions_df.empty:
        role_questions = questions_df[questions_df['role'].str.lower() == role.lower()]['question'].tolist()
        # Filter out questions we already have
        new_questions = [q for q in role_questions if q not in relevant_questions]
        relevant_questions.extend(new_questions)
        print(f"Added {len(new_questions)} questions from original dataset")
    
    # If still not enough, add some targeted general questions based on skills
    if len(relevant_questions) < 5:
        skill_based_questions = []
        
        # Generate skill-specific questions
        for skill in skills_lower:
            if 'python' in skill and 'python' in [s.lower() for s in skills]:
                skill_based_questions.extend([
                    "How do you handle memory management and garbage collection in Python?",
                    "Explain Python's Global Interpreter Lock (GIL) and its implications for concurrent programming.",
                    "What are Python decorators and how do you implement custom decorators?",
                    "How do you optimize Python code for performance?",
                    "Explain the difference between lists, tuples, and dictionaries in Python."
                ])
            elif ('javascript' in skill or 'js' in skill) and any('javascript' in s.lower() or 'js' in s.lower() for s in skills):
                skill_based_questions.extend([
                    "How does JavaScript handle asynchronous operations and what are Promises?",
                    "Explain the difference between var, let, and const in JavaScript.",
                    "How do you handle closures and scope in JavaScript?",
                    "What are the different ways to create objects in JavaScript?",
                    "How does JavaScript's prototype inheritance work?"
                ])
            elif 'react' in skill and 'react' in [s.lower() for s in skills]:
                skill_based_questions.extend([
                    "How do you manage state in a React application?",
                    "Explain the component lifecycle in React and hooks vs class components.",
                    "How do you optimize React application performance?",
                    "What is the virtual DOM in React and how does it work?",
                    "How do you handle forms and user input in React?"
                ])
            elif 'node' in skill and 'node' in [s.lower() for s in skills]:
                skill_based_questions.extend([
                    "How do you handle asynchronous operations in Node.js?",
                    "Explain the event loop in Node.js and how it works.",
                    "How do you scale a Node.js application?",
                    "What are streams in Node.js and how do you use them?",
                    "How do you handle errors and exceptions in Node.js?"
                ])
            elif 'sql' in skill and any('sql' in s.lower() for s in skills):
                skill_based_questions.extend([
                    "How do you optimize database queries for performance?",
                    "Explain the difference between INNER JOIN, LEFT JOIN, and RIGHT JOIN.",
                    "How do you handle database normalization and denormalization?",
                    "What are indexes in databases and how do they improve performance?",
                    "How do you handle database transactions and ACID properties?"
                ])
            elif 'aws' in skill and 'aws' in [s.lower() for s in skills]:
                skill_based_questions.extend([
                    "How do you design for scalability and high availability on AWS?",
                    "Explain the difference between EC2, Lambda, and ECS for compute services.",
                    "How do you implement security best practices on AWS?",
                    "What are the different storage options on AWS and when to use each?",
                    "How do you monitor and troubleshoot applications on AWS?"
                ])
            elif 'docker' in skill and 'docker' in [s.lower() for s in skills]:
                skill_based_questions.extend([
                    "How do you create and manage Docker containers?",
                    "Explain the difference between Docker images and containers.",
                    "How do you orchestrate multiple containers with Docker Compose?",
                    "What are Docker volumes and how do you persist data?",
                    "How do you optimize Docker images for size and security?"
                ])
            elif any(word in skill for word in ['machine learning', 'ml', 'tensorflow', 'pytorch', 'scikit']):
                skill_based_questions.extend([
                    "How do you handle overfitting and underfitting in machine learning models?",
                    "Explain the bias-variance tradeoff in machine learning.",
                    "How do you preprocess data for machine learning algorithms?",
                    "What is cross-validation and why is it important?",
                    "How do you evaluate and compare different machine learning models?"
                ])
            elif 'django' in skill and 'django' in [s.lower() for s in skills]:
                skill_based_questions.extend([
                    "How do you handle database migrations in Django?",
                    "Explain Django's ORM and how to use it effectively.",
                    "How do you implement authentication and authorization in Django?",
                    "What are Django middleware and how do you use them?",
                    "How do you optimize Django application performance?"
                ])
            elif 'flask' in skill and 'flask' in [s.lower() for s in skills]:
                skill_based_questions.extend([
                    "How do you structure a Flask application for scalability?",
                    "Explain how Flask handles routing and URL generation.",
                    "How do you implement authentication in Flask applications?",
                    "What are Flask blueprints and how do you use them?",
                    "How do you handle database connections in Flask?"
                ])
        
        # Remove duplicates and add to relevant questions
        skill_based_questions = [q for q in skill_based_questions if q not in relevant_questions]
        relevant_questions.extend(skill_based_questions)
        print(f"Added {len(skill_based_questions)} skill-specific questions")
    
    # Final fallback to general questions
    if len(relevant_questions) < 3:
        general_questions = [
            "Can you walk me through your problem-solving approach for a complex technical challenge?",
            "How do you stay updated with the latest developments in your field?",
            "Describe a situation where you had to learn a new technology quickly.",
            "How do you approach debugging a complex issue?",
            "What are your thoughts on code quality and best practices?"
        ]
        relevant_questions.extend(general_questions)
    
    # Shuffle and return first 5-7 questions, prioritizing skill-relevant ones
    import random
    
    # Separate skill-specific questions from general ones
    skill_specific = []
    general_questions = []
    
    # First, collect all skill-based questions that were generated
    all_skill_based = []
    for skill in skills_lower:
        if 'python' in skill and 'python' in [s.lower() for s in skills]:
            all_skill_based.extend([
                "How do you handle memory management and garbage collection in Python?",
                "Explain Python's Global Interpreter Lock (GIL) and its implications for concurrent programming.",
                "What are Python decorators and how do you implement custom decorators?",
                "How do you optimize Python code for performance?",
                "Explain the difference between lists, tuples, and dictionaries in Python."
            ])
        elif ('javascript' in skill or 'js' in skill) and any('javascript' in s.lower() or 'js' in s.lower() for s in skills):
            all_skill_based.extend([
                "How does JavaScript handle asynchronous operations and what are Promises?",
                "Explain the difference between var, let, and const in JavaScript.",
                "How do you handle closures and scope in JavaScript?",
                "What are the different ways to create objects in JavaScript?",
                "How does JavaScript's prototype inheritance work?"
            ])
        elif 'react' in skill and 'react' in [s.lower() for s in skills]:
            all_skill_based.extend([
                "How do you manage state in a React application?",
                "Explain the component lifecycle in React and hooks vs class components.",
                "How do you optimize React application performance?",
                "What is the virtual DOM in React and how does it work?",
                "How do you handle forms and user input in React?"
            ])
        elif 'node' in skill and 'node' in [s.lower() for s in skills]:
            all_skill_based.extend([
                "How do you handle asynchronous operations in Node.js?",
                "Explain the event loop in Node.js and how it works.",
                "How do you scale a Node.js application?",
                "What are streams in Node.js and how do you use them?",
                "How do you handle errors and exceptions in Node.js?"
            ])
        elif 'sql' in skill and any('sql' in s.lower() for s in skills):
            all_skill_based.extend([
                "How do you optimize database queries for performance?",
                "Explain the difference between INNER JOIN, LEFT JOIN, and RIGHT JOIN.",
                "How do you handle database normalization and denormalization?",
                "What are indexes in databases and how do they improve performance?",
                "How do you handle database transactions and ACID properties?"
            ])
        elif 'aws' in skill and 'aws' in [s.lower() for s in skills]:
            all_skill_based.extend([
                "How do you design for scalability and high availability on AWS?",
                "Explain the difference between EC2, Lambda, and ECS for compute services.",
                "How do you implement security best practices on AWS?",
                "What are the different storage options on AWS and when to use each?",
                "How do you monitor and troubleshoot applications on AWS?"
            ])
        elif 'docker' in skill and 'docker' in [s.lower() for s in skills]:
            all_skill_based.extend([
                "How do you create and manage Docker containers?",
                "Explain the difference between Docker images and containers.",
                "How do you orchestrate multiple containers with Docker Compose?",
                "What are Docker volumes and how do you persist data?",
                "How do you optimize Docker images for size and security?"
            ])
        elif any(word in skill for word in ['machine learning', 'ml', 'tensorflow', 'pytorch', 'scikit']):
            all_skill_based.extend([
                "How do you handle overfitting and underfitting in machine learning models?",
                "Explain the bias-variance tradeoff in machine learning.",
                "How do you preprocess data for machine learning algorithms?",
                "What is cross-validation and why is it important?",
                "How do you evaluate and compare different machine learning models?"
            ])
        elif 'django' in skill and 'django' in [s.lower() for s in skills]:
            all_skill_based.extend([
                "How do you handle database migrations in Django?",
                "Explain Django's ORM and how to use it effectively.",
                "How do you implement authentication and authorization in Django?",
                "What are Django middleware and how do you use them?",
                "How do you optimize Django application performance?"
            ])
        elif 'flask' in skill and 'flask' in [s.lower() for s in skills]:
            all_skill_based.extend([
                "How do you structure a Flask application for scalability?",
                "Explain how Flask handles routing and URL generation.",
                "How do you implement authentication in Flask applications?",
                "What are Flask blueprints and how do you use them?",
                "How do you handle database connections in Flask?"
            ])
    
    # Remove duplicates from skill-based questions
    all_skill_based = list(set(all_skill_based))
    skill_specific.extend(all_skill_based)
    
    # Now check the remaining questions from Kaggle dataset
    for q in relevant_questions:
        if q not in skill_specific:  # Don't double-count
            q_lower = q.lower()
            is_skill_specific = False
            for skill in skills_lower:
                # Check for specific technology mentions
                if skill in q_lower and len(skill) > 3:  # Avoid matching short words
                    skill_specific.append(q)
                    is_skill_specific = True
                    break
            if not is_skill_specific:
                general_questions.append(q)
    
    # Prioritize skill-specific questions, then add general ones
    final_questions = skill_specific + general_questions
    random.shuffle(final_questions)
    
    # Ensure we have at least 5 questions, but no more than 7
    selected_questions = final_questions[:7]
    if len(selected_questions) < 5 and len(final_questions) >= 5:
        selected_questions = final_questions[:5]
    
    print(f"Selected {len(skill_specific)} skill-specific and {len(general_questions)} general questions")
    print(f"Final selection: {len(selected_questions)} questions")
    
    return selected_questions

def evaluate_answer(question: str, user_answer: str, reference_answer: str) -> dict:
    """Evaluate user answer using LLM and reference."""
    prompt = f"""Rate this answer 1-10:
Q: {question}
User: {user_answer[:200]}
Ref: {reference_answer[:200]}

Give score and brief feedback (50 words max)."""
    
    response = call_llm(prompt)
    import json
    import random
    
    try:
        if response.strip().startswith('{'):
            data = json.loads(response)
            return {
                "score": int(data.get("score", 6)),
                "feedback": str(data.get("feedback", "Good response")),
                "strengths": str(data.get("strengths", "Clear communication")),
                "weaknesses": str(data.get("weaknesses", "Could be more detailed"))
            }
    except:
        pass
    
    # Default score
    score = random.randint(6, 8)
    return {
        "score": score,
        "feedback": "Good response. Could add more details.",
        "strengths": "Clear explanation",
        "weaknesses": "Consider providing examples"
    }

def generate_first_question(role: str, analysis: dict) -> str:
    """Generate the first interview question based on role and resume analysis."""
    skills = analysis.get("skills", ["general skills"])
    experience = analysis.get("experience", "relevant experience")
    
    prompt = f"""Generate a natural, conversational first question for a {role} interview.
    
Candidate background:
- Skills: {', '.join(skills[:3])}
- Experience: {experience[:100]}

Make it engaging and relevant to their background. Keep it under 20 words."""
    
    response = call_llm(prompt)
    if response and len(response.strip()) > 10:
        return response.strip()
    return f"Tell me about your experience as a {role} and what interests you about this role."

def interviewer_agent(role: str, history: list, latest_answer: str, analysis: dict = None) -> str:
    """Generate the next adaptive interviewer question from role and conversation history."""
    analysis = analysis or {}
    level = analysis.get("experience", "")

    recent_turns = history[-6:] if history else []
    history_text = "\n".join([
        f"Q: {turn.get('question', '')}\nA: {turn.get('answer', '')}"
        for turn in recent_turns
    ])

    prompt = f"""You are a professional technical interviewer.

ROLE: {role}
LEVEL: {level}

Your job:
- Ask questions based on the role
- Adapt based on candidate answers
- Go deeper if answer is good
- Ask easier if answer is weak
- Keep interview natural and human-like

Conversation so far:
{history_text}

Candidate's latest answer:
{latest_answer[:500]}

Now decide:
1. Evaluate the answer internally
2. Ask the next best question

IMPORTANT RULES:
- Ask only one question
- Do not give explanation
- Do not repeat prior questions
- Keep it relevant to the role
- Keep it under 25 words

Return only the question text."""

    response = (call_llm(prompt) or "").strip()
    cleaned = response.split("\n")[0].strip().strip('"').strip("'")
    if cleaned and cleaned != "{}" and "?" in cleaned:
        return cleaned

    return "Can you explain your approach with one concrete example?"

def generate_final_feedback(chat_history: list, role: str) -> str:
    """Generate comprehensive final feedback based on the entire interview conversation."""
    
    # Extract questions and answers
    conversation_text = ""
    for item in chat_history:
        if item["type"] == "question":
            conversation_text += f"Q: {item['content']}\n"
        elif item["type"] == "answer":
            conversation_text += f"A: {item['content']}\n"
    
    prompt = f"""Provide comprehensive feedback for a {role} interview based on this conversation:

{conversation_text[:1000]}

Structure your feedback as:
1. Overall assessment (2-3 sentences)
2. Key strengths (3-4 points)
3. Areas for improvement (3-4 points)  
4. Recommendations for preparation (2-3 points)
5. Final thoughts (1 sentence)

Keep it constructive, specific, and encouraging."""
    
    response = call_llm(prompt)
    if response and len(response.strip()) > 50:
        return response.strip()
    
    return f"""Thank you for completing the {role} interview. You demonstrated good communication skills and relevant experience. Keep practicing technical questions and behavioral scenarios. Consider preparing specific examples from your work experience. Overall, you show promise for the role - continue building your skills and confidence."""