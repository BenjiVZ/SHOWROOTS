const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
  const htmlPath = path.resolve(__dirname, 'RESUMEN_PULSAR.html');
  const pdfPath = path.resolve(__dirname, 'RESUMEN_PULSAR.pdf');

  console.log('Abriendo navegador...');
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();

  // Load the HTML file
  await page.goto(`file:///${htmlPath.replace(/\\/g, '/')}`, {
    waitUntil: 'networkidle0',
    timeout: 30000,
  });

  // Wait for fonts to load
  await page.evaluateHandle('document.fonts.ready');

  console.log('Generando PDF...');
  await page.pdf({
    path: pdfPath,
    format: 'A4',
    margin: { top: '20mm', right: '18mm', bottom: '20mm', left: '18mm' },
    printBackground: true,
    preferCSSPageSize: true,
  });

  await browser.close();
  console.log(`✅ PDF generado: ${pdfPath}`);
})();
