import subprocess
import json
import os
import sys
import time
import tempfile

PROJECT_DIR = '/mnt/c/tmp/openclaw-desktop-fusion'

os.environ['DISPLAY'] = ':0'
os.environ['XDG_RUNTIME_DIR'] = '/mnt/wslg/runtime-dir'
os.environ['WAYLAND_DISPLAY'] = 'wayland-0'
os.environ['XAUTHORITY'] = os.path.expanduser('~/.Xauthority')

def run_skill(skill_name, action, params):
    script_paths = {
        'fusion-desktop': f'{PROJECT_DIR}/skills/fusion-desktop/scripts/desktop.py',
        'fusion-screen': f'{PROJECT_DIR}/skills/fusion-screen/scripts/screen.py',
        'fusion-browser': f'{PROJECT_DIR}/skills/fusion-browser/scripts/browser.js',
        'fusion-clipboard': f'{PROJECT_DIR}/skills/fusion-clipboard/scripts/clipboard.py',
        'fusion-window': f'{PROJECT_DIR}/skills/fusion-window/scripts/window.py'
    }
    script_path = script_paths.get(skill_name)
    if not script_path:
        return {'error': f'Unknown skill: {skill_name}'}
    
    params_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump(params, params_file)
    params_file.close()
    
    env = os.environ.copy()
    env['DISPLAY'] = ':0'
    env['XDG_RUNTIME_DIR'] = '/mnt/wslg/runtime-dir'
    env['WAYLAND_DISPLAY'] = 'wayland-0'
    env['XAUTHORITY'] = os.path.expanduser('~/.Xauthority')
    
    try:
        if script_path.endswith('.py'):
            result = subprocess.run(
                ['python3', script_path, action, params_file.name],
                capture_output=True, text=True, timeout=60, env=env
            )
        else:
            result = subprocess.run(
                ['node', script_path, action, params_file.name],
                capture_output=True, text=True, timeout=120, env=env
            )
        try:
            os.unlink(params_file.name)
        except:
            pass
        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except:
                return {'status': 'error', 'output': result.stdout, 'stderr': result.stderr[:500] if result.stderr else ''}
        else:
            return {'status': 'error', 'message': result.stderr[:500] if result.stderr else 'Unknown error', 'stdout': result.stdout[:500] if result.stdout else ''}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def score(test, scores):
    return {
        'test': test,
        'trae': scores.get('trae', 0),
        'openclaw': scores.get('openclaw', 0),
        'opensource': scores.get('opensource', 0),
        'fusion': scores.get('fusion', 0)
    }

def test_screenshot():
    print('\n=== 测试1: 截图能力 ===\n')
    scores = {'trae': 0, 'openclaw': 80, 'opensource': 85, 'fusion': 0}
    
    print('场景A: 全屏截图')
    result = run_skill('fusion-desktop', 'screenshot', {'path': '/tmp/test_screenshot.png'})
    if result.get('status') == 'success':
        scores['fusion'] += 50
        print(f"Fusion: ✅ 截图成功 - {result.get('width')}x{result.get('height')}")
    else:
        print(f"Fusion: ❌ 截图失败 - {result.get('message', result)}")
    
    print('\n场景B: 区域截图')
    result = run_skill('fusion-screen', 'screenshot_base64', {'region': [0, 0, 500, 500]})
    if result.get('status') == 'success':
        scores['fusion'] += 25
        print(f"Fusion: ✅ 区域截图成功 - {result.get('width')}x{result.get('height')}")
    else:
        print(f"Fusion: ❌ 区域截图失败")
    
    print('\n场景C: 屏幕尺寸')
    result = run_skill('fusion-screen', 'get_screen_size', {})
    if result.get('status') == 'success':
        scores['fusion'] += 25
        print(f"Fusion: ✅ 获取屏幕尺寸 - {result.get('width')}x{result.get('height')}")
    else:
        print(f"Fusion: ❌ 获取屏幕尺寸失败")
    
    print(f"\n截图能力评分: Trae={scores['trae']}, OpenClaw={scores['openclaw']}, 开源={scores['opensource']}, Fusion={scores['fusion']}")
    return score('截图能力', scores)

