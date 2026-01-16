import fitz

def load_pdf(file_path:str) -> str:
    reader=fitz.open(file_path)
    text=""
    print("load pdf called")
    for page in reader:
        text+=page.get_text()+" "

    print(text)

    return text