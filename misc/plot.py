from datetime import datetime
import numpy
from matplotlib import pyplot
import csv

def get_data_from_csv():
    with open('wordcounts.tsv') as f:
        reader = csv.DictReader(f, dialect="excel-tab")
        data = []
        for ix, row in enumerate(reader):
            fixed_row = {}
            if ix > 4:
                break
            for field in reader.fieldnames:
                if 'words' in field:
                    val = row[field]
                    if val:
                        fixed_row[field] = val
                    else:
                        fixed_row[field] = 0
            date = datetime(int(row['date.year']), int(row['date.month']), int(row['date.day']), int(row['date.hour']),)
            fixed_row['date'] = date
            data.append(fixed_row)
    return data


# print(len(data))
data = {}
data['date'] = [1, 4, 3, 2]
data['words1'] = [0, 3, 3, 5]
data['words2'] = [4, 6, 0, 2]
array = [data['date'], data['words1'], data['words2']]
numpy.sort(array, 0)

data = get_data_from_csv()
data.sort(key=lambda d: d['date'])
x = [d['date'] for d in data]
y = [
    [d[key] for d in data]
    for key in data[0].keys() if 'words' in key
]
pyplot.stackplot(x, y)

# pyplot.stackplot(data['date'], [values for (field, values) in data.items() if 'words' in field])
# for (field, values) in data.items():
    # if 'words' in field:
        # pyplot.plot(data['date'], values)

pyplot.show()