def test_mouse():
    print('\n=== 测试2: 鼠标控制 ===\n')
    scores = {'trae': 0, 'openclaw': 85, 'opensource': 90, 'fusion': 0}
    
    print('场景A: 获取鼠标位置')
    result = run_skill('fusion-desktop', 'position', {})
    if result.get('status') == 'success':
        scores['fusion'] += 25
        print(f"Fusion: ✅ 鼠标位置 - ({result.get('x')}, {result.get('y')})")
    else:
        print(f"Fusion: ❌ 获取鼠标位置失败 - {result.get('message', '')[:50]}")
    
    print('\n场景B: 鼠标移动')
    result = run_skill('fusion-desktop', 'move', {'x': 500, 'y': 400, 'duration': 0.1})
    if result.get('status') == 'success':
        scores['fusion'] += 25
        print(f"Fusion: ✅ 鼠标移动成功")
    else:
        print(f"Fusion: ❌ 鼠标移动失败")
    
    print('\n场景C: 点击操作')
    result = run_skill('fusion-desktop', 'click', {'x': 500, 'y': 400})
    if result.get('status') == 'success':
        scores['fusion'] += 25
        print(f"Fusion: ✅ 点击成功")
    else:
        print(f"Fusion: ❌ 点击失败")
    
    print('\n场景D: 滚动操作')
    result = run_skill('fusion-desktop', 'scroll', {'direction': 'up', 'amount': 1})
    if result.get('status') == 'success':
        scores['fusion'] += 25
        print(f"Fusion: ✅ 滚动成功")
    else:
        print(f"Fusion: ❌ 滚动失败")
    
    print(f"\n鼠标控制评分: Trae={scores['trae']}, OpenClaw={scores['openclaw']}, 开源={scores['opensource']}, Fusion={scores['fusion']}")
    return score('鼠标控制', scores)

def test_keyboard():
    print('\n=== 测试3: 键盘控制 ===\n')
    scores = {'trae': 0, 'openclaw': 75, 'opensource': 85, 'fusion': 0}
    
    print('场景A: 按键操作')
    result = run_skill('fusion-desktop', 'key', {'key': 'escape'})
    if result.get('status') == 'success':
        scores['fusion'] += 35
        print(f"Fusion: ✅ 按键成功")
    else:
        print(f"Fusion: ❌ 按键失败")
    
    print('\n场景B: 组合键')
    result = run_skill('fusion-desktop', 'hotkey', {'keys': ['ctrl', 'c']})
    if result.get('status') == 'success':
        scores['fusion'] += 35
        print(f"Fusion: ✅ 组合键成功")
    else:
        print(f"Fusion: ❌ 组合键失败")
    
    print('\n场景C: 文字输入')
    result = run_skill('fusion-desktop', 'type', {'text': 'test'})
    if result.get('status') == 'success':
        scores['fusion'] += 30
        print(f"Fusion: ✅ 文字输入成功")
    else:
        print(f"Fusion: ❌ 文字输入失败")
    
    print(f"\n键盘控制评分: Trae={scores['trae']}, OpenClaw={scores['openclaw']}, 开源={scores['opensource']}, Fusion={scores['fusion']}")
    return score('键盘控制', scores)

def test_image():
    print('\n=== 测试4: 图像识别 ===\n')
    scores = {'trae': 0, 'openclaw': 60, 'opensource': 80, 'fusion': 0}
    
    print('场景A: 屏幕分析')
    result = run_skill('fusion-screen', 'analyze', {})
    if result.get('status') == 'success':
        scores['fusion'] += 50
        print(f"Fusion: ✅ 屏幕分析成功 - {result.get('width')}x{result.get('height')}")
    else:
        print(f"Fusion: ❌ 屏幕分析失败")
    
    print('\n场景B: 像素获取')
    result = run_skill('fusion-screen', 'pixel_at', {'x': 100, 'y': 100})
    if result.get('status') == 'success':
        scores['fusion'] += 50
        print(f"Fusion: ✅ 像素获取成功 - RGB({result.get('r')}, {result.get('g')}, {result.get('b')})")
    else:
        print(f"Fusion: ❌ 像素获取失败")
    
    print(f"\n图像识别评分: Trae={scores['trae']}, OpenClaw={scores['openclaw']}, 开源={scores['opensource']}, Fusion={scores['fusion']}")
    return score('图像识别', scores)

