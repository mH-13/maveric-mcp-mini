#!/usr/bin/env python3
"""
Performance Trends and Predictions Analysis
Fixed version without LinAlgError
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta, timezone
import warnings
warnings.filterwarnings('ignore')

def analyze_performance_trends(df):
    """Analyze performance trends with robust error handling"""
    if df.empty:
        print("⚠️ No data available for trend analysis")
        return
    
    # Performance trends and predictions
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Performance Trends & Predictions', fontsize=16, fontweight='bold')
    
    # 1. System uptime trend over time
    df_hourly = df.set_index('ts').groupby('cell_id')['status_numeric'].resample('H').mean().reset_index()
    system_hourly = df_hourly.groupby('ts')['status_numeric'].mean()
    
    if len(system_hourly) > 1:
        axes[0,0].plot(system_hourly.index, system_hourly.values * 100, 'b-', linewidth=2)
        axes[0,0].set_title('System Uptime Trend (Hourly)')
        axes[0,0].set_ylabel('Uptime %')
        axes[0,0].grid(True, alpha=0.3)
        
        # Add trend line with error handling
        try:
            x_numeric = np.arange(len(system_hourly))
            if len(set(system_hourly.values)) > 1:  # Check for variation in data
                z = np.polyfit(x_numeric, system_hourly.values, 1)
                p = np.poly1d(z)
                axes[0,0].plot(system_hourly.index, p(x_numeric) * 100, "--", alpha=0.8, color='red', label='Trend')
                
                # Predict next hour
                next_hour_pred = p(len(system_hourly)) * 100
                trend_direction = 'improving' if z[0] > 0 else 'declining' if z[0] < 0 else 'stable'
                axes[0,0].text(0.02, 0.98, f'Trend: {trend_direction}\nPredicted next: {next_hour_pred:.1f}%', 
                            transform=axes[0,0].transAxes, verticalalignment='top',
                            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            else:
                axes[0,0].text(0.02, 0.98, 'Stable performance', 
                            transform=axes[0,0].transAxes, verticalalignment='top',
                            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
        except Exception as e:
            print(f"Note: Trend analysis skipped due to insufficient data variation")
    
    # 2. Cell performance ranking
    cell_performance = df.groupby('cell_id')['status_numeric'].mean().sort_values(ascending=False)
    colors = ['green' if x > 0.95 else 'orange' if x > 0.8 else 'red' for x in cell_performance.values]
    axes[0,1].barh(range(len(cell_performance)), cell_performance.values * 100, color=colors)
    axes[0,1].set_yticks(range(len(cell_performance)))
    axes[0,1].set_yticklabels([f'Cell {i}' for i in cell_performance.index])
    axes[0,1].set_title('Cell Performance Ranking')
    axes[0,1].set_xlabel('Uptime %')
    axes[0,1].axvline(x=95, color='orange', linestyle='--', alpha=0.7, label='SLA Target')
    axes[0,1].legend()
    
    
    
    # 3. Failure pattern analysis
    failure_times = df[df['status'] == 'OFF']['ts'].dt.hour.value_counts().sort_index()
    if len(failure_times) > 0:
        axes[1,0].bar(failure_times.index, failure_times.values, color='red', alpha=0.7)
        axes[1,0].set_title('Failure Pattern by Hour of Day')
        axes[1,0].set_xlabel('Hour of Day')
        axes[1,0].set_ylabel('Failure Count')
        axes[1,0].grid(True, alpha=0.3)
    else:
        axes[1,0].text(0.5, 0.5, 'No failures detected', ha='center', va='center', 
                    transform=axes[1,0].transAxes, fontsize=12)
        axes[1,0].set_title('Failure Pattern by Hour of Day')
    
    # 4. SLA compliance forecast
    sla_compliance = (cell_performance > 0.95).sum() / len(cell_performance) * 100
    axes[1,1].pie([sla_compliance, 100-sla_compliance], 
                  labels=[f'SLA Compliant\n({sla_compliance:.1f}%)', 
                         f'Below SLA\n({100-sla_compliance:.1f}%)'],
                  colors=['green', 'red'], autopct='%1.1f%%', startangle=90)
    axes[1,1].set_title('Current SLA Compliance')
    
    plt.tight_layout()
    plt.show()
    
    # Performance insights
    print("\n📈 PERFORMANCE INSIGHTS:")
    print("=" * 40)
    print(f"• Current SLA compliance: {sla_compliance:.1f}%")
    print(f"• Best performing cell: {cell_performance.index[0]} ({cell_performance.iloc[0]*100:.1f}% uptime)")
    print(f"• Worst performing cell: {cell_performance.index[-1]} ({cell_performance.iloc[-1]*100:.1f}% uptime)")
    
    if len(failure_times) > 0:
        peak_failure_hour = failure_times.idxmax()
        print(f"• Peak failure time: {peak_failure_hour}:00 ({failure_times.max()} failures)")
    else:
        print("• No specific failure patterns detected")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    print("=" * 40)
    
    critical_cells = cell_performance[cell_performance < 0.8]
    if len(critical_cells) > 0:
        print(f"• Immediate attention needed for cells: {list(critical_cells.index)}")
    
    if sla_compliance < 80:
        print("• System-wide performance review required")
        print("• Consider infrastructure upgrades")
    
    if len(failure_times) > 0 and failure_times.max() > failure_times.mean() * 2:
        peak_failure_hour = failure_times.idxmax()
        print(f"• Schedule maintenance during low-activity periods (avoid {peak_failure_hour}:00)")
    
    # Simple prediction based on current performance
    avg_uptime = cell_performance.mean() * 100
    if avg_uptime > 90:
        print("• System performance is generally good")
    elif avg_uptime > 70:
        print("• System performance needs improvement")
    else:
        print("• Critical system performance issues detected")

if __name__ == "__main__":
    # This would be called from the notebook
    pass