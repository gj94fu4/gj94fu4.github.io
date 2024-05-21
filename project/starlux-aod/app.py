from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/ask', methods=['POST'])
def ask():
    question = request.get_json().get('question')
    # Process the question and generate an answer
    answer = "This is a placeholder answer."
    return jsonify(answer=answer)

if __name__ == '__main__':
    app.run(debug=True)