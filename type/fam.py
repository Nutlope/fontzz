"""Family definitions. Tuples are per-master values (Thin 100, Regular 400, Black 900)."""

MASTERS = [("Thin", 100), ("Regular", 400), ("Black", 900)]


class F:
    """A family resolved at one master."""

    def __init__(self, spec, mi):
        self.spec = spec
        self.mi = mi
        self.master_name, self.wght = MASTERS[mi]

    def __getattr__(self, key):
        spec = self.__dict__["spec"]
        if key not in spec:
            raise AttributeError(key)
        v = spec[key]
        if isinstance(v, tuple) and len(v) == 3:
            return v[self.__dict__["mi"]]
        return v

    def get(self, key, default=None):
        try:
            return getattr(self, key)
        except AttributeError:
            return default

    def has(self, key):
        return key in self.spec


BASE = dict(
    upm=1000,
    xh=540, cap=720, asc=750, desc=-210,
    o=10, oc=12,
    # stems
    S=(20, 84, 192), T=(18, 74, 152),
    SU=(22, 90, 204), TU=(20, 80, 172),
    # curve tension (outer, inner)
    k=0.60, ki=(0.60, 0.62, 0.68),
    kU=0.60, kiU=(0.60, 0.62, 0.68),
    # widths
    n_c=(300, 278, 214),       # n counter
    o_w=(1.04, 1.03, 1.0),     # o width relative to n ink
    # spacing
    sb=(62, 56, 40), sbU=(78, 70, 52),
    rr=0.66,                   # round side bearing ratio
    # shoulder (n, m, h, r, u)
    sh_oy=(500, 452, 398),     # outer notch height
    sh_oa=(64, 60, 52),        # outer junction angle
    sh_iy=(474, 352, 262),     # inner junction height
    sh_ia=(62, 58, 52),
    sh_kj=(0.56, 0.56, 0.58),
    sh_xt=0.54, sh_xti=0.56,
    sh_yr=(0.56, 0.56, 0.54),  # right side becomes vertical at xh*this
    sh_k=(0.60, 0.60, 0.60), sh_ki=(0.60, 0.62, 0.66),
    sh_crotch_dy=(0, 0, 0),    # h: crotch adjustments
    # bowls (b d p q)
    bw_c=(0.0, 0.0, 0.0),
    junction="notch",          # notch | smooth
    # terminals
    term="flat",               # flat | radial | angled | round
    term_tilt=0,               # extra tilt for angled cuts (deg)
    dot="square",              # square | round
    a_story=2, g_story=1,
    l_tail=False, y_tail="straight", t_top="flat",
    R_leg="straight", G_spur=True, M_splay=False,
    one_flag="hook", Q_tail="cross",
    contrast_term=1.0,
)


def fam(**kw):
    d = dict(BASE)
    d.update(kw)
    return d




BASE.update(
    jk=(0.56, 0.56, 0.58),
    # junctions: (outer depth, outer angle, inner depth, inner angle)
    # junctions: (outer depth, outer corner frac, inner depth, inner corner frac)
    j_notch=((40, 0.30, 66, 0.30), (90, 0.32, 186, 0.34), (148, 0.36, 272, 0.36)),
    j_crotch=((40, 0.30, 66, 0.30), (94, 0.32, 192, 0.34), (150, 0.36, 276, 0.36)),
    j_spur=((16, 0.40, 40, 0.30), (44, 0.42, 150, 0.30), (70, 0.44, 236, 0.34)),
    j_crotch_b=((36, 0.32, 60, 0.30), (80, 0.36, 160, 0.32), (120, 0.40, 226, 0.34)),
    bw_xt=0.56, bw_xti=0.54, bw_xb=0.54, bw_xbi=0.52,
    m_c=0.86, r_w=(0.62, 0.62, 0.66), r_th=38,
    c_w=0.95, c_th=38, c_thb=-40,
    e_w=1.0, e_th=(-36, -38, -44), e_bar=(0.92, 0.88, 0.76), e_bar_pos=(0.42, 0.40, 0.24), e_T=(1.0, 0.97, 0.92),
    i_dot_y=(650, 626, 604), dotw=(42, 98, 184),
    j_rx=(150, 168, 250), j_ry=(130, 150, 216), j_th=212,
)


BASE.update(r_drop=(50, 66, 72), r_tt=(1.0, 0.98, 0.86), r_xt=0.30, r_xti=0.40, r_k=0.62, r_ki=0.62, r_co=0.45, r_ci=0.5,
            r_w=(0.66, 0.68, 1.02))


