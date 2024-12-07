from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()
key = os.environ["OPENAI_API_KEY"]
client = OpenAI(api_key= key)

def strip_json_enclosure(raw_output):
    stripped_output = raw_output.strip("```json").strip("```").strip()

    return json.loads(stripped_output)


def generate_workout_prompt(num_plans, split, structure, equipment):
    return (
        f"Generate {num_plans} workout plans using the '{split}' split. Each workout should follow the structure: "
        f"{structure}. The equipment available is: {equipment}. For each workout, include:\n"
        "- A title (e.g., 'Push Workout').\n"
        "- A warmup section with one cardio exercise ex: 5 min treadmill, and one relevant exercise ex: arm circles\n"
        "- A list of compound lifts with exercise name, sets, reps, and rest.\n"
        "- A list of isolation lifts with exercise name, sets, reps, and rest.\n"
        "- A cooldown section with appropriate cooldown exercises.\n"
        "Output the workout plans in this JSON format:\n"
        "[{\n"
        '    "title": "Workout Title",\n'
        '    "warmup": ["Warmup Exercise 1", "Warmup Exercise 2"],\n'
        '    "compoundLifts": [\n'
        '        { "name": "Compound Exercise 1", "sets": X, "reps": Y, "rest": Z },\n'
        '        { "name": "Compound Exercise 2", "sets": X, "reps": Y, "rest": Z }\n'
        '    ],\n'
        '    "isolationLifts": [\n'
        '        { "name": "Isolation Exercise 1", "sets": X, "reps": Y, "rest": Z },\n'
        '        { "name": "Isolation Exercise 2", "sets": X, "reps": Y, "rest": Z }\n'
        '    ],\n'
        '    "cooldown": ["Cooldown Exercise 1", "Cooldown Exercise 2"]\n'
        "}]\n"
    )

def get_workout_plan_from_gpt(num_plans, split, structure, equipment):
    prompt = generate_workout_prompt(num_plans, split, structure, equipment)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a fitness coach and workout planner."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    result = strip_json_enclosure(response.choices[0].message.content)
    return result
