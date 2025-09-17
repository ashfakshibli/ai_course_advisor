# ai_course_advisor/src/rag_system.py
import json
import os
from typing import List, Dict, Any
from difflib import SequenceMatcher

class CourseRAG:
    """
    Retrieval-Augmented Generation system for university course recommendations.
    Handles course catalog loading, searching, and filtering based on user criteria.
    """
    
    def __init__(self, catalog_path: str = None):
        if catalog_path is None:
            # Default path relative to the src directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            catalog_path = os.path.join(os.path.dirname(current_dir), 'data', 'course_catalog.json')
        
        self.catalog_path = catalog_path
        self.courses = self.load_course_catalog()
    
    def load_course_catalog(self) -> List[Dict[str, Any]]:
        """Load course catalog from JSON file."""
        try:
            with open(self.catalog_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return data.get('courses', [])
        except FileNotFoundError:
            print(f"Course catalog file not found at {self.catalog_path}")
            return []
        except json.JSONDecodeError:
            print(f"Invalid JSON in course catalog file: {self.catalog_path}")
            return []
    
    def search_courses_by_level(self, level: str) -> List[Dict[str, Any]]:
        """Filter courses by education level (1st year, 2nd year, 3rd year, graduate)."""
        level_map = {
            "freshman": "1st year",
            "first year": "1st year",
            "1st year": "1st year",
            "sophomore": "2nd year", 
            "second year": "2nd year",
            "2nd year": "2nd year",
            "junior": "3rd year",
            "third year": "3rd year", 
            "3rd year": "3rd year",
            "senior": "4th year",
            "fourth year": "4th year",
            "4th year": "4th year",
            "graduate": "graduate",
            "grad": "graduate",
            "masters": "graduate",
            "phd": "graduate"
        }
        
        normalized_level = level_map.get(level.lower(), level)
        return [course for course in self.courses if course.get('level', '').lower() == normalized_level.lower()]
    
    def search_courses_by_keywords(self, keywords: List[str], max_results: int = 10) -> List[Dict[str, Any]]:
        """Search courses by keywords in title, description, and keywords fields."""
        scored_courses = []
        
        # Mapping for checkbox-style interests to course-relevant keywords
        interest_mapping = {
            'AI/ML': ['artificial intelligence', 'machine learning', 'data science', 'computer science'],
            'Web Dev': ['web', 'programming', 'computer science', 'development'],
            'Security': ['security', 'computer science', 'networking'],
            'Data Science': ['data', 'statistics', 'mathematics', 'computer science', 'analysis'],
            'Mobile Dev': ['mobile', 'programming', 'computer science', 'development'],
            'Game Dev': ['game', 'programming', 'computer science', 'development'],
            'Entrepreneurship': ['business', 'entrepreneurship', 'management'],
            'Management': ['business', 'management', 'leadership'],
            'Business Strategy': ['business', 'strategy', 'management'],
            'Finance/Accounting': ['finance', 'accounting', 'business', 'economics'],
            'Biology/Biotech': ['biology', 'science', 'biotechnology'],
            'Chemistry': ['chemistry', 'science'],
            'Mathematics': ['mathematics', 'statistics', 'calculus'],
            'Physics': ['physics', 'science'],
            'Nursing': ['nursing', 'healthcare', 'medical'],
            'Healthcare': ['healthcare', 'medical', 'health'],
            'Psychology': ['psychology', 'social', 'behavior'],
            'Communication': ['communication', 'media', 'writing'],
            'Education': ['education', 'teaching', 'learning'],
            'History/Humanities': ['history', 'humanities', 'literature'],
            'UI/UX Design': ['design', 'art', 'creative', 'computer'],
            'Music': ['music', 'performance', 'creative'],
            'Visual Arts': ['art', 'visual', 'creative', 'design'],
            'Theatre Arts': ['theatre', 'performance', 'art', 'creative']
        }
        
        # Expand keywords using the mapping
        expanded_keywords = []
        for keyword in keywords:
            expanded_keywords.append(keyword.lower())
            if keyword in interest_mapping:
                expanded_keywords.extend(interest_mapping[keyword])
        
        for course in self.courses:
            score = 0
            search_text = " ".join([
                course.get('title', '').lower(),
                course.get('description', '').lower(),
                course.get('category', '').lower(),
                " ".join(course.get('keywords', [])).lower()
            ])
            
            for keyword in expanded_keywords:
                keyword = keyword.lower().strip()
                if keyword in search_text:
                    # Boost score for exact matches in title
                    if keyword in course.get('title', '').lower():
                        score += 3
                    # Medium score for description matches
                    elif keyword in course.get('description', '').lower():
                        score += 2
                    # Lower score for keyword matches
                    else:
                        score += 1
            
            if score > 0:
                scored_courses.append((course, score))
        
        # Sort by score descending and return top results
        scored_courses.sort(key=lambda x: x[1], reverse=True)
        return [course for course, score in scored_courses[:max_results]]
    
    def search_courses_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Filter courses by category/field of study."""
        category_map = {
            "business": ["Business", "MBA"],
            "science": ["Natural Sciences", "Computer Science"],
            "computer science": ["Computer Science"],
            "cs": ["Computer Science"],
            "programming": ["Computer Science"],
            "health": ["Health Sciences", "Nursing"],
            "nursing": ["Nursing"],
            "medical": ["Health Sciences"],
            "medicine": ["Health Sciences"],
            "education": ["Education"],
            "teaching": ["Education"],
            "music": ["Music"],
            "art": ["Fine Arts"],
            "english": ["Humanities"],
            "literature": ["Humanities"],
            "history": ["Humanities"],
            "psychology": ["Social Sciences"],
            "math": ["Mathematics"],
            "mathematics": ["Mathematics"],
            "religion": ["Religion"],
            "communications": ["Communications"]
        }
        
        target_categories = category_map.get(category.lower(), [category])
        return [course for course in self.courses 
                if any(cat.lower() in course.get('category', '').lower() 
                      for cat in target_categories)]
    
    def search_courses_by_career_goal(self, career_goal: str) -> List[Dict[str, Any]]:
        """Recommend courses based on career goals."""
        career_keywords = {
            "doctor": ["biology", "chemistry", "anatomy", "physiology", "pre-med", "medical", "health"],
            "physician": ["biology", "chemistry", "anatomy", "physiology", "pre-med", "medical", "health"],
            "nurse": ["nursing", "anatomy", "physiology", "healthcare", "patient care", "medical"],
            "teacher": ["education", "psychology", "classroom management", "learning", "teaching"],
            "business": ["business", "management", "marketing", "finance", "entrepreneurship"],
            "entrepreneur": ["business", "management", "marketing", "finance", "entrepreneurship"],
            "software engineer": ["computer science", "programming", "algorithms", "data structures"],
            "programmer": ["computer science", "programming", "algorithms", "data structures"], 
            "data scientist": ["statistics", "computer science", "mathematics", "data analysis"],
            "musician": ["music", "performance", "theory", "composition"],
            "artist": ["art", "studio", "creative", "visual arts"],
            "lawyer": ["english", "communication", "history", "critical thinking"],
            "researcher": ["research methods", "statistics", "methodology", "analysis"],
            "counselor": ["psychology", "developmental", "behavior", "social"],
            "therapist": ["psychology", "developmental", "behavior", "social"]
        }
        
        keywords = []
        for goal_key, goal_keywords in career_keywords.items():
            if goal_key.lower() in career_goal.lower():
                keywords.extend(goal_keywords)
        
        if not keywords:
            # If no specific career match, use the career goal as keywords
            keywords = career_goal.lower().split()
        
        return self.search_courses_by_keywords(keywords)
    
    def get_recommended_courses(self, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get course recommendations based on comprehensive user profile.
        
        Args:
            user_profile: Dictionary containing:
                - education_level: str (e.g., "1st year", "graduate")
                - interests: List[str] 
                - career_goal: str (optional)
                - preferred_categories: List[str] (optional)
        """
        recommended_courses = []
        
        # 1. Filter by education level first
        level = user_profile.get('education_level', '')
        if level:
            level_courses = self.search_courses_by_level(level)
        else:
            level_courses = self.courses
        
        # 2. Get courses by interests
        interests = user_profile.get('interests', [])
        if interests:
            interest_courses = []
            for interest in interests:
                interest_matches = self.search_courses_by_keywords([interest], max_results=5)
                interest_courses.extend(interest_matches)
        else:
            interest_courses = level_courses
        
        # 3. Get courses by career goal
        career_goal = user_profile.get('career_goal', '')
        if career_goal:
            career_courses = self.search_courses_by_career_goal(career_goal)
        else:
            career_courses = []
        
        # 4. Get courses by preferred categories
        categories = user_profile.get('preferred_categories', [])
        category_courses = []
        for category in categories:
            category_matches = self.search_courses_by_category(category)
            category_courses.extend(category_matches)
        
        # Combine all results, prioritizing career and interest matches
        all_courses = career_courses + interest_courses + category_courses
        
        # Remove duplicates while preserving order (priority)
        seen_ids = set()
        unique_courses = []
        for course in all_courses:
            if course['id'] not in seen_ids and course in level_courses:
                seen_ids.add(course['id'])
                unique_courses.append(course)
        
        # If we still don't have enough courses, add some general level-appropriate courses
        if len(unique_courses) < 8:
            for course in level_courses:
                if course['id'] not in seen_ids and len(unique_courses) < 12:
                    unique_courses.append(course)
                    seen_ids.add(course['id'])
        
        return unique_courses[:12]  # Return top 12 recommendations
    
    def get_course_by_id(self, course_id: str) -> Dict[str, Any]:
        """Get a specific course by its ID."""
        for course in self.courses:
            if course['id'] == course_id:
                return course
        return {}
    
    def get_courses_by_semester(self, semester: str) -> List[Dict[str, Any]]:
        """Filter courses by semester availability."""
        return [course for course in self.courses 
                if semester.lower() in [s.lower() for s in course.get('semesters', [])]]
    
    def format_course_for_llm(self, course: Dict[str, Any]) -> str:
        """Format course information for LLM consumption."""
        return f"""
Course: {course.get('title', 'N/A')} ({course.get('id', 'N/A')})
Level: {course.get('level', 'N/A')}
Category: {course.get('category', 'N/A')}
Credits: {course.get('credits', 'N/A')}
Description: {course.get('description', 'N/A')}
Prerequisites: {course.get('prerequisites', 'None')}
Available: {', '.join(course.get('semesters', []))}
"""

    def get_context_for_llm(self, recommended_courses: List[Dict[str, Any]]) -> str:
        """Format multiple courses as context for LLM."""
        if not recommended_courses:
            return "No courses found matching the criteria."
        
        context = "Here are the recommended courses:\n\n"
        for i, course in enumerate(recommended_courses, 1):
            context += f"{i}. {self.format_course_for_llm(course)}\n"
        
        return context