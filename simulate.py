"""
========================================================================================
TEİAŞ 154/380 kV Substation Congestion & BESS Duration Optimization Model
Türkiye 33.1 GW Storage Pipeline Feeder Saturation Simulator
Author: Muhammed Talha Çırak (@talhacirak_energy / GitHub: talhacrak01)
Energy Systems Engineering, Adana Alparslan Türkeş Science and Technology University
========================================================================================
"""

import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# Visual aesthetic configuration
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#334155'
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['text.color'] = '#f8fafc'
plt.rcParams['axes.labelcolor'] = '#94a3b8'
plt.rcParams['xtick.color'] = '#94a3b8'
plt.rcParams['ytick.color'] = '#94a3b8'

FEEDER_THERMAL_LIMIT_MW = 108.0  # Typical 154 kV overhead transmission feeder N-1 threshold
BATTERY_CAPACITY_MWH = 110.0      # Nominal storage energy capacity

def calculate_profiles():
    time_h = np.linspace(0, 4.5, 450)
    
    # Base load on 154 kV substation feeder during evening peak
    p_base = 25.0 + 8.0 * np.sin(np.pi * time_h / 4.5)
    
    # Profile 1: 1.1h Shock Discharge (100 MW / 110 MWh - TR Regulatory Minimum 1:1)
    p_bess_1h = np.zeros_like(time_h)
    p_bess_1h[time_h <= 1.1] = 100.0
    
    # Profile 2: 2.5h Balanced Discharge (44 MW / 110 MWh)
    p_bess_2_5h = np.zeros_like(time_h)
    p_bess_2_5h[time_h <= 2.5] = 44.0
    
    # Profile 3: 4.0h Deep Shift (27.5 MW / 110 MWh)
    p_bess_4h = np.zeros_like(time_h)
    p_bess_4h[time_h <= 4.0] = 27.5
    
    # Total Feeder Loadings
    total_1h = p_base + p_bess_1h
    total_2_5h = p_base + p_bess_2_5h
    total_4h = p_base + p_bess_4h
    
    # Substation Loading Percentages
    pct_1h = (total_1h / FEEDER_THERMAL_LIMIT_MW) * 100.0
    pct_2_5h = (total_2_5h / FEEDER_THERMAL_LIMIT_MW) * 100.0
    pct_4h = (total_4h / FEEDER_THERMAL_LIMIT_MW) * 100.0
    
    return time_h, p_base, p_bess_1h, p_bess_2_5h, p_bess_4h, total_1h, total_2_5h, total_4h, pct_1h, pct_2_5h, pct_4h

