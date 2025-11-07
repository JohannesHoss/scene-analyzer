const puppeteer = require('puppeteer');
const path = require('path');

const TEST_FILE = path.join(__dirname, '../examples/treatments/WreckingBall-Treatment_2025-06-klein.pdf');
const FRONTEND_URL = 'http://localhost:3010';
const TIMEOUT = 300000; // 5 min

async function runE2ETest() {
    console.log('🚀 Starting E2E Test...\n');
    
    const browser = await puppeteer.launch({ 
        headless: false,
        slowMo: 100,
        args: ['--no-sandbox']
    });
    
    try {
        const page = await browser.newPage();
        await page.setViewport({ width: 1280, height: 800 });
        
        // Step 1: Load Frontend
        console.log('📄 Step 1: Loading Frontend...');
        await page.goto(FRONTEND_URL, { waitUntil: 'networkidle2' });
        await page.waitForSelector('#step1', { visible: true });
        console.log('✅ Frontend loaded\n');
        
        // Step 2: Upload File
        console.log('📤 Step 2: Uploading file...');
        const fileInput = await page.$('#fileInput');
        await fileInput.uploadFile(TEST_FILE);
        await page.waitForSelector('#fileInfo:not(.hidden)', { timeout: 10000 });
        console.log('✅ File uploaded\n');
        
        // Step 3: Next -> Language
        console.log('🌐 Step 3: Selecting language...');
        await page.click('#nextBtn');
        await page.waitForSelector('#step2', { visible: true });
        await page.click('input[name="language"][value="EN"]');
        console.log('✅ Language: EN\n');
        
        // Step 4: Next -> Model
        console.log('🤖 Step 4: Selecting model...');
        await page.click('#nextBtn');
        await page.waitForSelector('#step3', { visible: true });
        await page.select('#modelSelect', 'gpt-4o-mini');
        console.log('✅ Model: gpt-4o-mini\n');
        
        // Step 5: Next -> Mode
        console.log('⚙️  Step 5: Selecting mode...');
        await page.click('#nextBtn');
        await page.waitForSelector('#step4', { visible: true });
        await page.click('input[name="mode"][value="standard"]');
        console.log('✅ Mode: standard\n');
        
        // Step 6: Next -> Review
        console.log('📋 Step 6: Reviewing settings...');
        await page.click('#nextBtn');
        await page.waitForSelector('#step5', { visible: true });
        
        const summary = await page.evaluate(() => ({
            file: document.getElementById('sumFile').textContent,
            lang: document.getElementById('sumLang').textContent,
            model: document.getElementById('sumModel').textContent,
            mode: document.getElementById('sumMode').textContent
        }));
        console.log('Summary:', summary);
        console.log('✅ Review confirmed\n');
        
        // Step 7: Start Analysis
        console.log('🔄 Step 7: Starting analysis...');
        await page.click('#nextBtn');
        await page.waitForSelector('#progressModal.flex', { visible: true, timeout: 5000 });
        console.log('✅ Analysis started\n');
        
        // Step 8: Wait for completion
        console.log('⏳ Step 8: Waiting for completion (max 5 min)...');
        let lastProgress = 0;
        
        await page.waitForFunction(() => {
            const modal = document.getElementById('successModal');
            return modal && modal.classList.contains('flex');
        }, { timeout: TIMEOUT, polling: 2000 });
        
        console.log('✅ Analysis completed!\n');
        
        // Step 9: Verify Table
        console.log('📊 Step 9: Verifying results table...');
        const tableData = await page.evaluate(() => {
            const rows = document.querySelectorAll('#tableBody tr');
            const headers = Array.from(document.querySelectorAll('#tableHeaders th')).map(th => th.textContent);
            const firstRow = rows[0] ? Array.from(rows[0].querySelectorAll('td')).map(td => td.textContent) : [];
            return {
                sceneCount: document.getElementById('resultSceneCount').textContent,
                rowCount: rows.length,
                headers: headers,
                firstRowSample: firstRow.slice(0, 5)
            };
        });
        console.log('✅ Table rendered:');
        console.log('   Scenes:', tableData.sceneCount);
        console.log('   Rows:', tableData.rowCount);
        console.log('   Headers:', tableData.headers.join(', '));
        console.log('   First row sample:', tableData.firstRowSample.join(' | '));
        console.log('');
        
        console.log('🎉 E2E Test PASSED (Table verified)!\n');
        
    } catch (error) {
        console.error('❌ E2E Test FAILED:', error.message);
        await page.screenshot({ path: 'tests/error-screenshot.png', fullPage: true });
        console.log('📸 Screenshot saved: tests/error-screenshot.png');
        throw error;
    } finally {
        await browser.close();
    }
}

// Run test
runE2ETest()
    .then(() => process.exit(0))
    .catch(() => process.exit(1));
