import shutil

import streamlit as st
import PyPDF2 as pdf
import os
import zipfile

def add_multiple_files_to_zip(zip_file_path, files_to_add):
    with zipfile.ZipFile(zip_file_path, 'a') as zip_ref:
        for file in files_to_add:
            zip_ref.write(file)
    return True


def render_test():

    file_lst = []

    uploaded_file = st.file_uploader("Загрузить пдф", type=["pdf"])

    if uploaded_file:
        reader = pdf.PdfReader(uploaded_file)
        st.write(f'Количество страниц в файле: {len(reader.pages)}')

        try:
            os.mkdir('temp')
        except:
            pass

        try:
            os.remove('result/output_archive.zip')
        except:
            pass

        for i in range(len(reader.pages)):
            text = reader.pages[i].extract_text()
            check_for_ozon = text.split()[1]

            check_for_sber = text.split()[1]

            if check_for_ozon == 'FBS:':
                marketplace = 'ozon'

                filename = text.split()[3]
                obj = reader.pages[i]
                output_pdf = pdf.PdfWriter()
                output_pdf.add_page(obj)

                with open(fr'temp/{marketplace}_{filename}.pdf', "wb") as writefile:
                    output_pdf.write(writefile)
                    file_lst.append(f'temp/{marketplace}_{filename}.pdf')

            elif check_for_sber == 'Дата':
                marketplace = 'sber'

                filename = text.split()[0]
                obj = reader.pages[i]
                output_pdf = pdf.PdfWriter()
                output_pdf.add_page(obj)

                with open(fr'temp/{marketplace}_{filename}.pdf', "wb") as writefile:
                    output_pdf.write(writefile)
                    file_lst.append(f'temp/{marketplace}_{filename}.pdf')


            elif len(text.split()) == 2:
                marketplace = 'wb'

                filename = f'{text.split()[0]}_{text.split()[1]}'

                obj = reader.pages[i]
                output_pdf = pdf.PdfWriter()
                output_pdf.add_page(obj)

                with open(fr'temp/{marketplace}_{filename}.pdf', "wb") as writefile:
                    output_pdf.write(writefile)
                    file_lst.append(f'temp/{marketplace}_{filename}.pdf')

            else:
                marketplace = 'yandex_'

                filename = text.split()[0]
                obj = reader.pages[i]
                output_pdf = pdf.PdfWriter()
                output_pdf.add_page(obj)

                with open(fr'temp/{marketplace}_{filename}.pdf', "wb") as writefile:
                    output_pdf.write(writefile)
                    file_lst.append(f'temp/{marketplace}_{filename}.pdf')

        flag = add_multiple_files_to_zip('result/output_archive.zip', file_lst)


        if flag:
            shutil.rmtree('temp')

            with open("result/output_archive.zip", "rb") as file:
                btn = st.download_button(
                    label="Скачать zip-архив",
                    data=file,
                    file_name="result/output_archive.zip",
                    mime="application/zip",
                    use_container_width=True
                )