def plot_substation_congestion(time_h, p_base, p_bess_1h, p_bess_2_5h, total_1h, total_2_5h, pct_1h, pct_2_5h, out_dir="."):
    fig = plt.figure(figsize=(12, 10), facecolor='#0f172a')
    gs = gridspec.GridSpec(2, 1, height_ratios=[1.2, 1.0], hspace=0.35)
    
    # Subplot 1: Active Power Dispatch
    ax1 = fig.add_subplot(gs[0], facecolor='#1e293b')
    ax1.plot(time_h, p_bess_1h, color='#ef4444', linewidth=3.0, label='1.1h Şok Deşarj (100 MW - TR Mevzuat Oranı 1:1)')
    ax1.plot(time_h, p_bess_2_5h, color='#10b981', linewidth=3.0, label='2.5h Dengeli Deşarj (44 MW - Şebeke Dostu)')
    ax1.plot(time_h, p_base, color='#64748b', linestyle='--', linewidth=1.8, label='Fider Arka Plan Temel Yükü (P_base)')
    
    ax1.axvline(1.1, color='#ef4444', linestyle=':', alpha=0.7)
    ax1.axvline(2.5, color='#10b981', linestyle=':', alpha=0.7)
    
    ax1.set_title('BESS Deşarj Güç Profili P(t) vs Süre Karşılaştırması', fontsize=14, fontweight='bold', pad=14, color='#f8fafc')
    ax1.set_ylabel('Aktif Güç (MW)', fontsize=12, fontweight='bold')
    ax1.set_xlim(0, 4.2)
    ax1.set_ylim(0, 115)
    ax1.grid(True, linestyle='--', alpha=0.25, color='#475569')
    ax1.legend(loc='upper right', frameon=True, facecolor='#0f172a', edgecolor='#334155', fontsize=10)
    
    # Subplot 2: Substation Feeder Thermal Loading & Overload
    ax2 = fig.add_subplot(gs[1], facecolor='#1e293b')
    ax2.plot(time_h, pct_1h, color='#ef4444', linewidth=2.8, label='1.1h BESS ile Fider Termal Yüklenmesi')
    ax2.plot(time_h, pct_2_5h, color='#10b981', linewidth=2.8, label='2.5h BESS ile Fider Termal Yüklenmesi')
    
    # 100% Thermal Limit
    ax2.axhline(100.0, color='#f59e0b', linestyle='-', linewidth=2.2, label='N-1 Termik Güvenlik Limiti (%100 - 108 MW)')
    ax2.fill_between(time_h, 100.0, np.maximum(pct_1h, 100.0), color='#ef4444', alpha=0.25, label='AŞIRI YÜKLENME (OVERLOAD BÖLGESİ)')
    
    ax2.set_title('TEİAŞ 154 kV Fider Doygunluk ve N-1 Termal Güvenlik Analizi', fontsize=14, fontweight='bold', pad=14, color='#f8fafc')
    ax2.set_xlabel('Zaman (Saat)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Fider Yüklenme Oranı (%)', fontsize=12, fontweight='bold')
    ax2.set_xlim(0, 4.2)
    ax2.set_ylim(20, 130)
    ax2.grid(True, linestyle='--', alpha=0.25, color='#475569')
    ax2.legend(loc='lower right', frameon=True, facecolor='#0f172a', edgecolor='#334155', fontsize=10)
    
    # Annotation
    max_ovl = np.max(pct_1h)
    ax2.annotate(f'PİK AŞIRI YÜK: %{max_ovl:.1f}\nTrafo/Fider Trip Riski!',
                 xy=(0.55, max_ovl), xytext=(1.4, 118),
                 arrowprops=dict(facecolor='#ef4444', shrink=0.08, width=2, headwidth=8),
                 bbox=dict(boxstyle='round,pad=0.5', facecolor='#270f14', edgecolor='#ef4444', linewidth=1.5),
                 fontsize=10, fontweight='bold', color='#fecaca')
                 
    out_path = os.path.join(out_dir, "substation_thermal_loading.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, facecolor='#0f172a')
    plt.close()
    print(f"[OK] Saved: {out_path}")

def plot_pipeline_funnel(out_dir="."):
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='#0f172a')
    ax.set_facecolor('#1e293b')
    
    categories = [
        'EPDK Başvurusu\n(2022-2023)',
        'Tahsis Edilen\nÖnlisans',
        'Tüm RES+GES\nKurulu Gücü (Ref)',
        'Fiilen Çalışan\nBESS (Bugün)',
        'TEİAŞ Kalan İletim\nKapasitesi (Kritik)'
    ]
    values = [221000, 33100, 39800, 530, 38.7]
    colors = ['#3b82f6', '#38bdf8', '#64748b', '#ef4444', '#f59e0b']
    
    # Logarithmic scale visualization due to massive scale differences
    y_pos = np.arange(len(categories))
    bars = ax.barh(y_pos, values, color=colors, height=0.55, edgecolor='#334155', linewidth=1.2)
    ax.set_xscale('log')
    
    for bar, val in zip(bars, values):
        w = bar.get_width()
        if val >= 1000:
            txt = f" {val/1000:,.1f} GW ({val:,} MW)"
        else:
            txt = f" {val:.1f} MW"
        ax.text(w * 1.15, bar.get_y() + bar.get_height()/2.0, txt,
                ha='left', va='center', fontsize=11, fontweight='bold', color='#f8fafc')
                
    ax.set_yticks(y_pos)
    ax.set_yticklabels(categories, fontsize=11, fontweight='bold')
    ax.invert_yaxis()
    ax.set_xlim(1, 1e6)
    ax.set_xlabel('Kurulu Güç / Kapasite (MW - Logaritmik Ölçek)', fontsize=12, fontweight='bold')
    ax.set_title('Türkiye Depolamalı Elektrik Piyasası Gerçekliği (33.1 GW vs 530 MW)', fontsize=14, fontweight='bold', pad=15)
    ax.grid(True, which='both', linestyle='--', alpha=0.2, color='#475569')
    
    out_path = os.path.join(out_dir, "pipeline_capacity_funnel.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, facecolor='#0f172a')
    plt.close()
    print(f"[OK] Saved: {out_path}")

def main():
    parser = argparse.ArgumentParser(description="TEİAŞ BESS Substation Congestion Simulator")
    parser.add_argument("--outdir", default=".", help="Output directory for plots")
    args = parser.parse_args()
    
    os.makedirs(args.outdir, exist_ok=True)
    
    print("\n=======================================================")
    print("TEİAŞ BESS 154/380 kV İletim ve Fider Doygunluk Analizi")
    print("=======================================================")
    
    time_h, p_base, p_bess_1h, p_bess_2_5h, p_bess_4h, total_1h, total_2_5h, total_4h, pct_1h, pct_2_5h, pct_4h = calculate_profiles()
    
    max_ovl_1h = np.max(pct_1h)
    max_ovl_2_5h = np.max(pct_2_5h)
    
    print(f"1.1h Şok Deşarj Maks Fider Yüklenmesi : %{max_ovl_1h:.1f} (AŞIRI YÜK / TRİP TEHLİKESİ)")
    print(f"2.5h Dengeli Deşarj Maks Fider Yüklenmesi: %{max_ovl_2_5h:.1f} (GÜVENLİ MARJ)")
    print(f"Kalan Şebeke İletim Seviyesi Tahsisi   : 38.7 MW (Türkiye Geneli)")
    
    plot_substation_congestion(time_h, p_base, p_bess_1h, p_bess_2_5h, total_1h, total_2_5h, pct_1h, pct_2_5h, out_dir=args.outdir)
    plot_pipeline_funnel(out_dir=args.outdir)
    print("\n[SUCCESS] Simülasyon tamamlandı ve grafikler kaydedildi.\n")

if __name__ == "__main__":
    main()