BASE.update(
    a_w=(0.92, 0.92, 0.96), a_hx=0.50, a_hy=(0.60, 0.60, 0.58), a_th=(150, 152, 158), a_bt=(0.56, 0.58, 0.66), a_bT=(0.95, 0.93, 0.85), a_bbT=(1.0, 0.98, 0.90),
    j_abowl=((6, 0.85, 26, 0.50), (16, 0.85, 92, 0.50), (24, 0.85, 168, 0.55)),
    j_gspur=((30, 0.36, 50, 0.36), (70, 0.38, 128, 0.40), (110, 0.40, 200, 0.40)),
    g_hx=0.48, g_hy=(150, 168, 236), g_th=(206, 208, 212),
    f_rx=(118, 130, 236), f_ry=(112, 124, 214), f_th=(36, 38, 44), f_cl=(84, 92, 104), f_cr=(96, 104, 118),
    t_rx=(104, 116, 226), t_ry=(100, 114, 206), t_th=(-40, -42, -48), t_top=(660, 650, 640), t_top_style="flat",
    t_cl=(78, 88, 98), t_cr=(98, 108, 124),
    k_w=(0.98, 1.0, 1.16), k_j=(0.44, 0.44, 0.46), k_lj=(0.40, 0.42, 0.46),
    v_w=(1.04, 1.04, 1.08), w_w=(0.84, 0.84, 0.90), x_w=(1.0, 1.0, 1.06), z_w=(0.92, 0.94, 0.98), z_t=(1.0, 0.94, 0.70), z_T=(1.0, 0.98, 0.90),
    s_w=(0.88, 0.88, 0.94), s_cyu=(0.73, 0.725, 0.70), s_cyl=(0.27, 0.275, 0.30), s_T=(1.0, 0.95, 0.80), s_spine=(0.96, 0.92, 0.80), s_rxu=0.94, s_flat=(0.62, 0.58, 0.45),
    s_tth=(38, 38, 42), s_bth=(-142, -142, -138),
)


BASE.update(
    H_c=(392, 372, 300),
    E_w=0.84, F_w=0.80, L_w=0.76, T_w=0.92,
    O_w=(1.12, 1.12, 1.10), C_w=(1.04, 1.04, 1.04), C_th=(40, 40, 44), C_thb=(-40, -40, -44),
    G_w=(1.10, 1.10, 1.08), G_th=(40, 40, 44), G_bar=(0.54, 0.54, 0.56), G_barx=0.54,
    D_w=(1.02, 1.02, 1.02), D_rx=1.04, B_w=(0.94, 0.94, 0.96), B_mid=0.52, B_up=0.92, B_rx=1.1,
    P_w=(0.92, 0.92, 0.94), P_bot=(0.43, 0.42, 0.40), P_rx=1.1,
    R_w=(0.96, 0.96, 1.0), R_bw=0.95, R_lx=0.56,
    U_w=(0.98, 0.98, 1.0), U_ry=0.42, J_w=(0.78, 0.78, 0.82), J_ry=0.36, J_th=(200, 202, 206),
    S_w=(0.92, 0.92, 0.96), S_tth=(40, 40, 44), S_bth=(-140, -140, -136),
    V_w=(1.08, 1.08, 1.12), A_w=(1.12, 1.12, 1.16), A_bar=(0.26, 0.26, 0.24), W_w=(0.84, 0.84, 0.88),
    X_w=(1.04, 1.04, 1.08), Y_w=(1.06, 1.06, 1.1), Y_mid=0.42, Z_w=(0.94, 0.95, 1.02), Z_t=(1.0, 0.95, 0.78),
    K_w=(1.0, 1.0, 1.06), K_j=0.33, K_lj=(0.40, 0.42, 0.44), N_w=(1.0, 1.0, 1.02), M_w=(1.2, 1.2, 1.24),
)


BASE.update(
    q_w=(0.74, 0.76, 0.86),
    fig_w=(0.86, 0.86, 0.90), one_x=0.56, one_fw=0.30, one_fh=0.16,
    two_ry=0.30, two_th=(152, 154, 158),
    three_m=0.555, three_up=0.92, three_tth=(150, 152, 156), three_bth=(-150, -150, -146), three_bar=0.30,
    four_x=0.80, four_bar=0.24,
    five_ry=0.34, five_bth=(-150, -150, -146), five_je=(138, 136, 132), five_bar=0.94,
    six_ry=(0.34, 0.34, 0.31), six_th=(48, 46, 54), seven_xb=0.30, eight_m=0.56, eight_up=0.90,
)


HALDEN = fam(
    name="Halden",
    hook_term="vertical",
    style_note="Neo-grotesque",
    xh=550, cap=720, asc=750, desc=-210,
    n_c=(292, 272, 208), sb=(48, 42, 30), sbU=(62, 54, 40),
    t_top_style="slant", t_slant=0.7,
)

