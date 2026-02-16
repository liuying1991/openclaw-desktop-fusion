import json
import sys
import os
import platform

def list_windows(params):
    try:
        import pygetwindow as gw
        windows = gw.getAllWindows()
        result = []
        for w in windows:
            if w.title:
                result.append({
                    'title': w.title,
                    'left': w.left,
                    'top': w.top,
                    'width': w.width,
                    'height': w.height,
                    'active': w.isActive
                })
        return {
            'status': 'success',
            'action': 'list',
            'count': len(result),
            'windows': result
        }
    except Exception as e:
        return {'status': 'error', 'action': 'list', 'message': str(e)}

def find_window(params):
    title = params.get('title', '')
    try:
        import pygetwindow as gw
        windows = gw.getWindowsWithTitle(title)
        if windows:
            w = windows[0]
            return {
                'status': 'success',
                'action': 'find',
                'found': True,
                'title': w.title,
                'left': w.left,
                'top': w.top,
                'width': w.width,
                'height': w.height,
                'active': w.isActive
            }
        else:
            return {'status': 'success', 'action': 'find', 'found': False}
    except Exception as e:
        return {'status': 'error', 'action': 'find', 'message': str(e)}

def activate_window(params):
    title = params.get('title', '')
    try:
        import pygetwindow as gw
        windows = gw.getWindowsWithTitle(title)
        if windows:
            windows[0].activate()
            return {'status': 'success', 'action': 'activate', 'title': title}
        else:
            return {'status': 'error', 'action': 'activate', 'message': 'Window not found'}
    except Exception as e:
        return {'status': 'error', 'action': 'activate', 'message': str(e)}

def move_window(params):
    title = params.get('title', '')
    x = params.get('x', 0)
    y = params.get('y', 0)
    try:
        import pygetwindow as gw
        windows = gw.getWindowsWithTitle(title)
        if windows:
            windows[0].moveTo(x, y)
            return {'status': 'success', 'action': 'move', 'title': title, 'x': x, 'y': y}
        else:
            return {'status': 'error', 'action': 'move', 'message': 'Window not found'}
    except Exception as e:
        return {'status': 'error', 'action': 'move', 'message': str(e)}

def resize_window(params):
    title = params.get('title', '')
    width = params.get('width', 800)
    height = params.get('height', 600)
    try:
        import pygetwindow as gw
        windows = gw.getWindowsWithTitle(title)
        if windows:
            windows[0].resizeTo(width, height)
            return {'status': 'success', 'action': 'resize', 'title': title, 'width': width, 'height': height}
        else:
            return {'status': 'error', 'action': 'resize', 'message': 'Window not found'}
    except Exception as e:
        return {'status': 'error', 'action': 'resize', 'message': str(e)}

def close_window(params):
    title = params.get('title', '')
    try:
        import pygetwindow as gw
        windows = gw.getWindowsWithTitle(title)
        if windows:
            windows[0].close()
            return {'status': 'success', 'action': 'close', 'title': title}
        else:
            return {'status': 'error', 'action': 'close', 'message': 'Window not found'}
    except Exception as e:
        return {'status': 'error', 'action': 'close', 'message': str(e)}

def minimize_window(params):
    title = params.get('title', '')
    try:
        import pygetwindow as gw
        windows = gw.getWindowsWithTitle(title)
        if windows:
            windows[0].minimize()
            return {'status': 'success', 'action': 'minimize', 'title': title}
        else:
            return {'status': 'error', 'action': 'minimize', 'message': 'Window not found'}
    except Exception as e:
        return {'status': 'error', 'action': 'minimize', 'message': str(e)}

def maximize_window(params):
    title = params.get('title', '')
    try:
        import pygetwindow as gw
        windows = gw.getWindowsWithTitle(title)
        if windows:
            windows[0].maximize()
            return {'status': 'success', 'action': 'maximize', 'title': title}
        else:
            return {'status': 'error', 'action': 'maximize', 'message': 'Window not found'}
    except Exception as e:
        return {'status': 'error', 'action': 'maximize', 'message': str(e)}

def get_monitors(params):
    try:
        import pyautogui
        size = pyautogui.size()
        return {
            'status': 'success',
            'action': 'monitors',
            'primary': {
                'width': size.width,
                'height': size.height
            }
        }
    except Exception as e:
        return {'status': 'error', 'action': 'monitors', 'message': str(e)}

def main():
    if len(sys.argv) < 2:
        print(json.dumps({'status': 'error', 'message': 'Usage: python window.py <action> [params]'}))
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
        'list': list_windows,
        'find': find_window,
        'activate': activate_window,
        'move': move_window,
        'resize': resize_window,
        'close': close_window,
        'minimize': minimize_window,
        'maximize': maximize_window,
        'monitors': get_monitors
    }
    
    if action in actions:
        result = actions[action](params)
    else:
        result = {'status': 'error', 'message': f'Unknown action: {action}'}
    
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
