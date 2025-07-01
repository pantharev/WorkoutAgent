# 🏋️ Workout Agent - AI-Powered Fitness Advisor

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-name.streamlit.app)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange.svg)](https://openai.com/)

> **🤖 AI-Generated Project**: This project was primarily developed using AI assistance (Claude 4 Sonnet via Cline) based on concepts from Eric Roby's tutorial.

A comprehensive AI-powered fitness advisor that provides personalized workout plans, nutrition guidance, and motivational coaching through an intuitive web interface.

## ✨ Features

- **🤖 AI-Powered Analysis**: Uses OpenAI GPT-4 to create personalized fitness plans
- **🏃 Custom Workout Plans**: Tailored exercise routines based on your profile
- **🥗 Nutrition Guidance**: Personalized meal plans with detailed nutritional information
- **💪 Motivational Coaching**: AI-generated motivational quotes and recommendations
- **📊 BMR Calculator**: Accurate Basal Metabolic Rate and calorie calculations
- **🎨 Beautiful UI**: User-friendly Streamlit interface with responsive design
- **🌐 REST API**: Complete FastAPI backend for integration

## 🚀 Live Demo

Try the live application: [Workout Agent on Streamlit Cloud](https://your-app-name.streamlit.app)

## 📸 Screenshots

*Screenshots will be added after deployment*

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **AI**: OpenAI GPT-4 via Pydantic AI
- **Data Validation**: Pydantic
- **Deployment**: Streamlit Cloud

## 🚀 Quick Start

### Option 1: Use the Live App (Recommended)
Visit the [live application](https://your-app-name.streamlit.app) - no setup required!

### Option 2: Run Locally

#### Prerequisites
- Python 3.8 or higher
- OpenAI API key

#### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/WorkoutAgent.git
   cd WorkoutAgent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Run the application**
   
   **Option A: Full Application (API + UI)**
   ```bash
   python run_app.py
   ```
   
   **Option B: Streamlit Only**
   ```bash
   streamlit run streamlit_app.py
   ```
   
   **Option C: API Server Only**
   ```bash
   python workout_agent.py
   ```

5. **Open your browser**
   - Streamlit UI: http://localhost:8501
   - API Documentation: http://localhost:8000/docs

## 📖 How to Use

### Using the Web Interface

1. **Fill Your Profile**: Enter your age, weight, height, gender, and activity level
2. **Set Goals**: Describe your specific fitness goals (optional)
3. **Get Analysis**: Click "Get AI Analysis" for a complete personalized plan
4. **Explore Results**: Browse through:
   - 🏃 **Workout Plan**: Custom exercises with sets, reps, and instructions
   - 🥗 **Nutrition Plan**: Personalized meals with nutritional breakdown
   - 💪 **Motivation**: Inspiring quotes and recommendations
   - 📊 **Summary**: Overview and BMR calculations

### Activity Levels Guide

- **Sedentary**: Little to no exercise
- **Lightly Active**: Light exercise 1-3 days/week
- **Moderately Active**: Moderate exercise 3-5 days/week
- **Very Active**: Hard exercise 6-7 days/week
- **Extremely Active**: Very hard exercise, physical job

## 🏗️ Architecture

The application consists of:

- **`streamlit_app.py`**: Main Streamlit interface
- **`workout_agent.py`**: FastAPI backend with AI agents
- **Pydantic Models**: Data validation and serialization
- **AI Agents**: OpenAI-powered fitness and motivational agents
- **Business Logic**: BMR calculations and profile analysis

## 📊 API Documentation

The FastAPI backend provides these endpoints:

- `GET /` - API information
- `GET /health` - Health check
- `POST /analyze` - Get personalized fitness plan
- `POST /bmr` - Calculate BMR and calorie needs

Full API documentation available at `/docs` when running locally.

## 🚀 Deployment to Streamlit Cloud

### Prerequisites
- GitHub account
- OpenAI API key

### Steps

1. **Fork this repository** to your GitHub account

2. **Go to [Streamlit Cloud](https://share.streamlit.io/)**

3. **Connect your GitHub account**

4. **Deploy the app**:
   - Repository: `yourusername/WorkoutAgent`
   - Branch: `main`
   - Main file path: `streamlit_app.py`

5. **Add secrets** in the Streamlit Cloud dashboard:
   ```toml
   OPENAI_API_KEY = "your_openai_api_key_here"
   ```

6. **Your app will be live** at `https://your-app-name.streamlit.app`

## 🧪 Testing

Run the test suite to verify functionality:

```bash
python test_workout_agent.py
```

Tests cover:
- Pydantic model validation
- BMR calculation accuracy
- API endpoint functionality
- Error handling

## 📁 Project Structure

```
WorkoutAgent/
├── streamlit_app.py          # Main Streamlit application
├── workout_agent.py          # FastAPI backend with AI agents
├── run_app.py               # Local development launcher
├── test_workout_agent.py    # Test suite
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
├── .streamlit/             # Streamlit configuration
│   └── config.toml
├── README.md               # This file
└── app/                    # Original modular structure (legacy)
```

## 🔧 Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)

### Streamlit Configuration

The app includes optimized settings for Streamlit Cloud deployment in `.streamlit/config.toml`.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 Credits & Acknowledgments

### Original Inspiration
This project was inspired by **Eric Roby's** excellent tutorial:
- **Video**: "Build Your Own POWERFUL Multi-Agent AI (FastAPI & PydanticAI)"
- **URL**: https://www.youtube.com/watch?v=VPdpVBV99SE
- **Creator**: [Eric Roby](https://www.youtube.com/@EricRoby)

### AI Development Transparency
This project was primarily developed using AI assistance:
- **AI Assistant**: Claude 4 Sonnet (Anthropic)
- **Development Tool**: Cline (VS Code Extension)
- **Human Input**: Initial concept, requirements, and guidance
- **AI Contribution**: Code generation, architecture design, documentation, and implementation

The human developer provided the initial idea (inspired by Eric Roby's tutorial) and guided the development process, while the AI assistant handled the majority of the code implementation, testing, and documentation.

## ⚠️ Disclaimer

- This application provides general fitness guidance and should not replace professional medical advice
- Always consult with healthcare professionals before starting any new fitness or nutrition program
- The AI-generated recommendations are based on general fitness principles and may not be suitable for everyone
- This is an educational project demonstrating AI-powered application development

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

If you encounter any issues:

1. Check the [live demo](https://your-app-name.streamlit.app) to see if it's working there
2. Verify your OpenAI API key is set correctly (for local development)
3. Run the test suite: `python test_workout_agent.py`
4. Check the [Issues](https://github.com/yourusername/WorkoutAgent/issues) page
5. Create a new issue if needed

## 🌟 Show Your Support

If you found this project helpful, please consider:
- ⭐ Starring the repository
- 🍴 Forking it for your own use
- 📢 Sharing it with others
- 🐛 Reporting bugs or suggesting improvements

---

**Happy Training! 💪**

*Built with ❤️ using AI assistance*