RONDEL = fam(
    name="Rondel",
    style_note="Geometric",
    xh=470, cap=700, asc=780, desc=-230, o=11, oc=12, t_top=(626, 616, 606),
    S=(20, 80, 166), T=(19, 76, 150), SU=(21, 86, 186), TU=(20, 82, 170),
    k=0.5523, ki=(0.5523, 0.56, 0.60), kU=0.5523, kiU=(0.5523, 0.56, 0.60),
    junction="smooth", term="radial", hook_term="radial", dot="round",
    a_story=1, sh_xt=0.5, sh_xti=0.5, sh_round=1.0, sh_k=0.5523, sh_ki=(0.5523, 0.56, 0.60),
    sh_yr=(0.48, 0.48, 0.48),
    n_c=(326, 300, 232), o_circle=1.0, a1_w=1.0, b_w=1.0,
    c_w=0.97, c_th=(46, 46, 50), c_thb=(-46, -46, -50), e_w=1.0, e_th=(-40, -42, -46),
    r_w=(0.58, 0.58, 0.72), r_drop=(60, 76, 90), r_xt=0.35, r_xti=0.42,
    s_w=(0.86, 0.86, 0.90),
    O_circle=1.0, H_c=(390, 370, 300),
    C_w=(1.22, 1.22, 1.20), C_th=(44, 44, 48), C_thb=(-44, -44, -48), G_w=(1.26, 1.26, 1.22),
    G_th=(44, 44, 48), G_bar=(0.52, 0.52, 0.54), G_barx=0.56,
    D_w=(1.14, 1.14, 1.12), D_rx=1.7, B_w=(0.88, 0.88, 0.92), B_rx=1.3, P_w=(0.86, 0.86, 0.9), P_rx=1.3,
    R_w=(0.90, 0.90, 0.96), E_w=0.74, F_w=0.70, L_w=0.66, T_w=0.92, S_w=(0.84, 0.84, 0.90),
    U_w=(1.0, 1.0, 1.02), U_ry=0.46, A_w=(1.2, 1.2, 1.22), V_w=(1.14, 1.14, 1.16), W_w=(0.9, 0.9, 0.94),
    N_w=(1.06, 1.06, 1.06), M_w=(1.28, 1.28, 1.3), A_apex=0.12, V_apex=0.12, v_apex=0.12, M_apex=0.12,
    dotw=(44, 104, 196), i_dot_y=(600, 580, 562), sb=(60, 54, 38), sbU=(74, 66, 50),
    dash_y=250,
)

TESSERA = fam(
    name="Tessera",
    style_note="Squared grotesque",
    xh=580, cap=720, asc=750, desc=-190, o=6, oc=7, t_top=(680, 672, 664), i_dot_y=(672, 652, 632),
    S=(20, 84, 188), T=(19, 76, 160), SU=(22, 88, 198), TU=(20, 80, 168),
    k=0.83, ki=(0.85, 0.87, 0.89), kU=0.83, kiU=(0.85, 0.87, 0.89), a_bt=(0.56, 0.58, 0.6), a_hy=(0.6, 0.6, 0.62),
    sh_k=0.83, sh_ki=(0.85, 0.87, 0.89), r_k=0.78, r_ki=0.8, jk=(0.64, 0.64, 0.64),
    hook_term="vertical", dot="square",
    n_c=(340, 318, 250), o_w=(1.08, 1.08, 1.05),
    c_th=(28, 30, 34), c_thb=(-30, -32, -36), e_th=(-30, -32, -38),
    s_tth=(32, 32, 36), s_bth=(-148, -148, -144), s_ks=0.66,
    H_c=(404, 384, 312), O_w=(1.14, 1.14, 1.10), C_w=(1.06, 1.06, 1.04), C_th=(32, 32, 36), C_thb=(-32, -32, -36),
    G_w=(1.12, 1.12, 1.08), G_th=(32, 32, 36), G_spur=False, D_rx=0.82, B_rx=0.9, P_rx=0.9,
    S_tth=(32, 32, 36), S_bth=(-148, -148, -144), two_th=(160, 160, 164), three_tth=(160, 160, 164),
    three_bth=(-160, -160, -156), five_bth=(-160, -160, -156), six_th=(36, 36, 46),
    a_th=(160, 160, 164), j_th=(220, 220, 222), g_th=(216, 216, 218), f_th=(28, 30, 34), t_th=(-32, -34, -40),
    U_ry=0.36, J_ry=0.32, dotw=(42, 96, 180),
)

ALDER = fam(
    name="Alder",
    style_note="Humanist",
    xh=496, cap=700, asc=760, desc=-230, o=10, oc=12, i_dot_y=(610, 590, 572), t_top=(630, 620, 610),
    S=(20, 82, 182), T=(15, 56, 120), SU=(21, 86, 192), TU=(16, 60, 128),
    k=0.57, ki=(0.59, 0.60, 0.64), kU=0.57, kiU=(0.59, 0.60, 0.64),
    term="angled", term_pen=76, term_mix=(0.3, 0.24, 0.1), hook_term="angled", arm_cut=76, dot="round",
    n_c=(268, 248, 194), o_w=(1.02, 1.02, 1.0), sh_xt=0.52,
    c_th=(52, 52, 54), c_thb=(-52, -52, -52), e_th=(-50, -50, -52), c_w=0.94,
    s_tth=(48, 48, 50), s_bth=(-134, -134, -132),
    a_th=(144, 146, 152), j_th=(204, 204, 208), g_th=(200, 200, 204), f_th=(48, 48, 52),
    t_th=(-52, -52, -56), t_top_style="slant", t_slant=0.9,
    l_tail=True, l_rx=(96, 106, 224), l_ry=(96, 106, 204), l_th=(-56, -56, -60),
    y_tail="curved",
    H_c=(376, 356, 290), C_th=(50, 50, 52), C_thb=(-50, -50, -52), G_th=(50, 50, 52), J_th=(208, 208, 210),
    S_tth=(48, 48, 50), S_bth=(-134, -134, -132), two_th=(146, 148, 152), three_tth=(146, 148, 152),
    three_bth=(-146, -146, -142), five_bth=(-146, -146, -142), six_th=(54, 52, 58),
    dotw=(44, 98, 188), sb=(60, 54, 40), sbU=(76, 68, 52),
)

