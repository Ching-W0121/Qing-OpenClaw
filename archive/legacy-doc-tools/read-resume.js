const fs = require('fs');
const path = require('path');
const pdfjsLib = require('pdfjs-dist');

const pdfPath = 'C:/Users/TR/Desktop/王庆个人简历.pdf';
const data = new Uint8Array(fs.readFileSync(pdfPath));

// 设置 worker
pdfjsLib.GlobalWorkerOptions.workerSrc = path.join(__dirname, 'node_modules', 'pdfjs-dist', 'build', 'pdf.worker.js');

async function extractText() {
    try {
        const pdf = await pdfjsLib.getDocument({ data }).promise;
        console.log('=== 王庆简历内容 ===\n');
        console.log('页数:', pdf.numPages);
        
        let fullText = '';
        for (let i = 1; i <= pdf.numPages; i++) {
            const page = await pdf.getPage(i);
            const textContent = await page.getTextContent();
            const pageText = textContent.items.map(item => item.str).join(' ');
            fullText += pageText + '\n';
        }
        
        console.log(fullText);
    } catch (err) {
        console.error('错误:', err.message);
    }
}

extractText();
