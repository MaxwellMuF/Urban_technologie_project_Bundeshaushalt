# Summary of the project

## Questions to Prof Bießmann
The project has developed in such a way that mainly a data set is created. Now the question is, what happens next? Is it more important to do something with this data such as visualization, analysis, clustering, etc.? Or is creating the data set more interesting and should it be developed into an API or at least a structured database?

Options for creating a database:
#### 1. Database
Previously, 10 years of the budget were mapped to the year 2023 (HR10y_on_id.csv, HR10y_on_nlp.csv). If you only map the last 5 years, you get almost twice as many matches because the last 5 years match more than the last 10.

#### 2. API:
Currently 11 Budgets.xlsx are used as the data basis (number can be extended). So far, the last year 2023 has always been taken as the reference year, i.e. all other years are mapped to 2023. This means that all bookings (rows) that do not occur in 2023 are lost. If you use a different year (e.g. 2018), you get completely different results (mapped rows) for the subset of years to be mapped (e.g. 2012-2017).
A simple API or just a well-structured pipeline in the form of a python file could generalize this approach.
The user could then specify a reference year (e.g. 2018) and a period to be mapped (e.g. 2012-2017) and get a dataset in about 25min.
I'm thinking of simply running through all embeddings for the years 2012-2023 once (on the cluster) and creating a database with them. As an example, for the year 2015 there would be either 11 csv files with a total of 14MB or one json file with a total of 20MB. 
This would allow a user to create a dataset locally and without BERT in seconds (pd.merge(ref_year, [year_1,...,year_n])). 

#### 3. Docker Image
I could also build a Docker image and load it onto the DATEXIS registry. The raw data is very small at 5MB and could be integrated into the Docker image. So everyone could generate their data with a template yaml. (e.g. yaml variable: reference year: 2018 and period: 2012-2017)


## 1. Data download (1_Download_data.ipynb)
The notebook (Download_data.ipynb) downloads the data. Since there is no sitemap and the url makes unforeseen changes every year (e.g. “.../v2/...” or “.../ist/...”), this unfortunately had to be done manually.

## 2. Data cleaning und preparing (2_Data_procession.ipynb)
Around 6k bookings are listed each year. Only some of the bookings occur in all 10 years under consideration. A part is therefore lost.
Issue: There is no unique id. By combining the columns ("Epl." + "Kap." + "Tit."), a unique id could be created and approx. 1k of the 6k rows could be mapped in the first step (over 10 years, see "HR10y_on_id.csv"). The problem is that hte new id is not constant over the years because the columns ("Epl.", "Kap.", "Tit.") have changed.

## 3. Datenmapping mit NLP-Methoden (3_embeddings.py)
The approach is to use an encoder model (BERT or similar) to embed a newly created column (for a reference year, here 2023). The resulting vector database can be used - after the other years have also been embedded - to find the next vector for the year 2023. In this way, the rows (“bookings”) of other years are mapped to the row in 2023 that is most similar.

## 4. Check the mappings and repeat step 3 (4_Check_embeddings.ipynb)
There are many problems with mapping and the data seems very challenging:
- The name (col “Zweckbestimmung”) is not unique. For example, the value “Vermischte Verwaltungsausgaben” occurs 119 times in 2012 and 137 times in 2022. The values of the column “IST 2022” (price €) for these rows run in a range of 1k - 30m.
- the new id + “Zweckbestimmung” gives a better index, but the FP (false positiv) predictions cause problems (see "example_data/check_mapping_80.txt"). The solution is to create a new column containing “all available information”. id ("Epl." + "Kap." + "Tit.") + “Zweckbestimmung” + price (e.g. col “IST 2022”) and embed it. 
- the embedding model does not handle numbers well, so a mapper was used to turn numbers into words ({"0" : "null", ..., "9" : "neun"}), which worked surprisingly well.
- names such as “Bürgergeld” and “Arbeitslosengeld II” are not matchable, which is why a manual mapper was used here as an example (but only in this case and as an example)
- Each line (reference year 2023) may only be mapped once. And FP should be avoided. The mapper was set so that each line may only be used once (memory) + a threshold value of 85% similarity (cosine similarity) was reached + all df was sorted by price so that the large items are mapped first.

## Conclusion
Overall, another 2k rows were mapped. So out of 6k a total of 3k were mapped. Unfortunately, it is difficult to estimate whether there are still FP predictions among them.
Since a lot of time was spent on mapping, the evaluation will be somewhat shorter. So the main success of the project is to have created a dataset of more than 10 that could be used in other projects (perhaps also good?).
