import os
# [[time, [precision, angle, distance], [precision, angle, distance], ...], ...]
file_data = "datav2.txt"
with os.open(file_data, 'r') as f:
    data = f.read()
    print(data)
    data = data.split(",")