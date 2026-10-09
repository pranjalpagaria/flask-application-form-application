from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def register():
    message = None
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        city = request.form.get('city')

        # Process form data (e.g., save to DB or print)
        message = f"Registration successful for {full_name}!"

    return render_template('index.html', message=message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
