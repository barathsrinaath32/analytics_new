{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 34,
   "id": "015246da",
   "metadata": {},
   "outputs": [],
   "source": [
    "from matplotlib import pyplot as plt\n",
    "from pandas import DataFrame, read_csv\n",
    "from seaborn import barplot, lineplot"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 37,
   "id": "c8f6e348",
   "metadata": {},
   "outputs": [],
   "source": [
    "import requests\n",
    "import streamlit as st\n",
    "from matplotlib.backends.backend_agg import RendererAgg\n",
    "from matplotlib.figure import Figure\n",
    "from statsmodels.tsa.arima.model import ARIMA\n",
    "from streamlit_lottie import st_lottie\n",
    "from pandas import DataFrame, read_csv\n",
    "from seaborn import barplot, lineplot\n",
    "\n",
    "st.set_page_config(layout=\"wide\")\n",
    "sns.set_style(\"darkgrid\")\n",
    "\n",
    "def load_lottieurl(url: str):\n",
    "    r = requests.get(url)\n",
    "    if r.status_code != 200:\n",
    "        return None\n",
    "    return r.json()\n",
    "\n",
    "lottie_amazon = load_lottieurl(\"https://assets6.lottiefiles.com/private_files/lf30_zERHJg.json\")\n",
    "st_lottie(lottie_amazon, speed=1, height=200, key=\"initial\")\n",
    "\n",
    "_lock = RendererAgg.lock\n",
    "\n",
    "sns.set_style(\"darkgrid\")\n",
    "row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.columns((0.1, 2, 0.2, 1, 0.1))\n",
    "row0_1.title(\"Analyzing Your Amazon Purchase Habits\")\n",
    "with row0_2:\n",
    "    st.write(\"\")\n",
    "row0_2.subheader(\"A Web App by [Tyler Richards](http://www.tylerjrichards.com)\")\n",
    "\n",
    "row1_spacer1, row1_1, row1_spacer2 = st.columns((0.1, 3.2, 0.1))\n",
    "with row1_1:\n",
    "    \"\"\"\n",
    "    Hey there! Welcome to my Amazon Analysis App. I found that I was spending an\n",
    "    insane amount on Amazon every year, but I didn't have a great idea about what\n",
    "    exactly I was spending it on. I tried a few methods, like [different budgeting apps](https://copilot.money/)\n",
    "    and [Amazon's puchase history page](https://www.amazon.com/gp/your-account/order-history)\n",
    "    , but none of them gave me enough detail.\n",
    "\n",
    "    In addition to that, Jeff Bezos has put $19 billion of his fortune into going into space and making space flight cheaper\n",
    "    with Blue Origin, and after doing so,\n",
    "    said \"I want to thank every Amazon employee and every Amazon customer because you guys paid for all of this\". So\n",
    "    how much of this did I actually pay for? An insignificant amount to Jeff, but significant to me, surely.\n",
    "\n",
    "    This app analyzes your Amazon purchase habits over time, the items you've bought,\n",
    "    how much you've spent, and where this is trending over time. Have fun!\n",
    "\n",
    "    **To begin, please download [Amazon order history](https://www.amazon.com/gp/b2b/reports). This app works best on desktop, and\n",
    "    also works best with multiple years of Amazon history, so please select a few years of data to download from Amazon! The\n",
    "     report should take a few minutes to be ready from Amazon, so be patient and if it looks slow, try clicking the 'Refresh List' button. When it downloads, upload it to this app below.\n",
    "    This app neither records nor stores your data, ever.**\n",
    "    \"\"\"\n",
    "    file_name = st.file_uploader(\"Upload Your Amazon Data Here\")\n",
    "\n",
    "if file_name is not None:\n",
    "    df = read_csv(file_name)\n",
    "\n",
    "    # data cleaning\n",
    "    df[\"Order Date\"] = pd.to_datetime(df[\"Order Date\"])\n",
    "    df[\"Item Total\"] = df[\"Item Total\"].replace({\"\\$\": \"\"}, regex=True)\n",
    "    df[\"Item Total\"] = pd.to_numeric(df[\"Item Total\"])\n",
    "    df[\"Order Year\"] = df[\"Order Date\"].dt.year\n",
    "    df[\"Order Month\"] = df[\"Order Date\"].dt.strftime(\"%B\")\n",
    "    df[\"Order Month Digit\"] = df[\"Order Date\"].dt.month\n",
    "\n",
    "    # spend per year\n",
    "    df_orders_year = DataFrame(df.groupby(\"Order Year\").sum()[\"Item Total\"]).reset_index()\n",
    "    fig_spend_per_year, ax_spend_per_year = Figure(figsize=(8, 7), dpi=900).subplots()\n",
    "    barplot(data=df_orders_year, x=\"Order Year\", y=\"Item Total\", palette=\"viridis\", ax=ax_spend_per_year)\n",
    "    ax_spend_per_year.set_ylabel(\"Amount Spent ($)\")\n",
    "    ax_spend_per_year.set_xlabel(\"Date\")\n",
    "    ax_spend_per_year.set_title(\"Amazon Purchase Total By Year\")\n",
    "    max_val = df_orders_year[\"Item Total\"].max()\n",
    "    max_year = list(df_orders_year[df_orders_year[\"Item Total\"] == max_val][\"Order Year\"])[0]\n",
    "\n",
    "    # orders over time\n",
    "    df_copy = df.copy()\n",
    "    df_copy.set_index(\"Order Date\", inplace=True)\n",
    "    df_month_date = DataFrame(df_copy.resample(\"1M\").count()[\"Order ID\"]).reset_index()\n",
    "    df_month_date.columns = [\"date\", \"count\"]\n",
    "    fig_orders_over_time, ax_orders_over_time = Figure(figsize=(8, 7), dpi=900).subplots()\n",
    "    lineplot(data=df_month_date, x=\"date\", y=\"count\", palette=\"viridis\", ax=ax_orders_over_time)\n",
    "    ax_orders_over_time.set_ylabel(\"Purchase Count\")\n",
    "    ax_orders_over_time.set_xlabel(\"Date\")\n",
    "    ax_orders_over_time.set_title(\"Amazon Purchases Over Time\")\n",
    "\n",
    "    # orders over month\n",
    "    df_month = df.groupby([\"Order Month\", \"Order Month Digit\"]).count()[\"Order Date\"].reset_index()\n",
    "    df_month.columns = [\"Month\", \"Month_digit\", \"Order_count\"]\n",
    "    df_month.sort_values(by=\"Month_digit\", inplace=True)\n",
    "    fig_month, ax_month = Figure(figsize=(8, 7), dpi=900).subplots()\n",
    "    barplot(data=df_month, palette=\"viridis\", x=\"Month\", y=\"Order_count\", ax=ax_month)\n",
    "    ax_month.set_xticklabels(df_month[\"Month\"], rotation=45)\n",
    "    ax_month.set_title(\"Amazon Shopping: Monthly Trend\")\n",
    "    ax_month.set_ylabel(\"Purchase Count\")\n",
    "    max_month_val = list(df_month.sort_values(by=\"Order_count\", ascending=False).head(1)[\"Order_count\"])[0]\n",
    "    max_month = list(df_month[df_month[\"Order_count\"] == max_month_val][\"Month\"])[0]\n",
    "\n",
    "    # orders per city\n",
    "    df_cities = DataFrame(df[\"Shipping Address City\"].str.upper().value_counts()).reset_index()\n",
    "    df_cities.columns = [\"City\", \"Order Count\"]\n",
    "    df_cities.sort_values(by=\"Order Count\", inplace=True)\n",
    "    df_cities = df_cities.head(15)\n",
    "    fig_cities, ax_cities = Figure(figsize=(8, 7), dpi=900).subplots()\n",
    "    barplot(data=df_cities, palette=\"viridis\", x=\"City\", y=\"Order Count\", ax=ax_cities)\n",
    "    ax_cities.set_xticklabels(df_cities[\"City\"], rotation=45)\n",
    "    ax_cities.set_title(\"Where Have Your Amazon Packages Gone? Top 15 Cities\")\n",
    "\n",
    "    # order categories\n",
    "    df_cat = df.groupby([\"Category\"]).count()[\"Order Date\"].reset_index()\n",
    "    df_cat.columns = [\"Category\", \"Purchase Count\"]\n",
    "    df_cat.sort_values(by=\"Purchase Count\", ascending=False, inplace=True)\n",
    "    df_cat = df_cat.head(15)\n",
    "    fig_cat, ax_cat = Figure(figsize=(8, 7), dpi=900).subplots()\n",
    "    barplot(data=df_cat, palette=\"viridis\", x=\"Category\", y=\"Purchase Count\", ax=ax_cat)\n",
    "    ax_cat.set_xticklabels(df_cat[\"Category\"], rotation=45, fontsize=8)\n",
    "    ax_cat.set_title(\"Top 15 Purchase Categories\")\n",
    "    ax_cat.set_ylabel(\"Purchase Count\")\n",
    "    pop_cat = list(df_cat.head(1)[\"Category\"])[0]\n",
    "\n",
    "    # month prediction, moving average\n",
    "    data = list(df_month_date[\"count\"])\n",
    "    # fit model\n",
    "    model = ARIMA(data, order=(0, 0, 1))\n",
    "    model_fit = model.fit()\n",
    "    # make prediction\n",
    "    yhat = np.round(model_fit.predict(len(data), len(data))[0])\n",
    "\n",
    "    st.write(\"## **Amazon Purchasing Over Time**\")\n",
    "    st.write(\"-------------------\")\n",
    "    col1, col2 = st.columns(2)\n",
    "    with col1:\n",
    "        st.pyplot(fig_spend_per_year)\n",
    "        st.write(\"This graph showed me that I have depended more and more on Amazon for commerce over time, and especially when there were too many COVID cases in the US to go shopping. Looks like your biggest spending year was {} when you spent ${} on Amazon.\".format(max_year, round(max_val)))\n",
    "    with col2:\n",
    "        st.pyplot(fig_orders_over_time)\n",
    "        st.write(\"For me, this graph was useful because I could see two big upticks, once when I graduated high school and moved in for college and the second when I got my first internship and could actually afford to shop more. I also made a simple moving average model on your data, and predict that next month you will buy {} items.\".format(yhat))\n",
    "\n",
    "    st.write(\"## **More Item Specific Analysis**\")\n",
    "    st.write(\"-------------------\")\n",
    "    col3, col4, col5 = st.columns(3)\n",
    "    with col3:\n",
    "        st.pyplot(fig_month)\n",
    "        st.write(\"Over time, you have bought the most items in {}, a total of {} items. My biggest Amazon month was January, but only because I moved during two Januaries!\".format(max_month, max_month_val))\n",
    "    with col4:\n",
    "        st.pyplot(fig_cities)\n",
    "        st.write(\"I love this graph because it so clearly showed me where I have moved over time!\")\n",
    "    with col5:\n",
    "        st.pyplot(fig_cat)\n",
    "        st.write(\"My biggest category here by far was books, I've bought 3x more books than any other category! Your most popular category was {}\".format(pop_cat))\n",
    "\n",
    "    st.write(\"### **Amazon Smile**\")\n",
    "    st.write(\"-------------------\")\n",
    "    \"\"\"\n",
    "    My good friend [Elle](https://twitter.com/ellebeecher) reminded me the other\n",
    "    day that Amazon has this great program called\n",
    "    [Amazon Smile](https://t.co/F2XATkkBDF?amp=1), where they'll donate .5%\n",
    "    of each purchase to the charity of your choice. If you haven't done that\n",
    "    already, give it a shot!\n",
    "    \"\"\"\n",
    "    total = round(df_copy[\"Item Total\"].sum() * 0.5 * 0.01, 2)\n",
    "    st.write(\"Since as far back as your data goes, you would have donated a total of ${} to charity at no cost to you, so what are you waiting for?\".format(total))\n",
    "\n",
    "st.write(\"-------------------\")\n",
    "st.write(\"Thank you for walking through this Amazon analysis with me! If you liked this, follow me on [Twitter](https//www.twitter.com/tylerjrichards) or take a look at my [new book on Streamlit apps](https://www.amazon.com/Getting-Started-Streamlit-Data-Science-ebook/dp/B095Z1R3BP). If you like budget apps, my personal favorite is [Copilot](https://copilot.money/link/uZ9ZRvAaRXQCqgwE7), check it out and get a free month.\")\n"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
