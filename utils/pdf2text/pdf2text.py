# -*- coding: utf-8 -*-
# @createTime    : 2020/5/7 17:22
# @author  : Huanglg
# @fileName: pdf2text.py
# @email: luguang.huang@mabotech.com
import pdf2image
import uuid


class Pdf2Text(object):

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def pdf2images(self, dpi=400, thread_count=4, fmt='png', output_folder=None, output_file=str(uuid.uuid4())):
        """

        :param dpi:
        :param thread_count:
        :param fmt:
        :param output_folder:
        :param output_file: []
        :return:
        """
        return pdf2image.convert_from_path(self.pdf_path,
                                           dpi=dpi,
                                           thread_count=thread_count,
                                           fmt=fmt,
                                           output_folder=output_folder,
                                           output_file=output_file)


if __name__ == '__main__':
    pdf2text = Pdf2Text(pdf_path='F:/code/PDFRecognition/example/19.03.10 20099B .PDF')
    pdf2text.pdf2images(output_folder='F:/code/PDFRecognition/images')
