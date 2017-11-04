
# coding: utf-8

# In[4]:


import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
#get_ipython().magic(u'matplotlib inline')
from sklearn.feature_selection import RFE, f_regression
from sklearn.linear_model import (LinearRegression, Ridge, Lasso, RandomizedLasso)
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor


# In[67]:


house = pd.read_csv("/home/shilpitha/Desktop/kc_house_data.csv")
house.head()


# ### **To see the distribution id and the price we used the Barplot of id vs price**

# In[ ]:



plt.figure(figsize = (12,6))
sns.barplot(house['id'],house['price'], alpha = 0.9,color = 'darkorange')
plt.xticks(rotation = 'vertical')
plt.xlabel('id', fontsize =14)
plt.ylabel('price', fontsize = 14)
plt.show()


# In[40]:


# Checking the null values
print(house.isnull().sum())


# **Calculating age of house for better analysis**
# 
# **Creating another column named age_of_house for visualization**

# In[41]:


import datetime
current_year = datetime.datetime.now().year
house["age_of_house"] = current_year - pd.to_datetime(house["date"]).dt.year
house.head()


# ## **Checking the info of the house data**

# In[42]:


house.info()


# ##  **checking the columns names**

# In[43]:


house.columns


# ## Selecting features and target

# In[44]:


feature_cols = [ u'age_of_house',  u'bedrooms', u'bathrooms', u'sqft_living',
       u'sqft_lot', u'floors', u'waterfront', u'view', u'condition', u'grade',
       u'sqft_above', u'sqft_basement', u'yr_built', u'yr_renovated']
x = house[feature_cols]
y = house["price"]


# ## Splitting Training and Test Data

# In[45]:


from sklearn.model_selection import train_test_split
x_train,x_test,y_train,y_test = train_test_split(x, y, random_state=3)


# In[46]:


# Fitting Data to Linear Regressor using scikit
from sklearn.linear_model import LinearRegression
regressor = LinearRegression()
regressor.fit(x_train, y_train)


# In[47]:


accuracy = regressor.score(x_test, y_test)
"Accuracy: {}%".format(int(round(accuracy * 100)))


# ## **The above Accuracy was not so good it is coming like 66% so we are taking the Lasso Regression, Random Forest feature ranking, Linear Model Feature Ranking**
# 
# ** Before that we will use the Seaborn Pairplot to check the classical linear distribution of the data points , then we used the correlation heatmap **
# 
# **method: indicates the correlation coefficient to be computed. The default is pearson correlation coefficient which measures the linear dependence between two variables. kendall and spearman correlation methods are non-parametric rank-based correlation test**
# 

# In[48]:


# Pairplot
g = sns.pairplot(house[['sqft_lot','sqft_above','price','sqft_living','bedrooms']], hue='bedrooms', palette='Blues',size=4)
g.set(xticklabels=[])


# In[49]:


str_list = [] # empty list to contain columns with strings (words)
for colname, colvalue in house.iteritems():
    if type(colvalue[1]) == str:
         str_list.append(colname)
# Get to the numeric columns by inversion            
num_list = house.columns.difference(str_list) 
# Create Dataframe containing only numerical features
house_num = house[num_list]
f, ax = plt.subplots(figsize=(16, 12))
plt.title('Pearson Correlation of features')
# Draw the heatmap using seaborn
sns.heatmap(house_num.astype(float).corr(),linewidths=0.25,vmax=1.0, square=True, cmap="gist_rainbow", linecolor='k', annot=True)


# **The data is pretty clean. There are no pesky nulls which we need to treat and most of the features are in numeric format. Let's go ahead and drop the "id" and "date" columns as these 2 features will not be used in this analysis.**

# In[50]:


# Dropping the id and date columns
house = house.drop(['id', 'date'],axis=1)


# ***Again we will do Pairplot Visualisation without id and date in the house data**

# In[51]:


str_list = [] # empty list to contain columns with strings (words)
for colname, colvalue in house.iteritems():
    if type(colvalue[1]) == str:
         str_list.append(colname)
# Get to the numeric columns by inversion            
num_list = house.columns.difference(str_list) 
# Create Dataframe containing only numerical features
house_num = house[num_list]
f, ax = plt.subplots(figsize=(16, 12))
plt.title('Pearson Correlation of features')
# Draw the heatmap using seaborn
sns.heatmap(house_num.astype(float).corr(),linewidths=0.25,vmax=1.0, square=True, cmap="PuBuGn", linecolor='k', annot=True)


# In[52]:


# First extract the target variable which is our House prices
Y = house.price.values
# Drop price from the house dataframe and create a matrix out of the house data
house = house.drop(['price'], axis=1)
X = house.as_matrix()
# Store the column/feature names into a list "colnames"
colnames = house.columns 


# In[53]:


# Define dictionary to store our rankings
ranks = {}
# Create our function which stores the feature rankings to the ranks dictionary
def ranking(ranks, names, order=1):
    minmax = MinMaxScaler()
    ranks = minmax.fit_transform(order*np.array([ranks]).T).T[0]
    ranks = map(lambda x: round(x,2), ranks)
    return dict(zip(names, ranks))


# In[54]:


# Finally let's run our Selection Stability method with Randomized Lasso
rlasso = RandomizedLasso(alpha=0.04)
rlasso.fit(X, Y)
ranks["rlasso/Stability"] = ranking(np.abs(rlasso.scores_), colnames)
print('finished')


