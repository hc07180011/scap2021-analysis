import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

BAR_WIDTH = .8
font = FontProperties(fname=r"DFLiHei-Bd.ttc")

time_series = list(["2022 年二月\n(產品上市)", "2022 年三月", "2022 年四月",
                   "2022 年五月", "2022 年六月", "2022 年七月", "2022 年八月"])

# new
yt_final_target = 5000 * 0.16 * 0.18
hahow_final_target = 1500 * 0.2
community_final_target = (2000 + 0) * (0.18 - 0.14)

print("{} 名用戶".format(round(yt_final_target +
      hahow_final_target + community_final_target)))

yt_history = list()
hahow_history = list()
community_history = list()

n = 7

# YouTube - 6 個月平均
for i in range(n):
    yt_history.append(round(yt_final_target / (n - 1) * i))

# Hahow - Pre-defined（後三個月有東西）
hahow_history = list([0.0, 0.0, 0.0, 0.0, 60.0, 180.0, 300.0])

# Community - 平均 5 個月（第一個月是 build-up）
n = 6
for i in range(1):
    community_history.append(0.0)
for i in range(n):
    community_history.append(round(community_final_target / (n - 1) * i))

print(yt_history,
      hahow_history,
      community_history)

# cost-revenue
plt.figure(dpi=200, figsize=(16, 8))
for i in range(7):
    if i:
        bottom = (yt_history[i-1] + hahow_history[i-1] +
                  community_history[i-1])
        plt.plot(((i - 1) * 4 + 0 + 0.4, (i - 1) * 4 + 1 - 0.4),
                 (bottom, bottom), c="gray", linewidth=0.5)
        plt.bar((i - 1) * 4 + 1,
                hahow_history[i] - hahow_history[i-1], bottom=bottom, color="#ff9100", width=BAR_WIDTH)
        plt.annotate("{}".format(round(
            hahow_history[i] - hahow_history[i-1])), ((i - 1) * 4 + 1, bottom - 15), c="gray")
        plt.annotate("Hahow", ((i - 1) * 4 + 1 - 0.5, bottom +
                     hahow_history[i] - hahow_history[i-1] + 10), c="gray")

        bottom = (yt_history[i-1] + hahow_history[i-1] +
                  community_history[i-1] + (hahow_history[i] - hahow_history[i-1]))
        plt.plot(((i - 1) * 4 + 1 + 0.4, (i - 1) * 4 + 2 - 0.4),
                 (bottom, bottom), c="gray", linewidth=0.5)
        plt.bar((i - 1) * 4 + 2,
                yt_history[i] - yt_history[i-1], bottom=bottom, color="#ff6000", width=BAR_WIDTH)
        plt.annotate("{}".format(round(
            yt_history[i] - yt_history[i-1])), ((i - 1) * 4 + 2, bottom - 15), c="gray")
        plt.annotate("YT", ((i - 1) * 4 + 2 - 0.2, bottom +
                     yt_history[i] - yt_history[i-1] + 10), c="gray")

        bottom = (yt_history[i-1] + hahow_history[i-1] + community_history[i-1] + (
            yt_history[i] - yt_history[i-1]) + (hahow_history[i] - hahow_history[i-1]))
        plt.plot(((i - 1) * 4 + 2 + 0.4, (i - 1) * 4 + 3 - 0.4),
                 (bottom, bottom), c="gray", linewidth=0.5)
        plt.bar((i - 1) * 4 + 3,
                community_history[i] - community_history[i-1], bottom=bottom, color="#f4af00", width=BAR_WIDTH)
        plt.annotate("{}".format(round(
            community_history[i] - community_history[i-1])), ((i - 1) * 4 + 3, bottom - 15), c="gray")
        plt.annotate("社群", ((i - 1) * 4 + 3 - 0.3, bottom +
                     community_history[i] - community_history[i-1] + 10), c="gray", fontproperties=font)

        top = yt_history[i] + hahow_history[i] + community_history[i]
        plt.plot(((i - 1) * 4 + 3 + 0.4, (i - 1) * 4 + 4 - 0.4),
                 (top, top), c="gray", linewidth=0.5)

    plt.bar(i * 4, yt_history[i] + hahow_history[i] +
            community_history[i], width=BAR_WIDTH, color="#FECF0F")
    # plt.plot((i * 4 - 1.5, i * 4), (yt_history[i] + hahow_history[i] + community_history[i] +
    #          65, yt_history[i] + hahow_history[i] + community_history[i]), c="gray", linewidth=0.5)
    plt.annotate("{}".format(round(yt_history[i] + hahow_history[i] + community_history[i])), ((
        i) * 4 - 0.35, yt_history[i] + hahow_history[i] + community_history[i] + 20), fontsize=14, fontproperties=font)
    plt.scatter(0, yt_history[i] + hahow_history[i] +
                community_history[i] + 100, s=0.1)

plt.xticks([0, 4, 8, 12, 16, 20, 24], time_series, fontproperties=font)
# plt.xlabel("月份", fontproperties=font)
plt.ylabel("預期獲得人數", fontproperties=font)

ax = plt.gca()
ax.get_yaxis().set_visible(False)
ax.get_xaxis().set_ticks([])
ax.spines["left"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["top"].set_visible(False)
ax.spines["bottom"].set_visible(False)

plt.savefig("test.png", bbox_inches="tight", pad_inches=0.1, transparent=True)
