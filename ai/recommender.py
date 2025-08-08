def get_ai_recommendations(user):
    goals = (user.get('goals') or '').lower()

    if 'weight loss' in goals:
        workouts = ['30min Cardio', 'HIIT', 'Walking']
        meals = ['Oats with fruits', 'Low-carb salad', 'Grilled veggies']
    elif 'muscle gain' in goals:
        workouts = ['Deadlifts', 'Push-Pull-Legs', 'Bodybuilding Hypertrophy']
        meals = ['Chicken rice', 'Protein smoothie', 'Paneer + Rice']
    else:
        workouts = ['Stretching', 'Yoga', 'Jogging']
        meals = ['Balanced plate', 'Fruits & veggies', 'Whole grain wrap']

    tips = [
        "Stay consistent — results come over time.",
        "Drink at least 2L of water daily.",
        "Sleep 7–9 hours for recovery.",
        "Log your mood and hydration daily."
    ]

    return {
        "workouts": workouts,
        "meals": meals,
        "tips": tips
    }
