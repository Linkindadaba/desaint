import urllib.parse

def normalize_wsgi_path(environ):
    query_string = environ.get('QUERY_STRING', '')
    
    # 1. Extract __path__ from vercel.json rewrite
    if '__path__' in query_string:
        parsed_qs = urllib.parse.parse_qs(query_string, keep_blank_values=True)
        if '__path__' in parsed_qs:
            raw_captured_path = parsed_qs.pop('__path__')[0]
            clean_path = '/' + raw_captured_path.lstrip('/')
            
            if clean_path in ('/api/index.py', '/api/index', '/api'):
                clean_path = '/'
                
            environ['PATH_INFO'] = clean_path or '/'
            environ['QUERY_STRING'] = urllib.parse.urlencode(parsed_qs, doseq=True)
            return

    # 2. Inspect fallback Vercel forward headers
    for header_key in (
        'HTTP_X_FORWARDED_URI',
        'HTTP_X_INVOKE_PATH',
        'HTTP_X_VERCEL_FORWARDED_URI',
        'HTTP_X_FORWARDED_PATH',
        'REQUEST_URI',
        'RAW_URI',
    ):
        header_val = environ.get(header_key)
        if header_val and not header_val.startswith('/api/index'):
            orig_path = header_val.split('?')[0]
            if orig_path:
                environ['PATH_INFO'] = '/' + orig_path.lstrip('/')
                return

    # 3. Fallback root
    current_path = environ.get('PATH_INFO', '')
    if current_path in ('/api/index.py', '/api/index', '/api', '/api/index.py/'):
        environ['PATH_INFO'] = '/'
