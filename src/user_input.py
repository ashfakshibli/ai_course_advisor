# ai_course_advisor/src/user_input.py
from typing import Dict, List, Any, Optional
import re

class UserProfileProcessor:
    """
    Handles collection and processing of user input for the Course Advisor.
    Validates and structures user information for the recommendation system.
    """
    
    def __init__(self):
        self.valid_education_levels = [
            "1st year", "first year", "freshman",
            "2nd year", "second year", "sophomore", 
            "3rd year", "third year", "junior",
            "4th year", "fourth year", "senior",
            "graduate", "grad", "masters", "phd"
        ]
        
        self.common_interests = [
            "business", "science", "technology", "medicine", "nursing", "education",
            "music", "art", "psychology", "history", "literature", "mathematics",
            "computer science", "biology", "chemistry", "physics", "economics",
            "communications", "religion", "philosophy", "sociology", "political science"
        ]
        
        self.career_categories = {
            "healthcare": ["doctor", "physician", "nurse", "therapist", "pharmacist", "dentist"],
            "education": ["teacher", "professor", "counselor", "administrator", "tutor"],
            "business": ["manager", "entrepreneur", "consultant", "analyst", "accountant"],
            "technology": ["software engineer", "developer", "data scientist", "analyst", "programmer"],
            "creative": ["artist", "musician", "writer", "designer", "photographer"],
            "law": ["lawyer", "attorney", "judge", "paralegal"],
            "research": ["researcher", "scientist", "analyst", "academic"]
        }
    
    def process_user_input(self, raw_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and validate user input into a structured profile.
        
        Args:
            raw_input: Dictionary with user responses
                - education_level: str
                - interests: str or List[str] 
                - career_goal: str (optional)
                - additional_info: str (optional)
        
        Returns:
            Processed user profile dictionary
        """
        profile = {
            'education_level': self._process_education_level(raw_input.get('education_level', '')),
            'interests': self._process_interests(raw_input.get('interests', [])),
            'career_goal': self._process_career_goal(raw_input.get('career_goal', '')),
            'preferred_categories': self._derive_categories_from_interests(raw_input.get('interests', [])),
            'additional_info': raw_input.get('additional_info', '').strip()
        }
        
        return profile
    
    def _process_education_level(self, level_input: str) -> str:
        """Normalize and validate education level input."""
        if not level_input:
            return ""
        
        level_clean = level_input.lower().strip()
        
        # Direct mapping for common variations
        level_map = {
            "freshman": "1st year",
            "first year": "1st year", 
            "1": "1st year",
            "1st": "1st year",
            "sophomore": "2nd year",
            "second year": "2nd year",
            "2": "2nd year", 
            "2nd": "2nd year",
            "junior": "3rd year",
            "third year": "3rd year",
            "3": "3rd year",
            "3rd": "3rd year", 
            "senior": "4th year",
            "fourth year": "4th year",
            "4": "4th year",
            "4th": "4th year",
            "graduate": "graduate",
            "grad": "graduate",
            "masters": "graduate",
            "master's": "graduate",
            "phd": "graduate",
            "doctoral": "graduate"
        }
        
        return level_map.get(level_clean, level_input)
    
    def _process_interests(self, interests_input) -> List[str]:
        """Process and clean interests input."""
        if isinstance(interests_input, str):
            # Split by common delimiters
            interests = re.split(r'[,;]|\sand\s', interests_input.lower())
            interests = [interest.strip() for interest in interests if interest.strip()]
        elif isinstance(interests_input, list):
            # Handle checkbox-style interests - keep original case
            interests = [str(interest).strip() for interest in interests_input if str(interest).strip()]
        else:
            return []
        
        # Clean and validate interests
        cleaned_interests = []
        for interest in interests:
            # For checkbox inputs, preserve the original format
            if isinstance(interests_input, list):
                cleaned_interests.append(interest)
            else:
                # Remove extra whitespace and common prefixes for text input
                interest = re.sub(r'^(i like|i love|i enjoy|i am interested in|interested in)\s+', '', interest.lower())
                interest = interest.strip()
                
                if len(interest) > 1:  # Avoid single characters
                    cleaned_interests.append(interest)
        
        return cleaned_interests[:15]  # Allow more interests for checkbox format
    
    def _process_career_goal(self, career_input: str) -> str:
        """Clean and normalize career goal input."""
        if not career_input:
            return ""
        
        career_clean = career_input.lower().strip()
        
        # Remove common prefixes
        prefixes_to_remove = [
            "i want to be a", "i want to be an", "i want to become a", "i want to become an",
            "i would like to be a", "i would like to be an", "becoming a", "becoming an",
            "my goal is to be a", "my goal is to be an", "i plan to be a", "i plan to be an"
        ]
        
        for prefix in prefixes_to_remove:
            if career_clean.startswith(prefix):
                career_clean = career_clean[len(prefix):].strip()
                break
        
        return career_clean
    
    def _derive_categories_from_interests(self, interests_input) -> List[str]:
        """Derive academic categories from user interests."""
        interests = self._process_interests(interests_input)
        categories = []
        
        category_keywords = {
            "Business": ["business", "management", "marketing", "finance", "economics", "entrepreneurship"],
            "Natural Sciences": ["science", "biology", "chemistry", "physics", "environmental"],
            "Computer Science": ["computer", "programming", "technology", "coding", "software", "data"],
            "Health Sciences": ["health", "medicine", "medical", "nursing", "pharmacy", "therapy"],
            "Social Sciences": ["psychology", "sociology", "anthropology", "political", "social work"],
            "Humanities": ["history", "literature", "philosophy", "languages", "cultural studies"],
            "Fine Arts": ["art", "creative", "visual", "painting", "drawing", "design"],
            "Music": ["music", "musical", "instrument", "singing", "composition"],
            "Education": ["education", "teaching", "children", "learning", "classroom"],
            "Mathematics": ["math", "statistics", "calculus", "algebra", "numbers"],
            "Communications": ["communication", "media", "journalism", "writing", "public relations"]
        }
        
        for interest in interests:
            for category, keywords in category_keywords.items():
                if any(keyword in interest for keyword in keywords):
                    if category not in categories:
                        categories.append(category)
        
        return categories
    
    def validate_profile(self, profile: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Validate user profile and return any issues found.
        
        Returns:
            Dictionary with validation results:
                - 'errors': List of error messages
                - 'warnings': List of warning messages
        """
        errors = []
        warnings = []
        
        # Check education level
        if not profile.get('education_level'):
            warnings.append("Education level not specified. Recommendations will include all levels.")
        
        # Check interests
        interests = profile.get('interests', [])
        if not interests:
            warnings.append("No interests specified. Consider adding some to get better recommendations.")
        elif len(interests) > 10:
            warnings.append("Many interests specified. Consider focusing on your top priorities.")
        
        # Check career goal
        if not profile.get('career_goal'):
            warnings.append("Career goal not specified. Adding one can help tailor recommendations.")
        
        return {'errors': errors, 'warnings': warnings}
    
    def create_profile_summary(self, profile: Dict[str, Any]) -> str:
        """Create a human-readable summary of the user profile."""
        summary_parts = []
        
        # Education level
        level = profile.get('education_level', '')
        if level:
            summary_parts.append(f"Education Level: {level.title()}")
        
        # Interests 
        interests = profile.get('interests', [])
        if interests:
            interests_str = ", ".join(interests[:5])  # Show first 5
            if len(interests) > 5:
                interests_str += f" (and {len(interests) - 5} more)"
            summary_parts.append(f"Interests: {interests_str}")
        
        # Career goal
        career = profile.get('career_goal', '')
        if career:
            summary_parts.append(f"Career Goal: {career.title()}")
        
        # Additional info
        additional = profile.get('additional_info', '')
        if additional and len(additional) > 10:
            summary_parts.append(f"Additional Notes: {additional[:100]}...")
        
        return "\n".join(summary_parts) if summary_parts else "Profile information not provided"
    
    def suggest_missing_info(self, profile: Dict[str, Any]) -> List[str]:
        """Suggest what information might help improve recommendations."""
        suggestions = []
        
        if not profile.get('education_level'):
            suggestions.append("Adding your current education level (freshman, sophomore, etc.) will help us recommend appropriate courses.")
        
        if not profile.get('interests'):
            suggestions.append("Sharing your academic interests will help us find courses you'll enjoy.")
        
        if not profile.get('career_goal'):
            suggestions.append("Mentioning your career goals can help us recommend courses that support your future plans.")
        
        return suggestions
    
    @staticmethod
    def get_sample_inputs() -> Dict[str, Any]:
        """Return sample input for testing purposes."""
        return {
            'education_level': '2nd year',
            'interests': ['computer science', 'business', 'data analysis'],
            'career_goal': 'software engineer',
            'additional_info': 'I am particularly interested in artificial intelligence and machine learning applications in business.'
        }