# -*- coding: utf-8 -*-

from xlrd import open_workbook
import erppeek
URL = 'http://localhost:8069'
    
#remoteClient = erppeek.Client(URL, 'career', 'admin', '123456')
#cat_obj =  remoteClient.model('career.question_category')
#question_obj =  remoteClient.model('career.question')

wb = open_workbook('E:\\tmp\question3.xlsx')
#wb = open_workbook('F:\\Testbed\\ribbon.xls')
i = 1
j=1
prev_cat = ""
for s in wb.sheets():
        for row in range(s.nrows):
            category = (s.cell(row,0).value).strip()
            if category:
                category =  category.strip()
                prev_cat = 'career.question_category_%d' % i
                print "<record model='career.question_category' id='%s'>" %prev_cat
                print "<field name='title'>%s</field>"%category
                print "</record>"
                i = i+1
            question = (s.cell(row,1).value).strip()
            print "<record model='career.question' id='career.question_%d'>" %j
            j= j+1
            print "<field name='title'>%s</field>"%question
            print "<field name='category_id' ref='%s'/>"%prev_cat
            print "</record>"

    