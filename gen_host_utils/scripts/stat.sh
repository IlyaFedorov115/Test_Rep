#!/bin/bash
input_file=$1
format=$2
output_file=$3
work_dir=$4
prefixes=("${@:5}")
cd $work_dir
if [ ! -f $output_file ]; then
    touch $output_file
fi
echo "filename,ssim,count_packets" > $output_file
for prefix in "${prefixes[@]}"; do
    for file in "$prefix"*."$format"; do
        if [[ -f "$file" ]]; then
            ssim=$(ffmpeg -i "$input_file" -i "$file" -lavfi ssim=stats_file=ssim_log.txt -f null - 2>&1 | grep "All:" | awk -F'All:' '/All:/ {print $2}' | awk '{print $1}')
            count_packets=$(ffprobe -v error -select_streams v:0 -count_packets -show_entries stream=nb_read_packets -of csv=p=0 "$file" 2>/dev/null | tail -1)
            echo "$file,$ssim,$count_packets" >> $output_file
        fi
    done
done        
        