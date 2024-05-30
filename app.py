"""
__________________________________________
Modified (Gemini model)
__________________________________________
"""
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
import os
import random
import google.generativeai as genai

app = Flask(__name__)

genai.configure(api_key = os.getenv("gemini_api_key" ))

# Define DSA topics
dsa_topics = {
    "Arrays": [
        "Dynamic Programming (DP) problems related to arrays.",
        "Sorting algorithms for arrays.",
        "Search algorithms for arrays."
    ],
    "Linked Lists": [
        "Dynamic Programming (DP) problems related to linked lists.",
        "Insertion and deletion operations in linked lists.",
        "Cyclic detection and removal in linked lists."
    ],
    "Stacks and Queues": [
        "Implementing stacks and queues using arrays or linked lists.",
        "Applications of stacks and queues in algorithm design.",
        "Optimizing stack and queue operations for efficiency."
    ],
    "Trees": [
        "Dynamic Programming (DP) problems related to trees.",
        "Traversal algorithms for trees (e.g., inorder, preorder, postorder).",
        "Balancing techniques for binary search trees."
    ]
}

def generate_dsa_question(topic, difficulty="medium"):
    prompt = f"""
    **Topic:** {topic}
    **Difficulty:** {difficulty}

    **Instructions:**
    - This question is commonly encountered in programming competitions and assessments.
    - The problem statement should revolve around a concept or problem related to {topic}.
    - Provide a concise description of the problem or concept, ensuring clarity and accuracy.
    - Include examples or test cases to illustrate the problem statement effectively.
    - Ensure proper formatting and punctuation for clear presentation.

    Write a question that adheres to the provided instructions.
    """

    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text.strip()
    except genai.RequestError as e:
        return f"Error: API request failed ({e})"
    except genai.APIError as e:
        return f"Error: Generative AI API error ({e})"
    except Exception as e:
        return f"Error generating DSA question: {e}"

def generate_test_cases(question, num_test_cases=10):
    prompt = f"""
    **Question:** {question}

    Instructions:
    - Generate {num_test_cases} test cases where input and/or output are numerical values.
    - Each test case should include numerical input values and the expected numerical output.
    - Ensure that the test cases cover various scenarios related to the given question.
    - Use proper formatting and punctuation for readability.

    Example Test Cases:
    Input: [Specify numerical input values here]
    Output: [Specify expected numerical output here]

    Write {num_test_cases} test cases that thoroughly test the problem related to the given question.
    """

    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        response_text = response.text.strip()

        # Debug: Print the raw response
        print("Raw response from model:", response_text)

        test_cases = response_text.split("\n\n")
        parsed_cases = []

        for case in test_cases:
            lines = case.splitlines()
            input_val = None
            output_val = None

            for line in lines:
                if line.startswith("Input:"):
                    input_val = line.split("Input:")[1].strip()
                elif line.startswith("Output:"):
                    output_val = line.split("Output:")[1].strip()

            if input_val and output_val:
                parsed_cases.append({"input": input_val, "output": output_val})

        return parsed_cases

    except genai.RequestError as e:
        return f"Error: API request failed ({e})"
    except genai.APIError as e:
        return f"Error: Generative AI API error ({e})"
    except Exception as e:
        return f"Error generating test cases: {e}"

@app.route('/')
def index():
    return render_template('indexD.html', topics=list(dsa_topics.keys()))

@app.route('/generate_dsa_questions', methods=['POST'])
def generate_dsa_questions():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing data in request"}), 400

    num_questions = int(data.get('num_questions', 5))
    topics = data.get('topics', list(dsa_topics.keys()))  # Get the list of topics from the request
    difficulty = data.get('difficulty', 'medium')

    generated_questions = []
    for _ in range(num_questions):
        topic = random.choice(topics)
        question = generate_dsa_question(topic, difficulty)
        test_cases = generate_test_cases(question)
        formatted_question = {
            "topic": topic,
            "question": question,
            "test_cases": test_cases
        }
        generated_questions.append(formatted_question)

    return jsonify({"questions": generated_questions})
if __name__ == '__main__':
    app.run(debug=True)
