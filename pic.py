import csv
import matplotlib.pyplot as plt
from collections import defaultdict
import argparse

def generate_cpu_usage_graph(input_file, output_file):
    # CSVファイルを開く
    with open(input_file, mode='r', newline='') as infile:
        reader = csv.reader(infile)
        header = next(reader)  # ヘッダー行を読み飛ばす
        
        # CPUごとの%usrを格納するための辞書
        cpu_data = defaultdict(list)
        times = []
        
        # CSVデータを行ごとに読み込み
        for row in reader:
            time = int(row[0])  # time列
            cpu = row[1]        # CPU列
            usr = float(row[2]) # %usr列
            
            # timeをリストに追加（最初の行のみ追加）
            if len(times) == 0 or times[-1] != time:
                times.append(time)
            
            # CPUごとに%usrを格納
            cpu_data[cpu].append(usr)
    
    # グラフ作成
    plt.figure(figsize=(12, 6))

    # カラーマップを用意して、各CPUに異なる色を割り当てる
    colors = plt.cm.tab20.colors  # 色を増やすためにtab20カラーマップを使用
    color_idx = 0
    
    # 各CPUについてプロット
    for cpu, usage in cpu_data.items():
        plt.plot(times[:len(usage)], usage, label=f"CPU {cpu}", marker='o', color=colors[color_idx % len(colors)])
        color_idx += 1
    
    # グラフの設定
    plt.title('CPU Usage Over Time', fontsize=14)
    plt.xlabel('Time (s)', fontsize=12)
    plt.ylabel('CPU Usage (%)', fontsize=12)
    plt.legend(loc='upper right', bbox_to_anchor=(1.05, 1), fontsize=10)
    plt.grid(True)
    
    # x軸の目盛り間隔を調整
    plt.xticks(range(0, max(times) + 1, max(1, (max(times) - min(times)) // 10)))
    
    # y軸の範囲を設定して、0から100%の範囲に固定
    plt.ylim(0, 100)
    
    # レイアウト調整
    plt.tight_layout()

    # グラフをファイルに保存
    plt.savefig(output_file, dpi=300)
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a CPU usage graph from a CSV file.")
    parser.add_argument("input_file", help="Path to the input CSV file.")
    parser.add_argument("output_file", help="Path to save the output graph image.")
    
    args = parser.parse_args()
    
    generate_cpu_usage_graph(args.input_file, args.output_file)
