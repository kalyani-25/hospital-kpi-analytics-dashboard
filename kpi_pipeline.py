"""
Project 4: Hospital Operations KPI Pipeline
Generates 2 years of daily metrics for Power BI dashboard
Run: python kpi_pipeline.py
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

np.random.seed(42)

departments = {
    'ICU':      {'beds': 20, 'base_occ': 0.92},
    'ER':       {'beds': 40, 'base_occ': 0.87},
    'Med-Surg': {'beds': 80, 'base_occ': 0.80},
    'Surgery':  {'beds': 30, 'base_occ': 0.72},
    'Peds':     {'beds': 25, 'base_occ': 0.61},
}

dates   = pd.date_range('2023-01-01', '2024-12-31', freq='D')
records = []
for date in dates:
    month   = date.month
    weekday = date.weekday()
    season  = 1.15 if month in [12,1,2] else 0.92 if month in [6,7,8] else 1.0
    weekend = 0.88 if weekday >= 5 else 1.0
    for dept, info in departments.items():
        occ = info['base_occ'] * season * weekend * np.random.normal(1, 0.03)
        occ = min(1.0, max(0.3, occ))
        los_means = {'ICU':6.2,'ER':0.5,'Med-Surg':4.1,'Surgery':3.8,'Peds':2.9}
        records.append({
            'date': date,
            'department': dept,
            'total_beds': info['beds'],
            'occupied_beds': round(info['beds'] * occ),
            'occupancy_rate': round(occ * 100, 1),
            'admissions': max(0, round(info['beds'] * 0.12 * season * weekend * np.random.normal(1, 0.15))),
            'discharges': max(0, round(info['beds'] * 0.11 * season * weekend * np.random.normal(1, 0.15))),
            'avg_los': round(abs(np.random.normal(los_means[dept], 0.5)), 1),
            'cost_per_day': round(np.random.normal({'ICU':4200,'ER':800,'Med-Surg':1800,'Surgery':2500,'Peds':2100}[dept], 200)),
        })

df = pd.DataFrame(records)
df['alert'] = df['occupancy_rate'].apply(
    lambda x: 'CRITICAL' if x >= 95 else 'WARNING' if x >= 90 else 'OK'
)
df['year_month'] = df['date'].dt.to_period('M').astype(str)

df.to_csv('hospital_kpis.csv', index=False)
print(f"Saved hospital_kpis.csv ({len(df):,} rows)")

latest = df[df['date'] == df['date'].max()]
print("\nLatest occupancy rates:")
print(df.groupby('department')['occupancy_rate'].mean().sort_values(ascending=False).round(1))

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Hospital Operations KPI Dashboard', fontsize=15, fontweight='bold')

occ_by_dept = df.groupby('department')['occupancy_rate'].mean().sort_values(ascending=False)
bar_colors = ['#E24B4A' if v>=90 else '#EF9F27' if v>=80 else '#1D9E75' for v in occ_by_dept.values]
axes[0,0].barh(occ_by_dept.index, occ_by_dept.values, color=bar_colors)
axes[0,0].axvline(85, color='orange', linestyle='--', linewidth=1.5, label='85% target')
axes[0,0].axvline(95, color='red',    linestyle='--', linewidth=1.5, label='95% critical')
axes[0,0].set_title('Average Bed Occupancy by Department (%)')
axes[0,0].set_xlabel('Occupancy %')
axes[0,0].legend(fontsize=9)
axes[0,0].set_xlim(0, 105)

monthly = df.groupby([df['date'].dt.to_period('M'), 'department'])['admissions'].sum().unstack()
dept_colors = {'ICU':'#E24B4A','ER':'#EF9F27','Med-Surg':'#378ADD','Surgery':'#7F77DD','Peds':'#1D9E75'}
for dept in ['ICU','ER','Med-Surg']:
    if dept in monthly.columns:
        axes[0,1].plot(range(len(monthly)), monthly[dept], label=dept, color=dept_colors[dept])
axes[0,1].set_title('Monthly Admissions Trend')
axes[0,1].set_xlabel('Month (0 = Jan 2023)')
axes[0,1].set_ylabel('Admissions')
axes[0,1].legend()
axes[0,1].grid(alpha=0.3)

los = df.groupby('department')['avg_los'].mean().sort_values()
axes[1,0].bar(los.index, los.values, color='#7F77DD')
axes[1,0].set_title('Average Length of Stay by Department (days)')
axes[1,0].set_ylabel('Days')
for i, v in enumerate(los.values):
    axes[1,0].text(i, v + 0.05, f'{v:.1f}', ha='center', fontsize=10)

alert_counts = df['alert'].value_counts()
pie_colors = {'OK':'#1D9E75','WARNING':'#EF9F27','CRITICAL':'#E24B4A'}
axes[1,1].pie(alert_counts.values, labels=alert_counts.index,
              colors=[pie_colors.get(k,'gray') for k in alert_counts.index],
              autopct='%1.1f%%', startangle=90)
axes[1,1].set_title('Capacity Alert Distribution (All Days)')

plt.tight_layout()
plt.savefig('hospital_kpis.png', dpi=150, bbox_inches='tight')
print("Saved hospital_kpis.png")
