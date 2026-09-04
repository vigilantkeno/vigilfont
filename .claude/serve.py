# Local dev server emulating Vercel cleanUrls + trailingSlash:false
import http.server, socketserver, os, functools
class H(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        p = super().translate_path(path.split('?')[0])
        if os.path.isdir(p):
            idx = os.path.join(p, 'index.html')
            if os.path.exists(idx): return idx
        if not os.path.exists(p) and not p.endswith('.html'):
            if os.path.exists(p + '.html'): return p + '.html'
            if os.path.exists(os.path.join(p, 'index.html')): return os.path.join(p, 'index.html')
        return p
    def log_message(self, *a): pass
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("127.0.0.1", 4321), H) as s:
    print("serving on http://localhost:4321"); s.serve_forever()
