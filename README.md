# Instruction on how to use data_transparency_analysis
This file includes codes for data analysis on data-transparency reported to BSCC. There are three main parts: data pre-processing, data visualization and Urban & Rural Analysis

As for data pre-processing part: data-transparency reporting to BSCC is aggregated to county/facility level and then the averages are calculated.

As for data visualization part: the data-transparency of facilities is shown on map and that of counties is shown on scattergram. The conclusions are listed in each part.

As for Urban & Rural Analysis part: the relationship between data-transparency and urban-level is calculated. The results show that there is no correlation.

[Here](https://github.com/covidincustody/data-transparency/blob/main/Code/data_transparency_utils.py) is the functions for those three parts

Reminder: There is no need to change the dataset links in the files but the raw data are also shown in the repository.

Please contact info@covidincustody.org for any questions or concerns.

# Usage
There are no prerequisites or installation required. The preprocessing results and data visulization/analysis results will be stored in the same directory as utils.py and run.py. Once both code files are downloaded, please run the following:
```python3 run.py```
