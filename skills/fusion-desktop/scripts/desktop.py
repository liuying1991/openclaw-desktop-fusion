import pyautogui
import json
import sys
import os
import platform
from PIL import Image
import subprocess
import time

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

def screenshot(params):
    path = params.get('path', '/tmp/screenshot.png')
    region = params.get('region', None)
    try:
        if platform.system() == 'Linux':
            if region:
                x, y, w, h = region
                subprocess.run(['scrot', '-a', f'{x},{y},{w},{h}', path], check=True, capture_output=True, timeout=10)
            else:
                subprocess.run(['scrot', path], check=True, capture_output=True, timeout=10)
            img = Image.open(path)
            return {
                'status': 'success',
                'action': 'screenshot',
                'path': path,
                'width': img.width,
                'height': img.height,
                'region': region
            }
        else:
            if region:
                x, y, w, h = region
                img = pyautogui.screenshot(region=(x, y, w, h))
            else:
                img = pyautogui.screenshot()
            img.save(path)
            return {
                'status': 'success',
                'action': 'screenshot',
                'path': path,
                'width': img.width,
                'height': img.height,
                'region': region
            }
    except Exception as e:
        return {'status': 'error', 'action': 'screenshot', 'message': str(e)}

def move(params):
    x = params.get('x', 0)
    y = params.get('y', 0)
    duration = params.get('duration', 0.2)
    try:
        pyautogui.moveTo(x, y, duration=duration)
        return {'status': 'success', 'action': 'move', 'x': x, 'y': y}
    except Exception as e:
        return {'status': 'error', 'action': 'move', 'message': str(e)}

def click(params):
    x = params.get('x')
    y = params.get('y')
    button = params.get('button', 'left')
    clicks = params.get('clicks', 1)
    duration = params.get('duration', 0.1)
    try:
        if x is not None and y is not None:
            pyautogui.click(x, y, clicks=clicks, button=button, duration=duration)
        else:
            pyautogui.click(clicks=clicks, button=button)
        return {'status': 'success', 'action': 'click', 'x': x, 'y': y, 'button': button, 'clicks': clicks}
    except Exception as e:
        return {'status': 'error', 'action': 'click', 'message': str(e)}

def double_click(params):
    params['clicks'] = 2
    return click(params)

def right_click(params):
    params['button'] = 'right'
    params['clicks'] = 1
    return click(params)

def drag(params):
    start = params.get('start', [0, 0])
    end = params.get('end', [0, 0])
    duration = params.get('duration', 0.5)
    try:
        pyautogui.moveTo(start[0], start[1])
        pyautogui.drag(end[0] - start[0], end[1] - start[1], duration=duration, button='left')
        return {'status': 'success', 'action': 'drag', 'start': start, 'end': end}
    except Exception as e:
        return {'status': 'error', 'action': 'drag', 'message': str(e)}

def scroll(params):
    direction = params.get('direction', 'down')
    amount = params.get('amount', 3)
    x = params.get('x')
    y = params.get('y')
    try:
        scroll_amount = amount if direction == 'up' else -amount
        if x is not None and y is not None:
            pyautogui.scroll(scroll_amount, x, y)
        else:
            pyautogui.scroll(scroll_amount)
        return {'status': 'success', 'action': 'scroll', 'direction': direction, 'amount': amount}
    except Exception as e:
        return {'status': 'error', 'action': 'scroll', 'message': str(e)}

def position(params):
    try:
        x, y = pyautogui.position()
        return {'status': 'success', 'action': 'position', 'x': x, 'y': y}
    except Exception as e:
        return {'status': 'error', 'action': 'position', 'message': str(e)}

def type_text(params):
    text = params.get('text', '')
    interval = params.get('interval', 0.02)
    try:
        if any('\u4e00' <= c <= '\u9fff' for c in text):
            import pyperclip
            pyperclip.copy(text)
            pyautogui.hotkey('ctrl', 'v')
        else:
            pyautogui.typewrite(text, interval=interval)
        return {'status': 'success', 'action': 'type', 'text': text, 'length': len(text)}
    except Exception as e:
        return {'status': 'error', 'action': 'type', 'message': str(e)}

def key(params):
    key = params.get('key', 'enter')
    try:
        pyautogui.press(key)
        return {'status': 'success', 'action': 'key', 'key': key}
    except Exception as e:
        return {'status': 'error', 'action': 'key', 'message': str(e)}

def hotkey(params):
    keys = params.get('keys', [])
    try:
        pyautogui.hotkey(*keys)
        return {'status': 'success', 'action': 'hotkey', 'keys': keys}
    except Exception as e:
        return {'status': 'error', 'action': 'hotkey', 'message': str(e)}

def locate(params):
    image_path = params.get('image', '')
    confidence = params.get('confidence', 0.9)
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        if location:
            center = pyautogui.center(location)
            return {
                'status': 'success',
                'action': 'locate',
                'found': True,
                'left': location.left,
                'top': location.top,
                'width': location.width,
                'height': location.height,
                'center_x': center.x,
                'center_y': center.y
            }
        else:
            return {'status': 'success', 'action': 'locate', 'found': False}
    except Exception as e:
        return {'status': 'error', 'action': 'locate', 'message': str(e)}

def locate_and_click(params):
    image_path = params.get('image', '')
    confidence = params.get('confidence', 0.9)
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        if location:
            center = pyautogui.center(location)
            pyautogui.click(center.x, center.y)
            return {
                'status': 'success',
                'action': 'locate_and_click',
                'found': True,
                'clicked': True,
                'x': center.x,
                'y': center.y
            }
        else:
            return {'status': 'success', 'action': 'locate_and_click', 'found': False, 'clicked': False}
    except Exception as e:
        return {'status': 'error', 'action': 'locate_and_click', 'message': str(e)}

def main():
    if len(sys.argv) < 2:
        print(json.dumps({'status': 'error', 'message': 'Usage: python desktop.py <action> [params]'}))
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
        'screenshot': screenshot,
        'move': move,
        'click': click,
        'double_click': double_click,
        'right_click': right_click,
        'drag': drag,
        'scroll': scroll,
        'position': position,
        'type': type_text,
        'key': key,
        'hotkey': hotkey,
        'locate': locate,
        'locate_and_click': locate_and_click
    }
    
    if action in actions:
        result = actions[action](params)
    else:
        result = {'status': 'error', 'message': f'Unknown action: {action}'}
    
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
