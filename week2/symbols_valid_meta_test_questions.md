# Test Questions for `symbols_valid_meta.csv`

The following questions have been designed specifically for the `symbols_valid_meta.csv` dataset. You can copy and paste these directly into the Financial Data Analysis Agent (Streamlit App) to test its capabilities.

---

### Data Overview (Describe Tool)
- `Give me a general description and overview of this dataset.`
- `What are the data types of each column in this dataset?`

### Categorical Analysis & Statistics (Stats Tool)
- `What is the total number of ETFs versus non-ETFs in the dataset?`
- `List the top 5 most common Market Categories.`
- `How many unique Listing Exchanges are present in the dataset?`
- `What is the average and maximum Round Lot Size across all securities?`
- `How many securities have a Financial Status of 'N'?`

### Visualizations (Plot Tool)
- `Plot a bar chart showing the count of symbols by Listing Exchange.`
- `Create a pie chart showing the proportion of ETFs versus non-ETFs.`
- `Show a bar chart of the top 10 most common Market Categories.`
- `Plot a pie chart showing the distribution of Nasdaq Traded symbols (Y vs N).`

### Data Filtering (Filter Tool)
- `Filter the dataset to show only symbols where ETF is 'Y' and Listing Exchange is 'Q'.`
- `Show me all the symbols where the Round Lot Size is greater than 100.`
- `Filter the data to find the Security Name and Symbol for 'Apple Inc. - Common Stock'.`
- `Find all securities that are classified as a Test Issue ('Y').`

### Advanced / Cross-Column
- `What percentage of Nasdaq Traded ('Y') symbols are also ETFs ('Y')?`
- `Which Listing Exchange has the highest number of ETFs?`
