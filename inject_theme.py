import os

templates_dir = r"c:\Users\Vichu\Music\quizz management\templates"
script_tag = """    <script src="{{ url_for('static', filename='js/theme.js') }}"></script>\n"""

for filename in os.listdir(templates_dir):
    if filename.endswith(".html"):
        filepath = os.path.join(templates_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "js/theme.js" not in content:
            content = content.replace("</head>", f"{script_tag}</head>")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

print("Injected successfully.")
