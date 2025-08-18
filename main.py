from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Sample data for search
options = ["dog", "cat", "bird", "fish", "hamster", "lizard", "rabbit"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').lower()
    results = [option for option in options if query in option.lower()]
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
