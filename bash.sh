#!/bin/bash

# Проверка аргументов
if [[ $# -ne 9 ]]; then
    echo "Использование: $0 num_launch time_launch log_file_prefix c_num n_num t_num T_num N_num h1_str"
    exit 1
fi

# Получение аргументов
num_launch=$1
time_launch=$2
log_file_prefix=$3
c_num=$4
n_num=$5
t_num=$6
T_num=$7
N_num=$8
h1_str=$9

# Запуск h2load в цикле
for (( i=1; i<=num_launch; i++ ))
do
    log_file="${log_file_prefix}_${i}.txt"
    echo "Запуск теста №$i с параметрами: -c $c_num -n $n_num -t $t_num -T $T_num -N $N_num --logfile $log_file --h1 $h1_str"
    h2load -c $c_num -n $n_num -t $t_num -T $T_num -N $N_num --logfile $log_file --h1 $h1_str &
    sleep $time_launch
    kill -INT $!
done














#!/bin/bash

# Входной файл с данными
input_file="data.txt"

# Файл для записи результатов
output_file="result.csv"

# Поиск количества строк, в которых во втором столбце стоит 200
count=$(awk '{ if ($2 == 200) count++ } END { print count }' $input_file)

# Поиск минимального значения в третьем столбце
min=$(awk 'NR == 1 { min = $3 } $3 < min { min = $3 } END { print min }' $input_file)

# Поиск максимального значения в третьем столбце
max=$(awk 'NR == 1 { max = $3 } $3 > max { max = $3 } END { print max }' $input_file)

# Поиск среднего значения в третьем столбце
sum=$(awk '{ sum += $3 } END { print sum }' $input_file)
average=$(awk "BEGIN { print $sum / NR }")

# Запись результатов в файл .csv
echo "$count,$min,$max,$average" > $output_file








