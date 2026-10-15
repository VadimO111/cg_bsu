import colorsys

def rgb_to_cmyk(r, g, b):
    if (r, g, b) == (0, 0, 0): 
        return 0, 0, 0, 100
    r_d, g_d, b_d = r / 255.0, g / 255.0, b / 255.0
    k = 1.0 - max(r_d, g_d, b_d)
    c = (1.0 - r_d - k) / (1.0 - k)
    m = (1.0 - g_d - k) / (1.0 - k)
    y = (1.0 - b_d - k) / (1.0 - k)
    return round(c*100), round(m*100), round(y*100), round(k*100)

def cmyk_to_rgb(c, m, y, k):
    c, m, y, k = c / 100.0, m / 100.0, y / 100.0, k / 100.0
    r = round(255 * (1 - c) * (1 - k))
    g = round(255 * (1 - m) * (1 - k))
    b = round(255 * (1 - y) * (1 - k))
    return r, g, b

def rgb_to_hsv(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
    return round(h*360), round(s*100), round(v*100)

def hsv_to_rgb(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h/360.0, s/100.0, v/100.0)
    return round(r*255), round(g*255), round(b*255)