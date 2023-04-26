
#!/bin/bash
format=$1
output_file=$2
work_dir=$3
prefixes=("${@:4}")
cd "$work_dir"
for prefix in "${prefixes[@]}"; do
    for file in "$prefix"*."$format"; do
        if [[ -f "$file" ]]; then
            ffmpeg -i "$file" "$prefix"_"$output_file".avi >/dev/null 2>&1
        fi
    done
done
        