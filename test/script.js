const express = require('express');
const multer = require('multer');
const { PDFDocument } = require('pdf-lib');
const T = require('tesseract.js');
const fs = require('fs');
const { createCanvas } = require('canvas');
const pdfjsLib = require('pdfjs-dist/legacy/build/pdf');
const path = require('path');

const app = express();
const upload = multer({ dest: 'uploads/' });

// Helper function to extract text from PDF
async function extractTextFromPDF(pdfPath) {
    const pdf = await pdfjsLib.getDocument(pdfPath).promise;
    const numPages = pdf.numPages;
    let recognizedText = '';

    for (let pageNum = 1; pageNum <= numPages; pageNum++) {
        const page = await pdf.getPage(pageNum);
        const viewport = page.getViewport({ scale: 2.0 });

        const canvas = createCanvas(viewport.width, viewport.height);
        const context = canvas.getContext('2d');
        await page.render({ canvasContext: context, viewport }).promise;

        const imgData = canvas.toBuffer();
        const out = await T.recognize(imgData, 'eng', { logger: e => console.log(e) });
        recognizedText += out.data.text + '\n';
    }

    return recognizedText;
}

// Helper function to fill PDF form
async function fillPDF(templatePath, data) {
    const existingPdfBytes = fs.readFileSync(templatePath);
    const pdfDoc = await PDFDocument.load(existingPdfBytes);

    const form = pdfDoc.getForm();
    const formFields = form.getFields();
    formFields.forEach(field => {
        const fieldName = field.getName();
        if (data.hasOwnProperty(fieldName)) {
            field.setText(data[fieldName] || '');
        }
    });

    const pdfBytes = await pdfDoc.save();
    return pdfBytes;
}

// Route to handle file processing
app.post('/process-files', upload.fields([{ name: 'templateFile' }, { name: 'infoFile' }]), async (req, res) => {
    const { templateFile, infoFile } = req.files;

    try {
        // Path to uploaded files
        const templatePath = path.join(__dirname, templateFile[0].path);
        const infoPath = path.join(__dirname, infoFile[0].path);

        let data = {};

        // Check file type of the info file
        if (infoFile[0].mimetype === 'application/pdf') {
            // Extract text from the PDF and convert to key-value pairs
            const extractedText = await extractTextFromPDF(infoPath);
            data = extractKeyValuePairs(extractedText);
        } else if (infoFile[0].mimetype === 'text/csv') {
            // Parse CSV (you can add CSV parsing logic here)
            // For simplicity, use hardcoded data or implement CSV parsing
            data = { customer_id: '123', address: 'Example Street', price: '100' };
        }

        // Fill the PDF template with the extracted or CSV data
        const filledPdfBytes = await fillPDF(templatePath, data);

        // Send the filled PDF to the client (or save it on the server)
        res.contentType('application/pdf');
        res.send(filledPdfBytes);
    } catch (error) {
        console.error('Error processing files:', error);
        res.status(500).json({ success: false, message: 'Internal server error' });
    } finally {
        // Clean up uploaded files
        fs.unlinkSync(templatePath);
        fs.unlinkSync(infoPath);
    }
});

app.listen(3000, () => console.log('Server running on http://localhost:3000'));