MALLOW = fam(
    name="Mallow",
    style_note="Rounded",
    xh=570, cap=720, asc=770, desc=-200, o=10, oc=11, i_dot_y=(676, 656, 634), t_top=(690, 682, 674),
    S=(22, 88, 192), T=(21, 84, 180), SU=(23, 90, 198), TU=(22, 86, 184),
    a_story=1, y_tail="curved", l_tail=True, l_rx=(96, 106, 224), l_ry=(96, 106, 204), l_th=(-56, -56, -60),
    k=0.58, ki=(0.58, 0.60, 0.64), kU=0.58, kiU=(0.58, 0.60, 0.64),
    term="round", dot="round",
    n_c=(338, 316, 250), o_w=(1.04, 1.04, 1.02),
    c_th=(40, 42, 46), c_thb=(-40, -42, -46), e_th=(-36, -38, -42),
    a_bt=(0.56, 0.57, 0.64), a_bT=(0.95, 0.92, 0.82), a_th=(150, 148, 142), a_hy=(0.60, 0.60, 0.58),
    H_c=(396, 376, 306),
    dotw=(44, 100, 196), sb=(64, 58, 42), sbU=(80, 72, 54),
)

STRATA = fam(
    name="Strata",
    style_note="Condensed grotesque",
    xh=560, cap=720, asc=752, desc=-200, o=9, oc=10,
    S=(20, 80, 168), T=(18, 70, 142), SU=(22, 84, 176), TU=(20, 74, 150),
    k=0.68, ki=(0.70, 0.72, 0.78), kU=0.68, kiU=(0.70, 0.72, 0.78),
    sh_k=0.68, sh_ki=(0.70, 0.72, 0.78), r_k=0.66, r_ki=0.68, jk=(0.6, 0.6, 0.62),
    hook_term="vertical", dot="square",
    n_c=(206, 190, 136), o_w=(1.04, 1.04, 1.02), sb=(46, 42, 30), sbU=(56, 52, 38),
    H_c=(270, 256, 200), r_w=(0.66, 0.66, 0.94),
    c_th=(34, 34, 38), c_thb=(-34, -34, -38), e_th=(-32, -34, -40),
    j_rx=(116, 128, 206), j_ry=(110, 124, 196), f_rx=(100, 110, 204), f_ry=(104, 114, 200),
    f_cl=(62, 68, 82), f_cr=(72, 80, 94), t_rx=(92, 100, 196), t_ry=(92, 104, 196),
    t_cl=(56, 62, 72), t_cr=(70, 78, 90), g_hy=(140, 156, 226),
    dotw=(40, 92, 168), dash_y=270,
)

PLAZA = fam(
    name="Plaza",
    style_note="Extended grotesque",
    xh=520, cap=700, asc=740, desc=-200, o=10, oc=12,
    S=(22, 88, 194), T=(20, 78, 164), SU=(24, 92, 202), TU=(22, 82, 170),
    k=0.62, ki=(0.62, 0.64, 0.70), kU=0.62, kiU=(0.62, 0.64, 0.70),
    sh_k=0.62, sh_ki=(0.62, 0.64, 0.70),
    hook_term="vertical", dot="squircle",
    n_c=(430, 404, 326), o_w=(1.07, 1.07, 1.05), sb=(70, 64, 48), sbU=(84, 78, 58),
    H_c=(560, 530, 440), r_w=(0.50, 0.50, 0.62), m_c=0.80,
    c_th=(34, 34, 38), c_thb=(-34, -34, -38), e_th=(-30, -32, -38),
    f_rx=(150, 160, 250), f_ry=(112, 124, 214), f_cl=(110, 120, 140), f_cr=(130, 140, 160),
    t_rx=(130, 140, 240), t_ry=(100, 114, 206), t_cl=(100, 110, 130), t_cr=(120, 130, 150),
    j_rx=(176, 194, 270), fig_w=(0.94, 0.94, 0.96), k_w=(0.84, 0.84, 0.92),
    v_w=(0.86, 0.86, 0.92), w_w=(0.66, 0.66, 0.72), x_w=(0.84, 0.84, 0.9), z_w=(0.8, 0.8, 0.86),
    dotw=(44, 100, 194),
)

