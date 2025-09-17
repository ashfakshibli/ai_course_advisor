# ai_course_advisor/app.py
import os
import sys
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.llm_integration import AICourseAdvisor
from src.user_input import UserProfileProcessor
from src.rag_system import CourseRAG

app = Flask(__name__, template_folder='templates')
CORS(app)  # Enable CORS for all routes

# Initialize the course advisor system
advisor = AICourseAdvisor()
profile_processor = UserProfileProcessor()
rag_system = CourseRAG()

@app.route('/')
def index():
    """Serve the main course advisor interface."""
    return render_template('index.html')

@app.route('/api/recommend', methods=['POST'])
def get_recommendations():
    """
    Generate course recommendations based on user input.
    
    Expected JSON payload:
    {
        "education_level": "2nd year",
        "interests": ["AI/ML", "Web Dev"],
        "career_goal": "software engineer",
        "explore_new": false,
        "course_count": 5
    }
    """
    try:
        # Get user input
        raw_input = request.get_json(silent=True) or {}
        
        if not raw_input:
            return jsonify({'error': 'No input data provided'}), 400
        
        print(f"DEBUG: Received raw input: {raw_input}")  # Debug logging
        
        # Process user profile
        user_profile = profile_processor.process_user_input(raw_input)
        
        print(f"DEBUG: Processed user profile: {user_profile}")  # Debug logging
        
        # Get course recommendations from RAG system
        recommended_courses = rag_system.get_recommended_courses(user_profile)
        
        print(f"DEBUG: Found {len(recommended_courses)} courses before filtering")  # Debug logging
        
        # Limit to requested number of courses
        course_count = raw_input.get('course_count', 10)
        if course_count and len(recommended_courses) > course_count:
            recommended_courses = recommended_courses[:course_count]
        
        # Validate profile
        validation_results = profile_processor.validate_profile(user_profile)
        
        # Get profile summary for display
        profile_summary = profile_processor.create_profile_summary(user_profile)
        
        print(f"DEBUG: Returning {len(recommended_courses)} final recommendations")  # Debug logging
        
        return jsonify({
            'courses': recommended_courses,
            'profile_summary': profile_summary,
            'validation': validation_results,
            'success': True,
            'count': len(recommended_courses),
            'debug_info': {
                'interests_received': raw_input.get('interests', []),
                'academic_level': raw_input.get('education_level', 'Unknown'),
                'courses_found_total': len(rag_system.search_courses_by_keywords(user_profile.get('interests', []))),
                'courses_returned': len(recommended_courses),
                'profile_processed': True
            }
        })
        
    except Exception as e:
        print(f"Error in get_recommendations: {e}")
        return jsonify({
            'error': 'An error occurred while generating recommendations. Please try again.',
            'success': False
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Handle general chat messages with the course advisor.
    
    Expected JSON payload:
    {
        "message": "What courses should I take for pre-med?"
    }
    """
    try:
        payload = request.get_json(silent=True) or {}
        message = payload.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Generate response using the advisor
        response = advisor.chat_with_advisor(message)
        
        return jsonify({
            'response': response,
            'success': True
        })
        
    except Exception as e:
        print(f"Error in chat: {e}")
        return jsonify({
            'error': 'An error occurred while processing your message. Please try again.',
            'success': False
        }), 500

@app.route('/api/course/<course_id>')
def get_course_details(course_id):
    """Get detailed information about a specific course."""
    try:
        course_details = advisor.get_course_details(course_id)
        
        return jsonify({
            'course_details': course_details,
            'course_id': course_id,
            'success': True
        })
        
    except Exception as e:
        print(f"Error getting course details: {e}")
        return jsonify({
            'error': f'Could not retrieve details for course {course_id}',
            'success': False
        }), 500

@app.route('/api/courses/search')
def search_courses():
    """
    Search courses by various criteria.
    
    Query parameters:
    - level: education level (e.g., "1st year")
    - category: course category (e.g., "Computer Science")
    - semester: semester availability (e.g., "Spring")
    - keywords: comma-separated keywords
    """
    try:
        level = request.args.get('level', '')
        category = request.args.get('category', '')
        semester = request.args.get('semester', '')
        keywords = request.args.get('keywords', '')
        
        courses = []
        
        if level:
            courses = rag_system.search_courses_by_level(level)
        elif category:
            courses = rag_system.search_courses_by_category(category)
        elif semester:
            courses = rag_system.get_courses_by_semester(semester)
        elif keywords:
            keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]
            courses = rag_system.search_courses_by_keywords(keyword_list)
        else:
            # Return all courses if no specific criteria
            courses = rag_system.courses
        
        return jsonify({
            'courses': courses,
            'count': len(courses),
            'success': True
        })
        
    except Exception as e:
        print(f"Error searching courses: {e}")
        return jsonify({
            'error': 'An error occurred while searching courses.',
            'success': False
        }), 500

@app.route('/api/levels')
def get_education_levels():
    """Get available education levels."""
    return jsonify({
        'levels': [
            '1st year', '2nd year', '3rd year', '4th year', 'graduate'
        ],
        'success': True
    })

@app.route('/api/categories')
def get_course_categories():
    """Get available course categories."""
    try:
        categories = list(set(course.get('category', '') for course in rag_system.courses))
        categories = [cat for cat in categories if cat]  # Remove empty categories
        categories.sort()
        
        return jsonify({
            'categories': categories,
            'success': True
        })
        
    except Exception as e:
        print(f"Error getting categories: {e}")
        return jsonify({
            'error': 'Could not retrieve course categories',
            'success': False
        }), 500

@app.route('/api/interests')
def get_common_interests():
    """Get list of common academic interests for suggestions."""
    return jsonify({
        'interests': profile_processor.common_interests,
        'success': True
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'advisor_available': advisor.chat is not None,
        'rag_available': rag_system.courses is not None and len(rag_system.courses) > 0,
        'course_count': len(rag_system.courses) if rag_system.courses else 0
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Endpoint not found',
        'success': False
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'error': 'Internal server error',
        'success': False
    }), 500

if __name__ == '__main__':
    # Check if required environment variables are set
    if not os.getenv('GEMINI_API_KEY'):
        print("Warning: GEMINI_API_KEY not found in environment variables")
        print("Please create a .env file with your Gemini API key")
    
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"Starting AI Course Advisor on port {port}")
    print(f"Debug mode: {debug_mode}")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
