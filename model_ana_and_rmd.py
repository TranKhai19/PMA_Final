import pandas as pd
import json
from googletrans import Translator
import random
from sklearn.linear_model import LinearRegression
import requests

data = pd.read_csv('./Data/sales_data2.csv')

data['Date'] = pd.to_datetime(data['Date'])
data['Month'] = data['Date'].dt.to_period('M')

recent_5_months = data['Month'].sort_values().unique()[-5:]
data_5_months = data[data['Month'].isin(recent_5_months)]

X = data_5_months['Month'].dt.to_timestamp().apply(lambda x: x.toordinal()).values.reshape(-1, 1)
y = data_5_months['Quantity'].values.reshape(-1, 1)

model = LinearRegression()
model.fit(X, y)

# Dự đoán số lượng cho 3 tháng tiếp theo
next_3_months = data_5_months['Month'].max() + 3
next_3_months_timestamp = next_3_months.to_timestamp()
X_next = next_3_months_timestamp.toordinal()
X_next = X_next
predicted_quantity = model.predict([[X_next]])

top_products = data.groupby(['Product', 'Month'])['Quantity'].mean().nlargest(8).index
results_json = {"product": []}

another_results = {"abc": []}

translator = Translator()

api_key = 'AIzaSyCttqTF0YlSEiI9l3Qp8i444zVCKt0bLlQ'
for product_name, month_value in top_products: # Chọn 8 mặt hàng để đề xuất
    product = data[(data['Product'] == product_name) & (data['Month'] == month_value)]
    product_name = product['Product'].iloc[0]


    try:
        # Dịch tên sản phẩm sang tiếng Việt
        product_name_vi = translator.translate(product_name, src='en', dest='vi').text
    except Exception as e:
        print(f"Error translating product name: {e}")
        continue  # Skip to the next iteration

    suppliers_list = []
    num_results = 8

    search_query = f'{product_name_vi} suppliers'
    search_url = f'https://www.googleapis.com/customsearch/v1?q={search_query}&key={api_key}&num={num_results}'

    try:
        response = requests.get(search_url)
        response.raise_for_status()

        # Parse the JSON response
        search_results = response.json().get('items', [])

        for j, result in enumerate(search_results, 1):
            suppliers_list.append({f'supplier_{j}': result['link']})
    except Exception as e:
        print(f"Error during API request: {e}")

    predicted_quantity_product = predicted_quantity.mean()

    predicted_revenue_product = product['Revenue'].mean()

    month_value = product['Month'].values[0]

    random_color = f'rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 0.2)'

    product_entry = {
        "product_name": product_name_vi,
        "predicted_quantity": predicted_quantity_product,
        "suppliers": suppliers_list,
        "color": random_color,
        "month": str(month_value)
    }

    sum_entry = {
        "product_name": product_name_vi,
        "month": str(month_value),
        "sum": (predicted_revenue_product),
    }

    results_json["product"].append(product_entry)
    another_results["abc"].append(sum_entry)

# Lưu kết quả vào file JSON
with open('results_with_predictions.json', 'w', encoding='utf-8') as json_file:
    json.dump(results_json, json_file, ensure_ascii=False, indent=4)

with open('another.json', 'w', encoding='utf-8') as json_file:
    json.dump(another_results, json_file, ensure_ascii=False, indent=4)

print("Results with predictions saved to 'results_with_predictions.json'")
print("Results with predictions saved to 'another.json'")
