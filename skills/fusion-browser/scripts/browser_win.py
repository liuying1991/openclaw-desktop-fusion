import json
import sys
import os
import subprocess
import tempfile

def run_browser_action(action, params):
    script_content = '''
const { chromium } = require('playwright');

let browser = null;
let page = null;

async function open(params) {
    const url = params.url || 'https://example.com';
    const headless = params.headless !== false;
    
    try {
        browser = await chromium.launch({
            headless: headless,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        page = await browser.newPage();
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
        const title = await page.title();
        return {
            status: 'success',
            action: 'open',
            url: url,
            title: title
        };
    } catch (e) {
        if (browser) {
            try { await browser.close(); } catch {}
        }
        return { status: 'error', action: 'open', message: e.message };
    }
}

async function screenshot(params) {
    const path = params.path || 'C:/tmp/browser_screenshot.png';
    try {
        if (!page) {
            return { status: 'error', action: 'screenshot', message: 'No page open' };
        }
        await page.screenshot({ path: path, fullPage: false });
        return {
            status: 'success',
            action: 'screenshot',
            path: path
        };
    } catch (e) {
        return { status: 'error', action: 'screenshot', message: e.message };
    }
}

async function close(params) {
    try {
        if (browser) {
            await browser.close();
            browser = null;
            page = null;
        }
        return { status: 'success', action: 'close' };
    } catch (e) {
        return { status: 'error', action: 'close', message: e.message };
    }
}

async function main() {
    const action = process.argv[2];
    let params = {};
    if (process.argv[3]) {
        try {
            const fs = require('fs');
            if (fs.existsSync(process.argv[3])) {
                params = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
            } else {
                params = JSON.parse(process.argv[3]);
            }
        } catch (e) {
            params = {};
        }
    }

    let result;
    switch (action) {
        case 'open':
            result = await open(params);
            break;
        case 'screenshot':
            result = await screenshot(params);
            break;
        case 'close':
            result = await close(params);
            break;
        default:
            result = { status: 'error', message: 'Unknown action: ' + action };
    }
    console.log(JSON.stringify(result, null, 2));
}

main().catch(e => {
    console.log(JSON.stringify({ status: 'error', message: e.message }));
    process.exit(1);
});
'''
    
    script_path = 'C:/tmp/browser_automation.js'
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    params_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, dir='C:/tmp')
    json.dump(params, params_file)
    params_file.close()
    
    try:
        result = subprocess.run(
            ['node', script_path, action, params_file.name],
            capture_output=True, text=True, timeout=60
        )
        try:
            os.unlink(params_file.name)
        except:
            pass
        
        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except:
                return {'status': 'error', 'output': result.stdout}
        else:
            return {'status': 'error', 'message': result.stderr[:500] if result.stderr else 'Unknown error'}
    except subprocess.TimeoutExpired:
        return {'status': 'error', 'message': 'Timeout'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def main():
    if len(sys.argv) < 2:
        print(json.dumps({'status': 'error', 'message': 'Usage: python browser_win.py <action> [params]'}))
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
    
    result = run_browser_action(action, params)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
