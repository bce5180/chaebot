import os
from fpdf import FPDF

def convert_mp3_to_pdf(mp3_file_path, pdf_file_path):
    # PDF 파일을 저장할 디렉토리 생성
    os.makedirs(os.path.dirname(pdf_file_path), exist_ok=True)

    # 임시로 MP3 파일 이름을 PDF에 작성하는 예제
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # MP3 파일 이름을 PDF에 추가
    pdf.cell(200, 10, txt=os.path.basename(mp3_file_path), ln=True, align='C')
    
    # PDF 저장
    pdf.output(pdf_file_path)

    return pdf_file_path
