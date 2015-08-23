from PyPDF2 import PdfFileReader, PdfFileWriter
import os

for fileName in os.listdir('.'):
    if fileName.lower().endswith(".pdf"):
        #print("trying " + fileName)
        f = open(fileName, "rb")
        print(type(f))
        input1 = PdfFileReader(f)
        #input1 = PdfFileReader(fileName)
        if input1.isEncrypted:
            input1.decrypt('')
        # print the title of document1.pdf
        print('##1: ' + fileName + '; ##2: ' + input1.getDocumentInfo().title)