#  ### **Randomized Lasso value for the all variables in the Datasets**

# In[55]:


print(ranks["rlasso/Stability"])


# In[69]:


# Using Linear Regression
lr = LinearRegression(normalize=True)
lr.fit(X,Y)
ranks["LinReg"] = ranking(np.abs(lr.coef_), colnames)

# Using Ridge 
ridge = Ridge(alpha = 7)
ridge.fit(X,Y)
ranks['Ridge'] = ranking(np.abs(ridge.coef_), colnames)

# Using Lasso
lasso = Lasso(alpha=.05)
lasso.fit(X, Y)
ranks["Lasso"] = ranking(np.abs(lasso.coef_), colnames)


# ### **To select either the best or worst-performing feature we can use the Recursive Feature Elimination or RFE Sklearn conveniently possesses a RFE function via the sklearn.feature_selection call**

# In[70]:


# Construct our Linear Regression model
lr = LinearRegression(normalize=True)
lr.fit(X,Y)
#stop the search when only the last feature is left
rfe = RFE(lr, n_features_to_select=1, verbose =3 )
rfe.fit(X,Y)
ranks["RFE"] = ranking(list(map(float, rfe.ranking_)), colnames, order=-1)


# ### **Now, with the matrix above, the numbers and layout does not seem very easy or pleasant to the eye. Therefore, let's just collate the mean ranking score attributed to each of the feature and plot that via Seaborn's factorplot.**

# In[71]:


# Create empty dictionary to store the mean value calculated from all the scores
r = {}
for name in colnames:
    r[name] = round(np.mean([ranks[method][name] 
                             for method in ranks.keys()]), 2)
 
methods = sorted(ranks.keys())
ranks["Mean"] = r
methods.append("Mean")
 
print("\t%s" % "\t".join(methods))
for name in colnames:
    print("%s\t%s" % (name, "\t".join(map(str, 
                         [ranks[method][name] for method in methods]))))


# In[77]:


# Put the mean scores into a Pandas dataframe
meanplot = pd.DataFrame(list(r.items()), columns= ['Feature','Mean Ranking'])

# Sort the dataframe
meanplot = meanplot.sort_values('Mean Ranking', ascending=False)
# Let's plot the ranking of the features
sns.factorplot(x="Mean Ranking", y="Feature", data = meanplot, kind="bar", size=4, aspect=1.9, palette='rainbow')


# ## **** Now we selecting the best features and fit the model, here we are again loading the datasets because we are preprocessed the data so we need some features to select in order that we need to load data****

# In[5]:


house1 = pd.read_csv("../input/kc_house_data.csv")


# In[6]:


import datetime
current_year = datetime.datetime.now().year
house1["age_of_house"] = current_year - pd.to_datetime(house1["date"]).dt.year
house1.head()


# ### **Below we selected the best features what we obtained from the ranking of the features table and graph**
# 

# In[7]:


feature_cols = [ u'bedrooms', u'bathrooms', u'sqft_living',
       u'sqft_lot', u'floors', u'waterfront', u'view', u'condition', u'grade',
       u'sqft_above', u'sqft_basement', u'yr_built', u'yr_renovated',u'lat']
x = house1[feature_cols]
y = house1["price"]


# In[8]:


from sklearn.model_selection import train_test_split
x_train,x_test,y_train,y_test = train_test_split(x, y, random_state=3)


# In[9]:


# Fitting Data to Linear Regressor using scikit
from sklearn.linear_model import LinearRegression
regressor = LinearRegression()
regressor.fit(x_train, y_train)


# In[10]:


accuracy = regressor.score(x_test, y_test)
"Accuracy: {}%".format(int(round(accuracy * 100)))


# ## ** We are following the backward elimination procedure we will check the accuracy every time**

# In[12]:


feature_cols1 = [ u'bedrooms', u'bathrooms', u'sqft_living',
       u'sqft_lot', u'waterfront', u'view', u'grade',
       u'sqft_above', u'sqft_basement',u'lat']
x1 = house1[feature_cols1]


# In[13]:


from sklearn.model_selection import train_test_split
x_train1,x_test1,y_train1,y_test1 = train_test_split(x1, y, random_state=3)
# Fitting Data to Linear Regressor using scikit
from sklearn.linear_model import LinearRegression
regressor1 = LinearRegression()
regressor1.fit(x_train1, y_train1)


# In[14]:


accuracy1 = regressor1.score(x_test1, y_test1)
"Accuracy: {}%".format(int(round(accuracy1 * 100)))


# In[ ]:


feature_cols3 = [u'age_of_house',  u'bedrooms', u'bathrooms',
                 u'floors', u'waterfront', u'view', u'condition',
                 u'grade',u'zipcode', u'yr_built']
x3 = house1[feature_cols3]
from sklearn.model_selection import train_test_split
x_train3,x_test3,y_train3,y_test3 = train_test_split(x3, y, random_state=3)
# Fitting Data to Linear Regressor using scikit
from sklearn.linear_model import LinearRegression
regressor3 = LinearRegression()
regressor3.fit(x_train3, y_train3)
accuracy3 = regressor3.score(x_test3, y_test3)
"Accuracy: {}%".format(int(round(accuracy3 * 100)))


# ## ** So we conclude that Top 6 and last 3 or 4 variables will affect tha accuracy**
