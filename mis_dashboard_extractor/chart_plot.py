import matplotlib.pyplot as plt
from bidi.algorithm import get_display
from arabic_reshaper import reshape
import matplotlib
import pandas as pd

# Function to convert English numbers to Farsi
def en_to_fa(num, formatter='%1.1f%%'):
    num_as_string = formatter % num
    mapping = dict(list(zip('0123456789.%', '۰۱۲۳۴۵۶۷۸۹.%')))
    return ''.join(mapping[digit] for digit in num_as_string)

# Correcting font settings for Farsi display
font = {'family': 'B Nazanin', 'size': 12}
matplotlib.rc('font', **font)

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

fuel_consumed = [4667.4, 603.0, 1324.5, 237.1, 660.5, 769.3, 626.7, 474.9, 586.3, 127.7, 332.4, 166.0, 89.6,
                 74.7, 176.3, 131.4, 763.7, 217.4, 40.4, 1003.5, 74, 198.5, 181.1]

df['سوخت مصرفی(لیتر)'] = fuel_consumed

# Prepare Farsi labels for each driver
df['راننده_فارس'] = [get_display(reshape(driver)) for driver in df['راننده']]

# 1. Bar Chart: Fuel consumption comparison by driver
plt.figure(figsize=(10, 6))
plt.bar(df['راننده_فارس'], df['میانگین مصرف (لیتر بر صد کیلومتر)'], color='skyblue')
plt.title(get_display(reshape('میانگین مصرف سوخت بر حسب راننده')), fontsize=14)
plt.xlabel(get_display(reshape('راننده')), fontsize=12)
plt.ylabel(get_display(reshape('میانگین مصرف سوخت (لیتر بر صد کیلومتر)')), fontsize=12)
plt.xticks(rotation=90, fontsize=10)
plt.tight_layout()
plt.show()

# 2. Line Chart: Distance covered over time for each driver
plt.figure(figsize=(10, 6))
plt.plot(df['راننده_فارس'], df['مسافت پیموده شده (کیلومتر)'], marker='o', color='blue')
plt.title(get_display(reshape('مسافت پیموده‌شده در طول زمان برای هر راننده')), fontsize=14)
plt.xlabel(get_display(reshape('راننده')), fontsize=12)
plt.ylabel(get_display(reshape('مسافت پیموده‌شده (کیلومتر)')), fontsize=12)
plt.xticks(rotation=90, fontsize=10)
plt.tight_layout()
plt.show()

# 3. Scatter Plot: Average speed vs. fuel consumption
plt.figure(figsize=(10, 6))
plt.scatter(df['میانگین سرعت (کیلومتر بر ساعت)'], df['سوخت مصرفی(لیتر)'], color='blue')
plt.title(get_display(reshape('میانگین سرعت در مقابل میانگین مصرف سوخت')), fontsize=14)
plt.xlabel(get_display(reshape('میانگین سرعت (کیلومتر بر ساعت)')), fontsize=12)
plt.ylabel(get_display(reshape('میانگین مصرف سوخت (لیتر بر صد کیلومتر)')), fontsize=12)
plt.grid(True)
plt.tight_layout()
plt.show()

# 4. Pie Chart: Distance covered share by each driver
plt.figure(figsize=(10, 6))
plt.pie(df['مسافت پیموده شده (کیلومتر)'], labels=df['راننده_فارس'], autopct=en_to_fa, startangle=90)
plt.title(get_display(reshape('سهم مسافت پیموده‌شده توسط هر راننده از کل')), fontsize=14)
plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
plt.tight_layout()
plt.show()

# 5. Bar Chart: Microspheres used by driver
plt.figure(figsize=(10, 6))
plt.bar(df['راننده_فارس'], df['تعداد میکروسفر'], color='green')
plt.title(get_display(reshape('تعداد میکروسفر بر حسب راننده')), fontsize=14)
plt.xlabel(get_display(reshape('راننده')), fontsize=12)
plt.ylabel(get_display(reshape('تعداد میکروسفر')), fontsize=12)
plt.xticks(rotation=90, fontsize=10)
plt.tight_layout()
plt.show()

# 6. Combined Chart: Fuel consumption and distance covered by driver
fig, ax1 = plt.subplots(figsize=(10, 6))

# Bar chart for distance covered
ax1.bar(df['راننده_فارس'], df['مسافت پیموده شده (کیلومتر)'], color='lightblue', label=get_display(reshape('مسافت پیموده شده (کیلومتر)')))
ax1.set_xlabel(get_display(reshape('راننده')))
ax1.set_ylabel(get_display(reshape('مسافت پیموده شده (کیلومتر)')), color='blue')
ax1.tick_params(axis='x', rotation=90)
ax1.tick_params(axis='y', labelcolor='blue')

# Create a second y-axis for fuel consumption
ax2 = ax1.twinx()
ax2.plot(df['راننده_فارس'], df['سوخت مصرفی(لیتر)'], color='red', marker='o', label=get_display(reshape('سوخت مصرفی (لیتر)')))
ax2.set_ylabel(get_display(reshape('سوخت مصرفی (لیتر)')), color='red')
ax2.tick_params(axis='y', labelcolor='red')

fig.tight_layout()
plt.title(get_display(reshape('سوخت مصرفی و مسافت پیموده‌شده بر حسب راننده')))
plt.show()

# 7. Histogram: Distribution of average speed with Farsi labels
plt.figure(figsize=(10, 6))
plt.hist(df['میانگین سرعت (کیلومتر بر ساعت)'], bins=10, color='purple', edgecolor='black')
plt.title(get_display(reshape('توزیع میانگین سرعت بین رانندگان')), fontsize=14)
plt.xlabel(get_display(reshape('میانگین سرعت (کیلومتر بر ساعت)')), fontsize=12)
plt.ylabel(get_display(reshape('تعداد راننده')), fontsize=12)
plt.tight_layout()
plt.show()
