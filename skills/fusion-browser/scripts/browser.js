const { chromium } = require('playwright');
const fs = require('fs');

let browser = null;
let page = null;

async function open(params) {
    const url = params.url || 'https://example.com';
    const headless = params.headless !== false;
    
    try {
        browser = await chromium.launch({
            headless: headless,
            args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
        });
        page = await browser.newPage();
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
        const title = await page.title();
        return {
            status: 'success',
            action: 'open',
            url: url,
            title: title
        };
    } catch (e) {
        return { status: 'error', action: 'open', message: e.message };
    }
}

async function screenshot(params) {
    const path = params.path || '/tmp/browser_screenshot.png';
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
