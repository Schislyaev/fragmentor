from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('path_to_template_directory'))
template = env.get_template('email_template.html')

# Подставляйте реальные данные, которые нужно вставить в шаблон
confirmation_link = "https://example.com/confirm"
html_content = template.render(confirmation_link=confirmation_link)

print(html_content)

