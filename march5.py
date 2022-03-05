#!/usr/bin/env python
# coding: utf-8

# ## HOUSE PRICE PREDICTION

# In[1]:


import pandas as pd


# In[2]:


housing = pd.read_csv("data.csv")


# In[3]:


housing.head()


# In[4]:


housing.info()


# In[5]:


housing['CHAS'].value_counts()


# In[6]:


housing.describe()


# In[7]:


#get_ipython().run_line_magic('matplotlib', 'inline')


# In[8]:


# # For plotting histogram
# import matplotlib.pyplot as plt
# housing.hist(bins=50, figsize=(20, 15))


# ## Train-Test Splitting

# In[9]:


# For learning purpose
import numpy as np
def split_train_test(data, test_ratio):
    np.random.seed(42)
    shuffled = np.random.permutation(len(data))
    print(shuffled)
    test_set_size = int(len(data) * test_ratio)
    test_indices = shuffled[:test_set_size]
    train_indices = shuffled[test_set_size:] 
    return data.iloc[train_indices], data.iloc[test_indices]


# In[10]:


train_set, test_set = split_train_test(housing, 0.2)


# In[11]:


print(f"Rows in train set: {len(train_set)}\nRows in test set: {len(test_set)}\n")


# In[12]:


#from sklearn.model_selection import train_test_split
#train_set, test_set  = train_test_split(housing, test_size=0.2, random_state=42)
#print(f"Rows in train set: {len(train_set)}\nRows in test set: {len(test_set)}\n")


# In[13]:


from sklearn.model_selection import StratifiedShuffleSplit
split = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
for train_index, test_index in split.split(housing, housing['CHAS']):
    strat_train_set = housing.loc[train_index]
    strat_test_set = housing.loc[test_index]


# In[14]:


strat_test_set['CHAS'].value_counts()


# In[15]:


strat_train_set['CHAS'].value_counts()


# In[16]:


# 95/7


# In[17]:


# 376/28


# In[18]:


housing = strat_train_set.copy()


# ## Looking for Correlations

# In[19]:


corr_matrix = housing.corr()
corr_matrix['MEDV'].sort_values(ascending=False)


# In[20]:


# from pandas.plotting import scatter_matrix
# attributes = ["MEDV", "RM", "ZN", "LSTAT"]
# scatter_matrix(housing[attributes], figsize = (12,8))


# In[21]:


housing.plot(kind="scatter", x="RM", y="MEDV", alpha=0.8)


# ## Trying out Attribute combinations
# 

# In[22]:


housing["TAXRM"] = housing['TAX']/housing['RM']


# In[23]:


housing.head()


# In[24]:


corr_matrix = housing.corr()
corr_matrix['MEDV'].sort_values(ascending=False)


# In[25]:


housing.plot(kind="scatter", x="TAXRM", y="MEDV", alpha=0.8)


# In[26]:


housing = strat_train_set.drop("MEDV", axis=1)
housing_labels = strat_train_set["MEDV"].copy()


# ## Missing Attributes

# In[27]:


# To take care of missing attributes, you have three options:
#     1. Get rid of the missing data points
#     2. Get rid of the whole attribute
#     3. Set the value to some value(0, mean or median)


# In[28]:


a = housing.dropna(subset=["RM"]) #Option 1
a.shape
# Note that the original housing dataframe will remain unchanged


# In[29]:


housing.drop("RM", axis=1).shape # Option 2
# Note that there is no RM column and also note that the original housing dataframe will remain unchanged


# In[30]:


median = housing["RM"].median() # Compute median for Option 3


# In[31]:


housing["RM"].fillna(median) # Option 3
# Note that the original housing dataframe will remain unchanged


# In[32]:


housing.shape


# In[33]:


housing.describe() # before we started filling missing attributes


# In[34]:


from sklearn.impute import SimpleImputer
imputer = SimpleImputer(strategy="median")
imputer.fit(housing)


# In[35]:


imputer.statistics_


# In[36]:


X = imputer.transform(housing)


# In[37]:


housing_tr = pd.DataFrame(X, columns=housing.columns)


# In[38]:


housing_tr.describe()


# ## Scikit-learn Design

# Primarily, three types of objects
# 1. Estimators - It estimates some parameter based on a dataset. Eg. imputer. It has a fit method and transform method. Fit method - Fits the dataset and calculates internal parameters
# 
# 2. Transformers - transform method takes input and returns output based on the learnings from fit(). It also has a convenience function called fit_transform() which fits and then transforms.
# 
# 3. Predictors - LinearRegression model is an example of predictor. fit() and predict() are two common functions. It also gives score() function which will evaluate the predictions.

# ## Feature Scaling

