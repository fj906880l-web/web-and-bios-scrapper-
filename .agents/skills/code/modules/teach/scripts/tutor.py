#!/usr/bin/env python3
import sys
import os
import json
import argparse

STATE_FILE = ".agents/teach_state.json"
CHEATSHEET_FILE = ".agents/teach_cheatsheet.md"

CURRICULA = {
    "rubiks_cube": {
        "title": "Rubik's Cube Solving",
        "lessons": [
            {
                "tier": 0,
                "name": "White Cross",
                "content": "Create a cross of white edge pieces on the bottom layer. Each white edge must align with both the white center and its adjacent color center (e.g. green, red, blue, orange).",
                "question": "What shape do we build first on the white face of the Rubik's cube?",
                "answers": ["cross", "white cross", "a cross"]
            },
            {
                "tier": 1,
                "name": "White Corners",
                "content": "Insert the four white corner pieces to complete the first layer. Position a corner piece directly below its target position, then use the algorithm: R' D' R D to insert it.",
                "question": "What 4-move algorithm is repeatedly used to insert a corner piece from the bottom layer?",
                "answers": ["r' d' r d", "r'd'rd", "right trigger"]
            },
            {
                "tier": 2,
                "name": "Middle Layer (F2L)",
                "content": "Insert the edge pieces into the middle layer. Use U R U' R' U' F' U F if the edge needs to move to the right, or U' L' U L U F U' F' to move it to the left.",
                "question": "True or False: We use the same algorithm to insert edges to both the left and right in the middle layer.",
                "answers": ["false", "f"]
            },
            {
                "tier": 3,
                "name": "Yellow Cross (OLL)",
                "content": "Orient the top layer edges to form a yellow cross. Use the algorithm F R U R' U' F' repeatedly depending on the top pattern (Dot, L-shape, or Line).",
                "question": "What algorithm forms the yellow cross when orienting the top edges?",
                "answers": ["f r u r' u' f'", "fruru'f'"]
            },
            {
                "tier": 4,
                "name": "Yellow Corners (PLL)",
                "content": "Permute the corners and edges to complete the entire cube. Use R U R' U' R' F R2 U' R' U' R U R' F' to swap adjacent corners.",
                "question": "Congratulations! You have reached the final stage. What is the acronym for the final step of permuting the last layer?",
                "answers": ["pll", "permutation"]
            }
        ]
    },
    "regime_trader": {
        "title": "Regime Trader Architecture",
        "lessons": [
            {
                "tier": 0,
                "name": "HMM Regime Detection",
                "content": "Regime Trader uses a Hidden Markov Model (HMM) to classify volatility regimes (e.g. Bull, Bear, Volatile). Indicators like Z-score, RSI, and flow imbalance are updated dynamically.",
                "question": "Which mathematical model is used to detect volatility regimes in the bot?",
                "answers": ["hmm", "hidden markov", "hidden markov model"]
            },
            {
                "tier": 1,
                "name": "Multi-Agent NLP Routing",
                "content": "Parsed commands go through a Multi-Agent pipeline: Agent A (Reader) determines the general intent, and Agent B (Execution) extracts details like tickers and quantities.",
                "question": "What are the names of the two agents in the multi-agent router?",
                "answers": ["agent a and agent b", "reader and execution", "reader and exec"]
            },
            {
                "tier": 2,
                "name": "FINRA Compliance Rules",
                "content": "FINRA rules screen trades for wash-trading and enforce strict stop-loss bounds. Stops are capped at 5% and tightened to 4.9% automatically.",
                "question": "What is the maximum allowed stop-loss percentage from entry in Regime Trader?",
                "answers": ["5%", "5", "0.05", "five percent"]
            },
            {
                "tier": 3,
                "name": "Risk Sizing and Kelly Criterion",
                "content": "Position sizes are calibrated to the current HMM volatility regime. The bot leverages Kelly Criterion calculations to determine risk exposure.",
                "question": "What formula or criterion is used to size positions based on historical probability?",
                "answers": ["kelly", "kelly criterion", "kelly formula"]
            }
        ]
    }
}

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return None

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

def update_cheatsheet(state):
    topic_key = state.get("topic_key")
    curr_tier = state.get("current_tier", 0)
    
    curriculum = CURRICULA.get(topic_key)
    if not curriculum:
        # Custom topic cheat sheet
        title = state.get("topic_title", "Custom Topic")
        content = f"# Learning Cheat Sheet: {title}\n\n"
        content += f"- **Current Level**: Tier {curr_tier}\n"
        content += "- **Tip**: Keep reviewing the code and instructions.\n"
    else:
        title = curriculum["title"]
        content = f"# Learning Cheat Sheet: {title}\n\n"
        content += "Here are the key takeaways from the lessons you have completed or are currently studying:\n\n"
        for i in range(curr_tier + 1):
            if i < len(curriculum["lessons"]):
                lesson = curriculum["lessons"][i]
                status = "✅ Completed" if i < curr_tier else "🚀 Active"
                content += f"## {lesson['name']} ({status})\n"
                content += f"{lesson['content']}\n\n"
                
    with open(CHEATSHEET_FILE, "w") as f:
        f.write(content)

