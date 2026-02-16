import json
import sys
import os
import platform
import subprocess

def _copy_to_clipboard(text):
    if platform.system() == 'Linux':
        process = subprocess.Popen(
            ['xclip', '-selection', 'clipboard', '-i'],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        process.communicate(text.encode('utf-8'), timeout=5)
        return process.returncode == 0
    else:
        import pyperclip
        pyperclip.copy(text)
        return True

def _get_from_clipboard():
    if platform.system() == 'Linux':
        result = subprocess.run(
            ['xclip', '-selection', 'clipboard', '-o'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return result.stdout
        return ''
    else:
        import pyperclip
        return pyperclip.paste()

def copy_text(params):
    text = params.get('text', '')
    try:
        _copy_to_clipboard(text)
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
        text = _get_from_clipboard()
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
        text = _get_from_clipboard()
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
        _copy_to_clipboard('')
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
