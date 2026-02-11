import os
import json
from datetime import datetime, timedelta
from schemas import DailyContext, PlanResponse, NextAction, ConfusionDump, ConfusionResponse
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

def get_age_appropriate_tone(age_group: str) -> dict:
    tones = {
        "class3": {
            "style": "friendly and playful",
            "encouragement": "Great job! You're doing amazing!",
            "break_msg": "Time for a fun break! 🎮"
        },
        "class8": {
            "style": "supportive and guiding", 
            "encouragement": "You're making good progress. Keep it up!",
            "break_msg": "Take a break - you've earned it! 😊"
        },
        "class12": {
            "style": "direct and exam-focused",
            "encouragement": "Solid work. This will help in your exams.",
            "break_msg": "Strategic break time. Stay focused."
        },
        "college": {
            "style": "flexible and independent",
            "encouragement": "Good momentum. Trust your process.",
            "break_msg": "Break time. You know what you need."
        }
    }
    return tones.get(age_group, tones["college"])

def determine_next_action(context: DailyContext) -> NextAction:
    """Core engine: What should I do next?"""
    
    # Check if student is overloaded
    if context.available_hours < 2 or context.energy_level == "low" and len(context.assignments) > 3:
        return NextAction(
            task="Take a break - you're overloaded",
            duration=30,
            reason="Preventing burnout is more important than pushing through",
            difficulty="easy",
            type="break"
        )
    
    # Missed day recovery
    if context.missed_days > 0:
        easy_task = next((a for a in context.assignments if a.priority == "low"), None)
        if easy_task:
            return NextAction(
                task=f"Finish {easy_task.title} (easy win)",
                duration=30,
                reason="Building momentum after missed days",
                difficulty="easy", 
                type="recovery"
            )
    
    # Energy-aware task selection
    if context.energy_level == "high":
        # Tackle hardest work first
        hard_tasks = [a for a in context.assignments if a.priority == "high"]
        if hard_tasks:
            task = hard_tasks[0]
            return NextAction(
                task=f"Work on {task.title}",
                duration=90,
                reason="High energy = perfect for challenging work",
                difficulty="hard",
                type="study"
            )
    
    elif context.energy_level == "low":
        # Find revision or easy tasks
        revision_subjects = [s for s in context.subjects if s.last_studied and s.revision_count < 3]
        if revision_subjects:
            subject = revision_subjects[0]
            return NextAction(
                task=f"Quick revision: {subject.name} (20 min)",
                duration=20,
                reason="Low energy is perfect for light revision",
                difficulty="easy",
                type="revision"
            )
    
    # Default: medium energy or fallback
    if context.assignments:
        task = context.assignments[0]
        return NextAction(
            task=f"Work on {task.title}",
            duration=60,
            reason="Steady progress on your priorities",
            difficulty="medium",
            type="study"
        )
    
    # No assignments - suggest revision
    if context.subjects:
        return NextAction(
            task=f"Review {context.subjects[0].name} notes",
            duration=45,
            reason="Strengthening your foundation",
            difficulty="medium",
            type="revision"
        )
    
    return NextAction(
        task="Plan tomorrow's work",
        duration=15,
        reason="Preparation leads to success",
        difficulty="easy",
        type="study"
    )

def generate_plan(context: DailyContext) -> PlanResponse:
    """Generate intelligent, student-native plan"""
    
    tone = get_age_appropriate_tone(context.age_group)
    next_action = determine_next_action(context)
    
    # Build plan message based on context
    plan_parts = []
    
    if context.missed_days > 0:
        recovery_msg = "Yesterday didn't go well. That's okay. Let's reset and build momentum."
    else:
        recovery_msg = None
    
    # Check for revision reminders
    revision_reminder = None
    for subject in context.subjects:
        if subject.last_studied:
            days_ago = 6  # Simplified - in real app, calculate from last_studied date
            if days_ago >= 5:
                revision_reminder = f"You studied {subject.name} {days_ago} days ago. A quick revision today will help."
                break
    
    # Energy-aware plan message
    if context.energy_level == "high":
        plan_msg = f"Your energy is high today. Perfect time to tackle challenging work. {tone['encouragement']}"
    elif context.energy_level == "low":
        plan_msg = f"Low energy day - that's normal. Focus on easier tasks and revision. {tone['encouragement']}"
    else:
        plan_msg = f"Steady energy today. Good balance of work and breaks. {tone['encouragement']}"
    
    return PlanResponse(
        next_action=next_action,
        plan_message=plan_msg,
        recovery_message=recovery_msg,
        confidence_boost=tone['encouragement'],
        revision_reminder=revision_reminder
    )

def handle_confusion_dump(confusion_data: ConfusionDump) -> ConfusionResponse:
    """Convert student confusion into calm actions"""
    
    tone = get_age_appropriate_tone(confusion_data.age_group)
    
    prompt = f"""A student (age group: {confusion_data.age_group}) is feeling: "{confusion_data.confusion}"

Respond in a {tone['style']} tone. Provide:
1. A calm, reassuring response (1-2 sentences)
2. 2-3 specific action items
3. How to adjust today's plan

Return JSON:
{{
  "calm_response": "reassuring message",
  "action_items": ["action1", "action2", "action3"],
  "plan_adjustment": "how to modify today's plan"
}}"""

    response = model.generate_content(prompt)
    result = json.loads(response.text)
    return ConfusionResponse(**result)