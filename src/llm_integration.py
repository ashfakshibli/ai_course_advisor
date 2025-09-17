# ai_course_advisor/src/llm_integration.py
import os
from typing import List, Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv
from rag_system import CourseRAG

# Load environment variables
load_dotenv()

class AICourseAdvisor:
    """
    AI Course Advisor using Google Gemini for any university.
    Integrates RAG system for course recommendations with LLM for explanations.
    """
    
    def __init__(self):
        try:
            # Configure Gemini API
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.chat = self.model.start_chat(history=[])
            
            # Initialize RAG system
            self.rag_system = CourseRAG()
            
            # Set up system context
            self.system_context = """
            You are an expert academic advisor. Your role is to help students 
            select appropriate courses for Spring 2026 based on their education level, interests, and career goals.
            
            Key responsibilities:
            1. Provide personalized course recommendations
            2. Explain why specific courses are beneficial for the student's goals
            3. Consider prerequisites and course sequencing
            4. Offer guidance on academic planning and career preparation
            5. Be encouraging and supportive while being realistic about academic requirements
            
            Always be helpful, informative, and maintain a friendly, professional tone.
            Focus on how courses connect to the student's interests and career aspirations.
            
            IMPORTANT: When displaying the student's profile summary, preserve the exact formatting 
            and capitalization provided, especially for education levels (e.g., "1st Year (Freshman)", 
            "2nd Year (Sophomore)"). Do not change the capitalization or format of these terms.
            """
            
        except Exception as e:
            print(f"Error initializing AICourseAdvisor: {e}")
            self.chat = None
            self.rag_system = None
    
    def get_course_recommendations(self, user_profile: Dict[str, Any]) -> str:
        """
        Generate course recommendations based on user profile.
        
        Args:
            user_profile: Dictionary containing user information:
                - education_level: str
                - interests: List[str]
                - career_goal: str (optional)
                - preferred_categories: List[str] (optional)
                - additional_info: str (optional)
        """
        if not self.chat or not self.rag_system:
            return "I'm sorry, the course advisor system is not available right now."
        
        try:
            # Get relevant courses
            course_context = self.rag_system.get_relevant_courses_context(user_profile)
            
            # Create recommendation prompt
            prompt = self._create_recommendation_prompt(user_profile, course_context)
            
            print(f"\n{'='*60}")
            print("DEBUG: FULL PROMPT SENT TO GEMINI:")
            print(f"{'='*60}")
            print(prompt)
            print(f"{'='*60}")
            
            # Generate recommendation using Gemini
            response = self.model.generate_content(prompt)
            
            print(f"\n{'='*60}")
            print("DEBUG: RAW GEMINI RESPONSE:")
            print(f"{'='*60}")
            print(repr(response.text))  # Use repr to see exact characters
            print(f"{'='*60}")
            print("DEBUG: FORMATTED GEMINI RESPONSE:")
            print(f"{'='*60}")
            print(response.text)
            print(f"{'='*60}")
            
            return response.text
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return "I encountered an error while generating your course recommendations. Please try again."
    
    def _format_education_level(self, education_level: str) -> str:
        """Format education level for proper display."""
        print(f"DEBUG: _format_education_level called with: '{education_level}' (type: {type(education_level)})")
        
        if not education_level or education_level == 'Not specified':
            print("DEBUG: Returning 'Not specified'")
            return 'Not specified'
        
        # Mapping for proper display format
        level_mappings = {
            '1st year': '1st Year (Freshman)',
            '2nd year': '2nd Year (Sophomore)', 
            '3rd year': '3rd Year (Junior)',
            '4th year': '4th Year (Senior)',
            'graduate': 'Graduate Student'
        }
        
        lower_level = education_level.lower()
        print(f"DEBUG: Lowercased input: '{lower_level}'")
        print(f"DEBUG: Available mappings: {list(level_mappings.keys())}")
        
        if lower_level in level_mappings:
            result = level_mappings[lower_level]
            print(f"DEBUG: Found mapping: '{lower_level}' -> '{result}'")
            return result
        else:
            result = education_level.title()
            print(f"DEBUG: No mapping found, using title case: '{education_level}' -> '{result}'")
            return result
    
    def _create_recommendation_prompt(self, user_profile: Dict[str, Any], course_context: str) -> str:
        """Create a detailed prompt for course recommendations."""
        
        education_level = user_profile.get('education_level', 'Not specified')
        formatted_education_level = self._format_education_level(education_level)
        interests = user_profile.get('interests', [])
        career_goal = user_profile.get('career_goal', 'Not specified')
        additional_info = user_profile.get('additional_info', '')
        
        # Debug logging
        print(f"DEBUG: Original education_level: '{education_level}'")
        print(f"DEBUG: Formatted education_level: '{formatted_education_level}'")
        
        interests_str = ', '.join(interests) if interests else 'Not specified'
        
        prompt = f"""
        {self.system_context}
        
        STUDENT PROFILE:
        - Education Level: {formatted_education_level}
        - Interests: {interests_str}
        - Career Goal: {career_goal}
        - Additional Information: {additional_info}
        
        CRITICAL FORMATTING INSTRUCTION: When you create the "📝 Your Profile Summary" section, 
        you MUST use the EXACT text "{formatted_education_level}" for the Education Level field. 
        DO NOT change the capitalization, spacing, or format in any way.
        
        AVAILABLE COURSES:
        {course_context}
        
        TASK:
        Based on the student's profile and the available courses above, provide personalized course recommendations for Spring 2026. 

        Your response should include:
        1. A warm, personalized greeting
        2. 6-8 specific course recommendations from the list above
        3. For each recommended course, explain:
           - Why it's relevant to their interests/goals
           - How it fits their education level
           - What skills/knowledge they'll gain
        4. Suggestions for course sequencing if applicable
        5. Encouraging closing remarks about their academic journey
        
        Format your response in a friendly, conversational tone as if you're speaking directly to the student.
        Use bullet points or numbered lists for clarity where appropriate.
        """
        
        return prompt
    
    def _handle_no_courses_found(self, user_profile: Dict[str, Any]) -> str:
        """Handle cases where no courses match the criteria."""
        
        education_level = user_profile.get('education_level', 'your level')
        
        fallback_prompt = f"""
        {self.system_context}
        
        A student at the {education_level} level is looking for course recommendations, but no specific 
        courses matched their exact criteria. 
        
        Interests: {', '.join(user_profile.get('interests', []))}
        Career Goal: {user_profile.get('career_goal', 'Not specified')}
        
        Please provide helpful guidance about:
        1. General course categories they should consider
        2. Suggestions for refining their search criteria
        3. Advice on academic planning for their level
        4. Encouragement to meet with an academic advisor
        
        Be supportive and provide actionable next steps.
        """
        
        try:
            response = self.chat.send_message(fallback_prompt)
            return response.text
        except:
            return """
            I apologize, but I couldn't find specific courses matching your criteria right now. 
            Here are some general suggestions:
            
            • Consider foundational courses in your areas of interest
            • Meet with an academic advisor to discuss your goals
            • Explore prerequisite courses that might open up more options
            • Review the full course catalog for additional possibilities
            
            Feel free to try again with different interests or be more specific about your academic goals!
            """
    
    def answer_course_question(self, question: str, context: str = "") -> str:
        """
        Answer specific questions about courses or academic planning.
        
        Args:
            question: Student's question
            context: Additional context (optional)
        """
        if not self.chat:
            return "I'm sorry, I cannot answer questions right now."
        
        try:
            prompt = f"""
            {self.system_context}
            
            CONTEXT: {context}
            
            STUDENT QUESTION: {question}
            
            Please provide a helpful, accurate answer to the student's question. 
            If the question is about specific courses, try to provide relevant information.
            If you need more information to give a complete answer, ask clarifying questions.
            
            Keep your response conversational and supportive.
            """
            
            response = self.chat.send_message(prompt)
            return response.text
            
        except Exception as e:
            print(f"Error answering question: {e}")
            return "I encountered an error while processing your question. Please try asking again."
    
    def get_course_details(self, course_id: str) -> str:
        """Get detailed information about a specific course."""
        if not self.rag_system:
            return "Course information is not available right now."
        
        course = self.rag_system.get_course_by_id(course_id)
        
        if not course:
            return f"I couldn't find information for course {course_id}. Please check the course ID and try again."
        
        try:
            course_info = self.rag_system.format_course_for_llm(course)
            
            prompt = f"""
            {self.system_context}
            
            COURSE INFORMATION:
            {course_info}
            
            Please provide a detailed, student-friendly explanation of this course including:
            1. What the course covers
            2. Who should take this course
            3. What skills/knowledge students will gain
            4. How it might connect to career goals
            5. Any important notes about prerequisites or timing
            
            Make it engaging and informative for prospective students.
            """
            
            response = self.chat.send_message(prompt)
            return response.text
            
        except Exception as e:
            print(f"Error getting course details: {e}")
            return f"Here's the basic information for {course.get('title', course_id)}:\n\n{self.rag_system.format_course_for_llm(course)}"
    
    def chat_with_advisor(self, message: str) -> str:
        """
        General chat interface for ongoing conversations with the advisor.
        
        Args:
            message: Student's message/question
        """
        if not self.chat:
            return "I'm sorry, the advisor chat is not available right now."
        
        try:
            # Add context to maintain advisor role
            contextualized_message = f"""
            As an academic advisor, please respond to this student message:
            
            Student: {message}
            
            Provide helpful, supportive guidance related to course selection, academic planning, 
            or university life. If the student asks about specific courses, let them know they 
            can ask for detailed course recommendations or specific course information.
            """
            
            response = self.chat.send_message(contextualized_message)
            return response.text
            
        except Exception as e:
            print(f"Error in chat: {e}")
            return "I'm having trouble responding right now. Could you please try asking your question again?"