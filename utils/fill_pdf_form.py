from pdfrw import PdfWriter, PdfReader as PdfFormReader, PdfDict, PdfName, PdfString

def fill_pdf_form(template_path, parsed_data):
    reader = PdfFormReader(template_path)
    writer = PdfWriter()

    for page in reader.pages:
        annotations = page['/Annots']
        if annotations:
            for annotation in annotations:
                if '/T' in annotation:
                    field_name = annotation.get('/T')[1:-1]  # Extract field name, strip the surrounding quotes
                    if field_name in parsed_data:
                        annotation.update({
                            PdfName('/V'): PdfString(parsed_data[field_name])
                        })
        writer.addpage(page)
    
    output_path = template_path.replace('.pdf', '_filled.pdf')
    writer.write(output_path)
    return output_path
