import csv
import json
import xlrd
#csvfile = open('creditcard_kaggle_dataset.numbers', 'r')
#for line in csvfile:
 #          print line,
#csvfile.close()


def open_file(path):
    """
    Open and read an Excel file
    """
    print('Opening file')
    book = xlrd.open_workbook(path)
    worksheet = book.sheet_by_index(0)
    num_rows = worksheet.nrows - 1
    num_cells = worksheet.ncols - 1
    curr_row = -1
    header_row=worksheet.row(1)
    row_dict = {}
    while curr_row < num_rows:
        curr_row += 1
        row = worksheet.row(curr_row)
        print 'Row:', curr_row
        curr_cell = -1
        while curr_cell < num_cells:
            curr_cell += 1
            # Cell Types: 0=Empty, 1=Text, 2=Number, 3=Date, 4=Boolean, 5=Error, 6=Blank
            cell_type = worksheet.cell_type(curr_row, curr_cell)
            cell_value = worksheet.cell_value(curr_row, curr_cell)
            row_dict[worksheet.cell_value(1,curr_cell)]=cell_value
          #  print ' ', cell_type, ':', cell_value
        print(json.dumps(row_dict))


open_file('../simple_wine.xlsx')