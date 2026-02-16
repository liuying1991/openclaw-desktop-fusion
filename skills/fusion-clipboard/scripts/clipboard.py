import json
import sys
import os
import platform

def copy_text(params):
    text = params.get('text', '')
    try:
        import pyperclip
        pyperclip.copy(text)
        return {
            'status': 'success',
            'action': 'copy',
            'text': text,
            'length': len(text)
        }
    except Exception as e:
        return {'status': 'error', 'action': 'copy', 'message': str(e)}

def paste_text(params):
    try:
        import pyperclip
        text = pyperclip.paste()
        return {
            'status': 'success',
            'action': 'paste',
            'text': text,
            'length': len(text)
        }
    except Exception as e:
        return {'status': 'error', 'action': 'paste', 'message': str(e)}

def get_clipboard(params):
    try:
        import pyperclip
        text = pyperclip.paste()
        return {
            'status': 'success',
            'action': 'get',
            'text': text,
            'length': len(text)
        }
    except Exception as e:
        return {'status': 'error', 'action': 'get', 'message': str(e)}

def clear_clipboard(params):
    try:
        import pyperclip
        pyperclip.copy('')
        return {'status': 'success', 'action': 'clear'}
    except Exception as e:
        return {'status': 'error', 'action': 'clear', 'message': str(e)}

def main():
    if len(sys.argv) < 2:
        print(json.dumps({'status': 'error', 'message': 'Usage: python clipboard.py <action> [params]'}))
        sys.exit(1)
    
    action = sys.argv[1]
    params = {}
    if len(sys.argv) > 2:
        try:
            if os.path.exists(sys.argv[2]):
                with open(sys.argv[2], 'r', encoding='utf-8') as f:
                    params = json.load(f)
            else:
                params = json.loads(sys.argv[2])
        except:
            params = {}
    
    actions = {
        'copy': copy_text,
        'paste': paste_text,
        'get': get_clipboard,
        'clear': clear_clipboard
    }
    
    if action in actions:
        result = actions[action](params)
    else:
        result = {'status': 'error', 'message': f'Unknown action: {action}'}
    
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