VESPER = fam(
    name="Vesper",
    style_note="Contrast sans",
    xh=500, cap=700, asc=760, desc=-230, o=11, oc=13,
    S=(22, 90, 200), T=(11, 38, 90), SU=(24, 96, 210), TU=(12, 40, 94),
    k=0.57, ki=(0.6, 0.62, 0.68), kU=0.57, kiU=(0.6, 0.62, 0.68),
    sh_k=0.58, sh_ki=(0.6, 0.62, 0.66),
    term="flat", hook_term="vertical", arm_cut=90,
    dot="round", diag_c=0.45, N_s=0.56, M_s=0.62, dg=0.96, dgU=0.96,
    n_c=(286, 266, 206), o_w=(1.04, 1.04, 1.02), sb=(60, 54, 40), sbU=(74, 68, 52),
    H_c=(380, 360, 290),
    c_th=(48, 48, 50), c_thb=(-50, -50, -50), e_th=(-46, -46, -48),
    s_tth=(46, 46, 48), s_bth=(-136, -136, -134), C_th=(48, 48, 50), C_thb=(-48, -48, -50),
    G_th=(48, 48, 50), S_tth=(46, 46, 48), S_bth=(-136, -136, -134),
    a_th=(146, 148, 152), j_th=(206, 206, 208), g_th=(202, 202, 206), f_th=(46, 46, 50),
    t_th=(-50, -50, -54), two_th=(148, 150, 154), three_tth=(148, 150, 154),
    three_bth=(-148, -148, -144), five_bth=(-148, -148, -144), six_th=(52, 50, 56),
    dotw=(44, 100, 196), i_dot_y=(624, 604, 588),
)

LEDGER = fam(
    name="Ledger",
    style_note="Slab serif",
    xh=510, cap=700, asc=750, desc=-210, o=10, oc=12,
    S=(22, 84, 178), T=(20, 74, 150), SU=(24, 88, 186), TU=(22, 78, 156),
    k=0.60, ki=(0.60, 0.62, 0.68), kU=0.60, kiU=(0.60, 0.62, 0.68),
    serif="slab", sf_t=(22, 70, 104), sf_e=(48, 64, 52), sf_vt=(20, 66, 116), sf_vh=(40, 50, 34),
    sf_midbeak=False, x_w=(1.08, 1.12, 1.4), v_w=(1.08, 1.1, 1.2), K_lj=(0.42, 0.44, 0.5),
    term="vertical", hook_term="vertical", dot="square", one_base=True,
    n_c=(300, 282, 222), o_w=(1.04, 1.04, 1.02), sb=(34, 30, 22), sbU=(40, 34, 24),
    H_c=(420, 400, 330), E_w=0.88, F_w=0.84, L_w=0.82, T_w=0.94,
    c_th=(34, 32, 26), c_thb=(-34, -32, -26), e_th=(-32, -32, -30),
    C_th=(34, 32, 26), C_thb=(-34, -32, -26), G_th=(34, 32, 28),
    dotw=(44, 96, 180),
)

FOLIO = fam(
    name="Folio",
    style_note="Text serif",
    xh=470, cap=680, asc=740, desc=-240, o=11, oc=13,
    S=(22, 84, 184), T=(11, 40, 92), SU=(24, 90, 194), TU=(12, 42, 96),
    k=0.56, ki=(0.58, 0.60, 0.64), kU=0.56, kiU=(0.58, 0.60, 0.64),
    sh_k=0.58, sh_ki=(0.6, 0.62, 0.66),
    serif="bracket", sf_t=(10, 26, 50), sf_e=(50, 60, 64), sf_br=(28, 42, 52), sf_wedge=0.26,
    sf_vt=(14, 40, 76), sf_vh=(44, 58, 52), sf_de=0.95, sf_midbeak=False,
    x_w=(1.06, 1.12, 1.5), v_w=(1.06, 1.08, 1.16),
    term="angled", term_pen=80, term_mix=(0.4, 0.35, 0.0), hook_term="angled", arm_cut=80,
    dot="round", one_base=True, diag_c=0.42, N_s=0.5, M_s=0.56, dg=0.96, dgU=0.96,
    n_c=(288, 270, 212), o_w=(1.03, 1.03, 1.01), sb=(34, 30, 22), sbU=(40, 34, 24),
    H_c=(400, 380, 316), E_w=0.88, F_w=0.84, L_w=0.82,
    c_th=(52, 52, 54), c_thb=(-52, -52, -52), e_th=(-48, -48, -50),
    s_tth=(48, 48, 50), s_bth=(-134, -134, -132), C_th=(50, 50, 52), C_thb=(-50, -50, -52),
    G_th=(50, 50, 52), S_tth=(48, 48, 50), S_bth=(-134, -134, -132),
    a_th=(144, 146, 150), j_th=(204, 204, 208), g_th=(200, 200, 204), f_th=(48, 48, 52),
    t_th=(-52, -52, -56), two_th=(146, 148, 152), three_tth=(146, 148, 152),
    three_bth=(-146, -146, -142), five_bth=(-146, -146, -142), six_th=(54, 52, 58),
    dotw=(42, 94, 182), i_dot_y=(600, 580, 566),
)

