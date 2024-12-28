import matplotlib.pyplot as plt
from bidi.algorithm import get_display
from arabic_reshaper import reshape
import matplotlib
import pandas as pd
import seaborn as sns
import plotly.io as pio

# Function to convert English numbers to Farsi
def en_to_fa(num, formatter='%1.1f%%'):
    num_as_string = formatter % num
    mapping = dict(list(zip('0123456789.%', '۰۱۲۳۴۵۶۷۸۹.%')))
    return ''.join(mapping.get(digit, digit) for digit in num_as_string)

# Correcting font settings for Farsi display
font = {'family': 'B Nazanin', 'size': 12}
matplotlib.rc('font', **font)
sns.set(font='B Nazanin', font_scale=1.2, style="whitegrid")

# Creating the data
data = {
    "راننده": ["مهندس اصالت", "مهندس فتاحی", "مهندس نجات", "مهندس پیرمحمدی", "مهندس زالی", "مهندس طاهایی",
               "مهندس فرحانی", "مهندس ضیایی", "مهندس اطلاعات", "مهندس ممتازی", "مهندس رجبعلی", "مهندس صفی‌خانی",
               "مهندس شمس", "مهندس فغانی", "مهندس زارعی", "مهندس ارژنگی", "مهندس داوری", "مهندس دشتی",
               "مهندس حسینی", "مهندس خسروی", "مهندس یعقوبی", "مهندس شرقی", "مهندس نعیمایی"],
    "میانگین مصرف (لیتر بر صد کیلومتر)": [8.7, 6.9, 7.8, 8.0, 10.4, 8.8, 11.1, 10.7, 9.7, 12.8, 9.1, 10.2, 7.8, 7.7, 7.3, 8.1, 8.5, 7.9, 8.0, 8.3, 6.3, 9.2, 7.9],
    "مسافت پیموده شده (کیلومتر)": [53550.5, 8702.8, 16799.4, 2942, 6335.8, 8647.1, 5612.3, 4418.7, 6013.3, 997.0,
                                     3640.5, 1624.4, 1144.0, 967.0, 2399.0, 1608.3, 8962.0, 2747.0, 501, 12027.2,
                                     1170.0, 2138.0, 2278.5],
    "زمان پیمایش (ساعت)": [1233.5, 255.0, 570.3, 134.7, 176.5, 223.2, 165.1, 143.7, 173.0, 29.9, 101.4, 60.1,
                           19.3, 23.1, 53.2, 39.7, 256.7, 62.3, 12.9, 273.8, 25.8, 64.4, 53.6],
    "میانگین سرعت (کیلومتر بر ساعت)": [43.4, 34.1, 29.4, 21.8, 35.8, 38.7, 33.9, 30.7, 34.7, 33.3, 35.9, 27.0,
                                        59.2, 41.8, 45.0, 40.5, 34.9, 44.0, 38.8, 43.9, 45.3, 33.19, 42.5],
    "تعداد میکروسفر": [1495, 631, 1318, 137, 554, 622, 448, 300, 276, 41, 307, 188, 22, 46, 170, 99, 661, 152,
                        33, 644, 35, 247, 90]
}

df = pd.DataFrame(data)

# Prepare Farsi labels for each driver
df['راننده_فارس'] = [get_display(reshape(driver)) for driver in df['راننده']]

# Function to reshape and display Farsi text
def fa_text(text):
    return get_display(reshape(text))

# 1. Heatmap: Correlation matrix
plt.figure(figsize=(10, 8))
corr = df.drop(['راننده', 'راننده_فارس'], axis=1).corr()
sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
plt.title(fa_text('ماتریس همبستگی ویژگی‌ها'), fontsize=16)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.show()

# 2. Scatter Plot: Average speed vs. fuel consumption with Seaborn
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df,
                x='میانگین سرعت (کیلومتر بر ساعت)',
                y='میانگین مصرف (لیتر بر صد کیلومتر)',
                hue='راننده_فارس',
                palette='tab10',
                s=100)
plt.title(fa_text('میانگین سرعت در مقابل میانگین مصرف سوخت'), fontsize=16)
plt.xlabel(fa_text('میانگین سرعت (کیلومتر بر ساعت)'))
plt.ylabel(fa_text('میانگین مصرف (لیتر بر صد کیلومتر)'))
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0., title=fa_text('راننده'))
plt.tight_layout()
plt.show()

