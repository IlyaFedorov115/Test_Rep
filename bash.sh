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
