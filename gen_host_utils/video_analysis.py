import ffmpeg
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import subprocess
from platform_config import cPlatformConfig


class VideoProcessor:
    def __init__(self, config: cPlatformConfig):
        self._cfg = config

    def get_num_frames(self, video_path)->int:
        probe = ffmpeg.probe(video_path)
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        num_frames = int(video_info['nb_frames'])
        return num_frames

    def get_metrics_dicts(self, names:list, csv_filename:str):
        df = pd.read_csv(csv_filename)
        ssim_dict = {}
        count_packets_dict = {}
        for name in names:
            ssim_dict[name] = df[df['filename'].str.startswith(name)]['ssim'].values
            count_packets_dict[name] = df[df['filename'].str.startswith(name)]['count_packets'].values
        return ssim_dict, count_packets_dict
    
    def get_metric_dict(self, names:list, csv_filename:str, stat:str='count_packets'):
        df = pd.read_csv(csv_filename)
        stat_dict = {}
        for name in names:
            stat_dict[name] = df[df['filename'].str.startswith(name)][stat].values
        return stat_dict


    def run_stat_script(self, script_name:str='out_videos/analysis.sh',
                      work_dir='out_videos/',
                    prefixes:list=['video_before_attack', 'video_during_attack', 'video_after_attack'],):
        args = [self._cfg.getVideoProcessOrigVideo(), self._cfg.getVideoProcessFormat(), 
                self._cfg.getVideoProcessOutCsv(), self._cfg.getWorkDir()+self._cfg.getVideoProcessLclWorkDir()] + prefixes
        subprocess.run(['bash', script_name, *args], check=True)

    def process_analysis_videos(self, save_fig_to:str='video_stat_graph.png', graph_show=True):
        print('Start to get statistics of videos...')
        print('Collecting metrics...')
        ssim_dict, count_packets = self.get_metrics_dicts(self._cfg.getVideoProcessNames(), 
                                                          self._cfg.getVideoProcessLclWorkDir()+self._cfg.getVectorOfAttack()+"/"+self._cfg.getVideoProcessOutCsv())
        num_orig_frames = self.get_num_frames(self._cfg.getVideoProcessLclWorkDir() + self._cfg.getVideoProcessOrigVideo())
        print('Plot graphs...')
        save_fig_to = "outs/"+self._cfg.getVectorOfAttack()+f"/{save_fig_to}"
        self.plot_metrics(ssim_dict=ssim_dict, count_packets_dict=count_packets, orig_count_packets=num_orig_frames,
                          save_to=save_fig_to, names=self._cfg.getVideoProcessNames(), graph_show=graph_show)


    def plot_metrics(self, ssim_dict, count_packets_dict, orig_count_packets, save_to, names, graph_show):
        colors = ['green', 'red', 'green']
        ssim_means = {name: np.mean(ssim_dict[name]) for name in names}
        count_packets_means = {name: np.mean(count_packets_dict[name]) for name in names} 

        fig = plt.figure(figsize=(10, 12))
        gs = fig.add_gridspec(4, 2)

        # Plot data on subplots
        ax_ = []
        ax_.append(fig.add_subplot(gs[0, 0]))
        ax_.append(fig.add_subplot(gs[0, 1]))
        ax_.append(fig.add_subplot(gs[1, :]))
        ax_.append(fig.add_subplot(gs[2, :]))
        ax_.append(fig.add_subplot(gs[3, :]))

        # plot packets
        values_y = [count_packets_dict[key] for key in names]
        values_y = np.concatenate(values_y) * 100 / orig_count_packets
        ax_[0].plot(range(len(values_y)), values_y, 'b-', linewidth=1)
        # fill color
        start = -2
        for j, name in enumerate(names):
            end = start + len(count_packets_dict[name]) + 2
            ax_[0].fill_between(range(start, end), 0, 100, facecolor=colors[j], alpha=0.3)
            start = end - 1

        ax_[0].set_xticks([np.mean(range(len(count_packets_dict[name]))) + sum(len(count_packets_dict[name]) for name in names[:j]) for j in range(len(names))])
        ax_[0].set_xticklabels(names, rotation=10)
        ax_[0].set_ylabel('Packets (%)')
        ax_[0].set_xlim(0, len(values_y))
        ax_[0].hlines(y=95, xmin=0, xmax=len(values_y), color='black')

        count_packets_means_values_y = np.array([count_packets_means[key] for key in names]) * 100 / orig_count_packets
        ax_[1].plot(range(len(count_packets_means_values_y)), count_packets_means_values_y, 'b-', linewidth=1)
        ax_[1].hlines(y=95, xmin=0, xmax=len(count_packets_means_values_y), color='black')
        ax_[1].set_xlim(0, len(count_packets_means_values_y)-1)
        ax_[1].set_xticks([0.5, 1, 1.5])
        ax_[1].set_xticklabels(names, rotation=10)
        ax_[1].set_ylabel('Packets mean (%)')

        # plot ssim
        for i, name in enumerate(names):
            y_data = ssim_dict[name][~np.isnan(ssim_dict[name])] * 100
            if len(y_data) > 3:
                ax_[2+i].plot(range(len(y_data)), y_data, 'b-*', linewidth=1)
            else:
                ax_[2+i].text(0.5, 0.5, 'not enough data', ha='center', va='center', fontsize=20, color='gray')
            ax_[2+i].set_ylabel('SSIM (%)')
            ax_[2+i].set_title(name + ' SSIM')

        fig.tight_layout()
        #fig.suptitle('Videos metrics')
        plt.savefig(save_to, dpi=300)
        if graph_show:
            plt.show()

    def made_demonstation(self, output="Demonstarion", prefixes:list=['video_during_attack']):
        cmd = '''
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
        '''
        args = [self._cfg.getVideoProcessFormat(), output, self._cfg.getVideoProcessLclWorkDir()] + prefixes
        local_script_path = "scripts/demonstation.sh"
        with open(local_script_path, "w") as tmp_file:
            tmp_file.write(cmd)
        subprocess.run(['bash', "scripts/demonstation.sh", *args], check=True)
