# Local dev server emulating Vercel cleanUrls + trailingSlash:false
import http.server, socketserver, os, functools, sys
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
# Optional port argument: a scheduled run and a human session can both need a
# server at once, and two processes on 4321 means one of them silently gets the
# other's files.
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 4321
with socketserver.TCPServer(("127.0.0.1", PORT), H) as s:
    print(f"serving on http://localhost:{PORT}"); s.serve_forever()
