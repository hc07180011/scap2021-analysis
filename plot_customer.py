import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties


font = FontProperties(fname=r"DFLiHei-Bd.ttc")

time_series = list(["2022 年二月\n(產品上市)", "2022 年三月", "2022 年四月", "2022 年五月", "2022 年六月", "2022 年七月", "2022 年八月"])

yt_final_target = 5000 * 0.16 * 0.14
hahow_final_target = 1500 * 0.2
community_final_target = (2000 + 0) * 0.18

print("{} 名用戶".format(round(yt_final_target + hahow_final_target + community_final_target)))

yt_history = list()
hahow_history = list()
community_history = list()

n = 7
for i in range(n):
    yt_history.append(yt_final_target / (n - 1) * i)
n = 6
hahow_history.append(0.0)
for i in range(n):
    hahow_history.append(hahow_final_target / (n - 1) * i)
n = 4
for i in range(3):
    community_history.append(0.0)
for i in range(n):
    community_history.append(community_final_target / (n - 1) * i)

# cost-revenue
plt.figure(dpi=200, figsize=(16, 8))
for i in range(7):
    if i:
        bottom = (yt_history[i-1] + hahow_history[i-1] + community_history[i-1])
        plt.plot(((i - 1) * 4 + 0.4, (i - 1) * 4 + 1 - 0.4), (bottom, bottom), c="gray", linewidth=0.5)
        plt.bar((i - 1) * 4 + 1, yt_history[i] - yt_history[i-1], bottom=bottom, color="blanchedalmond")
        plt.annotate("{}".format(round(yt_history[i] - yt_history[i-1])), ((i - 1) * 4 + 1, bottom - 15), c="gray")
        plt.annotate("YT", ((i - 1) * 4 + 1 - 0.2, bottom + yt_history[i] - yt_history[i-1] + 10), c="gray")
        
        bottom = (yt_history[i-1] + hahow_history[i-1] + community_history[i-1] + (yt_history[i] - yt_history[i-1]))
        plt.plot(((i - 1) * 4 + 1 + 0.4, (i - 1) * 4 + 2 - 0.4), (bottom, bottom), c="gray", linewidth=0.5)
        plt.bar((i - 1) * 4 + 2, hahow_history[i] - hahow_history[i-1], bottom=bottom, color="navajowhite")
        plt.annotate("{}".format(round(hahow_history[i] - hahow_history[i-1])), ((i - 1) * 4 + 2, bottom - 15), c="gray")
        plt.annotate("Hahow", ((i - 1) * 4 + 2 - 0.5, bottom + hahow_history[i] - hahow_history[i-1] + 10), c="gray")
        
        bottom = (yt_history[i-1] + hahow_history[i-1] + community_history[i-1] + (yt_history[i] - yt_history[i-1]) + (hahow_history[i] - hahow_history[i-1]))
        plt.plot(((i - 1) * 4 + 2 + 0.4, (i - 1) * 4 + 3 - 0.4), (bottom, bottom), c="gray", linewidth=0.5)
        plt.bar((i - 1) * 4 + 3, community_history[i] - community_history[i-1], bottom=bottom, color="gold")
        plt.annotate("{}".format(round(community_history[i] - community_history[i-1])), ((i - 1) * 4 + 3, bottom - 15), c="gray")
        plt.annotate("社群", ((i - 1) * 4 + 3 - 0.3, bottom + community_history[i] - community_history[i-1] + 10), c="gray", fontproperties=font)

        top = yt_history[i] + hahow_history[i] + community_history[i]
        plt.plot(((i - 1) * 4 + 3 + 0.4, (i - 1) * 4 + 4 - 0.4), (top, top), c="gray", linewidth=0.5)

    plt.bar(i * 4, yt_history[i] + hahow_history[i] + community_history[i], width=0.8, color="darkorange")
    plt.annotate("{} 名用戶".format(round(yt_history[i] + hahow_history[i] + community_history[i])), (i * 4 - 0.5, yt_history[i] + hahow_history[i] + community_history[i] + 10), fontproperties=font)

plt.xticks([0, 4, 8, 12, 16, 20, 24], time_series, fontproperties=font)
plt.xlabel("月份", fontproperties=font)
plt.ylabel("預期獲得人數", fontproperties=font)
plt.savefig("test.png")