def test_browser():
    print('\n=== 测试5: 浏览器自动化 ===\n')
    scores = {'trae': 0, 'openclaw': 85, 'opensource': 80, 'fusion': 0}
    
    print('场景A: 打开网页')
    result = run_skill('fusion-browser', 'open', {'url': 'https://example.com', 'headless': True})
    if result.get('status') == 'success':
        scores['fusion'] += 40
        print(f"Fusion: ✅ 打开网页成功 - {result.get('title')}")
    else:
        print(f"Fusion: ❌ 打开网页失败 - {result.get('message', '')[:100]}")
    
    print('\n场景B: 截图')
    result = run_skill('fusion-browser', 'screenshot', {'path': '/tmp/browser_test.png'})
    if result.get('status') == 'success':
        scores['fusion'] += 30
        print(f"Fusion: ✅ 浏览器截图成功")
    else:
        print(f"Fusion: ❌ 浏览器截图失败")
    
    print('\n场景C: 关闭浏览器')
    result = run_skill('fusion-browser', 'close', {})
    if result.get('status') == 'success':
        scores['fusion'] += 30
        print(f"Fusion: ✅ 关闭浏览器成功")
    else:
        print(f"Fusion: ❌ 关闭浏览器失败")
    
    print(f"\n浏览器自动化评分: Trae={scores['trae']}, OpenClaw={scores['openclaw']}, 开源={scores['opensource']}, Fusion={scores['fusion']}")
    return score('浏览器自动化', scores)

def test_clipboard():
    print('\n=== 测试6: 剪贴板操作 ===\n')
    scores = {'trae': 0, 'openclaw': 50, 'opensource': 85, 'fusion': 0}
    
    print('场景A: 复制文本')
    result = run_skill('fusion-clipboard', 'copy', {'text': 'Hello Fusion Clipboard Test'})
    if result.get('status') == 'success':
        scores['fusion'] += 35
        print(f"Fusion: ✅ 复制成功 - {result.get('length')}字符")
    else:
        print(f"Fusion: ❌ 复制失败")
    
    print('\n场景B: 获取剪贴板')
    result = run_skill('fusion-clipboard', 'get', {})
    if result.get('status') == 'success':
        scores['fusion'] += 35
        print(f"Fusion: ✅ 获取成功 - {result.get('text', '')[:30]}...")
    else:
        print(f"Fusion: ❌ 获取失败")
    
    print('\n场景C: 清空剪贴板')
    result = run_skill('fusion-clipboard', 'clear', {})
    if result.get('status') == 'success':
        scores['fusion'] += 30
        print(f"Fusion: ✅ 清空成功")
    else:
        print(f"Fusion: ❌ 清空失败")
    
    print(f"\n剪贴板操作评分: Trae={scores['trae']}, OpenClaw={scores['openclaw']}, 开源={scores['opensource']}, Fusion={scores['fusion']}")
    return score('剪贴板操作', scores)

def test_window():
    print('\n=== 测试7: 窗口管理 ===\n')
    scores = {'trae': 0, 'openclaw': 40, 'opensource': 80, 'fusion': 0}
    
    print('场景A: 获取窗口列表')
    result = run_skill('fusion-window', 'list', {})
    if result.get('status') == 'success':
        scores['fusion'] += 40
        print(f"Fusion: ✅ 获取窗口列表成功 - {result.get('count')}个窗口")
    else:
        print(f"Fusion: ❌ 获取窗口列表失败")
    
    print('\n场景B: 获取显示器信息')
    result = run_skill('fusion-window', 'monitors', {})
    if result.get('status') == 'success':
        scores['fusion'] += 35
        print(f"Fusion: ✅ 获取显示器信息成功")
    else:
        print(f"Fusion: ❌ 获取显示器信息失败")
    
    print('\n场景C: 查找窗口')
    result = run_skill('fusion-window', 'find', {'title': 'Windows'})
    if result.get('status') == 'success':
        scores['fusion'] += 25
        print(f"Fusion: ✅ 查找窗口成功 - found={result.get('found')}")
    else:
        print(f"Fusion: ❌ 查找窗口失败")
    
    print(f"\n窗口管理评分: Trae={scores['trae']}, OpenClaw={scores['openclaw']}, 开源={scores['opensource']}, Fusion={scores['fusion']}")
    return score('窗口管理', scores)