# ---------------------------------------------------------------- second set

OPALINE = fam(
    name="Opaline",
    style_note="Didone",
    xh=450, cap=690, asc=760, desc=-240, o=12, oc=14,
    S=(20, 92, 200), T=(11, 20, 46), SU=(22, 98, 210), TU=(11, 22, 48),
    k=0.56, ki=(0.6, 0.64, 0.72), kU=0.56, kiU=(0.6, 0.64, 0.72),
    sh_k=0.58, sh_ki=(0.6, 0.64, 0.7),
    serif="bracket", sf_br=(0, 0, 0), sf_t=(10, 16, 28), sf_e=(46, 62, 70), sf_vt=(12, 20, 34), sf_vh=(40, 56, 58),
    sf_de=0.95, sf_midbeak=False,
    x_w=(1.06, 1.12, 1.5), v_w=(1.06, 1.08, 1.16),
    term="vertical", hook_term="vertical", arm_cut=90,
    dot="round", ball=0.6, one_base=True, diag_c=0.26, N_s=0.4, M_s=0.46, dg=0.96, dgU=0.96,
    n_c=(280, 262, 204), o_w=(1.02, 1.02, 1.0), sb=(32, 28, 20), sbU=(38, 32, 22),
    H_c=(400, 380, 316), E_w=0.86, F_w=0.82, L_w=0.8,
    c_th=(54, 52, 50), c_thb=(-48, -46, -40), e_th=(-40, -36, -30),
    s_tth=(52, 52, 54), s_bth=(-130, -130, -128), C_th=(52, 50, 48), C_thb=(-46, -44, -38),
    G_th=(44, 40, 34), S_tth=(52, 52, 54), S_bth=(-130, -130, -128),
    a_th=(132, 130, 128), j_th=(214, 216, 218), g_th=(200, 200, 204), f_th=(56, 58, 60),
    t_th=(-54, -54, -58), two_th=(144, 146, 150), three_tth=(144, 146, 150),
    three_bth=(-144, -144, -140), five_bth=(-144, -144, -140), six_th=(56, 54, 60),
    dotw=(40, 100, 196), i_dot_y=(580, 560, 546), t_top=(600, 590, 580),
)

SIGNAL = fam(
    name="Signal",
    style_note="Monospace",
    mono=600, mono_sb=40,
    xh=540, cap=700, asc=750, desc=-210, o=9, oc=10,
    S=(20, 80, 146), T=(18, 72, 130), SU=(20, 82, 150), TU=(18, 74, 134),
    k=0.66, ki=(0.68, 0.7, 0.76), kU=0.66, kiU=(0.68, 0.7, 0.76),
    sh_k=0.66, sh_ki=(0.68, 0.7, 0.76), jk=(0.6, 0.6, 0.62),
    serif="slab", serif_only=("i", "dotlessi", "j", "dotlessj", "l", "I", "r", "one"),
    sf_t=(18, 66, 118), sf_e=(150, 142, 118), sf_de=0.9, sf_vt=(18, 60, 100), sf_vh=(40, 40, 30),
    one_base=True, hook_term="vertical", dot="square",
    n_c=(400, 290, 214), m_c=(0.5, 0.44, 0.34), o_w=(1.0, 1.0, 1.0), sb=(40, 40, 40), sbU=(40, 40, 40),
    H_c=(400, 300, 226), r_w=(0.9, 0.9, 1.1),
    f_cl=(120, 124, 118), f_cr=(150, 150, 140), t_cl=(120, 124, 118), t_cr=(150, 150, 140),
    c_th=(34, 34, 38), c_thb=(-34, -34, -38), e_th=(-32, -34, -40),
    dotw=(42, 100, 170), i_dot_y=(650, 626, 600), circ_r=0.4,
)

TALLY = fam(
    name="Tally",
    style_note="Slab monospace",
    mono=600, mono_sb=24,
    xh=500, cap=680, asc=740, desc=-220, o=10, oc=12,
    S=(20, 74, 136), T=(18, 66, 120), SU=(22, 78, 142), TU=(20, 70, 126),
    k=0.58, ki=(0.6, 0.62, 0.68), kU=0.58, kiU=(0.6, 0.62, 0.68),
    serif="slab", sf_t=(18, 52, 80), sf_e=(76, 66, 40), sf_de=0.8, sf_vt=(18, 54, 90), sf_vh=(40, 46, 30),
    sf_midbeak=False, x_w=(1.0, 1.04, 1.2), v_w=(1.0, 1.02, 1.1), K_lj=(0.42, 0.44, 0.5),
    term="flat", hook_term="vertical", dot="round", one_base=True,
    n_c=(330, 268, 210), m_c=(0.48, 0.42, 0.3), o_w=(1.02, 1.02, 1.0), sb=(24, 24, 24), sbU=(24, 24, 24),
    H_c=(330, 270, 204), E_w=0.9, F_w=0.86, L_w=0.86, T_w=0.94, r_w=(0.86, 0.86, 1.04),
    f_cl=(104, 110, 106), f_cr=(130, 130, 124), t_cl=(104, 110, 106), t_cr=(130, 130, 124),
    c_th=(44, 44, 48), c_thb=(-44, -44, -48), e_th=(-40, -42, -46),
    dotw=(44, 96, 160), circ_r=0.4,
)

