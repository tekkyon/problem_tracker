import streamlit as st
# import pandas as pd
#
# from bitrix24_funcs import init_stickers

st.set_page_config(page_title='placeholder',
                   layout='wide',
                   initial_sidebar_state='collapsed',
                   page_icon=':seedling:')

with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

# cfg = {
#     'Ссылка на этикетку': st.column_config.LinkColumn(
#         'Ссылка на этикетку'
#     )
# }
#
# if st.button('get'):
#     temp_dict = init_stickers()
#     result = pd.DataFrame.from_dict(temp_dict, orient="index")
#
#     st.dataframe(result,
#                  use_container_width=True,
#                  column_config=cfg)

import shutil
import time

import streamlit as st
import PyPDF2 as pdf
import os
import zipfile

def render_test():
    def add_multiple_files_to_zip(zip_file_path, files_to_add):
        with zipfile.ZipFile(zip_file_path, 'a') as zip_ref:
            for file in files_to_add:
                zip_ref.write(file)
        return True

    file_lst = []

    uploaded_file = st.file_uploader("Загрузить пдф", type=["pdf"], label_visibility='collapsed')

    if uploaded_file:
        reader = pdf.PdfReader(uploaded_file)
        page_qny = len(reader.pages)
        st.write(f'Количество страниц в файле: {page_qny}')

        try:
            os.mkdir('temp')
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
                marketplace = 'yandex'

                filename = text.split()[0]
                obj = reader.pages[i]
                output_pdf = pdf.PdfWriter()
                output_pdf.add_page(obj)

                with open(fr'temp/{marketplace}_{filename}.pdf', "wb") as writefile:
                    output_pdf.write(writefile)
                    file_lst.append(f'temp/{marketplace}_{filename}.pdf')

        zip_archive_name = f'labels_{marketplace}_{page_qny}' + '.zip'
        flag = add_multiple_files_to_zip(zip_archive_name, file_lst)
        shutil.rmtree('temp')

        if flag:
            with open(f'{zip_archive_name}', "rb") as file:
                btn = st.download_button(
                    label="Скачать zip-архив",
                    data=file,
                    file_name=f'{zip_archive_name}',
                    mime="application/zip",
                    use_container_width=True
                )

    else:
        my_dir = './'
        for fname in os.listdir(my_dir):
            if fname.startswith("labels_"):
                os.remove(os.path.join(my_dir, fname))


render_test()

