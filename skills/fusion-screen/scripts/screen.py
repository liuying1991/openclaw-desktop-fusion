import pyautogui
import json
import sys
import os
import platform
import subprocess
from PIL import Image
import io
import base64

def _take_screenshot(region=None):
    if platform.system() == 'Linux':
        path = '/tmp/scrot_screenshot.png'
        try:
            if region:
                x, y, w, h = region
                subprocess.run(['scrot', '-a', f'{x},{y},{w},{h}', path], check=True, capture_output=True, timeout=10)
            else:
                subprocess.run(['scrot', path], check=True, capture_output=True, timeout=10)
            img = Image.open(path)
            img.load()
            return img
        except Exception as e:
            raise e
        finally:
            if os.path.exists(path):
                try:
                    os.unlink(path)
                except:
                    pass
    else:
        if region:
            x, y, w, h = region
            return pyautogui.screenshot(region=(x, y, w, h))
        return pyautogui.screenshot()

def screenshot_base64(params):
    region = params.get('region', None)
    try:
        img = _take_screenshot(region)
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        return {
            'status': 'success',
            'action': 'screenshot_base64',
            'width': img.width,
            'height': img.height,
            'base64': img_base64[:100] + '...',
            'full_length': len(img_base64)
        }
    except Exception as e:
        return {'status': 'error', 'action': 'screenshot_base64', 'message': str(e)}

def ocr(params):
    region = params.get('region', None)
    try:
        img = _take_screenshot(region)
        try:
            import pytesseract
            text = pytesseract.image_to_string(img, lang='chi_sim+eng')
            return {
                'status': 'success',
                'action': 'ocr',
                'text': text.strip(),
                'region': region
            }
        except ImportError:
            return {
                'status': 'success',
                'action': 'ocr',
                'text': 'OCR not available (pytesseract not installed)',
                'region': region
            }
    except Exception as e:
        return {'status': 'error', 'action': 'ocr', 'message': str(e)}

def find_image(params):
    template_path = params.get('template', '')
    confidence = params.get('confidence', 0.9)
    try:
        location = pyautogui.locateOnScreen(template_path, confidence=confidence)
        if location:
            center = pyautogui.center(location)
            return {
                'status': 'success',
                'action': 'find_image',
                'found': True,
                'left': location.left,
                'top': location.top,
                'width': location.width,
                'height': location.height,
                'center_x': center.x,
                'center_y': center.y
            }
        else:
            return {'status': 'success', 'action': 'find_image', 'found': False}
    except Exception as e:
        return {'status': 'error', 'action': 'find_image', 'message': str(e)}

def find_all(params):
    template_path = params.get('template', '')
    confidence = params.get('confidence', 0.9)
    try:
        locations = list(pyautogui.locateAllOnScreen(template_path, confidence=confidence))
        results = []
        for loc in locations:
            center = pyautogui.center(loc)
            results.append({
                'left': loc.left,
                'top': loc.top,
                'width': loc.width,
                'height': loc.height,
                'center_x': center.x,
                'center_y': center.y
            })
        return {
            'status': 'success',
            'action': 'find_all',
            'found': len(results) > 0,
            'count': len(results),
            'locations': results
        }
    except Exception as e:
        return {'status': 'error', 'action': 'find_all', 'message': str(e)}

def analyze(params):
    try:
        img = _take_screenshot()
        return {
            'status': 'success',
            'action': 'analyze',
            'width': img.width,
            'height': img.height,
            'mode': img.mode,
            'size': img.size
        }
    except Exception as e:
        return {'status': 'error', 'action': 'analyze', 'message': str(e)}

def get_screen_size(params):
    try:
        width, height = pyautogui.size()
        return {
            'status': 'success',
            'action': 'get_screen_size',
            'width': width,
            'height': height
        }
    except Exception as e:
        return {'status': 'error', 'action': 'get_screen_size', 'message': str(e)}

def pixel_at(params):
    x = params.get('x', 0)
    y = params.get('y', 0)
    try:
        img = _take_screenshot(region=[x, y, 1, 1])
        color = img.getpixel((0, 0))[:3]
        return {
            'status': 'success',
            'action': 'pixel_at',
            'x': x,
            'y': y,
            'r': color[0],
            'g': color[1],
            'b': color[2]
        }
    except Exception as e:
        return {'status': 'error', 'action': 'pixel_at', 'message': str(e)}

def main():
    if len(sys.argv) < 2:
        print(json.dumps({'status': 'error', 'message': 'Usage: python screen.py <action> [params]'}))
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
        'screenshot_base64': screenshot_base64,
        'ocr': ocr,
        'find_image': find_image,
        'find_all': find_all,
        'analyze': analyze,
        'get_screen_size': get_screen_size,
        'pixel_at': pixel_at
    }
    
    if action in actions:
        result = actions[action](params)
    else:
        result = {'status': 'error', 'message': f'Unknown action: {action}'}
    
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