def main():
    parser = argparse.ArgumentParser(description="Stateful Tutor Stateful Script")
    parser.add_argument("--init", type=str, help="Initialize a learning topic")
    parser.add_argument("--next", action="store_true", help="Show current lesson and ZPD context")
    parser.add_argument("--quiz", action="store_true", help="Output active quiz question")
    parser.add_argument("--grade", type=str, help="Grade user answer")
    args = parser.parse_args()

    # Ensure .agents exists
    os.makedirs(".agents", exist_ok=True)

    if args.init:
        topic_title = args.init
        topic_key = "custom"
        for k, v in CURRICULA.items():
            if v["title"].lower() in topic_title.lower() or topic_title.lower() in v["title"].lower():
                topic_key = k
                topic_title = v["title"]
                break
                
        state = {
            "topic_key": topic_key,
            "topic_title": topic_title,
            "current_tier": 0,
            "quiz_attempts": 0,
            "score": 0
        }
        save_state(state)
        update_cheatsheet(state)
        print(json.dumps({
            "status": "initialized",
            "topic": topic_title,
            "message": f"Successfully initialized tutoring session for '{topic_title}'."
        }))
        return

    state = load_state()
    if not state:
        print(json.dumps({
            "status": "error",
            "message": "No active tutoring session found. Please run with --init <topic> first."
        }))
        sys.exit(1)

    topic_key = state.get("topic_key")
    curr_tier = state.get("current_tier", 0)

    if args.next:
        curriculum = CURRICULA.get(topic_key)
        if not curriculum:
            # Custom curriculum response
            print(json.dumps({
                "status": "active",
                "tier": curr_tier,
                "lesson_name": "Custom Concept Exploration",
                "lesson_content": f"Exploring advanced details of {state.get('topic_title')}. Ask questions and take quizzes.",
                "question": "Explain one key aspect of the topic in your own words."
            }))
        else:
            lessons = curriculum["lessons"]
            if curr_tier >= len(lessons):
                print(json.dumps({
                    "status": "completed",
                    "message": f"Congratulations! You have completed all lessons for {state.get('topic_title')}."
                }))
            else:
                lesson = lessons[curr_tier]
                print(json.dumps({
                    "status": "active",
                    "tier": curr_tier,
                    "lesson_name": lesson["name"],
                    "lesson_content": lesson["content"],
                    "question": lesson["question"]
                }))
        return

    if args.quiz:
        curriculum = CURRICULA.get(topic_key)
        if not curriculum:
            print(json.dumps({"question": "Explain the core mechanics of the topic."}))
        else:
            lessons = curriculum["lessons"]
            if curr_tier < len(lessons):
                print(json.dumps({"question": lessons[curr_tier]["question"]}))
            else:
                print(json.dumps({"message": "Curriculum completed."}))
        return

    if args.grade:
        user_ans = args.grade.strip().lower()
        curriculum = CURRICULA.get(topic_key)
        
        passed = False
        feedback = ""
        
        if not curriculum:
            # Heuristic check for custom: length check or keyword check
            passed = len(user_ans) > 10
            feedback = "Grade passed based on detail." if passed else "Please provide more details."
        else:
            lessons = curriculum["lessons"]
            if curr_tier < len(lessons):
                lesson = lessons[curr_tier]
                # Match any predefined answers
                if any(ans in user_ans for ans in lesson["answers"]):
                    passed = True
                    feedback = f"Correct! You matched the expected answer: '{lesson['answers'][0]}'."
                else:
                    passed = False
                    feedback = f"Incorrect. Hint: {lesson['content'][:60]}..."
            else:
                passed = True
                feedback = "Curriculum already completed."

        if passed:
            state["current_tier"] = curr_tier + 1
            state["score"] += 1
            state["quiz_attempts"] = 0
            save_state(state)
            update_cheatsheet(state)
            print(json.dumps({
                "grade": "pass",
                "feedback": feedback,
                "next_tier": curr_tier + 1
            }))
        else:
            state["quiz_attempts"] += 1
            save_state(state)
            print(json.dumps({
                "grade": "fail",
                "feedback": feedback,
                "attempts": state["quiz_attempts"]
            }))
        return

if __name__ == "__main__":
    main()
