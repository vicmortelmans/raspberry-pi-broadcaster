from wsgiref.simple_server import make_server
import jinja2

templateLoader = jinja2.FileSystemLoader(searchpath="./")
templateEnv = jinja2.Environment(loader=templateLoader, autoescape=True)
rpb_console_template = templateEnv.get_template("rpb_console.html")

PORT = 80

def rpb_console(environ, start_response):
    global state_machine
    if environ['REQUEST_METHOD'] == 'POST':
        try:
            request_body_size = int(environ['CONTENT_LENGTH'])
            request_body = environ['wsgi.input'].read(request_body_size)
        except (TypeError, ValueError):
            request_body = "0"
        try:
            response_body = str(int(request_body) ** 2)
        except:
            response_body = "error"
        status = '200 OK'
        headers = [('Content-type', 'text/plain')]
        start_response(status, headers)
        return [response_body.encode()]
    else:
        response_body = rpb_console_template.render(state=state_machine.state)
        status = '200 OK'
        headers = [('Content-type', 'text/html'),
                   ('Content-Length', str(len(response_body)))]
        start_response(status, headers)
        return [response_body.encode()]

def start_server(sm):
    """Start the server."""
    global state_machine
    state_machine = sm
    httpd = make_server("", PORT, rpb_console)
    httpd.serve_forever()
