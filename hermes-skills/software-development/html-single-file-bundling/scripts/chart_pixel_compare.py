#!/usr/bin/env python3
"""两版图表裁图逐图像素等价比对（去 JS 化 / 改版回归验收用）。

依赖：PIL + numpy（`PYTHONPATH= python3` 跑，避免本机 venv 干扰）。

用法:
    # 目录模式：两目录里同名 png 配对比较
    PYTHONPATH= python3 chart_pixel_compare.py <新版目录> <原版目录>

    # 环形角度扫描：验证环图分段方向/顺序/分界角（单张图，或新版目录里的某张）
    PYTHONPATH= python3 chart_pixel_compare.py <图.png> --ring
    PYTHONPATH= python3 chart_pixel_compare.py <新版目录> <原版目录> --ring chRing750.png

判据（见 SKILL.md「静态化后的验收」）:
    平均色差 <= 3/255 且 强墨迹差异 <= 5% 视为等价。
    强墨迹 = 通道最大差 > 60（淡渐变 1~2 个 RGB 值的差异不算，避免假阳性）。
    二值「非白」掩膜的 IoU 只作粗略参考，别单独下结论。
"""
import os
import sys
import glob
import math

import numpy as np
from PIL import Image

STRONG = 60   # 强墨迹阈值：通道最大差超过它才算实质不同
WEAK = 8      # 二值「非白」掩膜阈值（仅用于 IoU 参考）


def load(path):
    return np.asarray(Image.open(path).convert("RGB")).astype(np.int16)


def compare(a, b):
    h = min(a.shape[0], b.shape[0])
    w = min(a.shape[1], b.shape[1])
    a, b = a[:h, :w], b[:h, :w]
    diff = np.abs(a - b)
    dmax = diff.max(axis=2)
    mean_diff = float(diff.mean())
    strong_pct = float((dmax > STRONG).mean() * 100.0)
    ma = a.min(axis=2) < (255 - WEAK)
    mb = b.min(axis=2) < (255 - WEAK)
    union = int(np.logical_or(ma, mb).sum())
    iou = float(np.logical_and(ma, mb).sum()) / union if union else 1.0
    ys, xs = np.where(dmax > STRONG)
    box = None if ys.size == 0 else (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))
    return mean_diff, strong_pct, iou, box


def ink_geometry(img):
    """从图中自动识别墨迹范围，返回 (圆心x, 圆心y, 外半径px)。"""
    ink = img.min(axis=2) < (255 - WEAK)
    ys, xs = np.where(ink)
    if ys.size == 0:
        raise SystemExit("图上找不到墨迹（全白？裁图坐标可能算偏了）")
    cx = (int(xs.min()) + int(xs.max())) / 2.0
    cy = (int(ys.min()) + int(ys.max())) / 2.0
    r_out = max(int(xs.max()) - int(xs.min()), int(ys.max()) - int(ys.min())) / 2.0
    return cx, cy, r_out, ink, xs, ys

def band_radius(img, cx, cy, r_out):
    """沿 12 点方向由内向外扫，取最长一段墨迹的中点作为环带半径。"""
    hits = []
    for r in range(1, int(r_out * 1.25) + 1):
        x, y = int(round(cx)), int(round(cy - r))
        if 0 <= y < img.shape[0] and 0 <= x < img.shape[1] and img[y, x].min() < (255 - WEAK):
            hits.append(r)
    if not hits:
        return r_out * 0.8
    runs, start, prev = [], hits[0], hits[0]
    for r in hits[1:]:
        if r != prev + 1:
            runs.append((start, prev))
            start = r
        prev = r
    runs.append((start, prev))
    lo, hi = max(runs, key=lambda t: t[1] - t[0])
    return (lo + hi) / 2.0


def ring_scan(path, step=1):
    """0° = 12 点方向，顺时针递增；打印各颜色分段的起止角度与均值色。"""
    img = load(path)
    cx, cy, r_out, _, _, _ = ink_geometry(img)
    r = band_radius(img, cx, cy, r_out)
    samples = []
    for deg in range(0, 360, step):
        rad = math.radians(deg)
        x = int(round(cx + r * math.sin(rad)))
        y = int(round(cy - r * math.cos(rad)))
        if 0 <= y < img.shape[0] and 0 <= x < img.shape[1]:
            samples.append((deg, img[y, x].astype(int)))
    print(f"# {os.path.basename(path)}  圆心=({cx:.0f},{cy:.0f}) 外半径={r_out:.1f}px 采样半径={r:.1f}px")
    segs, cur = [], None
    for deg, rgb in samples:
        if cur is None or int(np.abs(rgb - cur["mean"]).max()) > 24:
            if cur is not None:
                segs.append(cur)
            cur = {"start": deg, "end": deg, "colors": [rgb]}
        else:
            cur["end"] = deg
            cur["colors"].append(rgb)
    if cur is not None:
        segs.append(cur)
    for s in segs:
        span = s["end"] - s["start"]
        if span < 1:
            continue
        mean = np.mean(np.array(s["colors"]), axis=0).round().astype(int)
        print(f"  {s['start']:3d}° ~ {s['end']:3d}°  ({span:3d}°, 均值 RGB {tuple(mean.tolist())})")
    print("  ↳ 与原版 ECharts 的分界角比对（本例期望 0/189.6/324.6/343.9°，实测 0/190/324/344° 即合格）")
    return 0


def main():
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    ring = "--ring" in sys.argv
    if "--ring" in sys.argv:
        idx = sys.argv.index("--ring")
        # --ring 后面若跟了文件名，把它当环形扫描的单图
        tail = sys.argv[idx + 1:] if idx + 1 < len(sys.argv) else []
        if tail and not tail[0].startswith("--") and tail[0].lower().endswith(".png"):
            ring_name = tail[0]
            argv = [a for a in argv if a != ring_name]
            if len(argv) >= 2:
                return ring_scan(os.path.join(argv[0], ring_name))
            return ring_scan(ring_name)
    if len(argv) == 1 and os.path.isfile(argv[0]):
        return ring_scan(argv[0])
    if len(argv) < 2:
        print(__doc__)
        return 1

    da, db = argv[0], argv[1]
    names = sorted(os.path.basename(p) for p in glob.glob(os.path.join(da, "*.png")))
    if not names:
        print(f"目录里没有 png：{da}")
        return 1
    rows = []
    for n in names:
        pb = os.path.join(db, n)
        if not os.path.exists(pb):
            print(f"[跳过] {n} 在 {db} 里没有配对文件")
            continue
        rows.append((n,) + compare(load(os.path.join(da, n)), load(pb)))
    rows.sort(key=lambda t: t[1], reverse=True)
    print(f"{'图':34s} {'平均色差':>8s} {'强墨迹差异%':>11s} {'墨迹IoU':>8s}")
    bad = []
    for n, mean_diff, strong_pct, iou, box in rows:
        flag = "" if (mean_diff <= 3.0 and strong_pct <= 5.0) else "  <== 复核"
        print(f"{n:34s} {mean_diff:8.2f} {strong_pct:11.2f} {iou:8.3f}{flag}")
        if strong_pct > 1.0:
            print(f"{'':34s} 强差异区域 bbox(x0,y0,x1,y1)={box}（dpr=2，除以 2 得 CSS px）")
        if flag:
            bad.append(n)
    print(f"\n合计 {len(rows)} 张，需复核 {len(bad)} 张：{bad if bad else '无'}")
    if bad:
        print("提示：先看差异 bbox 落在哪，再决定是真实绘制差异还是阈值假阳性（见 SKILL.md 验收一节）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
