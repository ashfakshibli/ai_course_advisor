# AI Student Course Advisor 🎓

An AI-powered course recommendation system for university students. This application uses Google Gemini AI and a Retrieval-Augmented Generation (RAG) system to provide personalized course recommendations based on student interests, education level, and career goals.

## Features

- **Personalized Course Recommendations**: Get tailored course suggestions based on your profile
- **Interactive Chat Interface**: Ask questions about courses and academic planning
- **Smart Course Matching**: RAG system matches courses to your interests and career goals
- **User-Friendly Web Interface**: Clean, responsive design with Tailwind CSS
- **Real-time AI Responses**: Powered by Google Gemini for natural conversations

## Project Structure

```
ai_course_advisor/
├── app.py                          # Flask web application
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables (API keys)
├── README.md                      # This file
├── data/
│   └── course_catalog.json        # Course database with university courses
├── src/
│   ├── llm_integration.py         # Gemini AI integration and course advisor logic
│   ├── rag_system.py              # Retrieval-Augmented Generation system
│   └── user_input.py              # User profile processing and validation
└── templates/
    └── index.html                 # Main web interface
```

## Technology Stack

- **Backend**: Python, Flask
- **AI/LLM**: Google Gemini API
- **RAG System**: Custom implementation for course retrieval
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **Data**: JSON course catalog

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key (provided in .env file)
- Web browser for accessing the interface

### Step 1: Clone or Navigate to Project Directory

```bash
cd /path/to/ai_course_advisor
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Verify Environment Variables

The `.env` file should be configured with your Gemini API key:

```
GEMINI_API_KEY=""
FLASK_ENV=development
PORT=5000
```

### Step 5: Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## Usage Guide

### Getting Course Recommendations

1. **Open the Application**: Navigate to `http://localhost:5000` in your web browser

2. **Fill Out Your Profile**:
   - Select your current education level (1st year, 2nd year, etc.)
   - Enter your academic interests (e.g., "computer science, business, data analysis")
   - Optionally add your career goal (e.g., "software engineer")
   - Add any additional information about your preferences

3. **Get Recommendations**: Click "Get My Course Recommendations" to receive personalized suggestions

4. **Review Results**: The AI will provide detailed course recommendations with explanations of why each course fits your profile

### Using the Chat Feature

- Use the chat interface to ask specific questions about courses
- Examples:
  - "What are the prerequisites for Computer Science courses?"
  - "Which courses would help me prepare for medical school?"
  - "Can you tell me more about the nursing program?"

### API Endpoints

The application also provides REST API endpoints:

- `POST /api/recommend` - Get course recommendations
- `POST /api/chat` - Chat with the advisor
- `GET /api/course/<course_id>` - Get details about a specific course
- `GET /api/courses/search` - Search courses by criteria
- `GET /api/health` - Health check

## Course Catalog

The system includes a comprehensive course catalog with:

- **40+ courses** across various disciplines
- **Multiple education levels**: 1st year through graduate
- **Diverse categories**: Business, Computer Science, Natural Sciences, Humanities, etc.
- **Detailed information**: Prerequisites, descriptions, credit hours, availability

### Sample Courses Include:

- **Foundational**: English Composition, College Algebra, Introduction to Psychology
- **Specialized**: Data Structures & Algorithms, Organic Chemistry, Music Theory
- **Advanced**: Strategic Management (MBA), Pharmacology, Research Methods
- **Professional**: Nursing Fundamentals, Educational Psychology, Financial Management

## How It Works

### 1. User Input Processing
The system collects and validates user information including education level, interests, and career goals.

### 2. RAG System Course Retrieval
- Searches the course catalog using multiple criteria
- Matches courses to user interests using keyword analysis
- Filters by education level and prerequisites
- Ranks courses by relevance

### 3. AI-Powered Recommendations
- Gemini AI analyzes the matched courses and user profile
- Generates personalized explanations for each recommendation
- Provides guidance on course sequencing and academic planning

### 4. Interactive Chat
- Maintains conversation context for follow-up questions
- Provides detailed information about specific courses
- Offers academic planning advice

## Customization

### Adding New Courses
Edit `data/course_catalog.json` to add new courses:

```json
{
  "id": "NEW101",
  "title": "New Course Title",
  "level": "1st year",
  "category": "Category Name",
  "credits": 3,
  "description": "Course description...",
  "prerequisites": "Prerequisites if any",
  "semesters": ["Fall", "Spring"],
  "keywords": ["keyword1", "keyword2"]
}
```

### Modifying AI Behavior
Edit the system context in `src/llm_integration.py` to change how the AI advisor responds.

### Updating the Interface
Modify `templates/index.html` to change the web interface design and functionality.

## Development

### Running in Development Mode
```bash
export FLASK_ENV=development
python app.py
```

### Testing Individual Components
```python
# Test RAG system
from src.rag_system import CourseRAG
rag = CourseRAG()
courses = rag.search_courses_by_level("1st year")

# Test user input processing
from src.user_input import UserProfileProcessor
processor = UserProfileProcessor()
profile = processor.process_user_input({
    "education_level": "2nd year",
    "interests": "computer science, business"
})
```

## Troubleshooting

### Common Issues

1. **API Key Error**: Ensure your Gemini API key is correctly set in the `.env` file
2. **Import Errors**: Make sure all dependencies are installed: `pip install -r requirements.txt`
3. **Port Already in Use**: Change the PORT in `.env` or kill the process using port 5000
4. **No Recommendations**: Check that the course catalog JSON file is valid and accessible

### Error Logs
Check the console output when running the application for detailed error messages.

## Future Enhancements

Potential improvements for the system:

1. **User Authentication**: Add user accounts and saved preferences
2. **Course Scheduling**: Integration with actual semester schedules
3. **Prerequisites Tracking**: Advanced prerequisite checking and course sequencing
4. **Real Course Data**: Integration with university course management systems
5. **Mobile App**: Native mobile application
6. **Advanced Analytics**: Usage tracking and recommendation improvement

## Contributing

To contribute to this project:

1. Fork the repository or create a new branch
2. Make your changes
3. Test thoroughly with various user inputs
4. Submit a pull request with a description of changes

## License

This project is for educational purposes. Please ensure you have appropriate permissions for any production use.

## Support

For questions or issues:

1. Check the troubleshooting section above
2. Review error messages in the console
3. Ensure all dependencies are correctly installed
4. Verify the Gemini API key is valid and has appropriate permissions

---

**Built with ❤️ for university students everywhere**
