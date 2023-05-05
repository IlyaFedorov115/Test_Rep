#!/bin/bash

# Проверяем, что параметр передан
if [ $# -eq 0 ]
  then
    echo "Usage: $0 filename"
    exit 1
fi

# Присваиваем параметр переменной filename
filename=$1

# 1. Посчитать количество записей, в которых во втором столбце число равно 200
count=$(awk '$2==200{count++}END{print count}' "$filename")

# 2. Найти максимальное, минимальное и среднее значение в третьем столбце
max=$(awk 'NR==1{max=$3;min=$3;sum=0} $3>max{max=$3} $3<min{min=$3} {sum+=$3}END{print max}' "$filename")
min=$(awk 'NR==1{max=$3;min=$3;sum=0} $3>max{max=$3} $3<min{min=$3} {sum+=$3}END{print min}' "$filename")
avg=$(awk '{sum+=$3}END{print sum/NR}' "$filename")

# 3. Записать полученные значения в csv файл
echo "count, max, min, avg" > output.csv
echo "$count, $max, $min, $avg" >> output.csv


# Проверяем, что передан ключ
if [ "$1" == "-k" ]
then
    # Ваш код, который будет выполняться, если передан ключ
    echo "Ключ передан"
else
    # Ваш код, который будет выполняться, если ключ не передан
    echo "Ключ не передан"
fi
