from flask import Flask, jsonify, request
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from datetime import datetime
import json

app = Flask(__name__)

class PersonalizedLearningPlatform:
    def __init__(self):
        self.courses = []
        self.users = {}
        self.user_progress = {}
        self.vectorizer = TfidfVectorizer()
        self._initialize_sample_courses()

    def _initialize_sample_courses(self):
        sample_courses = [
            {
                "id": 1,
                "name": "Introduction to Python",
                "description": "Learn the basics of Python programming language, including variables, loops, and functions",
                "difficulty": "beginner",
                "topics": ["programming", "python", "computer science"],
                "modules": [
                    {"id": 1, "title": "Variables and Data Types", "duration": 30},
                    {"id": 2, "title": "Control Flow", "duration": 45},
                    {"id": 3, "title": "Functions", "duration": 40}
                ]
            },
            {
                "id": 2,
                "name": "Machine Learning Fundamentals",
                "description": "Understanding core concepts of machine learning, AI, and data analysis",
                "difficulty": "intermediate",
                "topics": ["AI", "machine learning", "data science"],
                "modules": [
                    {"id": 1, "title": "Introduction to ML", "duration": 45},
                    {"id": 2, "title": "Supervised Learning", "duration": 60},
                    {"id": 3, "title": "Model Evaluation", "duration": 45}
                ]
            },
            {
                "id": 3,
                "name": "Web Development Basics",
                "description": "Learn HTML, CSS, and JavaScript fundamentals for web development",
                "difficulty": "beginner",
                "topics": ["web development", "HTML", "CSS", "JavaScript"],
                "modules": [
                    {"id": 1, "title": "HTML Basics", "duration": 30},
                    {"id": 2, "title": "CSS Styling", "duration": 45},
                    {"id": 3, "title": "JavaScript Fundamentals", "duration": 60}
                ]
            }
        ]
        self.courses.extend(sample_courses)
        self._process_courses()

    def _process_courses(self):
        descriptions = [course["description"] for course in self.courses]
        self.tfidf_matrix = self.vectorizer.fit_transform(descriptions)

    def register_user(self, user_id, interests, learning_style):
        """Register a new user with their interests and learning style."""
        self.users[user_id] = {
            "interests": interests,
            "learning_style": learning_style,
            "registered_date": datetime.now().isoformat()
        }
        self.user_progress[user_id] = {}
        return self.users[user_id]

    def recommend_courses(self, user_id, top_n=2):
        """Recommend courses based on user interests."""
        if user_id not in self.users:
            return []
        
        user_interests = self.users[user_id]["interests"]
        user_vector = self.vectorizer.transform([user_interests])
        similarities = cosine_similarity(user_vector, self.tfidf_matrix)
        top_indices = similarities.argsort()[0][::-1][:top_n]
        
        recommendations = []
        for idx in top_indices:
            course = self.courses[idx].copy()
            if user_id in self.user_progress and course["id"] in self.user_progress[user_id]:
                course["progress"] = self.user_progress[user_id][course["id"]]
            else:
                course["progress"] = 0
            recommendations.append(course)
        
        return recommendations

    def update_progress(self, user_id, course_id, module_id, progress):
        """Update user's progress in a specific course module."""
        if user_id not in self.user_progress:
            self.user_progress[user_id] = {}
        
        if course_id not in self.user_progress[user_id]:
            self.user_progress[user_id][course_id] = {
                "overall_progress": 0,
                "modules": {}
            }
        
        self.user_progress[user_id][course_id]["modules"][module_id] = progress
        
        # Calculate overall progress
        course = next((c for c in self.courses if c["id"] == course_id), None)
        if course:
            total_modules = len(course["modules"])
            completed_modules = sum(1 for p in self.user_progress[user_id][course_id]["modules"].values() if p == 100)
            overall_progress = (completed_modules / total_modules) * 100
            self.user_progress[user_id][course_id]["overall_progress"] = overall_progress
        
        return self.user_progress[user_id][course_id]

# Initialize the platform
platform = PersonalizedLearningPlatform()

@app.route('/users', methods=['POST'])
def register_user():
    data = request.get_json()
    user_id = data.get('user_id')
    interests = data.get('interests')
    learning_style = data.get('learning_style')
    
    if not all([user_id, interests, learning_style]):
        return jsonify({"error": "Missing required fields"}), 400
    
    user = platform.register_user(user_id, interests, learning_style)
    return jsonify({"message": "User registered successfully", "user": user})

@app.route('/users/<user_id>/recommendations', methods=['GET'])
def get_recommendations(user_id):
    recommendations = platform.recommend_courses(user_id)
    return jsonify({"recommendations": recommendations})

@app.route('/users/<user_id>/progress', methods=['POST'])
def update_user_progress(user_id):
    data = request.get_json()
    course_id = data.get('course_id')
    module_id = data.get('module_id')
    progress = data.get('progress')
    
    if not all([course_id, module_id, progress is not None]):
        return jsonify({"error": "Missing required fields"}), 400
    
    updated_progress = platform.update_progress(user_id, course_id, module_id, progress)
    return jsonify({"message": "Progress updated successfully", "progress": updated_progress})

@app.route('/courses', methods=['GET'])
def get_courses():
    return jsonify({"courses": platform.courses})

if __name__ == '__main__':
    app.run(debug=True)