# Primarily, two types of feature scaling methods:
# 1. Min-max scaling (Normalization)
#     (value - min)/(max - min)
#     Sklearn provides a class called MinMaxScaler for this
#     
# 2. Standardization
#     (value - mean)/std
#     Sklearn provides a class called StandardScaler for this
# 

# ## Creating a Pipeline

# In[39]:


from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
my_pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy="median")),
    #     ..... add as many as you want in your pipeline
    ('std_scaler', StandardScaler()),
])


# In[40]:


housing_num_tr = my_pipeline.fit_transform(housing)


# In[41]:


housing_num_tr.shape


# ## Selecting a desired model

# In[42]:


from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
# model = LinearRegression()
# model = DecisionTreeRegressor()
model = RandomForestRegressor()
model.fit(housing_num_tr, housing_labels)


# In[43]:


some_data = housing.iloc[:5]


# In[44]:


some_labels = housing_labels.iloc[:5]


# In[45]:


prepared_data = my_pipeline.transform(some_data)


# In[46]:


model.predict(prepared_data)


# In[47]:


list(some_labels)


# ## Evaluating the model

# In[48]:


from sklearn.metrics import mean_squared_error
housing_predictions = model.predict(housing_num_tr)
mse = mean_squared_error(housing_labels, housing_predictions)
rmse = np.sqrt(mse)


# In[49]:


rmse


# ## Using better evaluation technique - Cross Validation

# In[50]:


# 1 2 3 4 5 6 7 8 9 10
from sklearn.model_selection import cross_val_score
scores = cross_val_score(model, housing_num_tr, housing_labels, scoring="neg_mean_squared_error", cv=10)
rmse_scores = np.sqrt(-scores)


# In[51]:


rmse_scores


# In[52]:


def print_scores(scores):
    print("Scores:", scores)
    print("Mean: ", scores.mean())
    print("Standard deviation: ", scores.std())
    


# In[53]:


print_scores(rmse_scores)


# Quiz: Convert this notebook into a python file and run the pipeline using Visual Studio Code

# ## Saving the model

# In[54]:


from joblib import dump, load
dump(model, 'project.joblib') 


# ## Testing the model on test data

# In[55]:


X_test = strat_test_set.drop("MEDV", axis=1)
Y_test = strat_test_set["MEDV"].copy()
X_test_prepared = my_pipeline.transform(X_test)
final_predictions = model.predict(X_test_prepared)
final_mse = mean_squared_error(Y_test, final_predictions)
final_rmse = np.sqrt(final_mse)
# print(final_predictions, list(Y_test))


# In[56]:


final_rmse


# In[57]:


prepared_data[0]


# ## Using the model

# In[58]:


from joblib import dump, load
import numpy as np
model = load('project.joblib') 
features = np.array([[-5.43942006, 4.12628155, -2.6165014, -0.67288841, -1.42262747,
       -11.44443979304, -49.31238772,  7.61111401, -26.0016879 , -0.5778192 ,
       -0.97491834,  0.41164221, -16.86091034]])
model.predict(features)


#         GRADIO

# In[59]:


print(housing.columns)


# In[60]:


def features( Per_capita_crime_rate_by_town, Proportion_of_residential_land_zoned_for_lots_over_25000_square_feet,Proportion_of_non_retail_business_acres_per_town, Charles_River_dummy_variable, Nitric_oxides_concentration, Average_number_of_rooms_per_dwelling, Proportion_of_owner_occupied_units_built_prior_to_1940, Weighted_distances_to_five_Boston_employment_centres, Index_of_accessibility_to_radial_highways, Full_value_property_tax_rate_per_10000_dollars, Pupil_teacher_ratio_by_town, The_proportion_of_blacks_by_town, percentage_of_lower_status_of_the_population):
    x = np.array([Per_capita_crime_rate_by_town, Proportion_of_residential_land_zoned_for_lots_over_25000_square_feet,Proportion_of_non_retail_business_acres_per_town, Charles_River_dummy_variable, Nitric_oxides_concentration, Average_number_of_rooms_per_dwelling, Proportion_of_owner_occupied_units_built_prior_to_1940, Weighted_distances_to_five_Boston_employment_centres, Index_of_accessibility_to_radial_highways, Full_value_property_tax_rate_per_10000_dollars, Pupil_teacher_ratio_by_town, The_proportion_of_blacks_by_town, percentage_of_lower_status_of_the_population])
    prediction = model.predict(x.reshape(1, -1))
    return prediction
    


# In[61]:


import gradio as gr
outputs = gr.outputs.Textbox()
app = gr.Interface(fn=features, inputs=['number','number','number','number','number','number','number','number', 'number','number','number','number','number'], outputs=outputs,description="HOUSE PRICE PREDICTION")


# In[62]:


app.launch(server_name="0.0.0.0", server_port=4000,)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