TOPSY = fam(
    name="Topsy",
    style_note="Reverse contrast",
    xh=560, cap=720, asc=760, desc=-200, o=12, oc=14,
    S=(14, 40, 84), T=(22, 96, 196), SU=(16, 44, 90), TU=(24, 102, 206),
    k=0.6, ki=(0.6, 0.6, 0.62), kU=0.6, kiU=(0.6, 0.6, 0.62),
    sh_k=0.6, sh_ki=(0.6, 0.6, 0.62),
    hook_term="vertical", dot="round", diag_c=1.6,
    n_c=(330, 320, 290), o_w=(1.08, 1.08, 1.08), sb=(54, 46, 36), sbU=(64, 56, 44),
    H_c=(420, 410, 380), m_c=0.9,
    c_th=(60, 64, 80), c_thb=(-60, -64, -80), e_th=(-60, -64, -80), e_bar=(0.9, 0.9, 0.86),
    s_tth=(60, 64, 80), s_bth=(-120, -120, -110), C_th=(60, 64, 80), C_thb=(-60, -64, -80),
    G_th=(60, 64, 80), S_tth=(60, 64, 80), S_bth=(-120, -120, -110),
    dotw=(40, 90, 190), i_dot_y=(660, 650, 640), t_top=(700, 690, 680), q_ry=(0.3, 0.36, 0.44),
)

TEMPO = fam(
    name="Tempo",
    style_note="Slanted grotesque",
    slant=11,
    xh=540, cap=710, asc=750, desc=-210,
    S=(20, 84, 188), T=(18, 72, 150), SU=(22, 88, 198), TU=(20, 76, 160),
    term="angled", term_pen=70, term_mix=(0.3, 0.25, 0.1), hook_term="angled", arm_cut=70,
    t_top_style="slant", t_slant=0.9, dot="round",
    n_c=(262, 244, 186), o_w=(1.0, 1.0, 0.98), sb=(48, 42, 30), sbU=(60, 54, 40),
    H_c=(360, 342, 276), E_w=0.82, F_w=0.78, L_w=0.74,
)

PEBBLE = fam(
    name="Pebble",
    style_note="Soft square",
    xh=550, cap=710, asc=750, desc=-200, o=8, oc=9,
    S=(22, 88, 172), T=(21, 82, 156), SU=(23, 92, 182), TU=(22, 86, 166),
    k=0.78, ki=(0.8, 0.82, 0.86), kU=0.78, kiU=(0.8, 0.82, 0.86),
    sh_k=0.78, sh_ki=(0.8, 0.82, 0.86), r_k=0.74, r_ki=0.76, jk=(0.64, 0.64, 0.64),
    a_bt=(0.56, 0.57, 0.56), a_hy=(0.6, 0.61, 0.64),
    term="round", dot="round", G_spur=False, a_story=1,
    n_c=(320, 300, 236), o_w=(1.04, 1.04, 1.02), sb=(56, 50, 38), sbU=(70, 62, 46),
    H_c=(400, 380, 310),
    c_th=(34, 36, 40), c_thb=(-34, -36, -40), e_th=(-32, -34, -38),
    dotw=(44, 100, 196), i_dot_y=(660, 640, 620), t_top=(680, 672, 664),
)

ORBIT = fam(
    name="Orbit",
    style_note="Extended square",
    xh=540, cap=700, asc=740, desc=-190, o=6, oc=7,
    S=(22, 88, 190), T=(20, 80, 166), SU=(24, 92, 198), TU=(22, 84, 172),
    k=0.88, ki=(0.9, 0.92, 0.93), kU=0.88, kiU=(0.9, 0.92, 0.93),
    sh_k=0.88, sh_ki=(0.9, 0.92, 0.93), r_k=0.84, r_ki=0.86, jk=(0.68, 0.68, 0.68),
    a_bt=(0.56, 0.58, 0.6), a_hy=(0.6, 0.6, 0.62),
    hook_term="vertical", dot="square", G_spur=False,
    n_c=(440, 414, 336), o_w=(1.06, 1.06, 1.04), sb=(66, 60, 46), sbU=(80, 74, 56),
    H_c=(580, 550, 460), r_w=(0.5, 0.5, 0.62), m_c=0.78,
    c_th=(26, 26, 30), c_thb=(-26, -26, -30), e_th=(-24, -26, -32),
    f_rx=(150, 160, 250), f_cl=(110, 120, 140), f_cr=(130, 140, 160),
    t_rx=(130, 140, 240), t_cl=(100, 110, 130), t_cr=(120, 130, 150),
    j_rx=(176, 194, 270), fig_w=(0.96, 0.96, 0.98), k_w=(0.84, 0.84, 0.92),
    v_w=(0.86, 0.86, 0.92), w_w=(0.66, 0.66, 0.72), x_w=(0.84, 0.84, 0.9), z_w=(0.8, 0.8, 0.86),
    S_tth=(32, 32, 36), S_bth=(-148, -148, -144), s_tth=(32, 32, 36), s_bth=(-148, -148, -144),
    dotw=(44, 100, 190), i_dot_y=(640, 620, 600),
)

