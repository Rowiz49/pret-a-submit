from django.shortcuts import render
from ..forms import PaperUploadForm
import pymupdf4llm
import pymupdf

def index(request):
    if request.method == 'POST':
        form = PaperUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Access cleaned data
            conference = form.cleaned_data['conference']
            ollama_url = form.cleaned_data['ollama_url']
            ollama_model = form.cleaned_data['ollama_model']
            ollama_api_key = form.cleaned_data['ollama_api_key']
            pdf_file = form.cleaned_data['files']
            
            print(conference, ollama_url, ollama_model, ollama_api_key, pdf_file)
            pdf_file.seek(0)
            doc = pymupdf.open(stream=pdf_file.read(), filetype="pdf")
            md_text = pymupdf4llm.to_markdown(doc)
            doc.close()
            return render(request, 'paper_grader/pdf.html', {"text": md_text})
    else:
        form = PaperUploadForm()
    
    return render(request, 'paper_grader/index.html', {
        'form': form,
    })


