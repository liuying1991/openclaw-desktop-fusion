const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

let browser = null;
let page = null;

async function open(params) {
    const { url, headless = true } = params;
    try {
        browser = await chromium.launch({
            headless,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        page = await browser.newPage({
            viewport: { width: 1920, height: 1080 }
        });
        await page.goto(url, { waitUntil: 'networkidle' });
        return {
            status: 'success',
            action: 'open',
            url,
            title: await page.title()
        };
    } catch (e) {
        return { status: 'error', action: 'open', message: e.message };
    }
}

async function screenshot(params) {
    const { path: savePath = 'C:/tmp/screenshot.png', fullPage = true } = params;
    try {
        if (!page) return { status: 'error', message: 'No page open' };
        await page.screenshot({ path: savePath, fullPage });
        return {
            status: 'success',
            action: 'screenshot',
            path: savePath,
            fullPage
        };
    } catch (e) {
        return { status: 'error', action: 'screenshot', message: e.message };
    }
}

async function title() {
    try {
        if (!page) return { status: 'error', message: 'No page open' };
        return {
            status: 'success',
            action: 'title',
            title: await page.title()
        };
    } catch (e) {
        return { status: 'error', action: 'title', message: e.message };
    }
}

async function click(params) {
    const { selector, timeout = 5000 } = params;
    try {
        if (!page) return { status: 'error', message: 'No page open' };
        await page.click(selector, { timeout });
        return { status: 'success', action: 'click', selector };
    } catch (e) {
        return { status: 'error', action: 'click', message: e.message };
    }
}

async function type(params) {
    const { selector, text, timeout = 5000 } = params;
    try {
        if (!page) return { status: 'error', message: 'No page open' };
        await page.fill(selector, text, { timeout });
        return { status: 'success', action: 'type', selector, text };
    } catch (e) {
        return { status: 'error', action: 'type', message: e.message };
    }
}

async function wait(params) {
    const { selector, timeout = 5000 } = params;
    try {
        if (!page) return { status: 'error', message: 'No page open' };
        await page.waitForSelector(selector, { timeout });
        return { status: 'success', action: 'wait', selector };
    } catch (e) {
        return { status: 'error', action: 'wait', message: e.message };
    }
}

async function search(params) {
    const { engine = 'baidu', query } = params;
    const engines = {
        baidu: { url: 'https://www.baidu.com', input: '#kw', form: '#form' },
        bing: { url: 'https://www.bing.com', input: '#sb_form_q', form: '#sb_form' },
        google: { url: 'https://www.google.com', input: 'input[name="q"]', form: 'form' }
    };
    try {
        const eng = engines[engine] || engines.baidu;
        browser = await chromium.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        page = await browser.newPage({
            viewport: { width: 1920, height: 1080 }
        });
        await page.goto(eng.url, { waitUntil: 'networkidle' });
        await page.fill(eng.input, query);
        await page.press(eng.input, 'Enter');
        await page.waitForLoadState('networkidle');
        return {
            status: 'success',
            action: 'search',
            engine,
            query,
            title: await page.title()
        };
    } catch (e) {
        return { status: 'error', action: 'search', message: e.message };
    }
}

async function close() {
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

async function getContent(params) {
    const { selector } = params;
    try {
        if (!page) return { status: 'error', message: 'No page open' };
        let content;
        if (selector) {
            content = await page.textContent(selector);
        } else {
            content = await page.content();
        }
        return { status: 'success', action: 'getContent', content: content.substring(0, 5000) };
    } catch (e) {
        return { status: 'error', action: 'getContent', message: e.message };
    }
}

async function main() {
    const args = process.argv.slice(2);
    if (args.length < 1) {
        console.log(JSON.stringify({ status: 'error', message: 'Usage: node browser.js <action> [params]' }));
        process.exit(1);
    }
    
    const action = args[0];
    let params = {};
    if (args.length > 1) {
        try {
            if (fs.existsSync(args[1])) {
                params = JSON.parse(fs.readFileSync(args[1], 'utf-8'));
            } else {
                params = JSON.parse(args[1]);
            }
        } catch (e) {
            params = {};
        }
    }
    
    const actions = {
        open, screenshot, title, click, type, wait, search, close, getContent
    };
    
    let result;
    if (actions[action]) {
        result = await actions[action](params);
    } else {
        result = { status: 'error', message: `Unknown action: ${action}` };
    }
    
    console.log(JSON.stringify(result, null, 2));
}

main();
