# Power BI DAX Measures -- Hospital Operations KPI Dashboard

## Setup: Import hospital_kpis.csv into Power BI
## Create a Calendar table: Calendar = CALENDARAUTO()

---

## Occupancy Measures

```dax
Occupancy Rate =
  DIVIDE(SUM(KPIs[occupied_beds]), SUM(KPIs[total_beds]), 0) * 100

Occupancy Rate % =
  FORMAT([Occupancy Rate], "0.0") & "%"

Over Capacity Days =
  CALCULATE(COUNTROWS(KPIs), KPIs[occupancy_rate] >= 90)

Critical Capacity Days =
  CALCULATE(COUNTROWS(KPIs), KPIs[occupancy_rate] >= 95)

Occupancy vs Target =
  [Occupancy Rate] - 85
```

## Volume Measures

```dax
Total Admissions = SUM(KPIs[admissions])
Total Discharges = SUM(KPIs[discharges])
Net Census       = [Total Admissions] - [Total Discharges]
Avg LOS          = AVERAGE(KPIs[avg_los])
Cost per Day     = AVERAGE(KPIs[cost_per_day])
```

## Time Intelligence

```dax
Admissions MoM% =
  VAR CurrentMonth = [Total Admissions]
  VAR PrevMonth    = CALCULATE([Total Admissions], PREVIOUSMONTH(Calendar[Date]))
  RETURN DIVIDE(CurrentMonth - PrevMonth, PrevMonth)

YTD Admissions = TOTALYTD([Total Admissions], Calendar[Date])

Rolling 7-Day Avg Occupancy =
  AVERAGEX(
    DATESINPERIOD(Calendar[Date], LASTDATE(Calendar[Date]), -7, DAY),
    CALCULATE([Occupancy Rate])
  )
```

## Alert Color (for conditional formatting)

```dax
Alert Color =
  SWITCH(TRUE(),
    [Occupancy Rate] >= 95, "#E24B4A",
    [Occupancy Rate] >= 90, "#EF9F27",
    "#1D9E75"
  )
```

## KPI Card Targets

```dax
Occupancy Status =
  IF([Occupancy Rate] >= 95, "Critical",
  IF([Occupancy Rate] >= 90, "Warning", "On Target"))

LOS Status =
  IF([Avg LOS] > 8, "Critical",
  IF([Avg LOS] > 5, "Warning", "On Target"))
```

---

## Recommended Dashboard Layout
1. Row 1: 4 KPI cards (Occupancy %, Avg LOS, Total Admissions today, Critical Alerts)
2. Row 2: Bar chart (Occupancy by Dept) + Line chart (Monthly trend)
3. Row 3: Table with per-department detail + Alert status column
4. Slicers: Date range, Department, Alert Status
