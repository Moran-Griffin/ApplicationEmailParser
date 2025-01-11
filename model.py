# %% [markdown]
# The NLP model that I will use to analyze emails to determine if they are internship-related or not

# %%
#Uncomment and run these cells if nltk is not downloaded
#Solution from https://stackoverflow.com/questions/38916452/nltk-download-ssl-certificate-verify-failed

#%pip install nltk
#import nltk
#import ssl

#try:
#    _create_unverified_https_context = ssl._create_unverified_context
#except AttributeError:
#    pass
#else:
#    ssl._create_default_https_context = _create_unverified_https_context
#
#nltk.download()

# %%
import pandas as pd
import nltk
import joblib
nltk.download('stopwords')
import string

# %%
emails = pd.read_csv('my_emails.csv',header=0)

# %%
emails.dropna(inplace=True)

# %% [markdown]
# PreProcessing

# %%
from nltk.corpus import stopwords

# %%
def text_process(mess):
    """
    Takes in a string of text, then performs the following:
    1. Remove all punctuation
    2. Remove all stopwords
    3. Returns a list of the cleaned text
    """
    # Check characters to see if they are in punctuation
    nopunc = [char for char in mess if char not in string.punctuation]

    # Join the characters again to form the string.
    nopunc = ''.join(nopunc)
    
    # Now just remove any stopwords
    return [word for word in nopunc.split() if word.lower() not in stopwords.words('english')]

# %%
from sklearn.feature_extraction.text import CountVectorizer

# %%
bow_transformer = CountVectorizer(analyzer=text_process).fit(emails['Body'])

# %% [markdown]
# Training the model

# %%
from sklearn.model_selection import train_test_split

mail_train, mail_test, job_train, job_test = \
train_test_split(emails['Body'], emails['Job'], test_size=.2)

# %%
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

mail_model = Pipeline([
    ('bow', CountVectorizer(analyzer=text_process)),
    ('tfidf', TfidfTransformer()),
    ('classifier', MultinomialNB()),
])

# %%
mail_model.fit(mail_train, job_train)

# %%
predictions = mail_model.predict(mail_test)

# %%
from sklearn.metrics import classification_report
print(classification_report(predictions, job_test))

# %% [markdown]
# Testing on my entire E-mail dataset

# %%
big_emails = pd.read_csv("my_emails1.csv")
big_emails.dropna(inplace = True)

# %%
pred2 = mail_model.predict(big_emails)
# Larger test size since model is already trained
mail_train2, mail_test2, job_train2, job_test2 = train_test_split(big_emails['Body'], big_emails['Job'], test_size=.4)

# %%
pred2 = mail_model.predict(mail_test2)
print(classification_report(pred2, job_test2))

# %% [markdown]
# Saving and exporting the model

# %%
joblib.dump(value = mail_model, filename = "mail_model.pkl")


