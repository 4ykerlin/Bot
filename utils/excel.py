from openpyxl import Workbook
from datetime import datetime

async def create_excel_report(orders):
    wb = Workbook()
    ws = wb.active
    ws.append(['ID', 'Пользователь', 'Категория', 'Модель', 'Характеристики', 'Состояние', 'Статус', 'Цена', 'Дата'])
    for o in orders:
        ws.append([o[0], o[1], o[2], o[3], o[4], o[5], o[7], o[8], o[9]])
    filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    wb.save(filename)
    return filename