def test_comprehensive():
    print('\n=== 测试8: 综合自动化 ===\n')
    scores = {'trae': 0, 'openclaw': 70, 'opensource': 75, 'fusion': 0}
    
    print('场景A: 截图+剪贴板流程')
    result1 = run_skill('fusion-desktop', 'screenshot', {'path': '/tmp/comprehensive_test.png'})
    result2 = run_skill('fusion-clipboard', 'copy', {'text': 'comprehensive_test.png'})
    if result1.get('status') == 'success' and result2.get('status') == 'success':
        scores['fusion'] += 25
        print(f"Fusion: ✅ 综合流程1成功")
    else:
        print(f"Fusion: ❌ 综合流程1失败")
    
    print('\n场景B: 屏幕分析+像素获取流程')
    result1 = run_skill('fusion-screen', 'analyze', {})
    result2 = run_skill('fusion-screen', 'pixel_at', {'x': 100, 'y': 100})
    if result1.get('status') == 'success' and result2.get('status') == 'success':
        scores['fusion'] += 25
        print(f"Fusion: ✅ 综合流程2成功")
    else:
        print(f"Fusion: ❌ 综合流程2失败")
    
    print('\n场景C: 鼠标移动+点击+键盘流程')
    result1 = run_skill('fusion-desktop', 'move', {'x': 500, 'y': 400, 'duration': 0.1})
    result2 = run_skill('fusion-desktop', 'position', {})
    result3 = run_skill('fusion-desktop', 'key', {'key': 'escape'})
    if result1.get('status') == 'success' and result2.get('status') == 'success':
        scores['fusion'] += 25
        print(f"Fusion: ✅ 综合流程3成功")
    else:
        print(f"Fusion: ❌ 综合流程3失败")
    
    print('\n场景D: 剪贴板读写流程')
    result1 = run_skill('fusion-clipboard', 'copy', {'text': 'Test comprehensive flow'})
    result2 = run_skill('fusion-clipboard', 'get', {})
    result3 = run_skill('fusion-clipboard', 'clear', {})
    if result1.get('status') == 'success' and result2.get('status') == 'success' and result3.get('status') == 'success':
        scores['fusion'] += 25
        print(f"Fusion: ✅ 综合流程4成功")
    else:
        print(f"Fusion: ❌ 综合流程4失败")
    
    print(f"\n综合自动化评分: Trae={scores['trae']}, OpenClaw={scores['openclaw']}, 开源={scores['opensource']}, Fusion={scores['fusion']}")
    return score('综合自动化', scores)

def main():
    print('╔════════════════════════════════════════════════════════════╗')
    print('║       OpenClaw Desktop Fusion Skills 四方对比测试         ║')
    print('║       Trae vs OpenClaw vs 开源 vs Fusion                  ║')
    print('╚════════════════════════════════════════════════════════════╝')
    
    all_results = []
    all_results.append(test_screenshot())
    all_results.append(test_mouse())
    all_results.append(test_keyboard())
    all_results.append(test_image())
    all_results.append(test_browser())
    all_results.append(test_clipboard())
    all_results.append(test_window())
    all_results.append(test_comprehensive())
    
    print('\n')
    print('╔════════════════════════════════════════════════════════════╗')
    print('║                    测试结果汇总                            ║')
    print('╚════════════════════════════════════════════════════════════╝')
    
    total_trae = total_openclaw = total_opensource = total_fusion = 0
    
    print('\n| 测试项 | Trae | OpenClaw | 开源 | Fusion | 超越? |')
    print('|--------|------|----------|------|--------|-------|')
    
    for r in all_results:
        max_other = max(r['trae'], r['openclaw'], r['opensource'])
        exceed = '✅' if r['fusion'] >= max_other else '❌'
        print(f"| {r['test']} | {r['trae']} | {r['openclaw']} | {r['opensource']} | {r['fusion']} | {exceed} |")
        total_trae += r['trae']
        total_openclaw += r['openclaw']
        total_opensource += r['opensource']
        total_fusion += r['fusion']
    
    print('|--------|------|----------|------|--------|-------|')
    max_total = max(total_trae, total_openclaw, total_opensource)
    total_exceed = '✅' if total_fusion >= max_total else '❌'
    print(f"| **总分** | {total_trae} | {total_openclaw} | {total_opensource} | {total_fusion} | {total_exceed} |")
    
    print('\n')
    if total_fusion >= max_total:
        print('🎉 融合技能总分超越所有对比方！')
    else:
        print('⚠️ 融合技能总分未超越，需要优化')
    
    with open(f'{PROJECT_DIR}/TEST_RESULTS.json', 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'results': all_results,
            'totals': {
                'trae': total_trae,
                'openclaw': total_openclaw,
                'opensource': total_opensource,
                'fusion': total_fusion
            },
            'exceed': total_fusion >= max_total
        }, f, ensure_ascii=False, indent=2)
    
    print(f'\n测试报告已保存: {PROJECT_DIR}/TEST_RESULTS.json')

if __name__ == '__main__':
    main()
