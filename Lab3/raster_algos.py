def algo_step(x0, y0, x1, y1):
    points = []
    if x0 == x1 and y0 == y1: return [(x0, y0)]
    dx, dy = x1 - x0, y1 - y0
    if abs(dx) >= abs(dy):
        if x0 > x1: x0, y0, x1, y1 = x1, y1, x0, y0
        k = dy / dx if dx != 0 else 0
        b = y0 - k * x0
        for x in range(x0, x1 + 1):
            points.append((x, round(k * x + b)))
    else:
        if y0 > y1: x0, y0, x1, y1 = x1, y1, x0, y0
        k = dx / dy if dy != 0 else 0
        b = x0 - k * y0
        for y in range(y0, y1 + 1):
            points.append((round(k * y + b), y))
    return points

def algo_dda(x0, y0, x1, y1):
    points = []
    dx, dy = x1 - x0, y1 - y0
    length = max(abs(dx), abs(dy))
    if length == 0: return [(x0, y0)]
    x_inc, y_inc = dx / length, dy / length
    x, y = x0, y0
    for _ in range(length + 1):
        points.append((round(x), round(y)))
        x += x_inc
        y += y_inc
    return points

def algo_bresenham_line(x0, y0, x1, y1):
    points = []
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        points.append((x0, y0))
        if x0 == x1 and y0 == y1: break
        e2 = err * 2
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
    return points

def algo_bresenham_circle(xc, yc, r):
    points = []
    x, y = 0, r
    d = 3 - 2 * r
    while y >= x:
        points.extend([
            (xc+x, yc+y), (xc-x, yc+y), (xc+x, yc-y), (xc-x, yc-y),
            (xc+y, yc+x), (xc-y, yc+x), (xc+y, yc-x), (xc-y, yc-x)
        ])
        x += 1
        if d > 0:
            y -= 1
            d += 4 * (x - y) + 10
        else:
            d += 4 * x + 6
    return points

def algo_wu_line(x0, y0, x1, y1):
    points = []
    steep = abs(y1 - y0) > abs(x1 - x0)
    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1
    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0
    dx, dy = x1 - x0, y1 - y0
    gradient = dy / dx if dx != 0 else 1
    xend = round(x0)
    yend = y0 + gradient * (xend - x0)
    xgap = 1 - (x0 + 0.5 - round(x0 + 0.5))
    xpxl1, ypxl1 = xend, int(yend)
    def fpart(x): return x - int(x)
    def rfpart(x): return 1 - fpart(x)
    if steep:
        points.append((ypxl1, xpxl1, rfpart(yend) * xgap))
        points.append((ypxl1 + 1, xpxl1, fpart(yend) * xgap))
    else:
        points.append((xpxl1, ypxl1, rfpart(yend) * xgap))
        points.append((xpxl1, ypxl1 + 1, fpart(yend) * xgap))
    intery = yend + gradient
    xend = round(x1)
    yend = y1 + gradient * (xend - x1)
    xgap = x1 + 0.5 - round(x1 + 0.5)
    xpxl2, ypxl2 = xend, int(yend)
    if steep:
        for x in range(xpxl1 + 1, xpxl2):
            points.append((int(intery), x, rfpart(intery)))
            points.append((int(intery) + 1, x, fpart(intery)))
            intery += gradient
    else:
        for x in range(xpxl1 + 1, xpxl2):
            points.append((x, int(intery), rfpart(intery)))
            points.append((x, int(intery) + 1, fpart(intery)))
            intery += gradient
    return points

def generate_log(algo, x0, y0, x1, y1):
    """Генерирует текстовое описание первых 20 шагов для интерфейса"""
    log = f"=== Журнал алгоритма: {algo} ===\n"
    if algo == "Брезенхем (Линия)":
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        log += f"Начальные данные: dx={dx}, dy={dy}, err={err}\n"
        log += "X\tY\tErr\tДействие\n" + "-"*40 + "\n"
        step = 0
        while step < 20:
            log += f"{x0}\t{y0}\t{err}\t"
            if x0 == x1 and y0 == y1:
                log += "Конец\n"; break
            e2 = err * 2
            action = ""
            if e2 > -dy:
                err -= dy; x0 += sx; action += f"X+={sx} "
            if e2 < dx:
                err += dx; y0 += sy; action += f"Y+={sy}"
            log += f"{action}\n"
            step += 1
        if x0 != x1 or y0 != y1: log += "... и т.д."
        return log
    return "Генерация журнала для этого алгоритма не встроена.\nОтображаются только сами пиксели."