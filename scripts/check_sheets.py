import openpyxl
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

wb = openpyxl.load_workbook('Money Heist/La_Casa_de_Papel_S3E01_台词.xlsx', read_only=True)
print("Sheets in S3E01 Excel:")
for name in wb.sheetnames:
    print(f"  - {name}")
wb.close()
