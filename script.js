// PDF.js initialization
const templateCanvas = document.getElementById('template-canvas');
const sourceCanvas = document.getElementById('source-canvas');
const ocrOutput = document.getElementById('ocr-output');
const extractOcrBtn = document.getElementById('extract-ocr');

document.getElementById('template-file').addEventListener('change', handleFileUpload.bind(null, 'template'));
document.getElementById('source-file').addEventListener('change', handleFileUpload.bind(null, 'source'));

function handleFileUpload(type, event) {
    const file = event.target.files[0];
    if (file) {
        const fileType = file.type;

        if (fileType === 'application/pdf') {
            renderPdf(file, type === 'template' ? templateCanvas : sourceCanvas);
        } else if (fileType === 'image/jpeg' || fileType === 'image/png') {
            renderImage(file, type === 'template' ? templateCanvas : sourceCanvas);
        }
    }
}

function renderPdf(file, canvas) {
    const reader = new FileReader();
    reader.onload = function (event) {
        const typedArray = new Uint8Array(event.target.result);
        pdfjsLib.getDocument(typedArray).promise.then(function (pdfDoc_) {
            pdfDoc_.getPage(1).then(function (page) {
                const context = canvas.getContext('2d');
                const viewport = page.getViewport({ scale: 1 });
                canvas.height = viewport.height;
                canvas.width = viewport.width;
                page.render({
                    canvasContext: context,
                    viewport: viewport
                });
            });
        });
    };
    reader.readAsArrayBuffer(file);
}

function renderImage(file, canvas) {
    const reader = new FileReader();
    reader.onload = function (event) {
        const img = new Image();
        img.onload = function () {
            const context = canvas.getContext('2d');
            canvas.width = img.width;
            canvas.height = img.height;
            context.drawImage(img, 0, 0);
        };
        img.src = event.target.result;
    };
    reader.readAsDataURL(file);
}

extractOcrBtn.addEventListener('click', function () {
    const fileInput = document.getElementById('source-file');
    const file = fileInput.files[0];
    if (file) {
        const fileType = file.type;
        
        if (fileType === 'application/pdf') {
            extractOcrFromPdf(file);
        } else if (fileType === 'image/jpeg' || fileType === 'image/png') {
            extractOcrFromImage(file);
        }
    }
});

function extractOcrFromPdf(file) {
    const reader = new FileReader();
    reader.onload = function (event) {
        const typedArray = new Uint8Array(event.target.result);
        pdfjsLib.getDocument(typedArray).promise.then(function (pdfDoc_) {
            pdfDoc_.getPage(1).then(function (page) {
                const canvas = document.createElement('canvas');
                const context = canvas.getContext('2d');
                const viewport = page.getViewport({ scale: 1 });
                canvas.height = viewport.height;
                canvas.width = viewport.width;
                page.render({
                    canvasContext: context,
                    viewport: viewport
                }).promise.then(function () {
                    performOcr(canvas);
                });
            });
        });
    };
    reader.readAsArrayBuffer(file);
}

function extractOcrFromImage(file) {
    const reader = new FileReader();
    reader.onload = function (event) {
        const img = new Image();
        img.onload = function () {
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            canvas.width = img.width;
            canvas.height = img.height;
            context.drawImage(img, 0, 0);
            performOcr(canvas);
        };
        img.src = event.target.result;
    };
    reader.readAsDataURL(file);
}

function performOcr(canvas) {
    Tesseract.recognize(
        canvas,
        'eng',
        {
            logger: info => console.log(info)
        }
    ).then(({ data: { text } }) => {
        const keyValuePairs = extractKeyValuePairs(text);
        ocrOutput.innerHTML = formatKeyValuePairs(keyValuePairs);
    });
}

function extractKeyValuePairs(text) {
    const lines = text.split('\n');
    const keyValuePairs = [];

    lines.forEach(line => {
        const separator = line.indexOf(':');
        if (separator !== -1) {
            const key = line.substring(0, separator).trim();
            const value = line.substring(separator + 1).trim();
            keyValuePairs.push({ key, value });
        } else {
            const match = line.match(/(\w+)\s+(.+)/);
            if (match) {
                keyValuePairs.push({ key: match[1], value: match[2] });
            }
        }
    });

    return keyValuePairs;
}

function formatKeyValuePairs(keyValuePairs) {
    let formattedText = '<ul>';
    keyValuePairs.forEach(pair => {
        formattedText += `<li><strong>${pair.key}:</strong> ${pair.value}</li>`;
    });
    formattedText += '</ul>';
    return formattedText;
}