CLEFT = fam(
    name="Cleft",
    style_note="Wedge serif",
    xh=500, cap=700, asc=750, desc=-220, o=10, oc=12,
    S=(22, 86, 184), T=(18, 66, 140), SU=(24, 90, 192), TU=(20, 70, 146),
    k=0.6, ki=(0.6, 0.62, 0.68), kU=0.6, kiU=(0.6, 0.62, 0.68),
    serif="wedge", sf_t=(8, 14, 22), sf_e=(52, 74, 84), sf_wh=1.5, sf_vt=(18, 52, 92), sf_vh=(36, 46, 30),
    sf_de=0.85, sf_midbeak=False, x_w=(1.08, 1.12, 1.4), v_w=(1.08, 1.1, 1.2), K_lj=(0.42, 0.44, 0.5),
    term="flat", hook_term="vertical", dot="square", one_base=True,
    n_c=(296, 278, 218), o_w=(1.04, 1.04, 1.02), sb=(36, 30, 22), sbU=(42, 36, 26),
    H_c=(410, 392, 324), E_w=0.88, F_w=0.84, L_w=0.82, T_w=0.94,
    c_th=(40, 40, 44), c_thb=(-40, -40, -44), e_th=(-36, -38, -42),
    dotw=(44, 96, 180),
)

BEACON = fam(
    name="Beacon",
    style_note="Legible sans",
    xh=560, cap=720, asc=760, desc=-210, o=10, oc=12,
    S=(20, 82, 180), T=(18, 74, 156), SU=(22, 86, 188), TU=(20, 78, 164),
    k=0.57, ki=(0.58, 0.6, 0.66), kU=0.57, kiU=(0.58, 0.6, 0.66),
    serif="slab", serif_only=("I",), sf_t=(18, 60, 110), sf_e=(80, 86, 80), sf_vt=(18, 60, 100), sf_vh=(30, 30, 30),
    hook_term="vertical", dot="round", l_tail=True, l_rx=(96, 106, 224), l_ry=(96, 106, 204), l_th=(-56, -56, -60),
    a_story=1, one_base=True,
    n_c=(318, 298, 236), o_w=(1.04, 1.04, 1.02), sb=(84, 78, 60), sbU=(96, 88, 68),
    c_th=(26, 28, 34), c_thb=(-26, -28, -34), e_th=(-26, -28, -34),
    s_tth=(34, 34, 38), s_bth=(-146, -146, -142),
    dotw=(44, 100, 190), i_dot_y=(666, 646, 626), t_top=(690, 680, 670),
)

BRIOCHE = fam(
    name="Brioche",
    style_note="Soft serif",
    xh=520, cap=700, asc=750, desc=-220, o=11, oc=13,
    S=(24, 92, 204), T=(20, 64, 132), SU=(26, 96, 212), TU=(22, 68, 140),
    k=0.58, ki=(0.6, 0.62, 0.68), kU=0.58, kiU=(0.6, 0.62, 0.68),
    serif="soft", sf_t=(22, 56, 86), sf_e=(44, 62, 74), sf_br=(30, 40, 40), sf_round=1.0,
    sf_vt=(22, 56, 92), sf_vh=(34, 40, 30), sf_de=0.9, sf_midbeak=False,
    x_w=(1.08, 1.12, 1.44), v_w=(1.08, 1.1, 1.2), K_lj=(0.42, 0.44, 0.5),
    term="round", dot="round", one_base=True,
    n_c=(300, 280, 222), o_w=(1.05, 1.05, 1.03), sb=(36, 30, 22), sbU=(42, 36, 26),
    H_c=(410, 392, 324), E_w=0.88, F_w=0.84, L_w=0.82, T_w=0.94,
    c_th=(44, 44, 48), c_thb=(-44, -44, -48), e_th=(-40, -42, -46),
    dotw=(46, 104, 196),
)

FAMILIES = {"halden": HALDEN, "rondel": RONDEL, "tessera": TESSERA, "alder": ALDER, "mallow": MALLOW,
            "strata": STRATA, "plaza": PLAZA, "vesper": VESPER, "ledger": LEDGER, "folio": FOLIO,
            "opaline": OPALINE, "signal": SIGNAL, "tally": TALLY, "topsy": TOPSY, "tempo": TEMPO,
            "pebble": PEBBLE, "orbit": ORBIT, "cleft": CLEFT, "beacon": BEACON, "brioche": BRIOCHE}
