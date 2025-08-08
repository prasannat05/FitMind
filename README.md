Note: FitMind is currently under development and testing. Some features may be incomplete or subject to change.

# FitMind - Fitness & Wellness Tracker

FitMind is a web application that helps users track their fitness activities and health metrics in real time. 

It provides AI-powered personalized workout and meal recommendations along with an AI chat coach for fitness guidance.

## Features

- User registration and secure login
- Personal profile management (age, gender, weight, goals)
- Logging daily health data: steps, calories, heart rate, sleep, mood, hydration
- Interactive charts visualizing your fitness data over time
- AI-generated workout and meal recommendations
- Typing-based AI chat coach powered by OpenAI GPT for instant advice
- Dark mode toggle for comfortable viewing
- Export logged fitness data as CSV for offline use
- Progressive Web App support for offline and installable mobile experience

## Technologies Used

- Flask (Python web framework)
- MySQL for data storage
- JavaScript and Chart.js for frontend interactivity and charts
- OpenAI GPT-3.5 for AI chat coaching
- Bootstrap 5 for responsive and clean UI
- PWA technologies: service worker and manifest for offline support

## Project Structure
```
FitMind/
├── app.py # Flask backend application
├── requirements.txt # Python dependencies
├── ai/ # AI recommendation logic
│ └── recommender.py
├── templates/ # HTML templates for UI pages
│ ├── base.html
│ ├── index.html
│ ├── dashboard.html
│ └── profile.html
├── static/ # Static files (CSS, JS, icons, PWA)
│ ├── style.css
│ ├── scripts.js
│ ├── sw.js
│ ├── manifest.json
```