# 3. Violin Plot: Distribution of average speed
plt.figure(figsize=(10, 6))
sns.violinplot(y=df['میانگین سرعت (کیلومتر بر ساعت)'], palette='Pastel1')
plt.title(fa_text('توزیع میانگین سرعت رانندگان'), fontsize=16)
plt.ylabel(fa_text('میانگین سرعت (کیلومتر بر ساعت)'))
plt.tight_layout()
plt.show()

# 4. Pair Plot: Relationships between variables with larger figure size and adjusted layout
pairplot = sns.pairplot(df.drop(['راننده', 'راننده_فارس'], axis=1), diag_kind='kde', corner=True, height=2.5)
pairplot.fig.suptitle(fa_text('نمودارهای جفتی ویژگی‌ها'), y=1.02, fontsize=16)

# Adjust the labels
for ax in pairplot.axes.flat:
    if ax:
        ax.set_xlabel(fa_text(ax.get_xlabel()))
        ax.set_ylabel(fa_text(ax.get_ylabel()))

# Increase space between subplots
plt.subplots_adjust(top=0.95, bottom=0.1, left=0.1, right=0.9, hspace=0.5, wspace=0.5)

plt.show()


# 5. Bar Chart: Distance covered by each driver with Seaborn
plt.figure(figsize=(12, 6))
sns.barplot(x='راننده_فارس',
            y='مسافت پیموده شده (کیلومتر)',
            data=df,
            palette='viridis')
plt.title(fa_text('مسافت پیموده‌شده بر حسب راننده'), fontsize=16)
plt.xlabel(fa_text('راننده'))
plt.ylabel(fa_text('مسافت پیموده شده (کیلومتر)'))
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

# 6. Box Plot: Fuel consumption by driver
plt.figure(figsize=(12, 6))
sns.boxplot(x='راننده_فارس', y='میانگین مصرف (لیتر بر صد کیلومتر)', data=df, palette='Set3')
plt.title(fa_text('میانگین مصرف سوخت بر حسب راننده'), fontsize=16)
plt.xlabel(fa_text('راننده'))
plt.ylabel(fa_text('میانگین مصرف (لیتر بر صد کیلومتر)'))
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

# 7. Regression Plot: Relationship between time and distance
plt.figure(figsize=(10, 6))
sns.regplot(x='زمان پیمایش (ساعت)', y='مسافت پیموده شده (کیلومتر)', data=df, color='teal')
plt.title(fa_text('رگرسیون مسافت پیموده‌شده بر حسب زمان'), fontsize=16)
plt.xlabel(fa_text('زمان پیمایش (ساعت)'))
plt.ylabel(fa_text('مسافت پیموده شده (کیلومتر)'))
plt.tight_layout()
plt.show()

# 8. Radar Chart: Performance metrics per driver
from math import pi

# Prepare data
categories = ['میانگین مصرف (لیتر بر صد کیلومتر)', 'میانگین سرعت (کیلومتر بر ساعت)', 'مسافت پیموده شده (کیلومتر)']
categories_fa = [fa_text(cat) for cat in categories]
N = len(categories)

# Normalize data for radar chart
df_radar = df[['راننده_فارس'] + categories].copy()
for cat in categories:
    max_value = df_radar[cat].max()
    df_radar[cat] = df_radar[cat] / max_value

# Start plotting
angles = [n / float(N) * 2 * pi for n in range(N)]
angles += angles[:1]

plt.figure(figsize=(8, 8))
ax = plt.subplot(111, polar=True)

for index, row in df_radar.iterrows():
    values = row[categories].tolist()
    values += values[:1]
    ax.plot(angles, values, linewidth=1, linestyle='solid', label=row['راننده_فارس'])

ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories_fa)

# Apply Farsi processing to tick labels
ax.tick_params(axis='x', pad=15)
for label in ax.get_xticklabels():
    label.set_fontsize(12)

plt.title(fa_text('نمودار راداری عملکرد رانندگان'), fontsize=16)
plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
plt.tight_layout()
plt.show()
